import asyncio
import json
import logging
import math
import os
import time
import uuid
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ichin.memory_engine")

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)

MEMORY_FILE = DATA_DIR / "memories.json"
WORKING_FILE = DATA_DIR / "working_memory.json"
SEMANTIC_FILE = DATA_DIR / "semantic_memory.json"
STRUCTURED_FILE = DATA_DIR / "structured_memory.json"

DECAY_HALF_LIFE_DAYS = 30
QUALITY_THRESHOLD = 0.3
PROMOTION_CONFIDENCE_THRESHOLD = 0.6
EMBEDDING_DIM = 128
DEFAULT_PERSIST_INTERVAL = 60

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class MemoryLayer(str, Enum):
    ephemeral = "ephemeral"
    working = "working"
    long_term = "long_term"
    structured = "structured"


class MemoryType(str, Enum):
    fact = "fact"
    pattern = "pattern"
    skill = "skill"


class Workspace(str, Enum):
    study = "study"
    coding = "coding"
    personal = "personal"


class PrivacyLevel(str, Enum):
    public = "public"
    sensitive = "sensitive"
    private = "private"


# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------

class MemoryBase(BaseModel):
    content: str
    workspace: Workspace = Workspace.personal
    privacy_level: PrivacyLevel = PrivacyLevel.public
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)


class EphemeralMemory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    session_id: str
    workspace: Workspace = Workspace.personal
    memory_type: str = "ephemeral"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class WorkingMemory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    session_id: str
    workspace: Workspace = Workspace.personal
    memory_type: str = "working"
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    access_count: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime = Field(
        default_factory=lambda: datetime.utcnow() + timedelta(hours=1)
    )

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at

    def touch(self) -> None:
        self.access_count += 1
        self.expires_at = datetime.utcnow() + timedelta(hours=1)


class SemanticMemory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    memory_type: MemoryType = MemoryType.fact
    workspace: Workspace = Workspace.personal
    privacy_level: PrivacyLevel = PrivacyLevel.public
    embedding: List[float] = Field(default_factory=list)
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    strength: float = Field(default=1.0, ge=0.0, le=1.0)
    critical: bool = False
    access_count: int = 0
    last_accessed: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @property
    def decayed_strength(self) -> float:
        days_elapsed = (datetime.utcnow() - self.last_accessed).total_seconds() / 86400.0
        return self.strength * (0.5 ** (days_elapsed / DECAY_HALF_LIFE_DAYS))

    def access(self) -> None:
        self.access_count += 1
        self.last_accessed = datetime.utcnow()
        boost = min(self.access_count * 0.01, 0.2)
        self.strength = min(self.strength + boost, 1.0)


class StructuredMemory(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    content: str
    category: str
    workspace: Workspace = Workspace.personal
    privacy_level: PrivacyLevel = PrivacyLevel.public
    structured_data: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class QualityScores(BaseModel):
    relevance_score: float = Field(default=0.0, ge=0.0, le=1.0)
    freshness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    conflict_score: float = Field(default=1.0, ge=0.0, le=1.0)
    redundancy_score: float = Field(default=1.0, ge=0.0, le=1.0)

    @property
    def is_high_quality(self) -> bool:
        return all(
            s >= QUALITY_THRESHOLD
            for s in [self.relevance_score, self.freshness_score,
                      self.conflict_score, self.redundancy_score]
        )


class ContextPacket(BaseModel):
    session_context: Dict[str, Any] = Field(default_factory=dict)
    working_memory: List[Dict[str, Any]] = Field(default_factory=list)
    long_term_memories: List[Dict[str, Any]] = Field(default_factory=list)
    structured_memories: List[Dict[str, Any]] = Field(default_factory=list)
    quality_scores: QualityScores = Field(default_factory=QualityScores)
    token_estimate: int = 0
    max_token_budget: int = 4096
    workspace: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# ---------------------------------------------------------------------------
# Request / Response Models
# ---------------------------------------------------------------------------

class StoreMemoryRequest(BaseModel):
    content: str
    workspace: Workspace = Workspace.personal
    privacy_level: PrivacyLevel = PrivacyLevel.public
    memory_type: Optional[MemoryType] = None
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    critical: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    session_id: Optional[str] = None
    category: Optional[str] = None
    structured_data: Dict[str, Any] = Field(default_factory=dict)
    force_layer: Optional[MemoryLayer] = None


class StoreMemoryResponse(BaseModel):
    id: str
    layer: MemoryLayer
    memory_type: Optional[str] = None
    promoted: bool = False
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class QueryMemoryRequest(BaseModel):
    query: str
    workspace: Optional[Workspace] = None
    top_k: int = 10
    min_score: float = QUALITY_THRESHOLD
    include_ephemeral: bool = False
    include_working: bool = True
    include_long_term: bool = True
    include_structured: bool = True
    memory_type: Optional[MemoryType] = None
    category: Optional[str] = None


class MemoryResult(BaseModel):
    id: str
    content: str
    layer: MemoryLayer
    memory_type: Optional[str] = None
    workspace: Workspace
    similarity: float = 0.0
    quality_scores: QualityScores = Field(default_factory=QualityScores)
    strength: float = 1.0
    importance: float = 0.5
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class QueryMemoryResponse(BaseModel):
    results: List[MemoryResult] = Field(default_factory=list)
    total_found: int = 0
    query: str
    workspace: Optional[str] = None
    quality_summary: Dict[str, float] = Field(default_factory=dict)
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class PromoteMemoryRequest(BaseModel):
    memory_id: str
    source_layer: MemoryLayer
    target_layer: MemoryLayer
    reason: Optional[str] = None


class PromoteMemoryResponse(BaseModel):
    success: bool
    new_id: Optional[str] = None
    source_layer: MemoryLayer
    target_layer: MemoryLayer
    reason: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class DecayResponse(BaseModel):
    memories_processed: int
    memories_removed: int
    average_strength_before: float
    average_strength_after: float
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class LayerStats(BaseModel):
    layer: MemoryLayer
    count: int
    memory_types: Dict[str, int] = Field(default_factory=dict)
    workspaces: Dict[str, int] = Field(default_factory=dict)
    average_importance: float = 0.0
    average_strength: float = 0.0
    oldest: Optional[str] = None
    newest: Optional[str] = None


class LayersResponse(BaseModel):
    layers: List[LayerStats] = Field(default_factory=list)
    total_memories: int = 0
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    uptime: float
    total_memories: int
    layers: Dict[str, int]


# ---------------------------------------------------------------------------
# Embedding Service
# ---------------------------------------------------------------------------

class EmbeddingService:
    def __init__(self, dimension: int = EMBEDDING_DIM):
        self.dimension = dimension
        self._rng = np.random.RandomState(42)
        self._basis: Optional[np.ndarray] = None

    def _get_basis(self) -> np.ndarray:
        if self._basis is None:
            self._basis = self._rng.randn(self.dimension, self.dimension).astype(np.float64)
            self._basis /= np.linalg.norm(self._basis, axis=1, keepdims=True) + 1e-10
        return self._basis

    def embed(self, text: str) -> List[float]:
        words = text.lower().split()
        if not words:
            return [0.0] * self.dimension
        seed = hash(text) % (2 ** 31)
        rng = np.random.RandomState(seed)
        emb = rng.randn(self.dimension).astype(np.float64)
        emb = emb / (np.linalg.norm(emb) + 1e-10)
        return emb.tolist()

    @staticmethod
    def cosine_similarity(a: List[float], b: List[float]) -> float:
        arr_a = np.array(a, dtype=np.float64)
        arr_b = np.array(b, dtype=np.float64)
        dot = float(np.dot(arr_a, arr_b))
        norm = float(np.linalg.norm(arr_a) * np.linalg.norm(arr_b) + 1e-10)
        return dot / norm


# ---------------------------------------------------------------------------
# JSON Persistence
# ---------------------------------------------------------------------------

class JsonStore:
    def __init__(self, path: Path):
        self.path = path
        self._lock = asyncio.Lock()

    async def read(self) -> List[Dict[str, Any]]:
        async with self._lock:
            if not self.path.exists():
                return []
            try:
                data = self.path.read_text(encoding="utf-8")
                return json.loads(data) if data.strip() else []
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("Failed to read %s: %s", self.path.name, exc)
                return []

    async def write(self, data: List[Dict[str, Any]]) -> None:
        async with self._lock:
            tmp = self.path.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, default=str, indent=2), encoding="utf-8")
            tmp.replace(self.path)

    async def append(self, item: Dict[str, Any]) -> None:
        data = await self.read()
        data.append(item)
        await self.write(data)

    async def remove(self, memory_id: str) -> bool:
        data = await self.read()
        filtered = [d for d in data if d.get("id") != memory_id]
        if len(filtered) == len(data):
            return False
        await self.write(filtered)
        return True

    async def update(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        data = await self.read()
        found = False
        for d in data:
            if d.get("id") == memory_id:
                d.update(updates)
                found = True
                break
        if found:
            await self.write(data)
        return found

    async def get(self, memory_id: str) -> Optional[Dict[str, Any]]:
        data = await self.read()
        for d in data:
            if d.get("id") == memory_id:
                return d
        return None

    async def clear(self) -> None:
        await self.write([])


# ---------------------------------------------------------------------------
# Memory Engine
# ---------------------------------------------------------------------------

class MemoryEngine:
    def __init__(self):
        self._embedder = EmbeddingService()
        self._ephemeral: Dict[str, Dict[str, EphemeralMemory]] = {}
        self._working: Dict[str, Dict[str, WorkingMemory]] = {}
        self._semantic: Dict[str, SemanticMemory] = {}
        self._structured: Dict[str, StructuredMemory] = {}
        self._persist_task: Optional[asyncio.Task] = None
        self._start_time = time.monotonic()

        self._persist_ephemeral = JsonStore(MEMORY_FILE)
        self._persist_working = JsonStore(WORKING_FILE)
        self._persist_semantic = JsonStore(SEMANTIC_FILE)
        self._persist_structured = JsonStore(STRUCTURED_FILE)

    async def start(self) -> None:
        await self._load_all()
        self._persist_task = asyncio.create_task(self._periodic_persist())
        logger.info("Memory Engine started with %d semantic, %d structured memories",
                     len(self._semantic), len(self._structured))

    async def stop(self) -> None:
        if self._persist_task:
            self._persist_task.cancel()
            try:
                await self._persist_task
            except asyncio.CancelledError:
                pass
        await self._persist_all()
        logger.info("Memory Engine stopped")

    async def _load_all(self) -> None:
        for raw in await self._persist_semantic.read():
            try:
                mem = SemanticMemory(**raw)
                self._semantic[mem.id] = mem
            except Exception as exc:
                logger.warning("Skipping invalid semantic memory: %s", exc)

        for raw in await self._persist_structured.read():
            try:
                mem = StructuredMemory(**raw)
                self._structured[mem.id] = mem
            except Exception as exc:
                logger.warning("Skipping invalid structured memory: %s", exc)

        for raw in await self._persist_working.read():
            try:
                mem = WorkingMemory(**raw)
                self._working.setdefault(mem.session_id, {})[mem.id] = mem
            except Exception as exc:
                logger.warning("Skipping invalid working memory: %s", exc)

    async def _persist_all(self) -> None:
        await self._persist_semantic.write(
            [m.model_dump(mode="json") for m in self._semantic.values()]
        )
        await self._persist_structured.write(
            [m.model_dump(mode="json") for m in self._structured.values()]
        )
        working_all = []
        for session in self._working.values():
            for mem in session.values():
                working_all.append(mem.model_dump(mode="json"))
        await self._persist_working.write(working_all)

    async def _periodic_persist(self) -> None:
        while True:
            await asyncio.sleep(DEFAULT_PERSIST_INTERVAL)
            try:
                await self._persist_all()
                logger.debug("Auto-persisted memory to disk")
            except Exception as exc:
                logger.error("Auto-persist failed: %s", exc)

    # -----------------------------------------------------------------------
    # Layer Detection
    # -----------------------------------------------------------------------

    def _detect_layer(self, req: StoreMemoryRequest) -> MemoryLayer:
        if req.force_layer:
            return req.force_layer
        if req.critical:
            return MemoryLayer.long_term
        if req.structured_data or req.category:
            return MemoryLayer.structured
        if req.importance >= PROMOTION_CONFIDENCE_THRESHOLD:
            return MemoryLayer.long_term
        if self._has_repeated_content(req.content, min_occurrences=2):
            logger.info("Repeated content detected, promoting to long-term")
            return MemoryLayer.long_term
        return MemoryLayer.working

    def _has_repeated_content(self, content: str, min_occurrences: int = 2) -> bool:
        content_lower = content.lower().strip()
        count = 0
        for mem in self._semantic.values():
            if mem.content.lower().strip() == content_lower:
                count += 1
                if count >= min_occurrences:
                    return True
        for session in self._working.values():
            for mem in session.values():
                if mem.content.lower().strip() == content_lower:
                    count += 1
                    if count >= min_occurrences:
                        return True
        return False

    # -----------------------------------------------------------------------
    # Store
    # -----------------------------------------------------------------------

    async def store(self, req: StoreMemoryRequest) -> StoreMemoryResponse:
        layer = self._detect_layer(req)
        promoted = False

        if layer == MemoryLayer.ephemeral:
            if not req.session_id:
                raise HTTPException(status_code=400, detail="session_id required for ephemeral memory")
            mem = EphemeralMemory(
                content=req.content,
                session_id=req.session_id,
                workspace=req.workspace,
                metadata=req.metadata,
            )
            self._ephemeral.setdefault(req.session_id, {})[mem.id] = mem
            logger.debug("Stored ephemeral memory %s", mem.id)
            return StoreMemoryResponse(id=mem.id, layer=MemoryLayer.ephemeral)

        elif layer == MemoryLayer.working:
            if not req.session_id:
                raise HTTPException(status_code=400, detail="session_id required for working memory")
            mem = WorkingMemory(
                content=req.content,
                session_id=req.session_id,
                workspace=req.workspace,
                importance=req.importance,
                metadata=req.metadata,
                expires_at=datetime.utcnow() + timedelta(hours=1),
            )
            self._working.setdefault(req.session_id, {})[mem.id] = mem
            logger.debug("Stored working memory %s", mem.id)
            return StoreMemoryResponse(id=mem.id, layer=MemoryLayer.working)

        elif layer == MemoryLayer.long_term:
            mem_type = req.memory_type or MemoryType.fact
            embedding = self._embedder.embed(req.content)
            mem = SemanticMemory(
                content=req.content,
                memory_type=mem_type,
                workspace=req.workspace,
                privacy_level=req.privacy_level,
                embedding=embedding,
                importance=req.importance,
                critical=req.critical,
                metadata=req.metadata,
                tags=req.tags,
            )
            if req.force_layer == MemoryLayer.working and req.session_id:
                promoted = True
                wm = WorkingMemory(
                    content=req.content,
                    session_id=req.session_id,
                    workspace=req.workspace,
                    importance=req.importance,
                    metadata=req.metadata,
                )
                self._working.setdefault(req.session_id, {})[wm.id] = wm
                logger.debug("Promoted from working to long-term: %s -> %s", wm.id, mem.id)
            self._semantic[mem.id] = mem
            self._check_contradictions(mem)
            logger.debug("Stored semantic memory %s (type=%s, critical=%s)",
                         mem.id, mem_type.value, mem.critical)
            return StoreMemoryResponse(id=mem.id, layer=MemoryLayer.long_term, promoted=promoted)

        elif layer == MemoryLayer.structured:
            mem = StructuredMemory(
                content=req.content,
                category=req.category or "general",
                workspace=req.workspace,
                privacy_level=req.privacy_level,
                structured_data=req.structured_data,
                metadata=req.metadata,
                tags=req.tags,
            )
            self._structured[mem.id] = mem
            logger.debug("Stored structured memory %s (category=%s)", mem.id, mem.category)
            return StoreMemoryResponse(id=mem.id, layer=MemoryLayer.structured)

        raise HTTPException(status_code=500, detail="Unknown memory layer")

    # -----------------------------------------------------------------------
    # Query
    # -----------------------------------------------------------------------

    async def query(self, req: QueryMemoryRequest) -> QueryMemoryResponse:
        results: List[MemoryResult] = []
        query_emb = self._embedder.embed(req.query)

        if req.include_long_term:
            for mem in self._semantic.values():
                if req.workspace and mem.workspace != req.workspace:
                    continue
                if req.memory_type and mem.memory_type != req.memory_type:
                    continue
                sim = EmbeddingService.cosine_similarity(query_emb, mem.embedding)
                if sim < req.min_score:
                    continue
                scores = self._score_quality(mem, sim)
                if not scores.is_high_quality:
                    continue
                strength = mem.decayed_strength
                results.append(MemoryResult(
                    id=mem.id,
                    content=mem.content,
                    layer=MemoryLayer.long_term,
                    memory_type=mem.memory_type.value,
                    workspace=mem.workspace,
                    similarity=sim,
                    quality_scores=scores,
                    strength=strength,
                    importance=mem.importance,
                    metadata=mem.metadata,
                    created_at=mem.created_at,
                ))

        if req.include_working:
            for session in self._working.values():
                for mem in session.values():
                    if mem.is_expired:
                        continue
                    if req.workspace and mem.workspace != req.workspace:
                        continue
                    sim = EmbeddingService.cosine_similarity(
                        query_emb, self._embedder.embed(mem.content)
                    )
                    if sim < req.min_score:
                        continue
                    results.append(MemoryResult(
                        id=mem.id,
                        content=mem.content,
                        layer=MemoryLayer.working,
                        workspace=mem.workspace,
                        similarity=sim,
                        quality_scores=QualityScores(relevance_score=sim, freshness_score=1.0),
                        strength=1.0,
                        importance=mem.importance,
                        metadata=mem.metadata,
                        created_at=mem.created_at,
                    ))

        if req.include_structured:
            for mem in self._structured.values():
                if req.workspace and mem.workspace != req.workspace:
                    continue
                if req.category and mem.category != req.category:
                    continue
                sim = EmbeddingService.cosine_similarity(
                    query_emb, self._embedder.embed(f"{mem.content} {json.dumps(mem.structured_data)}")
                )
                if sim < req.min_score:
                    continue
                results.append(MemoryResult(
                    id=mem.id,
                    content=mem.content,
                    layer=MemoryLayer.structured,
                    memory_type=mem.category,
                    workspace=mem.workspace,
                    similarity=sim,
                    quality_scores=QualityScores(relevance_score=sim, freshness_score=0.8),
                    strength=1.0,
                    importance=0.5,
                    metadata={**mem.metadata, "structured_data": mem.structured_data},
                    created_at=mem.created_at,
                ))

        if req.include_ephemeral:
            for session_id, session_mems in self._ephemeral.items():
                for mem in session_mems.values():
                    if req.workspace and mem.workspace != req.workspace:
                        continue
                    sim = EmbeddingService.cosine_similarity(
                        query_emb, self._embedder.embed(mem.content)
                    )
                    if sim < req.min_score:
                        continue
                    results.append(MemoryResult(
                        id=mem.id,
                        content=mem.content,
                        layer=MemoryLayer.ephemeral,
                        workspace=mem.workspace,
                        similarity=sim,
                        quality_scores=QualityScores(relevance_score=sim, freshness_score=1.0),
                        strength=1.0,
                        importance=0.0,
                        metadata=mem.metadata,
                        created_at=mem.created_at,
                    ))

        results.sort(key=lambda r: r.similarity, reverse=True)
        results = results[:req.top_k]

        for r in results:
            if r.layer == MemoryLayer.long_term:
                sem_mem = self._semantic.get(r.id)
                if sem_mem:
                    sem_mem.access()

        quality_summary = {}
        if results:
            quality_summary = {
                "avg_relevance": sum(q.similarity for q in results) / len(results),
                "avg_freshness": sum(q.quality_scores.freshness_score for q in results) / len(results),
                "avg_conflict": sum(q.quality_scores.conflict_score for q in results) / len(results),
                "avg_redundancy": sum(q.quality_scores.redundancy_score for q in results) / len(results),
            }

        return QueryMemoryResponse(
            results=results,
            total_found=len(results),
            query=req.query,
            workspace=req.workspace.value if req.workspace else None,
            quality_summary=quality_summary,
        )

    # -----------------------------------------------------------------------
    # Context Building Pipeline
    # -----------------------------------------------------------------------

    async def build_context(
        self,
        session_id: str,
        workspace: Optional[Workspace] = None,
        request: Optional[str] = None,
        max_tokens: int = 4096,
    ) -> ContextPacket:
        session_state: Dict[str, Any] = {}
        ephemeral_mems = self._ephemeral.get(session_id, {})
        if ephemeral_mems:
            session_state["ephemeral_context"] = [
                {"id": e.id, "content": e.content[:200], "type": e.memory_type}
                for e in ephemeral_mems.values()
            ]

        working_mems: List[Dict[str, Any]] = []
        session_working = self._working.get(session_id, {})
        for mem in session_working.values():
            if not mem.is_expired:
                working_mems.append({
                    "id": mem.id,
                    "content": mem.content[:200],
                    "importance": mem.importance,
                    "created_at": mem.created_at.isoformat(),
                })

        query_text = request or session_state.get("ephemeral_context", [{}])[0].get("content", "") if session_state.get("ephemeral_context") else ""
        query_req = QueryMemoryRequest(
            query=query_text or "general context",
            workspace=workspace,
            top_k=8,
            include_ephemeral=False,
            include_working=False,
        )
        query_result = await self.query(query_req)

        long_term_list = []
        for r in query_result.results:
            if r.layer == MemoryLayer.long_term:
                long_term_list.append({
                    "id": r.id,
                    "content": r.content[:300],
                    "memory_type": r.memory_type,
                    "strength": r.strength,
                    "similarity": r.similarity,
                    "quality": r.quality_scores.model_dump(),
                })

        structured_list = []
        for r in query_result.results:
            if r.layer == MemoryLayer.structured:
                structured_list.append({
                    "id": r.id,
                    "content": r.content[:300],
                    "category": r.memory_type,
                    "data": r.metadata.get("structured_data", {}),
                })

        quality_scores = self._compute_context_quality(query_result)

        token_estimate = (
            len(json.dumps(session_state)) // 4
            + sum(len(json.dumps(m)) // 4 for m in working_mems)
            + sum(len(json.dumps(m)) // 4 for m in long_term_list)
            + sum(len(json.dumps(m)) // 4 for m in structured_list)
        )

        ws_value = workspace.value if workspace else None

        if token_estimate > max_tokens:
            logger.info("Context exceeds token budget (%d > %d), compressing", token_estimate, max_tokens)
            while long_term_list and token_estimate > max_tokens:
                removed = long_term_list.pop()
                token_estimate -= len(json.dumps(removed)) // 4
            while working_mems and token_estimate > max_tokens:
                removed = working_mems.pop()
                token_estimate -= len(json.dumps(removed)) // 4

        return ContextPacket(
            session_context=session_state,
            working_memory=working_mems,
            long_term_memories=long_term_list,
            structured_memories=structured_list,
            quality_scores=quality_scores,
            token_estimate=token_estimate,
            max_token_budget=max_tokens,
            workspace=ws_value,
        )

    def _compute_context_quality(self, query_result: QueryMemoryResponse) -> QualityScores:
        if not query_result.results:
            return QualityScores()
        relevance = sum(r.similarity for r in query_result.results) / len(query_result.results)
        now = datetime.utcnow()
        freshness_total = 0.0
        for r in query_result.results:
            age_hours = (now - r.created_at).total_seconds() / 3600.0
            freshness_total += max(0.0, 1.0 - (age_hours / 720.0))
        freshness = freshness_total / len(query_result.results)

        conflicts = 0
        contents_seen: set = set()
        redundancies = 0
        for r in query_result.results:
            norm = r.content.lower().strip()[:100]
            if norm in contents_seen:
                redundancies += 1
            contents_seen.add(norm)
        conflict_score = max(0.0, 1.0 - (conflicts * 0.2))
        redundancy_score = max(0.0, 1.0 - (redundancies * 0.15))

        return QualityScores(
            relevance_score=min(relevance, 1.0),
            freshness_score=min(freshness, 1.0),
            conflict_score=conflict_score,
            redundancy_score=redundancy_score,
        )

    # -----------------------------------------------------------------------
    # Quality Scoring
    # -----------------------------------------------------------------------

    def _score_quality(self, mem: SemanticMemory, similarity: float) -> QualityScores:
        relevance_score = similarity
        age_hours = (datetime.utcnow() - mem.last_accessed).total_seconds() / 3600.0
        freshness_score = max(0.0, 1.0 - (age_hours / DECAY_HALF_LIFE_DAYS / 24.0))
        conflict_score = self._compute_conflict_score(mem)
        redundancy_score = self._compute_redundancy_score(mem)
        return QualityScores(
            relevance_score=min(relevance_score, 1.0),
            freshness_score=min(freshness_score, 1.0),
            conflict_score=conflict_score,
            redundancy_score=redundancy_score,
        )

    def _compute_conflict_score(self, mem: SemanticMemory) -> float:
        conflicts = 0
        for other in self._semantic.values():
            if other.id == mem.id:
                continue
            if other.workspace != mem.workspace:
                continue
            sim = EmbeddingService.cosine_similarity(mem.embedding, other.embedding)
            if sim > 0.85 and other.memory_type != mem.memory_type:
                conflicts += 1
        return max(0.0, 1.0 - (conflicts * 0.25))

    def _compute_redundancy_score(self, mem: SemanticMemory) -> float:
        duplicates = 0
        for other in self._semantic.values():
            if other.id == mem.id:
                continue
            sim = EmbeddingService.cosine_similarity(mem.embedding, other.embedding)
            if sim > 0.92:
                duplicates += 1
        return max(0.0, 1.0 - (duplicates * 0.2))

    # -----------------------------------------------------------------------
    # Decay
    # -----------------------------------------------------------------------

    async def apply_decay(self) -> DecayResponse:
        before_strengths: List[float] = [m.strength for m in self._semantic.values()]
        avg_before = sum(before_strengths) / len(before_strengths) if before_strengths else 0.0

        removed: List[str] = []
        processed = 0
        for mem_id, mem in list(self._semantic.items()):
            processed += 1
            decayed = mem.decayed_strength
            mem.strength = decayed
            if mem.critical:
                mem.strength = max(mem.strength, 0.5)
            if mem.strength < 0.05 and not mem.critical:
                removed.append(mem_id)

        for mem_id in removed:
            logger.info("Decay removed semantic memory %s (strength fell below threshold)", mem_id)
            self._semantic.pop(mem_id, None)

        expired_sessions: List[str] = []
        for session_id, session in self._working.items():
            expired_ids = [k for k, v in session.items() if v.is_expired]
            for k in expired_ids:
                session.pop(k, None)
            if not session:
                expired_sessions.append(session_id)
        for sid in expired_sessions:
            self._working.pop(sid, None)

        for session_id in list(self._ephemeral.keys()):
            self._ephemeral.pop(session_id, None)

        after_strengths = [m.strength for m in self._semantic.values()]
        avg_after = sum(after_strengths) / len(after_strengths) if after_strengths else 0.0

        logger.info("Decay applied: %d processed, %d removed, avg strength %.3f -> %.3f",
                     processed, len(removed), avg_before, avg_after)

        return DecayResponse(
            memories_processed=processed,
            memories_removed=len(removed),
            average_strength_before=avg_before,
            average_strength_after=avg_after,
        )

    # -----------------------------------------------------------------------
    # Promotion
    # -----------------------------------------------------------------------

    async def promote(self, req: PromoteMemoryRequest) -> PromoteMemoryResponse:
        source_layers = {
            MemoryLayer.ephemeral: self._ephemeral,
            MemoryLayer.working: self._working,
            MemoryLayer.long_term: self._semantic,
            MemoryLayer.structured: self._structured,
        }
        source = source_layers.get(req.source_layer)
        if source is None:
            raise HTTPException(status_code=400, detail=f"Invalid source layer: {req.source_layer}")

        found = None
        if req.source_layer == MemoryLayer.ephemeral:
            for sid, session in source.items():
                if req.memory_id in session:
                    found = session.pop(req.memory_id)
                    break
        elif req.source_layer == MemoryLayer.working:
            for sid, session in source.items():
                if req.memory_id in session:
                    found = session.pop(req.memory_id)
                    break
        elif req.source_layer == MemoryLayer.long_term:
            found = source.pop(req.memory_id, None)
        else:
            found = source.pop(req.memory_id, None)

        if found is None:
            raise HTTPException(status_code=404, detail=f"Memory {req.memory_id} not found in {req.source_layer}")

        if req.target_layer == MemoryLayer.long_term:
            content = found.content if hasattr(found, "content") else str(found)
            workspace = found.workspace if hasattr(found, "workspace") else Workspace.personal
            mem_type = MemoryType.fact
            if hasattr(found, "memory_type"):
                try:
                    mem_type = MemoryType(found.memory_type)
                except (ValueError, TypeError):
                    pass
            embedding = self._embedder.embed(content)
            sem_mem = SemanticMemory(
                content=content,
                memory_type=mem_type,
                workspace=workspace,
                embedding=embedding,
                importance=getattr(found, "importance", 0.5) + 0.1,
                metadata=getattr(found, "metadata", {}),
                tags=getattr(found, "tags", []),
            )
            self._semantic[sem_mem.id] = sem_mem
            new_id = sem_mem.id
            logger.info("Promoted memory %s from %s to long-term semantic", req.memory_id, req.source_layer)
            return PromoteMemoryResponse(
                success=True,
                new_id=new_id,
                source_layer=req.source_layer,
                target_layer=req.target_layer,
                reason=req.reason,
            )

        elif req.target_layer == MemoryLayer.structured:
            content = found.content if hasattr(found, "content") else str(found)
            struct_mem = StructuredMemory(
                content=content,
                category=getattr(found, "memory_type", "promoted"),
                workspace=getattr(found, "workspace", Workspace.personal),
                structured_data=getattr(found, "structured_data", {}),
                metadata=getattr(found, "metadata", {}),
                tags=getattr(found, "tags", []),
            )
            self._structured[struct_mem.id] = struct_mem
            logger.info("Promoted memory %s from %s to structured", req.memory_id, req.source_layer)
            return PromoteMemoryResponse(
                success=True,
                new_id=struct_mem.id,
                source_layer=req.source_layer,
                target_layer=req.target_layer,
                reason=req.reason,
            )

        elif req.target_layer == MemoryLayer.working:
            wm = WorkingMemory(
                content=getattr(found, "content", str(found)),
                session_id=f"promoted-{uuid.uuid4().hex[:8]}",
                workspace=getattr(found, "workspace", Workspace.personal),
                importance=getattr(found, "importance", 0.5),
            )
            self._working.setdefault(wm.session_id, {})[wm.id] = wm
            logger.info("Promoted memory %s from %s to working", req.memory_id, req.source_layer)
            return PromoteMemoryResponse(
                success=True,
                new_id=wm.id,
                source_layer=req.source_layer,
                target_layer=req.target_layer,
                reason=req.reason,
            )

        elif req.target_layer == MemoryLayer.ephemeral:
            em = EphemeralMemory(
                content=getattr(found, "content", str(found)),
                session_id=f"promoted-{uuid.uuid4().hex[:8]}",
                workspace=getattr(found, "workspace", Workspace.personal),
            )
            self._ephemeral.setdefault(em.session_id, {})[em.id] = em
            logger.info("Promoted memory %s from %s to ephemeral", req.memory_id, req.source_layer)
            return PromoteMemoryResponse(
                success=True,
                new_id=em.id,
                source_layer=req.source_layer,
                target_layer=req.target_layer,
                reason=req.reason,
            )

        raise HTTPException(status_code=400, detail="Invalid target layer")

    # -----------------------------------------------------------------------
    # Delete
    # -----------------------------------------------------------------------

    async def delete(self, memory_id: str) -> bool:
        if memory_id in self._semantic:
            del self._semantic[memory_id]
            logger.info("Deleted semantic memory %s", memory_id)
            return True
        if memory_id in self._structured:
            del self._structured[memory_id]
            logger.info("Deleted structured memory %s", memory_id)
            return True
        for session_id in list(self._working.keys()):
            if memory_id in self._working[session_id]:
                del self._working[session_id][memory_id]
                if not self._working[session_id]:
                    del self._working[session_id]
                logger.info("Deleted working memory %s", memory_id)
                return True
        for session_id in list(self._ephemeral.keys()):
            if memory_id in self._ephemeral[session_id]:
                del self._ephemeral[session_id][memory_id]
                if not self._ephemeral[session_id]:
                    del self._ephemeral[session_id]
                logger.info("Deleted ephemeral memory %s", memory_id)
                return True
        return False

    # -----------------------------------------------------------------------
    # Layers Stats
    # -----------------------------------------------------------------------

    async def get_layer_stats(self) -> LayersResponse:
        layers: List[LayerStats] = []

        semantic_types: Dict[str, int] = {}
        semantic_workspaces: Dict[str, int] = {}
        semantic_importance = 0.0
        semantic_strength = 0.0
        semantic_oldest: Optional[datetime] = None
        semantic_newest: Optional[datetime] = None
        for mem in self._semantic.values():
            t = mem.memory_type.value
            semantic_types[t] = semantic_types.get(t, 0) + 1
            ws = mem.workspace.value
            semantic_workspaces[ws] = semantic_workspaces.get(ws, 0) + 1
            semantic_importance += mem.importance
            semantic_strength += mem.strength
            if semantic_oldest is None or mem.created_at < semantic_oldest:
                semantic_oldest = mem.created_at
            if semantic_newest is None or mem.created_at > semantic_newest:
                semantic_newest = mem.created_at
        sc = len(self._semantic)
        layers.append(LayerStats(
            layer=MemoryLayer.long_term,
            count=sc,
            memory_types=semantic_types,
            workspaces=semantic_workspaces,
            average_importance=semantic_importance / sc if sc else 0.0,
            average_strength=semantic_strength / sc if sc else 0.0,
            oldest=semantic_oldest.isoformat() if semantic_oldest else None,
            newest=semantic_newest.isoformat() if semantic_newest else None,
        ))

        struct_categories: Dict[str, int] = {}
        struct_workspaces: Dict[str, int] = {}
        struct_oldest: Optional[datetime] = None
        struct_newest: Optional[datetime] = None
        for mem in self._structured.values():
            struct_categories[mem.category] = struct_categories.get(mem.category, 0) + 1
            ws = mem.workspace.value
            struct_workspaces[ws] = struct_workspaces.get(ws, 0) + 1
            if struct_oldest is None or mem.created_at < struct_oldest:
                struct_oldest = mem.created_at
            if struct_newest is None or mem.created_at > struct_newest:
                struct_newest = mem.created_at
        stc = len(self._structured)
        layers.append(LayerStats(
            layer=MemoryLayer.structured,
            count=stc,
            memory_types=struct_categories,
            workspaces=struct_workspaces,
            oldest=struct_oldest.isoformat() if struct_oldest else None,
            newest=struct_newest.isoformat() if struct_newest else None,
        ))

        working_count = sum(len(s) for s in self._working.values())
        working_workspaces: Dict[str, int] = {}
        for session in self._working.values():
            for mem in session.values():
                ws = mem.workspace.value
                working_workspaces[ws] = working_workspaces.get(ws, 0) + 1
        layers.append(LayerStats(
            layer=MemoryLayer.working,
            count=working_count,
            workspaces=working_workspaces,
        ))

        ephem_count = sum(len(s) for s in self._ephemeral.values())
        layers.append(LayerStats(
            layer=MemoryLayer.ephemeral,
            count=ephem_count,
        ))

        total = sc + stc + working_count + ephem_count

        return LayersResponse(
            layers=layers,
            total_memories=total,
        )

    # -----------------------------------------------------------------------
    # Contradiction Detection & Merge
    # -----------------------------------------------------------------------

    def _check_contradictions(self, new_mem: SemanticMemory) -> None:
        to_merge: List[str] = []
        for existing_id, existing in self._semantic.items():
            if existing.id == new_mem.id:
                continue
            if existing.workspace != new_mem.workspace:
                continue
            sim = EmbeddingService.cosine_similarity(new_mem.embedding, existing.embedding)
            if sim > 0.9:
                if existing.memory_type != new_mem.memory_type:
                    logger.info("Contradiction detected between %s (%s) and %s (%s), merging",
                                 new_mem.id, new_mem.memory_type, existing.id, existing.memory_type)
                    existing.metadata["merged_with"] = existing.metadata.get("merged_with", []) + [new_mem.id]
                    existing.strength = max(existing.strength, new_mem.strength)
                    existing.importance = max(existing.importance, new_mem.importance)
                    if new_mem.critical:
                        existing.critical = True
                    to_merge.append(new_mem.id)
        for mid in to_merge:
            self._semantic.pop(mid, None)
            logger.debug("Merged memory %s into contradicting counterpart", mid)


# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="ICHIN OS Service 3 — Memory + Context Engine",
    version="1.0.0",
    description="4-layer memory system with decay, promotion, and context engine",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = MemoryEngine()


@app.on_event("startup")
async def startup():
    await engine.start()


@app.on_event("shutdown")
async def shutdown():
    await engine.stop()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse)
async def health():
    stats = await engine.get_layer_stats()
    layer_counts = {s.layer.value: s.count for s in stats.layers}
    return HealthResponse(
        status="ok",
        service="ichin-memory-engine",
        version="1.0.0",
        uptime=time.monotonic() - engine._start_time,
        total_memories=stats.total_memories,
        layers=layer_counts,
    )


@app.post("/memory/store", response_model=StoreMemoryResponse)
async def store_memory(body: StoreMemoryRequest):
    try:
        return await engine.store(body)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Store memory failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/memory/query", response_model=QueryMemoryResponse)
async def query_memory(body: QueryMemoryRequest):
    try:
        return await engine.query(body)
    except Exception as exc:
        logger.exception("Query memory failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/memory/decay", response_model=DecayResponse)
async def decay_memories():
    try:
        return await engine.apply_decay()
    except Exception as exc:
        logger.exception("Decay process failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/memory/promote", response_model=PromoteMemoryResponse)
async def promote_memory(body: PromoteMemoryRequest):
    try:
        return await engine.promote(body)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Promote memory failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.delete("/memory/{memory_id}")
async def delete_memory(memory_id: str):
    try:
        deleted = await engine.delete(memory_id)
        if not deleted:
            raise HTTPException(status_code=404, detail=f"Memory {memory_id} not found")
        return {"status": "deleted", "memory_id": memory_id}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Delete memory failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/memory/layers", response_model=LayersResponse)
async def get_layers():
    try:
        return await engine.get_layer_stats()
    except Exception as exc:
        logger.exception("Get layer stats failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/context/build")
async def build_context(
    session_id: str,
    workspace: Optional[Workspace] = None,
    request: Optional[str] = None,
    max_tokens: int = 4096,
):
    try:
        packet = await engine.build_context(
            session_id=session_id,
            workspace=workspace,
            request=request,
            max_tokens=max_tokens,
        )
        return packet.model_dump()
    except Exception as exc:
        logger.exception("Context building failed")
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# Voice Memory Endpoints
# ---------------------------------------------------------------------------

class VoiceMemoryRequest(BaseModel):
    session_id: str
    text: Optional[str] = None
    audio_data: Optional[str] = None
    stt_latency_ms: Optional[float] = None
    tts_latency_ms: Optional[float] = None
    personality_used: Optional[str] = None
    orb_state: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VoiceMemoryResponse(BaseModel):
    id: str
    stored: bool
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class BrowserMemoryRequest(BaseModel):
    session_id: str
    url: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    research_findings: Optional[str] = None
    page_metadata: Dict[str, Any] = Field(default_factory=dict)
    links: List[str] = Field(default_factory=list)
    permission_level: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BrowserMemoryResponse(BaseModel):
    id: str
    stored: bool
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


voice_sessions: Dict[str, List[Dict[str, Any]]] = {}
browser_sessions: Dict[str, List[Dict[str, Any]]] = {}


@app.post("/memory/voice", response_model=VoiceMemoryResponse)
async def store_voice_memory(body: VoiceMemoryRequest):
    sid = body.session_id
    if sid not in voice_sessions:
        voice_sessions[sid] = []
    entry = body.model_dump()
    entry["timestamp"] = datetime.utcnow().isoformat()
    voice_sessions[sid].append(entry)
    logger.info(f"Voice memory stored for session {sid}: {len(voice_sessions[sid])} entries")
    return VoiceMemoryResponse(id=sid, stored=True)


@app.get("/memory/voice/{session_id}")
async def get_voice_memory(session_id: str, limit: int = 50):
    entries = voice_sessions.get(session_id, [])
    return {"session_id": session_id, "count": len(entries), "entries": entries[-limit:]}


@app.post("/memory/browser", response_model=BrowserMemoryResponse)
async def store_browser_memory(body: BrowserMemoryRequest):
    sid = body.session_id
    if sid not in browser_sessions:
        browser_sessions[sid] = []
    entry = body.model_dump()
    entry["timestamp"] = datetime.utcnow().isoformat()
    browser_sessions[sid].append(entry)
    logger.info(f"Browser memory stored for session {sid}: {len(browser_sessions[sid])} entries")
    return BrowserMemoryResponse(id=sid, stored=True)


@app.get("/memory/browser/{session_id}")
async def get_browser_memory(session_id: str, limit: int = 50):
    entries = browser_sessions.get(session_id, [])
    return {"session_id": session_id, "count": len(entries), "entries": entries[-limit:]}


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8013, reload=True)
