import asyncio
import json
import logging
import os
import time
import uuid
from collections import defaultdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ichin.ai-router")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
PROVIDERS_FILE = os.path.join(DATA_DIR, "providers.json")
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ProviderType(str, Enum):
    openai = "openai"
    anthropic = "anthropic"
    google = "google"
    groq = "groq"
    cohere = "cohere"
    mistral = "mistral"
    togetherai = "togetherai"
    fireworks = "fireworks"
    deepseek = "deepseek"
    perplexity = "perplexity"
    local_llama = "local_llama"
    local_phi = "local_phi"
    local_gemma = "local_gemma"
    llama_cpp = "llama_cpp"
    ollama = "ollama"


class RoutingStrategy(str, Enum):
    latency = "latency"
    cost = "cost"
    quality = "quality"
    privacy = "privacy"
    balanced = "balanced"
    fallback = "fallback"


class CapabilityDomain(str, Enum):
    chat = "chat"
    code = "code"
    reasoning = "reasoning"
    creative_writing = "creative_writing"
    analysis = "analysis"
    translation = "translation"
    summarization = "summarization"
    function_calling = "function_calling"
    vision = "vision"
    audio = "audio"
    embedding = "embedding"


class ModelTier(str, Enum):
    free = "free"
    low_cost = "low_cost"
    standard = "standard"
    premium = "premium"
    enterprise = "enterprise"


class ExecutionMode(str, Enum):
    streaming = "streaming"
    batch = "batch"
    background = "background"


class FailoverStrategy(str, Enum):
    sequential = "sequential"
    parallel = "parallel"
    fan_out = "fan_out"


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class ModelCapability(BaseModel):
    domain: CapabilityDomain
    score: float = Field(default=0.5, ge=0.0, le=1.0)
    max_tokens: int = 4096
    supports_streaming: bool = True
    supports_function_calling: bool = False
    supports_vision: bool = False
    supports_audio: bool = False
    context_window: int = 4096
    languages: List[str] = ["en"]


class ProviderConfig(BaseModel):
    id: str
    name: str
    provider_type: ProviderType
    base_url: str = ""
    api_key_env: Optional[str] = None
    models: List[str] = []
    default_model: str = ""
    tier: ModelTier = ModelTier.standard
    capabilities: List[ModelCapability] = []
    latency_p50_ms: float = 1000.0
    latency_p95_ms: float = 5000.0
    cost_per_1k_input: float = 0.0
    cost_per_1k_output: float = 0.0
    is_offline: bool = False
    requires_internet: bool = True
    privacy_rating: float = Field(default=0.5, ge=0.0, le=1.0)
    rate_limit_rpm: int = 60
    rate_limit_tpm: int = 100000
    enabled: bool = True
    fallback_providers: List[str] = []
    health_check_endpoint: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class CompletionRequest(BaseModel):
    messages: List[Dict[str, str]]
    model: Optional[str] = None
    provider: Optional[ProviderType] = None
    strategy: RoutingStrategy = RoutingStrategy.balanced
    max_tokens: Optional[int] = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    stream: bool = False
    domain: CapabilityDomain = CapabilityDomain.chat
    priority: str = "normal"
    max_cost: Optional[float] = None
    max_latency_ms: Optional[float] = None
    require_privacy: bool = False
    require_offline: bool = False
    require_vision: bool = False
    require_function_calling: bool = False
    failover_strategy: FailoverStrategy = FailoverStrategy.sequential
    session_id: Optional[str] = None
    metadata: Dict[str, Any] = {}


class CompletionResponse(BaseModel):
    id: str
    provider_used: str
    model_used: str
    content: str
    finish_reason: str = "stop"
    usage: Dict[str, int] = {}
    latency_ms: float = 0.0
    cost_estimate: float = 0.0
    routing_path: List[str] = []
    fallback_occurred: bool = False


class StreamChunk(BaseModel):
    id: str
    provider_used: str
    model_used: str
    content: str = ""
    finish_reason: Optional[str] = None
    usage: Optional[Dict[str, int]] = None


class ProviderHealth(BaseModel):
    provider_id: str
    healthy: bool
    latency_ms: float
    last_check: str
    error: Optional[str] = None


class RoutingDecision(BaseModel):
    provider_id: str
    model: str
    score: float
    factors: Dict[str, float] = {}
    reason: str = ""


class ProviderStats(BaseModel):
    provider_id: str
    total_requests: int = 0
    total_errors: int = 0
    avg_latency_ms: float = 0.0
    avg_cost: float = 0.0
    success_rate: float = 1.0
    last_used: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    uptime: float
    providers_count: int
    providers_healthy: int


# ---------------------------------------------------------------------------
# JSON Persistence
# ---------------------------------------------------------------------------

def _load_json(path: str, default: Any = None) -> Any:
    if not os.path.exists(path):
        return default if default is not None else []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        logger.error("Failed to load %s: %s", path, exc)
        return default if default is not None else []


def _save_json(path: str, data: Any) -> None:
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
    except OSError as exc:
        logger.error("Failed to save %s: %s", path, exc)


# ---------------------------------------------------------------------------
# Built-in Provider Registry
# ---------------------------------------------------------------------------

BUILTIN_PROVIDERS: Dict[str, ProviderConfig] = {
    "openai": ProviderConfig(
        id="openai",
        name="OpenAI",
        provider_type=ProviderType.openai,
        base_url="https://api.openai.com/v1",
        api_key_env="OPENAI_API_KEY",
        models=["gpt-4o", "gpt-4o-mini", "gpt-4-turbo", "gpt-3.5-turbo"],
        default_model="gpt-4o-mini",
        tier=ModelTier.premium,
        capabilities=[
            ModelCapability(domain=CapabilityDomain.chat, score=0.95, context_window=128000, supports_streaming=True, supports_function_calling=True, supports_vision=True),
            ModelCapability(domain=CapabilityDomain.code, score=0.90, context_window=128000, supports_function_calling=True),
            ModelCapability(domain=CapabilityDomain.reasoning, score=0.92, context_window=128000),
            ModelCapability(domain=CapabilityDomain.creative_writing, score=0.88, context_window=128000),
            ModelCapability(domain=CapabilityDomain.analysis, score=0.91, context_window=128000),
            ModelCapability(domain=CapabilityDomain.translation, score=0.85, context_window=128000),
            ModelCapability(domain=CapabilityDomain.summarization, score=0.90, context_window=128000),
        ],
        latency_p50_ms=800, latency_p95_ms=4000,
        cost_per_1k_input=0.01, cost_per_1k_output=0.03,
        privacy_rating=0.3, rate_limit_rpm=500, rate_limit_tpm=1000000,
    ),
    "anthropic": ProviderConfig(
        id="anthropic",
        name="Anthropic",
        provider_type=ProviderType.anthropic,
        base_url="https://api.anthropic.com/v1",
        api_key_env="ANTHROPIC_API_KEY",
        models=["claude-3-opus", "claude-3-sonnet", "claude-3-haiku"],
        default_model="claude-3-haiku",
        tier=ModelTier.premium,
        capabilities=[
            ModelCapability(domain=CapabilityDomain.chat, score=0.94, context_window=200000, supports_streaming=True, supports_vision=True),
            ModelCapability(domain=CapabilityDomain.code, score=0.93, context_window=200000),
            ModelCapability(domain=CapabilityDomain.reasoning, score=0.93, context_window=200000),
            ModelCapability(domain=CapabilityDomain.analysis, score=0.92, context_window=200000),
            ModelCapability(domain=CapabilityDomain.creative_writing, score=0.90, context_window=200000),
        ],
        latency_p50_ms=1200, latency_p95_ms=5000,
        cost_per_1k_input=0.015, cost_per_1k_output=0.075,
        privacy_rating=0.4, rate_limit_rpm=400, rate_limit_tpm=800000,
    ),
    "google": ProviderConfig(
        id="google",
        name="Google AI",
        provider_type=ProviderType.google,
        base_url="https://generativelanguage.googleapis.com/v1beta",
        api_key_env="GOOGLE_API_KEY",
        models=["gemini-1.5-pro", "gemini-1.5-flash"],
        default_model="gemini-1.5-flash",
        tier=ModelTier.standard,
        capabilities=[
            ModelCapability(domain=CapabilityDomain.chat, score=0.90, context_window=1048576, supports_streaming=True, supports_vision=True),
            ModelCapability(domain=CapabilityDomain.code, score=0.88, context_window=1048576),
            ModelCapability(domain=CapabilityDomain.reasoning, score=0.87, context_window=1048576),
            ModelCapability(domain=CapabilityDomain.analysis, score=0.88, context_window=1048576),
        ],
        latency_p50_ms=700, latency_p95_ms=3500,
        cost_per_1k_input=0.0, cost_per_1k_output=0.0,
        privacy_rating=0.3, rate_limit_rpm=360, rate_limit_tpm=500000,
    ),
    "groq": ProviderConfig(
        id="groq",
        name="Groq",
        provider_type=ProviderType.groq,
        base_url="https://api.groq.com/openai/v1",
        api_key_env="GROQ_API_KEY",
        models=["llama-3.1-70b", "llama-3.1-8b", "mixtral-8x7b"],
        default_model="llama-3.1-8b",
        tier=ModelTier.low_cost,
        capabilities=[
            ModelCapability(domain=CapabilityDomain.chat, score=0.85, context_window=32768, supports_streaming=True),
            ModelCapability(domain=CapabilityDomain.code, score=0.82, context_window=32768),
            ModelCapability(domain=CapabilityDomain.reasoning, score=0.80, context_window=32768),
        ],
        latency_p50_ms=300, latency_p95_ms=1500,
        cost_per_1k_input=0.0, cost_per_1k_output=0.0,
        privacy_rating=0.4, rate_limit_rpm=30, rate_limit_tpm=30000,
    ),
    "ollama": ProviderConfig(
        id="ollama",
        name="Ollama Local",
        provider_type=ProviderType.ollama,
        base_url="http://localhost:11434/v1",
        models=["llama3.2", "phi3", "gemma2", "mistral"],
        default_model="llama3.2",
        tier=ModelTier.free,
        capabilities=[
            ModelCapability(domain=CapabilityDomain.chat, score=0.70, context_window=8192, supports_streaming=True),
            ModelCapability(domain=CapabilityDomain.code, score=0.65, context_window=8192),
            ModelCapability(domain=CapabilityDomain.reasoning, score=0.60, context_window=8192),
            ModelCapability(domain=CapabilityDomain.summarization, score=0.70, context_window=8192),
        ],
        latency_p50_ms=200, latency_p95_ms=1000,
        cost_per_1k_input=0.0, cost_per_1k_output=0.0,
        is_offline=True, requires_internet=False,
        privacy_rating=1.0, rate_limit_rpm=99999, rate_limit_tpm=999999,
    ),
    "llama_cpp": ProviderConfig(
        id="llama_cpp",
        name="llama.cpp Server",
        provider_type=ProviderType.llama_cpp,
        base_url="http://localhost:8080/v1",
        models=["local-model"],
        default_model="local-model",
        tier=ModelTier.free,
        capabilities=[
            ModelCapability(domain=CapabilityDomain.chat, score=0.65, context_window=4096, supports_streaming=True),
            ModelCapability(domain=CapabilityDomain.code, score=0.60, context_window=4096),
        ],
        latency_p50_ms=100, latency_p95_ms=500,
        cost_per_1k_input=0.0, cost_per_1k_output=0.0,
        is_offline=True, requires_internet=False,
        privacy_rating=1.0, rate_limit_rpm=99999, rate_limit_tpm=999999,
    ),
    "deepseek": ProviderConfig(
        id="deepseek",
        name="DeepSeek",
        provider_type=ProviderType.deepseek,
        base_url="https://api.deepseek.com/v1",
        api_key_env="DEEPSEEK_API_KEY",
        models=["deepseek-chat", "deepseek-coder"],
        default_model="deepseek-chat",
        tier=ModelTier.low_cost,
        capabilities=[
            ModelCapability(domain=CapabilityDomain.chat, score=0.86, context_window=65536, supports_streaming=True),
            ModelCapability(domain=CapabilityDomain.code, score=0.89, context_window=65536),
            ModelCapability(domain=CapabilityDomain.reasoning, score=0.84, context_window=65536),
        ],
        latency_p50_ms=900, latency_p95_ms=4500,
        cost_per_1k_input=0.0005, cost_per_1k_output=0.002,
        privacy_rating=0.2, rate_limit_rpm=300, rate_limit_tpm=500000,
    ),
    "mistral": ProviderConfig(
        id="mistral",
        name="Mistral AI",
        provider_type=ProviderType.mistral,
        base_url="https://api.mistral.ai/v1",
        api_key_env="MISTRAL_API_KEY",
        models=["mistral-large", "mistral-medium", "mistral-small"],
        default_model="mistral-small",
        tier=ModelTier.standard,
        capabilities=[
            ModelCapability(domain=CapabilityDomain.chat, score=0.87, context_window=32768, supports_streaming=True),
            ModelCapability(domain=CapabilityDomain.code, score=0.85, context_window=32768, supports_function_calling=True),
            ModelCapability(domain=CapabilityDomain.reasoning, score=0.83, context_window=32768),
        ],
        latency_p50_ms=750, latency_p95_ms=3800,
        cost_per_1k_input=0.007, cost_per_1k_output=0.021,
        privacy_rating=0.5, rate_limit_rpm=250, rate_limit_tpm=400000,
    ),
}


# ---------------------------------------------------------------------------
# Routing Engine
# ---------------------------------------------------------------------------

class RoutingEngine:
    def __init__(self):
        self._providers: Dict[str, ProviderConfig] = {}
        self._stats: Dict[str, ProviderStats] = defaultdict(ProviderStats)
        self._latency_history: Dict[str, List[float]] = defaultdict(list)
        self._rate_limit_tracker: Dict[str, Dict[str, int]] = defaultdict(lambda: {"requests": 0, "tokens": 0, "reset_at": 0.0})
        self._health_cache: Dict[str, Tuple[bool, float, float]] = {}
        self._load_providers()

    def _load_providers(self) -> None:
        custom = _load_json(PROVIDERS_FILE, [])
        for p in BUILTIN_PROVIDERS.values():
            self._providers[p.id] = p.model_copy(deep=True)
        for p_data in custom:
            try:
                cfg = ProviderConfig(**p_data)
                self._providers[cfg.id] = cfg
            except Exception as exc:
                logger.warning("Skipping invalid custom provider: %s", exc)
        logger.info("Loaded %d providers (%d built-in, %d custom)",
                     len(self._providers), len(BUILTIN_PROVIDERS), len(custom))

    def _persist_providers(self) -> None:
        custom = [p.model_dump(mode="json") for p in self._providers.values()
                  if p.id not in BUILTIN_PROVIDERS]
        _save_json(PROVIDERS_FILE, custom)

    def list_providers(self) -> List[ProviderConfig]:
        return list(self._providers.values())

    def get_provider(self, provider_id: str) -> Optional[ProviderConfig]:
        return self._providers.get(provider_id)

    def add_provider(self, config: ProviderConfig) -> ProviderConfig:
        if config.id in self._providers:
            raise HTTPException(status_code=409, detail=f"Provider '{config.id}' already exists")
        self._providers[config.id] = config
        self._persist_providers()
        return config

    def remove_provider(self, provider_id: str) -> bool:
        if provider_id in BUILTIN_PROVIDERS:
            raise HTTPException(status_code=403, detail="Cannot remove built-in providers")
        result = self._providers.pop(provider_id, None)
        if result:
            self._persist_providers()
            return True
        return False

    # -----------------------------------------------------------------------
    # Provider Selection
    # -----------------------------------------------------------------------

    def select_provider(self, req: CompletionRequest) -> RoutingDecision:
        candidates = self._get_candidates(req)
        if not candidates:
            raise HTTPException(status_code=503, detail="No available providers matching criteria")

        if req.provider:
            matching = [c for c in candidates if c[0].provider_type == req.provider]
            if matching:
                candidates = matching
            else:
                logger.warning("Requested provider %s not available, using fallback", req.provider)

        strategy = req.strategy
        if req.require_offline:
            strategy = RoutingStrategy.privacy

        scored: List[Tuple[float, ProviderConfig, str, Dict[str, float]]] = []
        for provider, model in candidates:
            score, factors = self._score_provider(provider, model, req, strategy)
            scored.append((score, provider, model, factors))

        scored.sort(key=lambda x: x[0], reverse=True)

        if not scored:
            raise HTTPException(status_code=503, detail="No providers scored high enough")

        best_score, best_provider, best_model, best_factors = scored[0]
        return RoutingDecision(
            provider_id=best_provider.id,
            model=best_model,
            score=best_score,
            factors=best_factors,
            reason=self._build_decision_reason(best_provider, best_model, best_score, best_factors, strategy),
        )

    def _get_candidates(self, req: CompletionRequest) -> List[Tuple[ProviderConfig, str]]:
        candidates = []
        for provider in self._providers.values():
            if not provider.enabled:
                continue
            if req.require_offline and provider.requires_internet:
                continue
            if req.require_privacy and provider.privacy_rating < 0.7:
                continue

            if req.max_cost is not None:
                avg_cost = (provider.cost_per_1k_input + provider.cost_per_1k_output) / 2
                if avg_cost > req.max_cost:
                    continue

            if req.max_latency_ms is not None and provider.latency_p50_ms > req.max_latency_ms:
                continue

            model = self._select_model(provider, req)
            if model is None:
                continue

            if not self._check_rate_limit(provider):
                continue

            health_ok, _, _ = self._health_cache.get(provider.id, (True, 0, 0))
            if not health_ok:
                continue

            candidates.append((provider, model))

        return candidates

    def _select_model(self, provider: ProviderConfig, req: CompletionRequest) -> Optional[str]:
        if req.model:
            if req.model in provider.models:
                return req.model
            return None

        cap = self._find_best_capability(provider, req.domain)
        if cap is None:
            return None

        if req.require_vision and not cap.supports_vision:
            return None
        if req.require_function_calling and not cap.supports_function_calling:
            return None

        return provider.default_model or (provider.models[0] if provider.models else None)

    def _find_best_capability(self, provider: ProviderConfig, domain: CapabilityDomain) -> Optional[ModelCapability]:
        matching = [c for c in provider.capabilities if c.domain == domain]
        if not matching:
            return None
        return max(matching, key=lambda c: c.score)

    def _score_provider(
        self, provider: ProviderConfig, model: str, req: CompletionRequest, strategy: RoutingStrategy
    ) -> Tuple[float, Dict[str, float]]:
        factors: Dict[str, float] = {}

        if strategy == RoutingStrategy.latency:
            recent_latencies = self._latency_history.get(provider.id, [])
            avg_latency = sum(recent_latencies[-20:]) / max(len(recent_latencies[-20:]), 1) if recent_latencies else provider.latency_p50_ms
            latency_score = max(0.0, 1.0 - (avg_latency / 5000.0))
            factors["latency"] = latency_score
            return latency_score, factors

        if strategy == RoutingStrategy.cost:
            avg_cost = (provider.cost_per_1k_input + provider.cost_per_1k_output) / 2
            cost_score = max(0.0, 1.0 - (avg_cost / 0.1))
            factors["cost"] = cost_score
            return cost_score, factors

        if strategy == RoutingStrategy.privacy:
            factors["privacy"] = provider.privacy_rating
            if provider.is_offline:
                return 1.0, {**factors, "offline": 1.0}
            return provider.privacy_rating, factors

        if strategy == RoutingStrategy.quality:
            cap = self._find_best_capability(provider, req.domain)
            quality_score = cap.score if cap else 0.5
            factors["quality"] = quality_score
            return quality_score, factors

        latency = provider.latency_p50_ms
        latency_norm = max(0.0, 1.0 - (latency / 5000.0))
        cost = (provider.cost_per_1k_input + provider.cost_per_1k_output) / 2
        cost_norm = max(0.0, 1.0 - (cost / 0.1))
        cap = self._find_best_capability(provider, req.domain)
        quality = cap.score if cap else 0.5
        privacy = provider.privacy_rating

        if strategy == RoutingStrategy.balanced:
            score = (latency_norm * 0.2) + (cost_norm * 0.2) + (quality * 0.4) + (privacy * 0.2)
        elif strategy == RoutingStrategy.fallback:
            score = (latency_norm * 0.3) + (cost_norm * 0.1) + (quality * 0.3) + (privacy * 0.3)
        else:
            score = quality

        factors.update({
            "latency": latency_norm,
            "cost": cost_norm,
            "quality": quality,
            "privacy": privacy,
        })
        return score, factors

    def _build_decision_reason(
        self, provider: ProviderConfig, model: str, score: float, factors: Dict[str, float], strategy: RoutingStrategy
    ) -> str:
        top_factor = max(factors, key=factors.get) if factors else "unknown"
        return (
            f"Selected {provider.name}/{model} (score={score:.3f}) "
            f"via {strategy.value} strategy, driven by {top_factor} factor"
        )

    def _check_rate_limit(self, provider: ProviderConfig) -> bool:
        tracker = self._rate_limit_tracker[provider.id]
        now = time.monotonic()
        if now - tracker["reset_at"] > 60.0:
            tracker["requests"] = 0
            tracker["tokens"] = 0
            tracker["reset_at"] = now
        return tracker["requests"] < provider.rate_limit_rpm

    def _track_usage(self, provider_id: str, tokens: int = 0) -> None:
        tracker = self._rate_limit_tracker[provider_id]
        tracker["requests"] += 1
        tracker["tokens"] += tokens
        stats = self._stats[provider_id]
        stats.total_requests += 1

    def _track_latency(self, provider_id: str, latency_ms: float) -> None:
        self._latency_history[provider_id].append(latency_ms)
        if len(self._latency_history[provider_id]) > 100:
            self._latency_history[provider_id] = self._latency_history[provider_id][-100:]
        stats = self._stats[provider_id]
        stats.avg_latency_ms = (stats.avg_latency_ms * (stats.total_requests - 1) + latency_ms) / max(stats.total_requests, 1)

    # -----------------------------------------------------------------------
    # Completion Execution
    # -----------------------------------------------------------------------

    async def complete(self, req: CompletionRequest) -> CompletionResponse:
        start = time.monotonic()
        routing_path: List[str] = []
        fallback_occurred = False

        decision = self.select_provider(req)
        provider = self._providers[decision.provider_id]
        routing_path.append(f"{provider.name}/{decision.model}")

        try:
            result = await self._call_provider(provider, decision.model, req)
            latency = (time.monotonic() - start) * 1000
            self._track_latency(provider.id, latency)
            self._track_usage(provider.id, result.get("usage", {}).get("total_tokens", 0))
            cost_est = self._estimate_cost(provider, result.get("usage", {}))
            return CompletionResponse(
                id=str(uuid.uuid4()),
                provider_used=provider.id,
                model_used=decision.model,
                content=result.get("content", ""),
                finish_reason=result.get("finish_reason", "stop"),
                usage=result.get("usage", {}),
                latency_ms=round(latency, 2),
                cost_estimate=cost_est,
                routing_path=routing_path,
                fallback_occurred=False,
            )
        except Exception as exc:
            logger.warning("Primary provider %s failed: %s", provider.id, exc)
            fallback_providers = provider.fallback_providers or list(self._providers.keys())
            for fallback_id in fallback_providers:
                if fallback_id == provider.id:
                    continue
                fallback = self._providers.get(fallback_id)
                if not fallback or not fallback.enabled:
                    continue
                try:
                    routing_path.append(f"{fallback.name}/{decision.model}")
                    result = await self._call_provider(fallback, fallback.default_model, req)
                    latency = (time.monotonic() - start) * 1000
                    fallback_occurred = True
                    return CompletionResponse(
                        id=str(uuid.uuid4()),
                        provider_used=fallback.id,
                        model_used=fallback.default_model,
                        content=result.get("content", ""),
                        finish_reason=result.get("finish_reason", "stop"),
                        usage=result.get("usage", {}),
                        latency_ms=round(latency, 2),
                        cost_estimate=0.0,
                        routing_path=routing_path,
                        fallback_occurred=True,
                    )
                except Exception as fb_exc:
                    logger.warning("Fallback %s also failed: %s", fallback_id, fb_exc)
                    continue

            raise HTTPException(status_code=503, detail=f"All providers failed. Last error: {exc}")

    async def _call_provider(self, provider: ProviderConfig, model: str, req: CompletionRequest) -> Dict[str, Any]:
        if provider.is_offline:
            return self._simulate_offline(provider, model, req)

        api_key = os.environ.get(provider.api_key_env) if provider.api_key_env else None
        if provider.requires_internet and not api_key:
            logger.warning("No API key found for %s (env: %s)", provider.id, provider.api_key_env)
            raise ValueError(f"API key not configured for {provider.name}")

        headers = {"Content-Type": "application/json"}
        if api_key:
            if provider.provider_type in (ProviderType.anthropic,):
                headers["x-api-key"] = api_key
                headers["anthropic-version"] = "2023-06-01"
            else:
                headers["Authorization"] = f"Bearer {api_key}"

        url = f"{provider.base_url.rstrip('/')}/chat/completions"
        if provider.provider_type == ProviderType.anthropic:
            url = f"{provider.base_url.rstrip('/')}/messages"

        body: Dict[str, Any] = {
            "model": model,
            "messages": req.messages,
            "temperature": req.temperature,
        }
        if req.max_tokens:
            body["max_tokens"] = req.max_tokens
        if req.stream:
            body["stream"] = True

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(url, json=body, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                if provider.provider_type == ProviderType.anthropic:
                    content = "".join(c.get("text", "") for c in data.get("content", []))
                    return {
                        "content": content,
                        "finish_reason": data.get("stop_reason", "stop"),
                        "usage": {
                            "prompt_tokens": data.get("usage", {}).get("input_tokens", 0),
                            "completion_tokens": data.get("usage", {}).get("output_tokens", 0),
                            "total_tokens": data.get("usage", {}).get("input_tokens", 0) + data.get("usage", {}).get("output_tokens", 0),
                        },
                    }
                choice = data.get("choices", [{}])[0]
                return {
                    "content": choice.get("message", {}).get("content", ""),
                    "finish_reason": choice.get("finish_reason", "stop"),
                    "usage": data.get("usage", {}),
                }
        except httpx.HTTPStatusError as exc:
            raise ValueError(f"HTTP {exc.response.status_code}: {exc.response.text[:200]}")
        except httpx.RequestError as exc:
            raise ValueError(f"Connection failed: {exc}")

    def _simulate_offline(self, provider: ProviderConfig, model: str, req: CompletionRequest) -> Dict[str, Any]:
        last_msg = req.messages[-1]["content"] if req.messages else ""
        word_count = len(last_msg.split())
        simulated = f"[Offline {provider.name}/{model} response to: {last_msg[:100]}...]"
        return {
            "content": simulated,
            "finish_reason": "stop",
            "usage": {"prompt_tokens": word_count, "completion_tokens": word_count // 2, "total_tokens": word_count + word_count // 2},
        }

    @staticmethod
    def _estimate_cost(provider: ProviderConfig, usage: Dict[str, int]) -> float:
        in_tokens = usage.get("prompt_tokens", 0) / 1000 * provider.cost_per_1k_input
        out_tokens = usage.get("completion_tokens", 0) / 1000 * provider.cost_per_1k_output
        return round(in_tokens + out_tokens, 6)

    # -----------------------------------------------------------------------
    # Health Checks
    # -----------------------------------------------------------------------

    async def check_health(self, provider_id: str) -> ProviderHealth:
        provider = self._providers.get(provider_id)
        if not provider:
            raise HTTPException(status_code=404, detail=f"Provider '{provider_id}' not found")

        start = time.monotonic()
        try:
            if provider.is_offline:
                latency = (time.monotonic() - start) * 1000
                result = ProviderHealth(provider_id=provider_id, healthy=True, latency_ms=round(latency, 2), last_check=datetime.utcnow().isoformat())
            elif provider.health_check_endpoint:
                async with httpx.AsyncClient(timeout=5.0) as client:
                    resp = await client.get(provider.health_check_endpoint)
                    resp.raise_for_status()
                    latency = (time.monotonic() - start) * 1000
                    result = ProviderHealth(provider_id=provider_id, healthy=True, latency_ms=round(latency, 2), last_check=datetime.utcnow().isoformat())
            else:
                api_key = os.environ.get(provider.api_key_env) if provider.api_key_env else None
                if not api_key and provider.requires_internet:
                    latency = (time.monotonic() - start) * 1000
                    result = ProviderHealth(provider_id=provider_id, healthy=False, latency_ms=round(latency, 2), last_check=datetime.utcnow().isoformat(), error="API key not configured")
                else:
                    latency = (time.monotonic() - start) * 1000
                    result = ProviderHealth(provider_id=provider_id, healthy=True, latency_ms=round(latency, 2), last_check=datetime.utcnow().isoformat())

            self._health_cache[provider_id] = (result.healthy, result.latency_ms, time.monotonic())
            return result
        except Exception as exc:
            latency = (time.monotonic() - start) * 1000
            result = ProviderHealth(provider_id=provider_id, healthy=False, latency_ms=round(latency, 2), last_check=datetime.utcnow().isoformat(), error=str(exc))
            self._health_cache[provider_id] = (False, latency, time.monotonic())
            return result

    async def check_all_health(self) -> List[ProviderHealth]:
        tasks = [self.check_health(pid) for pid in self._providers]
        return await asyncio.gather(*tasks, return_exceptions=True)

    def get_stats(self) -> Dict[str, ProviderStats]:
        return dict(self._stats)


# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="ICHIN OS Service — AI Router",
    version="1.0.0",
    description="Provider-agnostic AI routing with cost-aware, latency-optimized, privacy-aware model selection",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = RoutingEngine()
_start_time = time.monotonic()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse)
async def health():
    healthy = sum(1 for p in engine._health_cache.values() if p[0]) if engine._health_cache else 0
    return HealthResponse(
        status="ok",
        service="ichin-ai-router",
        version="1.0.0",
        uptime=time.monotonic() - _start_time,
        providers_count=len(engine._providers),
        providers_healthy=healthy or len(engine._providers),
    )


@app.get("/providers")
async def list_providers():
    return [p.model_dump(mode="json") for p in engine.list_providers()]


@app.get("/provider/{provider_id}")
async def get_provider(provider_id: str):
    provider = engine.get_provider(provider_id)
    if not provider:
        raise HTTPException(status_code=404, detail=f"Provider '{provider_id}' not found")
    return provider.model_dump(mode="json")


@app.post("/providers")
async def add_provider(body: ProviderConfig):
    try:
        return engine.add_provider(body).model_dump(mode="json")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.delete("/provider/{provider_id}")
async def delete_provider(provider_id: str):
    if not engine.remove_provider(provider_id):
        raise HTTPException(status_code=404, detail=f"Provider '{provider_id}' not found")
    return {"status": "deleted", "provider_id": provider_id}


@app.post("/route", response_model=RoutingDecision)
async def route_request(body: CompletionRequest):
    try:
        decision = engine.select_provider(body)
        return decision
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Routing failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/complete", response_model=CompletionResponse)
async def complete(body: CompletionRequest):
    try:
        body.stream = False
        return await engine.complete(body)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Completion failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/provider/{provider_id}/health", response_model=ProviderHealth)
async def check_provider_health(provider_id: str):
    try:
        return await engine.check_health(provider_id)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/health/all")
async def check_all_health():
    results = await engine.check_all_health()
    return {"results": [r.model_dump() if isinstance(r, ProviderHealth) else {"error": str(r)} for r in results]}


@app.get("/stats")
async def get_stats():
    stats = engine.get_stats()
    return {k: v.model_dump() for k, v in stats.items()}


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8020, reload=True)
