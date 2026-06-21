import asyncio
import json
import logging
import math
import time
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ichin.orchestrator")

# ---------------------------------------------------------------------------
# Domain Enums
# ---------------------------------------------------------------------------

class RequestType(str, Enum):
    task = "task"
    question = "question"
    system_action = "system_action"
    chat = "chat"
    automation = "automation"


class UrgencyLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class SystemMode(str, Enum):
    normal = "normal"
    focus = "focus"
    deep_focus = "deep_focus"
    lock = "lock"


class ExecutionStatus(str, Enum):
    approved = "approved"
    requires_confirmation = "requires_confirmation"
    denied = "denied"
    escalated = "escalated"


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class AgentInput(BaseModel):
    request: str
    workspace: Optional[str] = None
    mode: SystemMode = SystemMode.normal
    context: Optional[Dict[str, Any]] = None


class AgentOutput(BaseModel):
    agent_name: str
    recommendation: str
    reasoning: str
    confidence: float = Field(ge=0.0, le=1.0)
    risk_score: float = Field(ge=0.0, le=1.0)
    efficiency_score: float = Field(ge=0.0, le=1.0, default=0.5)

    @field_validator("confidence", "risk_score", "efficiency_score")
    @classmethod
    def validate_range(cls, v: float) -> float:
        return max(0.0, min(1.0, v))


class OrchestratorDecision(BaseModel):
    decision_id: str
    result: str
    confidence: float
    agents_used: List[str]
    risk_level: RiskLevel
    action_log: List[Dict[str, Any]]
    execution_status: ExecutionStatus
    reasoning_summary: str
    requires_confirmation: bool = False
    mode: SystemMode


class ClassifyResponse(BaseModel):
    request_type: RequestType
    urgency: UrgencyLevel
    workspace_context: Optional[str] = None
    confidence: float


class SessionContext(BaseModel):
    session_id: str
    recent_interactions: List[Dict[str, Any]] = []
    working_memory: Dict[str, Any] = {}
    active_mode: SystemMode = SystemMode.normal
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(default_factory=lambda: datetime.utcnow() + timedelta(hours=1))


class ExecuteDecisionRequest(BaseModel):
    decision_id: str
    action: str
    params: Optional[Dict[str, Any]] = None
    confirmed: bool = False


class ExecuteDecisionResponse(BaseModel):
    status: str
    result: Optional[str] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    uptime: float
    active_sessions: int
    mode: SystemMode


class OrchestrateRequest(BaseModel):
    request: str
    session_id: Optional[str] = None
    workspace: Optional[str] = None
    mode: SystemMode = SystemMode.normal
    context: Optional[Dict[str, Any]] = None


class OrchestrateResponse(BaseModel):
    decision: OrchestratorDecision
    session_id: str


# ---------------------------------------------------------------------------
# Mode Controller
# ---------------------------------------------------------------------------

class ModeRules(BaseModel):
    min_confidence_threshold: float
    allow_execution: bool
    allow_suggestions: bool
    distraction_detection: bool
    intervention_level: str
    max_risk_allowed: float
    restricted_apps: List[str] = []
    agent_weights_override: Optional[Dict[str, float]] = None


MODE_RULES: Dict[SystemMode, ModeRules] = {
    SystemMode.normal: ModeRules(
        min_confidence_threshold=0.3,
        allow_execution=True,
        allow_suggestions=True,
        distraction_detection=False,
        intervention_level="none",
        max_risk_allowed=0.5,
    ),
    SystemMode.focus: ModeRules(
        min_confidence_threshold=0.5,
        allow_execution=True,
        allow_suggestions=True,
        distraction_detection=False,
        intervention_level="soft",
        max_risk_allowed=0.4,
    ),
    SystemMode.deep_focus: ModeRules(
        min_confidence_threshold=0.7,
        allow_execution=True,
        allow_suggestions=False,
        distraction_detection=True,
        intervention_level="strong",
        max_risk_allowed=0.2,
    ),
    SystemMode.lock: ModeRules(
        min_confidence_threshold=0.85,
        allow_execution=False,
        allow_suggestions=True,
        distraction_detection=True,
        intervention_level="strict",
        max_risk_allowed=0.1,
        restricted_apps=["entertainment", "social_media", "gaming"],
    ),
}


class ModeController:
    def __init__(self):
        self._current_mode: SystemMode = SystemMode.normal

    @property
    def current_mode(self) -> SystemMode:
        return self._current_mode

    def set_mode(self, mode: SystemMode) -> None:
        logger.info("Mode switch: %s -> %s", self._current_mode.value, mode.value)
        self._current_mode = mode

    def get_rules(self) -> ModeRules:
        return MODE_RULES[self._current_mode]

    def validate_decision(self, decision: OrchestratorDecision) -> OrchestratorDecision:
        rules = self.get_rules()
        if decision.confidence < rules.min_confidence_threshold:
            decision.execution_status = ExecutionStatus.denied
            decision.action_log.append({
                "action": "mode_denied",
                "reason": f"Confidence {decision.confidence:.2f} below threshold {rules.min_confidence_threshold}",
                "mode": self._current_mode.value,
                "timestamp": datetime.utcnow().isoformat(),
            })
            return decision
        risk_map = {"low": 0.1, "medium": 0.4, "high": 0.8}
        if risk_map.get(decision.risk_level, 0) > rules.max_risk_allowed:
            decision.execution_status = ExecutionStatus.denied
            decision.action_log.append({
                "action": "risk_denied",
                "reason": f"Risk level {decision.risk_level} exceeds max allowed {rules.max_risk_allowed}",
                "mode": self._current_mode.value,
                "timestamp": datetime.utcnow().isoformat(),
            })
            return decision
        if not rules.allow_execution:
            decision.execution_status = ExecutionStatus.denied
            decision.action_log.append({
                "action": "execution_blocked",
                "reason": f"Mode {self._current_mode.value} does not allow execution",
                "mode": self._current_mode.value,
                "timestamp": datetime.utcnow().isoformat(),
            })
            return decision
        return decision


# ---------------------------------------------------------------------------
# Memory System  (in-memory, Redis-ready interface)
# ---------------------------------------------------------------------------

class MemoryEntry(BaseModel):
    key: str
    value: Any
    ttl: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def is_expired(self) -> bool:
        if self.ttl is None:
            return False
        return datetime.utcnow() > self.created_at + timedelta(seconds=self.ttl)


class LongTermMemory(BaseModel):
    pattern_id: str
    embedding: List[float]
    content: str
    tags: List[str] = []
    access_count: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class MemorySystem:
    def __init__(self):
        self._working: Dict[str, Dict[str, MemoryEntry]] = {}
        self._long_term: List[LongTermMemory] = []
        self._cleanup_interval = 60
        self._last_cleanup = time.monotonic()

    def _auto_cleanup(self) -> None:
        now = time.monotonic()
        if now - self._last_cleanup < self._cleanup_interval:
            return
        self._last_cleanup = now
        for session_id in list(self._working.keys()):
            expired_keys = [
                k for k, v in self._working[session_id].items()
                if v.is_expired()
            ]
            for k in expired_keys:
                del self._working[session_id][k]
            if not self._working[session_id]:
                del self._working[session_id]

    def store_working(self, session_id: str, key: str, value: Any, ttl: Optional[int] = 3600) -> None:
        self._auto_cleanup()
        self._working.setdefault(session_id, {})[key] = MemoryEntry(
            key=key, value=value, ttl=ttl,
        )
        logger.debug("Working memory stored: session=%s key=%s", session_id, key)

    def get_working(self, session_id: str, key: str) -> Optional[Any]:
        self._auto_cleanup()
        entry = self._working.get(session_id, {}).get(key)
        if entry is None or entry.is_expired():
            return None
        return entry.value

    def get_all_working(self, session_id: str) -> Dict[str, Any]:
        self._auto_cleanup()
        result: Dict[str, Any] = {}
        for key, entry in self._working.get(session_id, {}).items():
            if not entry.is_expired():
                result[key] = entry.value
        return result

    def store_long_term(self, content: str, tags: Optional[List[str]] = None) -> str:
        pattern_id = str(uuid.uuid4())
        embedding = self._compute_embedding(content)
        memory = LongTermMemory(
            pattern_id=pattern_id,
            embedding=embedding,
            content=content,
            tags=tags or [],
        )
        self._long_term.append(memory)
        if len(self._long_term) > 1000:
            self._compact_long_term()
        logger.debug("Long-term memory stored: id=%s", pattern_id)
        return pattern_id

    def query_long_term(self, query: str, top_k: int = 5) -> List[LongTermMemory]:
        if not self._long_term:
            return []
        query_emb = self._compute_embedding(query)
        scored = []
        for mem in self._long_term:
            sim = self._cosine_similarity(query_emb, mem.embedding)
            scored.append((sim, mem))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [mem for _, mem in scored[:top_k]]
        for mem in results:
            mem.access_count += 1
        return results

    def build_context(self, session_id: str, workspace: Optional[str] = None) -> Dict[str, Any]:
        working = self.get_all_working(session_id)
        recent_query = working.get("last_request", "")
        memories = self.query_long_term(recent_query, top_k=3) if recent_query else []
        context = {
            "session_id": session_id,
            "working_memory": working,
            "long_term_memories": [m.content for m in memories],
            "workspace": workspace,
            "timestamp": datetime.utcnow().isoformat(),
        }
        logger.debug("Context built for session=%s", session_id)
        return context

    def _compute_embedding(self, text: str) -> List[float]:
        words = text.lower().split()
        if not words:
            return [0.0] * 64
        rng = np.random.RandomState(hash(text) % (2**31))
        emb = rng.randn(64).astype(float)
        emb = emb / (np.linalg.norm(emb) + 1e-10)
        return emb.tolist()

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        arr_a = np.array(a, dtype=np.float64)
        arr_b = np.array(b, dtype=np.float64)
        dot = float(np.dot(arr_a, arr_b))
        norm = float(np.linalg.norm(arr_a) * np.linalg.norm(arr_b) + 1e-10)
        return dot / norm

    def _compact_long_term(self) -> None:
        clusters: Dict[str, List[LongTermMemory]] = {}
        for mem in self._long_term:
            for tag in mem.tags:
                clusters.setdefault(tag, []).append(mem)
        merged: List[LongTermMemory] = []
        for tag, mems in clusters.items():
            if len(mems) > 1:
                combined = " | ".join(m.content for m in mems[:5])
                merged.append(LongTermMemory(
                    pattern_id=str(uuid.uuid4()),
                    embedding=self._compute_embedding(combined),
                    content=combined,
                    tags=[tag],
                    access_count=sum(m.access_count for m in mems),
                ))
            else:
                merged.append(mems[0])
        self._long_term = merged
        logger.info("Long-term memory compacted: %d entries", len(self._long_term))


# ---------------------------------------------------------------------------
# Agent Definitions
# ---------------------------------------------------------------------------

class BaseAgent:
    name: str = "base"
    description: str = ""

    async def process(self, inp: AgentInput) -> AgentOutput:
        raise NotImplementedError

    def _make_output(
        self,
        recommendation: str,
        reasoning: str,
        confidence: float,
        risk_score: float,
        efficiency_score: float = 0.5,
    ) -> AgentOutput:
        return AgentOutput(
            agent_name=self.name,
            recommendation=recommendation,
            reasoning=reasoning,
            confidence=confidence,
            risk_score=risk_score,
            efficiency_score=efficiency_score,
        )


class StudyAgent(BaseAgent):
    name = "study"
    description = "Handles study-related tasks, learning paths, and educational content"

    async def process(self, inp: AgentInput) -> AgentOutput:
        req_lower = inp.request.lower()
        if any(w in req_lower for w in ["study", "learn", "read", "review", "flashcard", "quiz"]):
            return self._make_output(
                recommendation="Generate study plan with spaced repetition",
                reasoning="Request matches study domain patterns",
                confidence=0.82,
                risk_score=0.05,
                efficiency_score=0.75,
            )
        return self._make_output(
            recommendation="No study action needed",
            reasoning="Request does not match study domain",
            confidence=0.4,
            risk_score=0.02,
            efficiency_score=0.3,
        )


class CodingAgent(BaseAgent):
    name = "coding"
    description = "Handles code generation, debugging, and software development tasks"

    async def process(self, inp: AgentInput) -> AgentOutput:
        req_lower = inp.request.lower()
        words = ["code", "program", "debug", "function", "algorithm", "api", "implement", "test", "script", "python", "javascript", "rust"]
        if any(w in req_lower for w in words):
            return self._make_output(
                recommendation="Provide code solution with explanation",
                reasoning="Request contains programming-related keywords",
                confidence=0.85,
                risk_score=0.15,
                efficiency_score=0.8,
            )
        return self._make_output(
            recommendation="No coding action needed",
            reasoning="Request does not match coding domain",
            confidence=0.35,
            risk_score=0.02,
            efficiency_score=0.3,
        )


class LearningAgent(BaseAgent):
    name = "learning"
    description = "Suggests learning resources, tracks skill development, and identifies knowledge gaps"

    async def process(self, inp: AgentInput) -> AgentOutput:
        req_lower = inp.request.lower()
        if any(w in req_lower for w in ["learn", "understand", "concept", "knowledge", "skill", "tutorial", "course", "resource"]):
            return self._make_output(
                recommendation="Curate learning resources and skill pathway",
                reasoning="Request involves learning or skill development",
                confidence=0.78,
                risk_score=0.05,
                efficiency_score=0.7,
            )
        return self._make_output(
            recommendation="No learning action needed",
            reasoning="Request does not match learning domain",
            confidence=0.3,
            risk_score=0.02,
            efficiency_score=0.25,
        )


class ProductivityAgent(BaseAgent):
    name = "productivity"
    description = "Manages task lists, priorities, time management, and workflow optimization"

    async def process(self, inp: AgentInput) -> AgentOutput:
        req_lower = inp.request.lower()
        if any(w in req_lower for w in ["task", "todo", "schedule", "priority", "deadline", "organize", "plan", "manage", "time", "productivity"]):
            return self._make_output(
                recommendation="Optimize task prioritization and workflow",
                reasoning="Request relates to productivity and task management",
                confidence=0.8,
                risk_score=0.08,
                efficiency_score=0.85,
            )
        return self._make_output(
            recommendation="No productivity action needed",
            reasoning="Request does not match productivity domain",
            confidence=0.3,
            risk_score=0.02,
            efficiency_score=0.3,
        )


class FocusAgent(BaseAgent):
    name = "focus"
    description = "Detects distractions, enforces focus modes, and maintains concentration"

    async def process(self, inp: AgentInput) -> AgentOutput:
        req_lower = inp.request.lower()
        distraction_words = ["distract", "focus", "concentrate", "break", "pause", "interrupt", "notification", "noise"]
        if inp.mode in (SystemMode.deep_focus, SystemMode.lock):
            if any(w in req_lower for w in distraction_words):
                return self._make_output(
                    recommendation="Apply focus enforcement: block distractions",
                    reasoning="Distraction detected in deep focus/lock mode",
                    confidence=0.9,
                    risk_score=0.1,
                    efficiency_score=0.9,
                )
            return self._make_output(
                recommendation="Maintain current focus mode restrictions",
                reasoning="Active mode requires sustained focus enforcement",
                confidence=0.85,
                risk_score=0.05,
                efficiency_score=0.85,
            )
        if inp.mode == SystemMode.focus:
            return self._make_output(
                recommendation="Soft focus guidance: minimize interruptions",
                reasoning="Focus mode active with reduced intervention",
                confidence=0.65,
                risk_score=0.1,
                efficiency_score=0.6,
            )
        return self._make_output(
            recommendation="No focus intervention needed",
            reasoning="Normal mode allows full flexibility",
            confidence=0.4,
            risk_score=0.05,
            efficiency_score=0.3,
        )


class SecurityAgent(BaseAgent):
    name = "security"
    description = "Validates actions against security policies, detects threats, and enforces permissions"

    async def process(self, inp: AgentInput) -> AgentOutput:
        req_lower = inp.request.lower()
        sensitive_keywords = [
            "delete", "remove", "sudo", "admin", "password", "token", "secret",
            "permission", "access", "grant", "revoke", "install", "uninstall",
            "execute", "shell", "command", "network", "firewall",
        ]
        matched = [w for w in sensitive_keywords if w in req_lower]
        if matched:
            risk = min(0.3 + len(matched) * 0.15, 0.95)
            return self._make_output(
                recommendation="Security review required before execution",
                reasoning=f"Sensitive keywords detected: {', '.join(matched)}",
                confidence=0.88,
                risk_score=risk,
                efficiency_score=0.7,
            )
        if inp.mode == SystemMode.lock:
            return self._make_output(
                recommendation="Lock mode: strict security enforcement active",
                reasoning="Lock mode requires maximum security scrutiny",
                confidence=0.95,
                risk_score=0.05,
                efficiency_score=0.85,
            )
        return self._make_output(
            recommendation="No security concerns detected",
            reasoning="Request passes security scan",
            confidence=0.75,
            risk_score=0.05,
            efficiency_score=0.6,
        )


class CalendarAgent(BaseAgent):
    name = "calendar"
    description = "Manages events, schedules, meetings, and time blocking"

    async def process(self, inp: AgentInput) -> AgentOutput:
        req_lower = inp.request.lower()
        if any(w in req_lower for w in ["calendar", "event", "meeting", "schedule", "appointment", "remind", "deadline", "date", "time"]):
            return self._make_output(
                recommendation="Manage calendar events and scheduling",
                reasoning="Request involves calendar or time-based operations",
                confidence=0.8,
                risk_score=0.1,
                efficiency_score=0.75,
            )
        return self._make_output(
            recommendation="No calendar action needed",
            reasoning="Request does not match calendar domain",
            confidence=0.3,
            risk_score=0.02,
            efficiency_score=0.2,
        )


class ResearchAgent(BaseAgent):
    name = "research"
    description = "Performs information gathering, analysis, and fact-checking"

    async def process(self, inp: AgentInput) -> AgentOutput:
        req_lower = inp.request.lower()
        if any(w in req_lower for w in ["research", "search", "find", "lookup", "investigate", "analyze", "explore", "what is", "how does", "why does", "tell me about", "information", "data", "source", "reference"]):
            return self._make_output(
                recommendation="Conduct research and synthesize findings",
                reasoning="Request involves information gathering or analysis",
                confidence=0.83,
                risk_score=0.08,
                efficiency_score=0.78,
            )
        return self._make_output(
            recommendation="No research action needed",
            reasoning="Request does not match research domain",
            confidence=0.3,
            risk_score=0.02,
            efficiency_score=0.25,
        )


# ---------------------------------------------------------------------------
# Input Classification
# ---------------------------------------------------------------------------

class InputClassifier:
    TYPE_PATTERNS: Dict[RequestType, List[str]] = {
        RequestType.task: ["do", "run", "execute", "create", "make", "build", "write", "update", "complete", "finish", "setup", "configure"],
        RequestType.question: ["what", "why", "how", "when", "where", "who", "which", "explain", "define", "meaning", "difference", "?", "tell me"],
        RequestType.system_action: ["install", "delete", "remove", "sudo", "admin", "system", "setting", "config", "update", "restart", "shutdown", "reboot", "network", "disk"],
        RequestType.chat: ["hello", "hi", "hey", "how are you", "thanks", "good", "great", "okay", "sure", "yes", "no", "maybe"],
        RequestType.automation: ["automate", "workflow", "pipeline", "cron", "scheduled", "trigger", "when", "if this", "auto", "batch", "script"],
    }

    def classify(self, request: str, workspace: Optional[str] = None) -> Tuple[RequestType, UrgencyLevel, float]:
        req_lower = request.lower().strip()

        best_type = RequestType.task
        best_score = 0.0
        for rtype, patterns in self.TYPE_PATTERNS.items():
            score = sum(1 for p in patterns if p in req_lower) / max(len(patterns), 1)
            normalized = score * (1.0 if rtype != RequestType.chat else 0.7)
            if normalized > best_score:
                best_score = normalized
                best_type = rtype

        if best_score < 0.05:
            best_type = RequestType.chat
            best_score = 0.5

        urgency = self._classify_urgency(req_lower, best_type)
        confidence = min(best_score + 0.2, 1.0)

        return best_type, urgency, confidence

    @staticmethod
    def _classify_urgency(text: str, rtype: RequestType) -> UrgencyLevel:
        critical_words = ["urgent", "critical", "emergency", "asap", "immediately", "now", "important"]
        high_words = ["soon", "today", "deadline", "due", "need", "must", "required"]

        if rtype == RequestType.system_action:
            return UrgencyLevel.high

        critical = sum(1 for w in critical_words if w in text)
        high = sum(1 for w in high_words if w in text)

        if critical >= 2:
            return UrgencyLevel.critical
        if critical >= 1:
            return UrgencyLevel.high
        if high >= 2:
            return UrgencyLevel.medium
        if high >= 1:
            return UrgencyLevel.medium
        return UrgencyLevel.low


# ---------------------------------------------------------------------------
# Agent Selector
# ---------------------------------------------------------------------------

# Service URLs for integration routing
SERVICE_URLS = {
    "ai_router": "http://localhost:8020",
    "voice_engine": "http://localhost:8030",
    "browser_engine": "http://localhost:8040",
    "ai_metasearch": "http://localhost:8050",
    "mail_ai": "http://localhost:8060",
    "knowledge_graph": "http://localhost:8070",
    "memory_engine": "http://localhost:8003",
    "agents": "http://localhost:8012",
    "ai_studio": "http://localhost:8016",
}

AGENT_REGISTRY: Dict[str, BaseAgent] = {
    "study": StudyAgent(),
    "coding": CodingAgent(),
    "learning": LearningAgent(),
    "productivity": ProductivityAgent(),
    "focus": FocusAgent(),
    "security": SecurityAgent(),
    "calendar": CalendarAgent(),
    "research": ResearchAgent(),
}

WORKSPACE_AGENT_MAP: Dict[str, List[str]] = {
    "study": ["study", "learning", "productivity", "focus", "research"],
    "coding": ["coding", "research", "productivity", "focus", "security"],
    "learning": ["learning", "study", "research", "productivity"],
    "productivity": ["productivity", "calendar", "focus", "research"],
    "research": ["research", "learning", "study", "productivity"],
    "browsing": ["research", "focus", "security", "productivity"],
    "voice": ["research", "focus", "productivity"],
    "general": ["research", "productivity", "focus", "security"],
}

REQUEST_TYPE_AGENT_MAP: Dict[RequestType, List[str]] = {
    RequestType.task: ["productivity", "coding", "study", "calendar", "focus"],
    RequestType.question: ["research", "learning", "study", "security", "coding"],
    RequestType.system_action: ["security", "focus", "productivity"],
    RequestType.chat: ["research", "learning", "productivity"],
    RequestType.automation: ["coding", "security", "productivity", "focus"],
}


def select_agents(request_type: RequestType, workspace: Optional[str]) -> List[str]:
    primary = REQUEST_TYPE_AGENT_MAP.get(request_type, ["productivity", "research"])
    workspace_agents = WORKSPACE_AGENT_MAP.get(workspace or "general", [])
    selected: List[str] = []
    seen: set = set()
    for agent in primary:
        if agent not in seen:
            selected.append(agent)
            seen.add(agent)
    for agent in workspace_agents:
        if agent not in seen:
            selected.append(agent)
            seen.add(agent)
    if not selected:
        selected = ["research", "productivity", "focus", "security"]
    logger.info("Selected agents for %s (workspace=%s): %s", request_type.value, workspace, selected)
    return selected


# ---------------------------------------------------------------------------
# Decision Engine  (Weighted Voting + Conflict Resolution)
# ---------------------------------------------------------------------------

MODE_WEIGHTS: Dict[SystemMode, Dict[str, float]] = {
    SystemMode.normal: {
        "productivity": 1.2, "study": 1.0, "coding": 1.0,
        "learning": 1.0, "research": 1.0, "focus": 0.8,
        "security": 1.0, "calendar": 0.8,
    },
    SystemMode.focus: {
        "focus": 1.3, "productivity": 1.1, "security": 1.1,
        "study": 1.0, "coding": 0.9, "learning": 0.9,
        "research": 0.9, "calendar": 0.6,
    },
    SystemMode.deep_focus: {
        "focus": 1.5, "security": 1.3, "productivity": 1.0,
        "study": 1.0, "coding": 0.8, "learning": 0.8,
        "research": 0.7, "calendar": 0.5,
    },
    SystemMode.lock: {
        "security": 1.5, "focus": 1.3, "productivity": 0.9,
        "study": 0.8, "coding": 0.7, "learning": 0.7,
        "research": 0.7, "calendar": 0.5,
    },
}

WORKSPACE_WEIGHTS: Dict[str, Dict[str, float]] = {
    "study": {"study": 1.3, "learning": 1.2},
    "coding": {"coding": 1.3, "research": 1.1},
    "learning": {"learning": 1.3, "study": 1.2, "research": 1.1},
    "productivity": {"productivity": 1.3, "calendar": 1.2},
    "research": {"research": 1.3, "learning": 1.1},
}


class DecisionEngine:
    def __init__(self, mode_controller: ModeController):
        self.mode_controller = mode_controller

    def aggregate(self, outputs: List[AgentOutput], workspace: Optional[str]) -> OrchestratorDecision:
        if not outputs:
            return OrchestratorDecision(
                decision_id=str(uuid.uuid4()),
                result="No agent outputs available",
                confidence=0.0,
                agents_used=[],
                risk_level=RiskLevel.medium,
                action_log=[{"action": "empty_outputs", "timestamp": datetime.utcnow().isoformat()}],
                execution_status=ExecutionStatus.denied,
                reasoning_summary="No agents produced outputs for this request",
                mode=self.mode_controller.current_mode,
            )

        mode = self.mode_controller.current_mode
        rules = self.mode_controller.get_rules()
        base_weights = MODE_WEIGHTS.get(mode, {})
        ws_weights = WORKSPACE_WEIGHTS.get(workspace or "", {})

        weighed: List[Tuple[float, AgentOutput]] = []
        for out in outputs:
            w = base_weights.get(out.agent_name, 1.0)
            w *= ws_weights.get(out.agent_name, 1.0)
            if rules.agent_weights_override and out.agent_name in rules.agent_weights_override:
                w *= rules.agent_weights_override[out.agent_name]
            weighed.append((w, out))

        weighed.sort(key=lambda x: x[0] * x[1].confidence, reverse=True)

        best = weighed[0][1]
        conflicts = self._detect_conflicts(weighed)

        if conflicts:
            best = self._resolve_conflicts(weighed, conflicts)

        effective_confidence = min(
            sum(w * o.confidence for w, o in weighed) / sum(w for w, _ in weighed),
            1.0,
        )

        avg_risk = sum(o.risk_score for _, o in weighed) / max(len(weighed), 1)
        if avg_risk > 0.5:
            risk_level = RiskLevel.high
        elif avg_risk > 0.2:
            risk_level = RiskLevel.medium
        else:
            risk_level = RiskLevel.low

        requires_confirm = avg_risk > 0.3 or any(o.risk_score > 0.5 for _, o in weighed)

        agents_used = list(dict.fromkeys(o.agent_name for _, o in weighed))
        action_log = self._build_action_log(weighed, mode, workspace)

        decision = OrchestratorDecision(
            decision_id=str(uuid.uuid4()),
            result=best.recommendation,
            confidence=effective_confidence,
            agents_used=agents_used,
            risk_level=risk_level,
            action_log=action_log,
            execution_status=ExecutionStatus.requires_confirmation if requires_confirm else ExecutionStatus.approved,
            reasoning_summary=best.reasoning,
            requires_confirmation=requires_confirm,
            mode=mode,
        )

        decision = self.mode_controller.validate_decision(decision)
        return decision

    @staticmethod
    def _detect_conflicts(weighed: List[Tuple[float, AgentOutput]]) -> List[Tuple[AgentOutput, AgentOutput]]:
        conflicts: List[Tuple[AgentOutput, AgentOutput]] = []
        for i in range(len(weighed)):
            for j in range(i + 1, len(weighed)):
                a, b = weighed[i][1], weighed[j][1]
                if a.confidence > 0.5 and b.confidence > 0.5:
                    if abs(a.confidence - b.confidence) <= 0.2:
                        conflicts.append((a, b))
        return conflicts

    @staticmethod
    def _resolve_conflicts(
        weighed: List[Tuple[float, AgentOutput]],
        conflicts: List[Tuple[AgentOutput, AgentOutput]],
    ) -> AgentOutput:
        conflict_count: Dict[str, int] = {}
        for a, b in conflicts:
            conflict_count[a.agent_name] = conflict_count.get(a.agent_name, 0) + 1
            conflict_count[b.agent_name] = conflict_count.get(b.agent_name, 0) + 1
        resolved = max(weighed, key=lambda x: x[1].confidence)[1]
        logger.info("Conflict resolved in favor of agent '%s' (confidence=%.2f)", resolved.agent_name, resolved.confidence)
        return resolved

    @staticmethod
    def _build_action_log(
        weighed: List[Tuple[float, AgentOutput]],
        mode: SystemMode,
        workspace: Optional[str],
    ) -> List[Dict[str, Any]]:
        log = [
            {
                "action": "decision_merge",
                "mode": mode.value,
                "workspace": workspace,
                "agents_processed": len(weighed),
                "timestamp": datetime.utcnow().isoformat(),
            }
        ]
        for w, out in weighed:
            log.append({
                "action": "agent_contribution",
                "agent": out.agent_name,
                "weight": round(w, 2),
                "confidence": out.confidence,
                "risk": out.risk_score,
                "recommendation": out.recommendation[:80],
                "timestamp": datetime.utcnow().isoformat(),
            })
        return log


# ---------------------------------------------------------------------------
# Safety Validation Layer
# ---------------------------------------------------------------------------

class SafetyValidator:
    def __init__(self, mode_controller: ModeController):
        self.mode_controller = mode_controller

    def validate(self, decision: OrchestratorDecision, request: str) -> OrchestratorDecision:
        risk_map = {"low": 0.1, "medium": 0.4, "high": 0.8}
        numeric_risk = risk_map.get(decision.risk_level, 0.5)
        rules = self.mode_controller.get_rules()

        if numeric_risk > rules.max_risk_allowed:
            decision.execution_status = ExecutionStatus.denied
            decision.action_log.append({
                "action": "safety_denied",
                "reason": f"Risk {numeric_risk:.2f} exceeds mode limit {rules.max_risk_allowed}",
                "mode": self.mode_controller.current_mode.value,
                "timestamp": datetime.utcnow().isoformat(),
            })
            return decision

        if numeric_risk > 0.3:
            decision.requires_confirmation = True
            if decision.execution_status == ExecutionStatus.approved:
                decision.execution_status = ExecutionStatus.requires_confirmation
            decision.action_log.append({
                "action": "user_confirmation_required",
                "reason": f"Risk level {decision.risk_level} exceeds 0.3 threshold",
                "risk_score": numeric_risk,
                "timestamp": datetime.utcnow().isoformat(),
            })

        denied_patterns = [
            ("rm -rf", "destructive filesystem operation"),
            ("DROP TABLE", "dangerous database operation"),
            ("format ", "disk format operation"),
            ("shutdown -r", "system restart without approval"),
        ]
        req_lower = request.lower()
        for pattern, reason in denied_patterns:
            if pattern in req_lower:
                decision.execution_status = ExecutionStatus.denied
                decision.action_log.append({
                    "action": "pattern_denied",
                    "reason": reason,
                    "pattern": pattern,
                    "timestamp": datetime.utcnow().isoformat(),
                })
                return decision

        decision.action_log.append({
            "action": "safety_check_passed",
            "risk_score": numeric_risk,
            "requires_confirmation": decision.requires_confirmation,
            "timestamp": datetime.utcnow().isoformat(),
        })

        return decision


# ---------------------------------------------------------------------------
# Application Factory
# ---------------------------------------------------------------------------

class OrchestratorApp:
    def __init__(self):
        self.mode_controller = ModeController()
        self.memory = MemorySystem()
        self.classifier = InputClassifier()
        self.decision_engine = DecisionEngine(self.mode_controller)
        self.safety_validator = SafetyValidator(self.mode_controller)
        self._start_time = time.monotonic()

    async def run_pipeline(self, request: str, session_id: str, workspace: Optional[str], mode: SystemMode, context: Optional[Dict[str, Any]]) -> OrchestratorDecision:
        logger.info("Pipeline start: session=%s mode=%s", session_id, mode.value)

        self.mode_controller.set_mode(mode)
        self.memory.store_working(session_id, "last_request", request, ttl=300)

        request_type, urgency, classify_conf = self.classifier.classify(request, workspace)
        logger.info("Classified as %s with urgency %s (conf=%.2f)", request_type.value, urgency.value, classify_conf)

        agent_names = select_agents(request_type, workspace)
        agents = [AGENT_REGISTRY[name] for name in agent_names if name in AGENT_REGISTRY]

        if not agents:
            raise HTTPException(status_code=500, detail="No agents available for selection")

        agent_input = AgentInput(request=request, workspace=workspace, mode=mode, context=context)
        tasks = [agent.process(agent_input) for agent in agents]
        outputs = await asyncio.gather(*tasks)

        decision = self.decision_engine.aggregate(outputs, workspace)
        decision = self.safety_validator.validate(decision, request)

        session_context = self.memory.build_context(session_id, workspace)
        self.memory.store_working(session_id, "last_context", session_context, ttl=600)
        self.memory.store_working(session_id, "last_decision", decision.model_dump(mode="json"), ttl=600)

        if classify_conf > 0.7:
            self.memory.store_long_term(
                content=f"[{request_type.value}] {request} -> {decision.result[:200]}",
                tags=[request_type.value, workspace or "general"],
            )

        logger.info("Pipeline complete: decision=%s status=%s", decision.decision_id[:8], decision.execution_status.value)
        return decision


# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="ICHIN OS Orchestrator",
    version="1.0.0",
    description="Central intelligence runtime for the ICHIN operating system",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orch = OrchestratorApp()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        service="ichin-orchestrator",
        version="1.0.0",
        uptime=time.monotonic() - orch._start_time,
        active_sessions=len(orch.memory._working),
        mode=orch.mode_controller.current_mode,
    )


@app.post("/orchestrate", response_model=OrchestrateResponse)
async def orchestrate(body: OrchestrateRequest):
    try:
        session_id = body.session_id or str(uuid.uuid4())
        decision = await orch.run_pipeline(
            request=body.request,
            session_id=session_id,
            workspace=body.workspace,
            mode=body.mode,
            context=body.context,
        )
        return OrchestrateResponse(decision=decision, session_id=session_id)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Orchestration failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/classify", response_model=ClassifyResponse)
async def classify_request(body: OrchestrateRequest):
    try:
        rtype, urgency, confidence = orch.classifier.classify(body.request, body.workspace)
        return ClassifyResponse(
            request_type=rtype,
            urgency=urgency,
            workspace_context=body.workspace,
            confidence=confidence,
        )
    except Exception as exc:
        logger.exception("Classification failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/context/{session_id}", response_model=SessionContext)
async def get_context(session_id: str):
    try:
        working = orch.memory.get_all_working(session_id)
        context_data = orch.memory.build_context(session_id)
        return SessionContext(
            session_id=session_id,
            recent_interactions=[working] if working else [],
            working_memory=working,
            active_mode=orch.mode_controller.current_mode,
        )
    except Exception as exc:
        logger.exception("Context retrieval failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/execute-decision", response_model=ExecuteDecisionResponse)
async def execute_decision(body: ExecuteDecisionRequest):
    try:
        decision_data = None
        for session_id in list(orch.memory._working.keys()):
            stored = orch.memory.get_working(session_id, "last_decision")
            if stored and isinstance(stored, dict) and stored.get("decision_id") == body.decision_id:
                decision_data = stored
                break

        if decision_data is None:
            raise HTTPException(status_code=404, detail=f"Decision {body.decision_id} not found")

        status = decision_data.get("execution_status")
        if status == ExecutionStatus.denied.value:
            raise HTTPException(status_code=403, detail="Decision was denied and cannot be executed")

        if status == ExecutionStatus.requires_confirmation.value and not body.confirmed:
            return ExecuteDecisionResponse(
                status="confirmation_required",
                result=None,
                error="User confirmation is required for this action",
            )

        logger.info("Executing decision %s: %s", body.decision_id, body.action)
        return ExecuteDecisionResponse(
            status="executed",
            result=f"Action '{body.action}' executed successfully",
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Execution failed")
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# Service Routing Endpoints
# ---------------------------------------------------------------------------

class ServiceRouteRequest(BaseModel):
    service: str
    endpoint: str
    method: str = "GET"
    body: Optional[Dict[str, Any]] = None
    params: Optional[Dict[str, str]] = None


@app.post("/services/route")
async def route_to_service(body: ServiceRouteRequest):
    service_url = SERVICE_URLS.get(body.service)
    if not service_url:
        raise HTTPException(status_code=404, detail=f"Service '{body.service}' not found")
    url = f"{service_url.rstrip('/')}/{body.endpoint.lstrip('/')}"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            if body.method.upper() == "GET":
                resp = await client.get(url, params=body.params)
            elif body.method.upper() == "DELETE":
                resp = await client.delete(url, params=body.params)
            else:
                resp = await client.post(url, json=body.body or {}, params=body.params)
            resp.raise_for_status()
            return {"service": body.service, "status": resp.status_code, "data": resp.json()}
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"{body.service} error: {exc.response.text[:500]}")
    except httpx.RequestError as exc:
        raise HTTPException(status_code=503, detail=f"Cannot reach {body.service}: {exc}")


@app.get("/services/status")
async def get_services_status():
    results = {}
    for name, url in SERVICE_URLS.items():
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                resp = await client.get(f"{url}/health")
                if resp.status_code == 200:
                    data = resp.json()
                    results[name] = {"status": "healthy", "version": data.get("version", "?"), "uptime": data.get("uptime", 0)}
                else:
                    results[name] = {"status": f"http_{resp.status_code}"}
        except Exception as exc:
            results[name] = {"status": "unreachable", "error": str(exc)[:100]}
    return results


class BatchOrchestrateRequest(BaseModel):
    request: str
    services: List[str]
    workspace: Optional[str] = None
    mode: SystemMode = SystemMode.normal


@app.post("/orchestrate/batch")
async def batch_orchestrate(body: BatchOrchestrateRequest):
    results = {}
    async def call_service(service_name: str) -> Tuple[str, Any]:
        try:
            url = SERVICE_URLS.get(service_name)
            if not url:
                return service_name, {"error": f"Unknown service '{service_name}'"}
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(f"{url}/process" if service_name == "mail_ai" else f"{url}/command",
                    json={"request": body.request, "query": body.request, "session_id": "orchestrator-batch"},
                    timeout=15)
                if resp.status_code == 200:
                    return service_name, resp.json()
                return service_name, {"error": f"HTTP {resp.status_code}", "detail": resp.text[:200]}
        except Exception as exc:
            return service_name, {"error": str(exc)[:200]}

    tasks = [call_service(s) for s in body.services]
    completed = await asyncio.gather(*tasks)
    for name, result in completed:
        results[name] = result
    return {"request": body.request, "services_used": body.services, "results": results, "workspace": body.workspace, "mode": body.mode.value}


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
