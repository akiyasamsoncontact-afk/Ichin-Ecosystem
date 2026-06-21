import json
import logging
import os
import time
import uuid
from collections import defaultdict
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ichin.knowledge-graph")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)
NODES_FILE = os.path.join(DATA_DIR, "nodes.json")
EDGES_FILE = os.path.join(DATA_DIR, "edges.json")

MEMORY_URL = "http://localhost:8003"
EMBEDDING_DIM = 128


class NodeType(str, Enum):
    concept = "concept"
    topic = "topic"
    skill = "skill"
    project = "project"
    note = "note"
    document = "document"
    task = "task"
    person = "person"
    tool = "tool"
    resource = "resource"
    category = "category"
    goal = "goal"
    habit = "habit"
    insight = "insight"


class EdgeType(str, Enum):
    relates_to = "relates_to"
    prerequisite = "prerequisite"
    extends = "extends"
    part_of = "part_of"
    example_of = "example_of"
    used_by = "used_by"
    created_by = "created_by"
    references = "references"
    depends_on = "depends_on"
    similar_to = "similar_to"
    opposite_of = "opposite_of"
    next_step = "next_step"
    mastered = "mastered"
    learning = "learning"
    interested = "interested"


class KnowledgeNode(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: NodeType = NodeType.concept
    description: str = ""
    tags: List[str] = []
    workspace: str = "general"
    embedding: List[float] = []
    importance: float = Field(default=0.5, ge=0.0, le=1.0)
    mastery: float = Field(default=0.0, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = {}
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class KnowledgeEdge(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str
    target_id: str
    type: EdgeType = EdgeType.relates_to
    weight: float = Field(default=1.0, ge=0.0, le=1.0)
    metadata: Dict[str, Any] = {}
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class GraphQuery(BaseModel):
    query: str = ""
    node_types: Optional[List[NodeType]] = None
    tags: Optional[List[str]] = None
    workspace: Optional[str] = None
    max_depth: int = 2
    top_k: int = 20
    min_importance: float = 0.0


class GraphResponse(BaseModel):
    nodes: List[KnowledgeNode] = []
    edges: List[KnowledgeEdge] = []
    total_nodes: int = 0
    total_edges: int = 0
    query_time_ms: float = 0.0


class NodeCreateRequest(BaseModel):
    name: str
    type: NodeType = NodeType.concept
    description: str = ""
    tags: List[str] = []
    workspace: str = "general"
    importance: float = 0.5
    mastery: float = 0.0
    metadata: Dict[str, Any] = {}
    edges: List[Dict[str, Any]] = []


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    uptime: float
    total_nodes: int
    total_edges: int


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


class KnowledgeGraph:
    def __init__(self):
        self._nodes: Dict[str, KnowledgeNode] = {}
        self._edges: Dict[str, KnowledgeEdge] = {}
        self._adjacency: Dict[str, Set[str]] = defaultdict(set)
        self._load()

    def _load(self) -> None:
        for n_data in _load_json(NODES_FILE, []):
            try:
                node = KnowledgeNode(**n_data)
                self._nodes[node.id] = node
            except Exception as exc:
                logger.warning("Skipping invalid node: %s", exc)
        for e_data in _load_json(EDGES_FILE, []):
            try:
                edge = KnowledgeEdge(**e_data)
                self._edges[edge.id] = edge
                self._adjacency[edge.source_id].add(edge.target_id)
                self._adjacency[edge.target_id].add(edge.source_id)
            except Exception as exc:
                logger.warning("Skipping invalid edge: %s", exc)
        logger.info("Loaded %d nodes, %d edges", len(self._nodes), len(self._edges))

    def _persist(self) -> None:
        _save_json(NODES_FILE, [n.model_dump(mode="json") for n in self._nodes.values()])
        _save_json(EDGES_FILE, [e.model_dump(mode="json") for e in self._edges.values()])

    def _compute_embedding(self, text: str) -> List[float]:
        words = text.lower().split()
        if not words:
            return [0.0] * EMBEDDING_DIM
        seed = hash(text) % (2**31)
        rng = np.random.RandomState(seed)
        emb = rng.randn(EMBEDDING_DIM).astype(np.float64)
        emb = emb / (np.linalg.norm(emb) + 1e-10)
        return emb.tolist()

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        arr_a = np.array(a, dtype=np.float64)
        arr_b = np.array(b, dtype=np.float64)
        dot = float(np.dot(arr_a, arr_b))
        norm = float(np.linalg.norm(arr_a) * np.linalg.norm(arr_b) + 1e-10)
        return dot / norm

    def create_node(self, req: NodeCreateRequest) -> KnowledgeNode:
        if any(n.name.lower() == req.name.lower() and n.workspace == req.workspace for n in self._nodes.values()):
            existing = next(n for n in self._nodes.values() if n.name.lower() == req.name.lower() and n.workspace == req.workspace)
            raise HTTPException(status_code=409, detail=f"Node '{req.name}' already exists (id={existing.id})")

        combined = f"{req.name} {req.description} {' '.join(req.tags)}"
        node = KnowledgeNode(
            name=req.name,
            type=req.type,
            description=req.description,
            tags=req.tags,
            workspace=req.workspace,
            embedding=self._compute_embedding(combined),
            importance=req.importance,
            mastery=req.mastery,
            metadata=req.metadata,
        )
        self._nodes[node.id] = node

        for edge_data in req.edges:
            edge = KnowledgeEdge(
                source_id=node.id,
                target_id=edge_data.get("target_id", ""),
                type=EdgeType(edge_data.get("type", "relates_to")),
                weight=edge_data.get("weight", 1.0),
                metadata=edge_data.get("metadata", {}),
            )
            if edge.target_id in self._nodes:
                self._edges[edge.id] = edge
                self._adjacency[edge.source_id].add(edge.target_id)
                self._adjacency[edge.target_id].add(edge.source_id)

        self._persist()
        logger.info("Created node %s (%s) in workspace %s", node.id, node.name, node.workspace)
        return node

    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        return self._nodes.get(node_id)

    def find_nodes_by_name(self, name: str, workspace: Optional[str] = None) -> List[KnowledgeNode]:
        name_lower = name.lower()
        results = []
        for node in self._nodes.values():
            if name_lower in node.name.lower():
                if workspace is None or node.workspace == workspace:
                    results.append(node)
        return results

    def update_node(self, node_id: str, updates: Dict[str, Any]) -> Optional[KnowledgeNode]:
        node = self._nodes.get(node_id)
        if not node:
            return None
        for key, value in updates.items():
            if hasattr(node, key) and value is not None and key != "id":
                setattr(node, key, value)
        node.updated_at = datetime.utcnow().isoformat()
        if "name" in updates or "description" in updates or "tags" in updates:
            combined = f"{node.name} {node.description} {' '.join(node.tags)}"
            node.embedding = self._compute_embedding(combined)
        self._persist()
        return node

    def delete_node(self, node_id: str) -> bool:
        if node_id not in self._nodes:
            return False
        del self._nodes[node_id]
        edge_ids_to_remove = [eid for eid, e in self._edges.items() if e.source_id == node_id or e.target_id == node_id]
        for eid in edge_ids_to_remove:
            edge = self._edges.pop(eid)
            self._adjacency[edge.source_id].discard(edge.target_id)
            self._adjacency[edge.target_id].discard(edge.source_id)
        self._adjacency.pop(node_id, None)
        self._persist()
        return True

    def create_edge(self, source_id: str, target_id: str, edge_type: EdgeType = EdgeType.relates_to, weight: float = 1.0) -> KnowledgeEdge:
        if source_id not in self._nodes:
            raise HTTPException(status_code=404, detail=f"Source node '{source_id}' not found")
        if target_id not in self._nodes:
            raise HTTPException(status_code=404, detail=f"Target node '{target_id}' not found")

        for existing in self._edges.values():
            if existing.source_id == source_id and existing.target_id == target_id and existing.type == edge_type:
                raise HTTPException(status_code=409, detail="Edge already exists")

        edge = KnowledgeEdge(source_id=source_id, target_id=target_id, type=edge_type, weight=weight)
        self._edges[edge.id] = edge
        self._adjacency[source_id].add(target_id)
        self._adjacency[target_id].add(source_id)
        self._persist()
        return edge

    def delete_edge(self, edge_id: str) -> bool:
        edge = self._edges.pop(edge_id, None)
        if not edge:
            return False
        self._adjacency[edge.source_id].discard(edge.target_id)
        self._adjacency[edge.target_id].discard(edge.source_id)
        self._persist()
        return True

    def query(self, req: GraphQuery) -> GraphResponse:
        start = time.monotonic()
        matched_nodes: Dict[str, KnowledgeNode] = {}
        query_emb = self._compute_embedding(req.query) if req.query else None

        for node in self._nodes.values():
            if req.node_types and node.type not in req.node_types:
                continue
            if req.tags and not any(t in node.tags for t in req.tags):
                continue
            if req.workspace and node.workspace != req.workspace:
                continue
            if node.importance < req.min_importance:
                continue
            if req.query:
                sim = self._cosine_similarity(query_emb, node.embedding) if query_emb else 0
                if sim < 0.1 and req.query.lower() not in node.name.lower() and req.query.lower() not in node.description.lower():
                    continue
            matched_nodes[node.id] = node

        if req.max_depth > 1:
            frontier = set(matched_nodes.keys())
            for _ in range(req.max_depth - 1):
                neighbors: Set[str] = set()
                for nid in frontier:
                    neighbors.update(self._adjacency.get(nid, set()))
                frontier = neighbors - set(matched_nodes.keys())
                for nid in frontier:
                    if nid in self._nodes:
                        matched_nodes[nid] = self._nodes[nid]

        matched_ids = set(matched_nodes.keys())
        edges = [e for e in self._edges.values() if e.source_id in matched_ids and e.target_id in matched_ids]

        sorted_nodes = sorted(matched_nodes.values(), key=lambda n: n.importance, reverse=True)

        return GraphResponse(
            nodes=sorted_nodes[:req.top_k],
            edges=edges[:req.top_k * 3],
            total_nodes=len(sorted_nodes),
            total_edges=len(edges),
            query_time_ms=(time.monotonic() - start) * 1000,
        )

    def get_related(self, node_id: str, max_depth: int = 2) -> GraphResponse:
        if node_id not in self._nodes:
            raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found")

        visited: Set[str] = {node_id}
        frontier: Set[str] = {node_id}
        for _ in range(max_depth):
            neighbors: Set[str] = set()
            for nid in frontier:
                neighbors.update(self._adjacency.get(nid, set()))
            frontier = neighbors - visited
            visited.update(frontier)

        nodes = [self._nodes[nid] for nid in visited if nid in self._nodes]
        edges = [e for e in self._edges.values() if e.source_id in visited and e.target_id in visited]
        return GraphResponse(nodes=nodes, edges=edges, total_nodes=len(nodes), total_edges=len(edges))

    def get_persona_map(self, workspace: str) -> GraphResponse:
        nodes = [n for n in self._nodes.values() if n.workspace == workspace]
        node_ids = {n.id for n in nodes}
        edges = [e for e in self._edges.values() if e.source_id in node_ids or e.target_id in node_ids]
        return GraphResponse(nodes=nodes, edges=edges, total_nodes=len(nodes), total_edges=len(edges))


app = FastAPI(
    title="ICHIN OS Service — Knowledge Graph",
    version="1.0.0",
    description="Knowledge graph with PARA + Zettelkasten + concept maps + skill trees",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graph = KnowledgeGraph()
_start_time = time.monotonic()


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        service="ichin-knowledge-graph",
        version="1.0.0",
        uptime=time.monotonic() - _start_time,
        total_nodes=len(graph._nodes),
        total_edges=len(graph._edges),
    )


@app.post("/nodes", response_model=KnowledgeNode)
async def create_node(body: NodeCreateRequest):
    try:
        return graph.create_node(body)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/nodes")
async def list_nodes(workspace: Optional[str] = None, type: Optional[str] = None):
    nodes = list(graph._nodes.values())
    if workspace:
        nodes = [n for n in nodes if n.workspace == workspace]
    if type:
        try:
            nt = NodeType(type)
            nodes = [n for n in nodes if n.type == nt]
        except ValueError:
            pass
    return [n.model_dump(mode="json") for n in sorted(nodes, key=lambda n: n.importance, reverse=True)[:200]]


@app.get("/node/{node_id}", response_model=KnowledgeNode)
async def get_node(node_id: str):
    node = graph.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found")
    return node


@app.put("/node/{node_id}")
async def update_node(node_id: str, body: Dict[str, Any]):
    node = graph.update_node(node_id, body)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found")
    return node.model_dump(mode="json")


@app.delete("/node/{node_id}")
async def delete_node(node_id: str):
    if not graph.delete_node(node_id):
        raise HTTPException(status_code=404, detail=f"Node '{node_id}' not found")
    return {"status": "deleted", "node_id": node_id}


@app.get("/nodes/search")
async def search_nodes(q: str, workspace: Optional[str] = None):
    nodes = graph.find_nodes_by_name(q, workspace)
    if not nodes:
        results = graph.query(GraphQuery(query=q, workspace=workspace))
        return [n.model_dump(mode="json") for n in results.nodes[:20]]
    return [n.model_dump(mode="json") for n in nodes[:20]]


@app.post("/edges")
async def create_edge(source_id: str, target_id: str, type: EdgeType = EdgeType.relates_to, weight: float = 1.0):
    try:
        edge = graph.create_edge(source_id, target_id, type, weight)
        return edge.model_dump(mode="json")
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.delete("/edge/{edge_id}")
async def delete_edge(edge_id: str):
    if not graph.delete_edge(edge_id):
        raise HTTPException(status_code=404, detail=f"Edge '{edge_id}' not found")
    return {"status": "deleted", "edge_id": edge_id}


@app.post("/query", response_model=GraphResponse)
async def query_graph(body: GraphQuery):
    try:
        return graph.query(body)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/node/{node_id}/related", response_model=GraphResponse)
async def get_related_nodes(node_id: str, depth: int = 2):
    try:
        return graph.get_related(node_id, depth)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/workspace/{workspace}/map", response_model=GraphResponse)
async def get_workspace_map(workspace: str):
    return graph.get_persona_map(workspace)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8070, reload=True)
