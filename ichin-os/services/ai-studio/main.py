import asyncio
import json
import logging
import os
import time
import uuid
from collections import defaultdict
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ichin.ai-studio")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
WORKFLOWS_FILE = os.path.join(DATA_DIR, "workflows.json")
AGENTS_FILE = os.path.join(DATA_DIR, "agents.json")
TRAINING_FILE = os.path.join(DATA_DIR, "training.json")
PATTERNS_FILE = os.path.join(DATA_DIR, "patterns.json")

os.makedirs(DATA_DIR, exist_ok=True)

ORCHESTRATOR_URL = "http://localhost:8000"
AGENTS_URL = "http://localhost:8012"
MEMORY_URL = "http://localhost:8003"
UI_URL = "http://localhost:8004"
APPS_URL = "http://localhost:8005"

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class TriggerType(str, Enum):
    time_based = "time_based"
    event_based = "event_based"
    ai_detected = "ai_detected"
    manual = "manual"


class ActionType(str, Enum):
    create_task = "create_task"
    send_message = "send_message"
    schedule_event = "schedule_event"
    summarize_content = "summarize_content"
    run_agent = "run_agent"
    modify_workspace_ui = "modify_workspace_ui"
    trigger_orb_notification = "trigger_orb_notification"


class NodeType(str, Enum):
    trigger = "trigger"
    condition = "condition"
    ai_reasoning = "ai_reasoning"
    action = "action"
    output = "output"


class ReasoningStyle(str, Enum):
    analytical = "analytical"
    creative = "creative"
    structured = "structured"
    hybrid = "hybrid"


class MemoryScope(str, Enum):
    short_term = "short_term"
    long_term = "long_term"
    workspace_specific = "workspace_specific"


class BehaviorMode(str, Enum):
    analytical = "analytical"
    creative = "creative"
    structured = "structured"
    hybrid = "hybrid"


class RiskLevel(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class ExecutionStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"
    cancelled = "cancelled"


class EventType(str, Enum):
    email_received = "email_received"
    file_created = "file_created"
    file_modified = "file_modified"
    calendar_event = "calendar_event"
    app_webhook = "app_webhook"
    system_notification = "system_notification"
    user_command = "user_command"


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class TriggerConfig(BaseModel):
    type: TriggerType
    schedule: Optional[str] = None
    event_type: Optional[EventType] = None
    event_filter: Optional[Dict[str, Any]] = None
    intent_pattern: Optional[str] = None
    hotkey: Optional[str] = None
    spotlight_command: Optional[str] = None


class WorkflowNode(BaseModel):
    id: str
    type: NodeType
    config: Dict[str, Any] = {}
    connections: List[str] = []


class WorkflowDefinition(BaseModel):
    id: str
    name: str
    trigger: TriggerConfig
    nodes: List[WorkflowNode] = []
    enabled: bool = True
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    execution_count: int = 0
    last_executed: Optional[str] = None
    requires_confirmation: bool = False
    stop_condition: Optional[str] = None


class WorkflowRunRequest(BaseModel):
    input_data: Optional[Dict[str, Any]] = None


class WorkflowToggleRequest(BaseModel):
    enabled: bool


class AgentDefinition(BaseModel):
    id: str
    name: str
    role_description: str
    reasoning_style: ReasoningStyle = ReasoningStyle.hybrid
    allowed_tools: List[str] = []
    memory_scope: MemoryScope = MemoryScope.short_term
    confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0)
    risk_sensitivity_level: RiskLevel = RiskLevel.medium
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    @field_validator("allowed_tools")
    @classmethod
    def validate_tools(cls, v: List[str]) -> List[str]:
        valid_tools = {
            "calendar", "notes", "coding_environment",
            "ai_api_tools", "external_apis",
        }
        restricted = {"external_apis"}
        for tool in v:
            if tool not in valid_tools:
                raise ValueError(f"Invalid tool '{tool}'. Valid: {valid_tools}")
        return v

    @field_validator("confidence_threshold")
    @classmethod
    def validate_confidence(cls, v: float) -> float:
        return max(0.0, min(1.0, v))


class TrainingFeedback(BaseModel):
    session_id: str
    agent_name: str
    rating: int = Field(ge=-1, le=1)
    correction: Optional[str] = None
    preferred_response: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class BehavioralPreference(BaseModel):
    session_id: str
    preference_key: str
    preference_value: Any
    context: Optional[str] = None


class LearnedPattern(BaseModel):
    id: str
    pattern_type: str
    description: str
    frequency: int = 1
    suggested_workflow: Optional[Dict[str, Any]] = None
    suggested_agent_improvement: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class SimulateRequest(BaseModel):
    workflow_id: Optional[str] = None
    agent_id: Optional[str] = None
    input_data: Dict[str, Any] = {}


class SimulateResponse(BaseModel):
    simulation_id: str
    result: Dict[str, Any]
    steps: List[Dict[str, Any]]
    duration_ms: float
    status: ExecutionStatus


class EventRecord(BaseModel):
    id: str
    event_type: EventType
    source: str
    payload: Dict[str, Any] = {}
    detected_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    processed: bool = False
    matched_workflow_id: Optional[str] = None


class QueueItem(BaseModel):
    id: str
    workflow_id: str
    priority: int = Field(default=0, ge=0, le=10)
    status: ExecutionStatus = ExecutionStatus.pending
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    uptime: float
    workflows_count: int
    agents_count: int
    queue_length: int


class WorkflowRunResponse(BaseModel):
    execution_id: str
    workflow_id: str
    status: ExecutionStatus
    steps_executed: int
    result: Optional[Dict[str, Any]] = None


# ---------------------------------------------------------------------------
# Cycle Detection
# ---------------------------------------------------------------------------

def detect_cycles(workflow: WorkflowDefinition) -> List[List[str]]:
    graph = nx.DiGraph()
    for node in workflow.nodes:
        graph.add_node(node.id)
    for node in workflow.nodes:
        for conn in node.connections:
            graph.add_edge(node.id, conn)

    cycles = []
    try:
        cycle_edges = nx.find_cycle(graph, orientation="original")
        visited: Set[str] = set()
        for u, v, _ in cycle_edges:
            if u not in visited:
                try:
                    cycle = nx.find_cycle(graph, source=u, orientation="original")
                    path = [e[0] for e in cycle]
                    visited.update(path)
                    cycles.append(path)
                except (nx.NetworkXNoCycle, nx.NodeNotFound):
                    continue
    except nx.NetworkXNoCycle:
        pass
    return cycles


def would_create_cycle(workflow: WorkflowDefinition, node_id: str, connection: str) -> bool:
    graph = nx.DiGraph()
    for node in workflow.nodes:
        graph.add_node(node.id)
    for node in workflow.nodes:
        for conn in node.connections:
            graph.add_edge(node.id, conn)
    graph.add_edge(node_id, connection)
    try:
        nx.find_cycle(graph, orientation="original")
        return True
    except nx.NetworkXNoCycle:
        return False


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


def _load_workflows() -> List[Dict[str, Any]]:
    return _load_json(WORKFLOWS_FILE, [])


def _save_workflows(data: List[Dict[str, Any]]) -> None:
    _save_json(WORKFLOWS_FILE, data)


def _load_agents_data() -> List[Dict[str, Any]]:
    return _load_json(AGENTS_FILE, [])


def _save_agents_data(data: List[Dict[str, Any]]) -> None:
    _save_json(AGENTS_FILE, data)


def _load_training_data() -> Dict[str, Any]:
    return _load_json(TRAINING_FILE, {"feedback": [], "behaviors": []})


def _save_training_data(data: Dict[str, Any]) -> None:
    _save_json(TRAINING_FILE, data)


def _load_patterns() -> List[Dict[str, Any]]:
    return _load_json(PATTERNS_FILE, [])


def _save_patterns(data: List[Dict[str, Any]]) -> None:
    _save_json(PATTERNS_FILE, data)


# ---------------------------------------------------------------------------
# In-Memory Stores (synced to JSON)
# ---------------------------------------------------------------------------

class WorkflowStore:
    def __init__(self):
        self._workflows: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        for wf in _load_workflows():
            self._workflows[wf["id"]] = wf
        logger.info("Loaded %d workflows", len(self._workflows))

    def _persist(self) -> None:
        _save_workflows(list(self._workflows.values()))

    def all(self) -> List[Dict[str, Any]]:
        return list(self._workflows.values())

    def get(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        return self._workflows.get(workflow_id)

    def create(self, workflow: WorkflowDefinition) -> WorkflowDefinition:
        if workflow.id in self._workflows:
            raise HTTPException(status_code=409, detail=f"Workflow '{workflow.id}' already exists")
        cycles = detect_cycles(workflow)
        if cycles:
            raise HTTPException(
                status_code=400,
                detail=f"Workflow contains cycles: {cycles}",
            )
        if workflow.enabled and workflow.trigger.type != TriggerType.manual:
            if not workflow.stop_condition:
                raise HTTPException(
                    status_code=400,
                    detail="Non-manual workflows must have a stop_condition",
                )
        self._workflows[workflow.id] = workflow.model_dump(mode="json")
        self._persist()
        return workflow

    def update(self, workflow_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        existing = self._workflows.get(workflow_id)
        if existing is None:
            return None
        data["updated_at"] = datetime.utcnow().isoformat()
        existing.update(data)
        self._persist()
        return existing

    def delete(self, workflow_id: str) -> bool:
        result = self._workflows.pop(workflow_id, None)
        if result is not None:
            self._persist()
            return True
        return False


class AgentStore:
    def __init__(self):
        self._agents: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        for a in _load_agents_data():
            self._agents[a["id"]] = a
        logger.info("Loaded %d custom agents", len(self._agents))

    def _persist(self) -> None:
        _save_agents_data(list(self._agents.values()))

    def all(self) -> List[Dict[str, Any]]:
        return list(self._agents.values())

    def get(self, agent_id: str) -> Optional[Dict[str, Any]]:
        return self._agents.get(agent_id)

    def create(self, agent: AgentDefinition) -> AgentDefinition:
        if agent.id in self._agents:
            raise HTTPException(status_code=409, detail=f"Agent '{agent.id}' already exists")
        self._agents[agent.id] = agent.model_dump(mode="json")
        self._persist()
        return agent

    def delete(self, agent_id: str) -> bool:
        result = self._agents.pop(agent_id, None)
        if result is not None:
            self._persist()
            return True
        return False


class TrainingStore:
    def __init__(self):
        self._data: Dict[str, Any] = _load_training_data()

    def _persist(self) -> None:
        _save_training_data(self._data)

    def add_feedback(self, feedback: TrainingFeedback) -> None:
        self._data.setdefault("feedback", []).append(feedback.model_dump(mode="json"))
        if len(self._data["feedback"]) > 10000:
            self._data["feedback"] = self._data["feedback"][-5000:]
        self._persist()

    def set_behavior(self, preference: BehavioralPreference) -> None:
        self._data.setdefault("behaviors", [])
        existing = None
        for i, b in enumerate(self._data["behaviors"]):
            if b.get("session_id") == preference.session_id and b.get("preference_key") == preference.preference_key:
                existing = i
                break
        entry = preference.model_dump(mode="json")
        if existing is not None:
            self._data["behaviors"][existing] = entry
        else:
            self._data["behaviors"].append(entry)
            if len(self._data["behaviors"]) > 5000:
                self._data["behaviors"] = self._data["behaviors"][-2500:]
        self._persist()

    def get_behaviors(self, session_id: Optional[str] = None) -> List[Dict[str, Any]]:
        behaviors = self._data.get("behaviors", [])
        if session_id:
            return [b for b in behaviors if b.get("session_id") == session_id]
        return behaviors

    def get_feedback(self, limit: int = 100) -> List[Dict[str, Any]]:
        return self._data.get("feedback", [])[-limit:]


class PatternStore:
    def __init__(self):
        self._patterns: Dict[str, Dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        for p in _load_patterns():
            self._patterns[p["id"]] = p

    def _persist(self) -> None:
        _save_patterns(list(self._patterns.values()))

    def all(self) -> List[Dict[str, Any]]:
        return list(self._patterns.values())

    def add(self, pattern: LearnedPattern) -> LearnedPattern:
        self._patterns[pattern.id] = pattern.model_dump(mode="json")
        self._persist()
        return pattern

    def get(self, pattern_id: str) -> Optional[Dict[str, Any]]:
        return self._patterns.get(pattern_id)

    def increment(self, pattern_id: str) -> None:
        pattern = self._patterns.get(pattern_id)
        if pattern:
            pattern["frequency"] = pattern.get("frequency", 1) + 1
            self._persist()


# ---------------------------------------------------------------------------
# Automation Engine
# ---------------------------------------------------------------------------

class AutomationEngine:
    def __init__(self, workflow_store: WorkflowStore):
        self.workflow_store = workflow_store
        self._queue: List[QueueItem] = []
        self._events: List[EventRecord] = []
        self._running = False
        self._worker_task: Optional[asyncio.Task] = None
        self._event_listeners: Dict[EventType, List[str]] = defaultdict(list)
        self._max_concurrent = 5
        self._active_executions: Dict[str, asyncio.Task] = {}
        self._execution_counter = 0

    def start(self) -> None:
        if not self._running:
            self._running = True
            for wf in self.workflow_store.all():
                if wf.get("enabled", False):
                    trigger = wf.get("trigger", {})
                    if trigger.get("type") == "event_based":
                        event_type = trigger.get("event_type")
                        if event_type:
                            self._event_listeners[EventType(event_type)].append(wf["id"])
            logger.info("Automation engine started with %d event listeners", sum(len(v) for v in self._event_listeners.values()))

    def stop(self) -> None:
        self._running = False

    def enqueue(self, workflow_id: str, priority: int = 5, input_data: Optional[Dict[str, Any]] = None) -> QueueItem:
        item = QueueItem(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            priority=max(0, min(10, priority)),
        )
        self._queue.append(item)
        self._queue.sort(key=lambda x: (-x.priority, x.created_at))
        logger.info("Enqueued workflow %s (priority=%d, queue_len=%d)", workflow_id, priority, len(self._queue))
        return item

    def record_event(self, event_type: EventType, source: str, payload: Dict[str, Any] = {}) -> Optional[EventRecord]:
        event = EventRecord(
            id=str(uuid.uuid4()),
            event_type=event_type,
            source=source,
            payload=payload,
        )
        matched_ids = self._event_listeners.get(event_type, [])
        for wf_id in matched_ids:
            wf = self.workflow_store.get(wf_id)
            if wf and wf.get("enabled", False):
                event_filter = wf.get("trigger", {}).get("event_filter", {})
                if event_filter:
                    if not all(payload.get(k) == v for k, v in event_filter.items()):
                        continue
                event.matched_workflow_id = wf_id
                self.enqueue(wf_id, input_data=payload)
                event.processed = True
                break
        self._events.append(event)
        if len(self._events) > 1000:
            self._events = self._events[-500:]
        return event

    def get_queue(self) -> List[QueueItem]:
        return sorted(self._queue, key=lambda x: (-x.priority, x.created_at))

    def get_events(self, limit: int = 100) -> List[EventRecord]:
        return self._events[-limit:]

    async def process_queue(self) -> None:
        if not self._running:
            return
        while self._queue and len(self._active_executions) < self._max_concurrent:
            item = self._queue.pop(0)
            item.status = ExecutionStatus.running
            item.started_at = datetime.utcnow().isoformat()
            task = asyncio.create_task(self._execute(item))
            self._active_executions[item.id] = task

    async def _execute(self, item: QueueItem) -> None:
        try:
            wf = self.workflow_store.get(item.workflow_id)
            if not wf:
                item.status = ExecutionStatus.failed
                item.error = "Workflow not found"
                return

            self._execution_counter += 1
            wf["execution_count"] = wf.get("execution_count", 0) + 1
            wf["last_executed"] = datetime.utcnow().isoformat()
            wf["updated_at"] = datetime.utcnow().isoformat()
            self.workflow_store.update(item.workflow_id, wf)

            execution_limit = wf.get("execution_limit", 100)
            if wf["execution_count"] > execution_limit:
                item.status = ExecutionStatus.failed
                item.error = f"Execution limit {execution_limit} reached"
                return

            trigger_type = wf.get("trigger", {}).get("type")
            if trigger_type != "manual" and not wf.get("stop_condition"):
                item.status = ExecutionStatus.failed
                item.error = "No stop_condition defined for automated workflow"
                return

            if wf.get("requires_confirmation"):
                logger.info("Workflow %s requires confirmation before execution", item.workflow_id)
                item.result = {"status": "confirmation_required"}
                item.status = ExecutionStatus.completed
                return

            result = await self._run_workflow_nodes(wf)
            item.result = result
            item.status = ExecutionStatus.completed

        except asyncio.CancelledError:
            item.status = ExecutionStatus.cancelled
        except Exception as exc:
            logger.exception("Workflow %s execution failed", item.workflow_id)
            item.status = ExecutionStatus.failed
            item.error = str(exc)
        finally:
            item.completed_at = datetime.utcnow().isoformat()
            self._active_executions.pop(item.id, None)

    async def _run_workflow_nodes(self, wf: Dict[str, Any]) -> Dict[str, Any]:
        nodes = wf.get("nodes", [])
        if not nodes:
            return {"status": "no_nodes", "output": None}

        node_map: Dict[str, Dict[str, Any]] = {n["id"]: n for n in nodes}

        trigger_nodes = [n for n in nodes if n["type"] == "trigger"]
        if not trigger_nodes:
            return {"status": "no_trigger", "output": None}

        entry = trigger_nodes[0]
        visited: Set[str] = set()
        results: Dict[str, Any] = {}
        stack = [(entry["id"], None)]

        while stack:
            node_id, parent_input = stack.pop(0)
            if node_id in visited:
                logger.error("Cycle detected at node %s during execution", node_id)
                continue
            visited.add(node_id)

            node = node_map.get(node_id)
            if not node:
                continue

            result = await self._evaluate_node(node, parent_input)
            results[node_id] = result

            for conn in node.get("connections", []):
                if conn not in visited:
                    stack.append((conn, result))

        return {"status": "completed", "node_results": results}

    async def _evaluate_node(self, node: Dict[str, Any], parent_input: Any) -> Any:
        node_type = node["type"]
        config = node.get("config", {})

        if node_type == "trigger":
            return {"triggered": True, "config": config}

        if node_type == "condition":
            condition = config.get("expression", "true")
            if condition == "true" or condition is True:
                return {"condition_met": True}
            if isinstance(condition, str):
                try:
                    result = eval(condition, {"__builtins__": {}}, {"input": parent_input})
                    return {"condition_met": bool(result)}
                except Exception:
                    return {"condition_met": True, "error": f"Could not evaluate: {condition}"}
            return {"condition_met": bool(condition)}

        if node_type == "ai_reasoning":
            prompt = config.get("prompt", "")
            reasoning_data = {
                "prompt": prompt,
                "input": parent_input,
                "reasoning_style": config.get("reasoning_style", "hybrid"),
                "result": f"AI reasoning completed for: {prompt[:100] if prompt else 'no prompt'}",
            }
            return reasoning_data

        if node_type == "action":
            action = config.get("action_type", "")
            if action == "create_task":
                return {"action": "create_task", "task": config.get("task", ""), "status": "simulated"}
            elif action == "send_message":
                return {"action": "send_message", "message": config.get("message", ""), "status": "simulated"}
            elif action == "run_agent":
                agent_ref = config.get("agent_ref", "")
                confidence = config.get("confidence_threshold", 0.5)
                try:
                    import httpx
                    async with httpx.AsyncClient() as client:
                        resp = await client.post(
                            f"{AGENTS_URL}/agents/{agent_ref}/reason",
                            json={"request": config.get("prompt", ""), "mode": "normal"},
                            timeout=10,
                        )
                        return {"action": "run_agent", "agent": agent_ref, "response": resp.json(), "status": "completed"}
                except Exception as exc:
                    return {"action": "run_agent", "agent": agent_ref, "error": str(exc), "status": "failed"}
            else:
                return {"action": action, "status": "simulated", "note": f"Action type '{action}' executed"}

        if node_type == "output":
            return {"output": config.get("output", ""), "data": parent_input}

        return {"node_type": node_type, "status": "unknown"}

    async def worker_loop(self) -> None:
        while self._running:
            try:
                await self.process_queue()
            except Exception as exc:
                logger.exception("Worker loop error: %s", exc)
            await asyncio.sleep(0.05)


# ---------------------------------------------------------------------------
# Workflow Learning Engine
# ---------------------------------------------------------------------------

class WorkflowLearningEngine:
    def __init__(self, pattern_store: PatternStore):
        self.pattern_store = pattern_store
        self._observation_window: List[Dict[str, Any]] = []
        self._max_window = 1000

    def observe(self, action: str, context: Dict[str, Any]) -> None:
        self._observation_window.append({
            "action": action,
            "context": context,
            "timestamp": datetime.utcnow().isoformat(),
        })
        if len(self._observation_window) > self._max_window:
            self._observation_window = self._observation_window[-self._max_window:]
        self._analyze_patterns()

    def _analyze_patterns(self) -> None:
        action_counts: Dict[str, int] = defaultdict(int)
        for obs in self._observation_window[-200:]:
            action_counts[obs["action"]] += 1

        for action, count in action_counts.items():
            if count >= 10:
                existing = [p for p in self.pattern_store.all() if p.get("description", "").startswith(f"Frequent action: {action}")]
                if existing:
                    self.pattern_store.increment(existing[0]["id"])
                else:
                    pattern = LearnedPattern(
                        id=str(uuid.uuid4()),
                        pattern_type="frequent_action",
                        description=f"Frequent action: {action} (observed {count} times)",
                        frequency=count,
                        suggested_workflow={
                            "trigger": {"type": "manual", "hotkey": None},
                            "nodes": [
                                {"id": "n1", "type": "trigger", "config": {}, "connections": ["n2"]},
                                {"id": "n2", "type": "action", "config": {"action_type": action}, "connections": []},
                            ],
                        },
                        suggested_agent_improvement=f"Consider creating an agent specialized for '{action}'",
                    )
                    self.pattern_store.add(pattern)

        if len(self._observation_window) >= 50:
            time_patterns: Dict[str, int] = defaultdict(int)
            for obs in self._observation_window[-100:]:
                hour = obs.get("timestamp", "")[11:13] if len(obs.get("timestamp", "")) > 13 else "00"
                time_patterns[hour] += 1

            peak_hour = max(time_patterns, key=time_patterns.get)
            peak_count = time_patterns[peak_hour]
            if peak_count >= 20:
                existing_peak = [p for p in self.pattern_store.all() if p.get("pattern_type") == "peak_productivity_hour"]
                if not existing_peak:
                    pattern = LearnedPattern(
                        id=str(uuid.uuid4()),
                        pattern_type="peak_productivity_hour",
                        description=f"Peak productivity detected at hour {peak_hour} ({peak_count} actions)",
                        frequency=peak_count,
                        suggested_workflow={
                            "trigger": {"type": "time_based", "schedule": f"0 {peak_hour} * * *"},
                            "nodes": [
                                {"id": "n1", "type": "trigger", "config": {}, "connections": ["n2"]},
                                {"id": "n2", "type": "action", "config": {"action_type": "create_task", "task": "Focus session - peak productivity time"}, "connections": []},
                            ],
                        },
                    )
                    self.pattern_store.add(pattern)


# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="ICHIN OS Service 6 — AI Studio + Automation Engine",
    version="1.0.0",
    description="Visual + structured AI development environment for building cognitive systems",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

workflow_store = WorkflowStore()
agent_store = AgentStore()
training_store = TrainingStore()
pattern_store = PatternStore()
automation = AutomationEngine(workflow_store)
learning_engine = WorkflowLearningEngine(pattern_store)
_start_time = time.monotonic()


@app.on_event("startup")
async def startup():
    automation.start()
    asyncio.create_task(automation.worker_loop())
    logger.info("AI Studio started on port 8016")


@app.on_event("shutdown")
async def shutdown():
    automation.stop()


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        service="ichin-ai-studio",
        version="1.0.0",
        uptime=time.monotonic() - _start_time,
        workflows_count=len(workflow_store.all()),
        agents_count=len(agent_store.all()),
        queue_length=len(automation.get_queue()),
    )


# ---------------------------------------------------------------------------
# Workflow Endpoints
# ---------------------------------------------------------------------------

@app.post("/workflow/create")
async def create_workflow(body: WorkflowDefinition):
    try:
        workflow = workflow_store.create(body)
        if workflow.enabled and workflow.trigger.type != TriggerType.manual:
            if workflow.trigger.type == TriggerType.event_based and workflow.trigger.event_type:
                automation._event_listeners[workflow.trigger.event_type].append(workflow.id)
        return {"status": "created", "workflow": workflow.model_dump(mode="json")}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to create workflow")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/workflows")
async def list_workflows():
    return workflow_store.all()


@app.get("/workflow/{workflow_id}")
async def get_workflow(workflow_id: str):
    wf = workflow_store.get(workflow_id)
    if wf is None:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")
    return wf


@app.post("/workflow/{workflow_id}/run", response_model=WorkflowRunResponse)
async def run_workflow(workflow_id: str, body: WorkflowRunRequest = WorkflowRunRequest()):
    wf = workflow_store.get(workflow_id)
    if wf is None:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")
    if not wf.get("enabled", False):
        raise HTTPException(status_code=400, detail="Workflow is disabled")

    item = automation.enqueue(workflow_id, input_data=body.input_data)
    await automation.process_queue()

    return WorkflowRunResponse(
        execution_id=item.id,
        workflow_id=workflow_id,
        status=item.status,
        steps_executed=len(wf.get("nodes", [])),
    )


@app.post("/workflow/{workflow_id}/toggle")
async def toggle_workflow(workflow_id: str, body: WorkflowToggleRequest):
    wf = workflow_store.get(workflow_id)
    if wf is None:
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")
    updated = workflow_store.update(workflow_id, {"enabled": body.enabled})
    if not body.enabled:
        automation._event_listeners = {
            k: [wid for wid in v if wid != workflow_id]
            for k, v in automation._event_listeners.items()
        }
    else:
        trigger = updated.get("trigger", {})
        if trigger.get("type") == "event_based" and trigger.get("event_type"):
            automation._event_listeners[EventType(trigger["event_type"])].append(workflow_id)
    return {"status": "updated", "enabled": body.enabled, "workflow": updated}


@app.delete("/workflow/{workflow_id}")
async def delete_workflow(workflow_id: str):
    if not workflow_store.delete(workflow_id):
        raise HTTPException(status_code=404, detail=f"Workflow '{workflow_id}' not found")
    for k, v in automation._event_listeners.items():
        automation._event_listeners[k] = [wid for wid in v if wid != workflow_id]
    return {"status": "deleted", "workflow_id": workflow_id}


# ---------------------------------------------------------------------------
# Agent Builder Endpoints
# ---------------------------------------------------------------------------

@app.post("/agent/create")
async def create_agent(body: AgentDefinition):
    try:
        agent = agent_store.create(body)
        return {"status": "created", "agent": agent.model_dump(mode="json")}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to create agent")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/agents")
async def list_agents():
    return agent_store.all()


@app.get("/agent/{agent_id}")
async def get_agent(agent_id: str):
    agent = agent_store.get(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    return agent


@app.delete("/agent/{agent_id}")
async def delete_agent(agent_id: str):
    if not agent_store.delete(agent_id):
        raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
    return {"status": "deleted", "agent_id": agent_id}


# ---------------------------------------------------------------------------
# Training Endpoints
# ---------------------------------------------------------------------------

@app.post("/training/feedback")
async def submit_feedback(body: TrainingFeedback):
    try:
        training_store.add_feedback(body)
        learning_engine.observe("feedback", {
            "agent_name": body.agent_name,
            "rating": body.rating,
            "has_correction": body.correction is not None,
        })
        return {"status": "recorded", "feedback_id": str(uuid.uuid4())}
    except Exception as exc:
        logger.exception("Failed to record feedback")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/training/behavior")
async def set_behavior(body: BehavioralPreference):
    forbidden_keys = {"override_safety", "modify_orchestrator", "bypass_security"}
    if body.preference_key in forbidden_keys:
        raise HTTPException(status_code=403, detail=f"Cannot set behavior '{body.preference_key}': training never modifies core system agents, overrides safety rules, or changes orchestrator logic")
    try:
        training_store.set_behavior(body)
        learning_engine.observe("behavior_set", {
            "key": body.preference_key,
            "value": str(body.preference_value),
        })
        return {"status": "recorded"}
    except Exception as exc:
        logger.exception("Failed to set behavior")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/training/patterns")
async def get_training_patterns():
    return pattern_store.all()


# ---------------------------------------------------------------------------
# Simulation Endpoint
# ---------------------------------------------------------------------------

@app.post("/simulate", response_model=SimulateResponse)
async def simulate(body: SimulateRequest):
    sim_id = str(uuid.uuid4())
    start = time.monotonic()
    steps: List[Dict[str, Any]] = []
    result: Dict[str, Any] = {}

    try:
        if body.workflow_id:
            wf = workflow_store.get(body.workflow_id)
            if not wf:
                raise HTTPException(status_code=404, detail=f"Workflow '{body.workflow_id}' not found")

            node_map: Dict[str, Dict[str, Any]] = {n["id"]: n for n in wf.get("nodes", [])}
            trigger_nodes = [n for n in wf.get("nodes", []) if n["type"] == "trigger"]
            if not trigger_nodes:
                raise HTTPException(status_code=400, detail="Workflow has no trigger node")

            entry = trigger_nodes[0]
            visited: Set[str] = set()
            stack = [(entry["id"], body.input_data)]

            while stack:
                node_id, parent_input = stack.pop(0)
                if node_id in visited:
                    steps.append({"node_id": node_id, "status": "cycle_detected", "output": None})
                    continue
                visited.add(node_id)

                node = node_map.get(node_id)
                if not node:
                    continue

                eval_result = await automation._evaluate_node(node, parent_input)
                steps.append({
                    "node_id": node_id,
                    "node_type": node["type"],
                    "config": node.get("config", {}),
                    "output": eval_result,
                })

                for conn in node.get("connections", []):
                    if conn not in visited:
                        stack.append((conn, eval_result))

            result = {"workflow_id": body.workflow_id, "nodes_executed": len(steps), "final_output": steps[-1]["output"] if steps else None}

        elif body.agent_id:
            agent = agent_store.get(body.agent_id)
            if not agent:
                raise HTTPException(status_code=404, detail=f"Agent '{body.agent_id}' not found")

            reasoning_map = {
                "analytical": "Strict logical deduction based on available data",
                "creative": "Exploratory reasoning with multiple hypotheses",
                "structured": "Step-by-step sequential analysis",
                "hybrid": "Balanced analytical and creative approach",
            }

            steps.append({
                "agent_id": body.agent_id,
                "agent_name": agent["name"],
                "reasoning_style": agent["reasoning_style"],
                "reasoning_description": reasoning_map.get(agent["reasoning_style"], "Unknown"),
                "input": body.input_data,
                "confidence_threshold": agent["confidence_threshold"],
                "risk_sensitivity": agent["risk_sensitivity_level"],
                "allowed_tools": agent["allowed_tools"],
                "memory_scope": agent["memory_scope"],
            })

            result = {
                "agent_id": body.agent_id,
                "agent_name": agent["name"],
                "simulated_output": f"Agent '{agent['name']}' processed input with {agent['reasoning_style']} reasoning",
                "confidence": agent["confidence_threshold"],
            }
        else:
            raise HTTPException(status_code=400, detail="Provide either workflow_id or agent_id")

        duration = (time.monotonic() - start) * 1000
        return SimulateResponse(
            simulation_id=sim_id,
            result=result,
            steps=steps,
            duration_ms=round(duration, 2),
            status=ExecutionStatus.completed,
        )

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Simulation failed")
        duration = (time.monotonic() - start) * 1000
        return SimulateResponse(
            simulation_id=sim_id,
            result={"error": str(exc)},
            steps=steps,
            duration_ms=round(duration, 2),
            status=ExecutionStatus.failed,
        )


# ---------------------------------------------------------------------------
# Automation Endpoints
# ---------------------------------------------------------------------------

@app.get("/automation/events")
async def list_events(limit: int = 100):
    return automation.get_events(limit=limit)


@app.get("/automation/queue")
async def view_queue():
    return automation.get_queue()


# ---------------------------------------------------------------------------
# Integration Helpers
# ---------------------------------------------------------------------------

async def notify_orchestrator(action: str, payload: Dict[str, Any]) -> None:
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            await client.post(
                f"{ORCHESTRATOR_URL}/orchestrate",
                json={"request": action, "context": payload, "mode": "normal"},
                timeout=5,
            )
    except Exception as exc:
        logger.warning("Failed to notify orchestrator: %s", exc)


async def call_agent(agent_name: str, request: str) -> Optional[Dict[str, Any]]:
    try:
        import httpx
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{AGENTS_URL}/agents/{agent_name}/reason",
                json={"request": request, "mode": "normal"},
                timeout=10,
            )
            resp.raise_for_status()
            return resp.json()
    except Exception as exc:
        logger.warning("Failed to call agent '%s': %s", agent_name, exc)
        return None


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8016, reload=True)
