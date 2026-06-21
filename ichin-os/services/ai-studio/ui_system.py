import asyncio
import logging
import time
import uuid
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ichin.ui-system")

# ---------------------------------------------------------------------------
# Service URLs
# ---------------------------------------------------------------------------

ORCHESTRATOR_URL = "http://localhost:8000"
AGENTS_URL = "http://localhost:8012"
MEMORY_URL = "http://localhost:8003"
AI_STUDIO_URL = "http://localhost:8016"

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class WorkspaceType(str, Enum):
    study = "study"
    coding = "coding"
    learning = "learning"
    personal = "personal"


class FocusMode(str, Enum):
    normal = "normal"
    focus = "focus"
    deep_focus = "deep_focus"
    lock = "lock"


class OrbStateEnum(str, Enum):
    idle = "idle"
    active = "active"
    critical = "critical"


class PanelPosition(str, Enum):
    center = "center"
    left = "left"
    right = "right"
    top = "top"
    bottom = "bottom"
    floating = "floating"


class Layer(str, Enum):
    orb = "orb"
    context_panels = "context_panels"
    workspace = "workspace"
    system_shell = "system_shell"
    kernel_events = "kernel_events"


class PanelVisibility(str, Enum):
    visible = "visible"
    fading_in = "fading_in"
    fading_out = "fading_out"
    hidden = "hidden"


class FocusAggression(str, Enum):
    none_ = "none"
    soft = "soft"
    strong = "strong"
    strict = "strict"


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    uptime: float
    current_workspace: str
    current_focus_mode: str
    orb_state: str
    visible_panels: int


class UIState(BaseModel):
    workspace: WorkspaceType = WorkspaceType.personal
    mode: FocusMode = FocusMode.normal
    orb_state: OrbStateEnum = OrbStateEnum.idle
    visible_panels: List[str] = Field(default_factory=list)
    focus_mode: FocusMode = FocusMode.normal
    active_task: Optional[str] = None
    last_interaction: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    @field_validator("last_interaction")
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        return v or datetime.utcnow().isoformat()


class PanelDefinition(BaseModel):
    id: str
    name: str
    position: PanelPosition
    layer: Layer = Layer.workspace
    visibility: PanelVisibility = PanelVisibility.hidden
    width: Optional[str] = None
    height: Optional[str] = None
    order: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AnimationConfig(BaseModel):
    duration_ms: int = Field(default=400, ge=100, le=2000)
    easing: str = "cubic-bezier(0.4, 0, 0.2, 1)"
    delay_ms: int = Field(default=0, ge=0, le=1000)


class LayoutConfig(BaseModel):
    animations: AnimationConfig = Field(default_factory=AnimationConfig)
    spacing: str = "normal"
    density: str = "normal"
    grid_columns: int = 12
    transition_duration_ms: int = 400
    allow_morph: bool = True
    blur_background: bool = True
    high_contrast: bool = False


class WorkspaceLayout(BaseModel):
    workspace: WorkspaceType
    panels: List[PanelDefinition] = Field(default_factory=list)
    layout_config: LayoutConfig = Field(default_factory=LayoutConfig)


class OrbNotification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    message: str
    severity: OrbStateEnum = OrbStateEnum.active
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    expires_at: str = Field(default_factory=lambda: (datetime.utcnow() + timedelta(seconds=30)).isoformat())
    actionable: bool = True
    dismissed: bool = False


class OrbState(BaseModel):
    state: OrbStateEnum = OrbStateEnum.idle
    notifications: List[OrbNotification] = Field(default_factory=list)
    timer_remaining: float = 0.0
    position: str = "mid-right"
    pulse_intensity: float = Field(default=0.0, ge=0.0, le=1.0)
    glow_opacity: float = Field(default=0.05, ge=0.0, le=1.0)


class FocusState(BaseModel):
    mode: FocusMode = FocusMode.normal
    aggression_level: FocusAggression = FocusAggression.none_
    blocked_apps: List[str] = Field(default_factory=list)
    active_since: Optional[str] = None


class SpotlightSuggestion(BaseModel):
    label: str
    icon: str = "sparkles"
    action: str
    context: Optional[Dict[str, Any]] = None


class IntentRequest(BaseModel):
    text: str
    workspace: Optional[WorkspaceType] = None
    context: Dict[str, Any] = Field(default_factory=dict)


class IntentResponse(BaseModel):
    original_intent: str
    target_workspace: WorkspaceType
    panels_to_show: List[str]
    panels_to_hide: List[str]
    orb_state_change: Optional[OrbStateEnum] = None
    focus_mode_change: Optional[FocusMode] = None
    layout_transforms: List[Dict[str, Any]] = Field(default_factory=list)
    suggestions: List[SpotlightSuggestion] = Field(default_factory=list)


class SetFocusModeRequest(BaseModel):
    mode: FocusMode
    aggression_level: Optional[FocusAggression] = None


class UpdateUIStateRequest(BaseModel):
    workspace: Optional[WorkspaceType] = None
    mode: Optional[FocusMode] = None
    active_task: Optional[str] = None


class AmbientTickRequest(BaseModel):
    idle_seconds: float = 0.0
    active_workspace: Optional[WorkspaceType] = None
    current_mode: FocusMode = FocusMode.normal


class AmbientTickResponse(BaseModel):
    ui_collapsed: bool
    hidden_panels: List[str]
    visible_panels: List[str]
    orb_state: OrbStateEnum
    focus_adjustment: Optional[FocusMode] = None


class ComponentState(BaseModel):
    id: str
    name: str
    layer: Layer
    visibility: PanelVisibility
    position: PanelPosition
    z_index: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class OrbNotifyRequest(BaseModel):
    title: str
    message: str
    severity: OrbStateEnum = OrbStateEnum.active
    expires_seconds: int = 30
    actionable: bool = True


class DismissNotificationRequest(BaseModel):
    notification_id: str


# ---------------------------------------------------------------------------
# Workspace Layout Definitions
# ---------------------------------------------------------------------------

WORKSPACE_LAYOUTS: Dict[WorkspaceType, WorkspaceLayout] = {
    WorkspaceType.study: WorkspaceLayout(
        workspace=WorkspaceType.study,
        panels=[
            PanelDefinition(id="concept_map", name="Concept Map", position=PanelPosition.center, layer=Layer.workspace, order=1, visibility=PanelVisibility.visible),
            PanelDefinition(id="flashcard_gen", name="Flashcard Generator", position=PanelPosition.right, layer=Layer.workspace, order=2),
            PanelDefinition(id="notes_layer", name="Notes Layer", position=PanelPosition.left, layer=Layer.workspace, order=3),
            PanelDefinition(id="ai_tutor", name="AI Tutor", position=PanelPosition.floating, layer=Layer.context_panels, order=4),
            PanelDefinition(id="progress_tracker", name="Progress Tracker", position=PanelPosition.bottom, layer=Layer.workspace, order=5),
        ],
        layout_config=LayoutConfig(
            animations=AnimationConfig(duration_ms=700, easing="cubic-bezier(0.4, 0, 0.2, 1)", delay_ms=100),
            spacing="calm",
            density="reduced",
            transition_duration_ms=700,
        ),
    ),
    WorkspaceType.coding: WorkspaceLayout(
        workspace=WorkspaceType.coding,
        panels=[
            PanelDefinition(id="editor", name="Editor", position=PanelPosition.center, layer=Layer.workspace, order=1, visibility=PanelVisibility.visible),
            PanelDefinition(id="file_tree", name="File Tree", position=PanelPosition.left, layer=Layer.workspace, order=2),
            PanelDefinition(id="ai_debugger", name="AI Debugger", position=PanelPosition.right, layer=Layer.context_panels, order=3),
            PanelDefinition(id="terminal", name="Terminal", position=PanelPosition.bottom, layer=Layer.workspace, order=4),
            PanelDefinition(id="problems_panel", name="Problems", position=PanelPosition.bottom, layer=Layer.workspace, order=5),
        ],
        layout_config=LayoutConfig(
            animations=AnimationConfig(duration_ms=300, easing="cubic-bezier(0.25, 0.1, 0.25, 1)", delay_ms=0),
            spacing="tight",
            density="compact",
            grid_columns=16,
            transition_duration_ms=300,
            high_contrast=True,
        ),
    ),
    WorkspaceType.learning: WorkspaceLayout(
        workspace=WorkspaceType.learning,
        panels=[
            PanelDefinition(id="knowledge_graph", name="Knowledge Graph", position=PanelPosition.center, layer=Layer.workspace, order=1, visibility=PanelVisibility.visible),
            PanelDefinition(id="course_tree", name="Course Progression Tree", position=PanelPosition.right, layer=Layer.workspace, order=2),
            PanelDefinition(id="ai_explanation", name="AI Explanation Layer", position=PanelPosition.floating, layer=Layer.context_panels, order=3),
            PanelDefinition(id="resource_stream", name="Resource Stream", position=PanelPosition.left, layer=Layer.workspace, order=4),
            PanelDefinition(id="quiz_panel", name="Quiz Panel", position=PanelPosition.bottom, layer=Layer.workspace, order=5),
        ],
        layout_config=LayoutConfig(
            animations=AnimationConfig(duration_ms=600, easing="cubic-bezier(0.4, 0, 0.2, 1)", delay_ms=50),
            spacing="comfortable",
            density="normal",
            transition_duration_ms=600,
        ),
    ),
    WorkspaceType.personal: WorkspaceLayout(
        workspace=WorkspaceType.personal,
        panels=[
            PanelDefinition(id="calendar_timeline", name="Calendar Timeline", position=PanelPosition.center, layer=Layer.workspace, order=1, visibility=PanelVisibility.visible),
            PanelDefinition(id="task_list", name="Task List", position=PanelPosition.right, layer=Layer.workspace, order=2),
            PanelDefinition(id="email_stream", name="Email/Event Stream", position=PanelPosition.left, layer=Layer.workspace, order=3),
            PanelDefinition(id="planning_panel", name="Planning Panel", position=PanelPosition.floating, layer=Layer.context_panels, order=4),
            PanelDefinition(id="focus_timer", name="Focus Timer", position=PanelPosition.top, layer=Layer.workspace, order=5),
        ],
        layout_config=LayoutConfig(
            animations=AnimationConfig(duration_ms=500, easing="cubic-bezier(0.4, 0, 0.2, 1)", delay_ms=80),
            spacing="normal",
            density="normal",
            transition_duration_ms=500,
        ),
    ),
}

# ---------------------------------------------------------------------------
# Focus Mode Configuration
# ---------------------------------------------------------------------------

FOCUS_CONFIGS: Dict[FocusMode, Dict[str, Any]] = {
    FocusMode.normal: {
        "aggression": FocusAggression.none_,
        "blocked_apps": [],
        "allow_suggestions": True,
        "allow_notifications": True,
        "visible_panels_ratio": 1.0,
        "ui_opacity": 1.0,
        "orb_glow": 0.05,
        "description": "Full UI visibility, AI suggestions active",
    },
    FocusMode.focus: {
        "aggression": FocusAggression.soft,
        "blocked_apps": ["entertainment", "social_media"],
        "allow_suggestions": True,
        "allow_notifications": False,
        "visible_panels_ratio": 0.6,
        "ui_opacity": 0.85,
        "orb_glow": 0.15,
        "description": "UI simplifies, only active task visible, suggestions reduced",
    },
    FocusMode.deep_focus: {
        "aggression": FocusAggression.strong,
        "blocked_apps": ["entertainment", "social_media", "gaming", "news"],
        "allow_suggestions": False,
        "allow_notifications": False,
        "visible_panels_ratio": 0.2,
        "ui_opacity": 0.95,
        "orb_glow": 0.3,
        "description": "UI collapses almost fully, Orb becomes only interaction layer",
    },
    FocusMode.lock: {
        "aggression": FocusAggression.strict,
        "blocked_apps": ["entertainment", "social_media", "gaming", "news", "shopping", "video"],
        "allow_suggestions": True,
        "allow_notifications": False,
        "visible_panels_ratio": 0.1,
        "ui_opacity": 1.0,
        "orb_glow": 0.5,
        "description": "Strict UI restriction, only approved apps visible, AI enforcement",
    },
}

# ---------------------------------------------------------------------------
# Intent-to-UI Mapping
# ---------------------------------------------------------------------------

INTENT_WORKSPACE_MAP: Dict[str, WorkspaceType] = {
    "study": WorkspaceType.study,
    "learn": WorkspaceType.learning,
    "read": WorkspaceType.study,
    "review": WorkspaceType.study,
    "quiz": WorkspaceType.study,
    "flashcard": WorkspaceType.study,
    "biology": WorkspaceType.study,
    "exam": WorkspaceType.study,
    "code": WorkspaceType.coding,
    "program": WorkspaceType.coding,
    "debug": WorkspaceType.coding,
    "fix bug": WorkspaceType.coding,
    "implement": WorkspaceType.coding,
    "build": WorkspaceType.coding,
    "develop": WorkspaceType.coding,
    "plan": WorkspaceType.personal,
    "schedule": WorkspaceType.personal,
    "calendar": WorkspaceType.personal,
    "task": WorkspaceType.personal,
    "organize": WorkspaceType.personal,
    "day": WorkspaceType.personal,
    "week": WorkspaceType.personal,
    "explore": WorkspaceType.learning,
    "understand": WorkspaceType.learning,
    "concept": WorkspaceType.learning,
    "knowledge": WorkspaceType.learning,
    "skill": WorkspaceType.learning,
    "tutorial": WorkspaceType.learning,
}

INTENT_PANEL_MAP: Dict[WorkspaceType, Dict[str, List[str]]] = {
    WorkspaceType.study: {
        "default": ["concept_map", "notes_layer", "ai_tutor"],
        "quiz": ["concept_map", "flashcard_gen", "progress_tracker", "ai_tutor"],
        "review": ["notes_layer", "concept_map", "ai_tutor"],
        "deep": ["concept_map", "ai_tutor"],
    },
    WorkspaceType.coding: {
        "default": ["editor", "file_tree", "terminal"],
        "debug": ["editor", "ai_debugger", "terminal", "problems_panel"],
        "architect": ["editor", "file_tree", "ai_debugger"],
        "test": ["editor", "terminal", "problems_panel"],
    },
    WorkspaceType.learning: {
        "default": ["knowledge_graph", "resource_stream", "ai_explanation"],
        "deep_dive": ["knowledge_graph", "course_tree", "ai_explanation"],
        "practice": ["quiz_panel", "knowledge_graph", "ai_explanation"],
        "explore": ["knowledge_graph", "resource_stream"],
    },
    WorkspaceType.personal: {
        "default": ["calendar_timeline", "task_list", "planning_panel"],
        "planning": ["calendar_timeline", "planning_panel", "focus_timer"],
        "review": ["calendar_timeline", "email_stream", "task_list"],
        "focus": ["focus_timer", "task_list"],
    },
}

# ---------------------------------------------------------------------------
# Ambient Behavior Configuration
# ---------------------------------------------------------------------------

IDLE_TIMEOUT_SECONDS = 30.0
DEEP_IDLE_TIMEOUT_SECONDS = 120.0
ACTIVITY_RECOVERY_GRACE_SECONDS = 5.0

FOCUS_AGGRESSION_MAP: Dict[FocusMode, FocusAggression] = {
    FocusMode.normal: FocusAggression.none_,
    FocusMode.focus: FocusAggression.soft,
    FocusMode.deep_focus: FocusAggression.strong,
    FocusMode.lock: FocusAggression.strict,
}

# ---------------------------------------------------------------------------
# UI System Engine
# ---------------------------------------------------------------------------

class UISystemEngine:
    def __init__(self):
        self._start_time = time.monotonic()
        self._state = UIState()
        self._orb = OrbState()
        self._focus = FocusState()
        self._focus_start_time: Optional[float] = None
        self._idle_since: Optional[float] = None
        self._ambient_collapsed: bool = False
        self._last_ambient_tick: float = 0.0

        self._component_registry: Dict[str, PanelDefinition] = {}
        self._build_component_registry()

    def _build_component_registry(self) -> None:
        for layout in WORKSPACE_LAYOUTS.values():
            for panel in layout.panels:
                key = f"{layout.workspace.value}::{panel.id}"
                self._component_registry[key] = panel.model_copy(deep=True)

    # -----------------------------------------------------------------------
    # UI State
    # -----------------------------------------------------------------------

    def get_ui_state(self) -> UIState:
        self._state.last_interaction = datetime.utcnow().isoformat()
        return self._state

    def update_ui_state(self, req: UpdateUIStateRequest) -> UIState:
        if req.workspace is not None:
            self._state.workspace = req.workspace
        if req.mode is not None:
            self._state.mode = req.mode
            self._set_focus_mode(req.mode)
        if req.active_task is not None:
            self._state.active_task = req.active_task
        self._state.last_interaction = datetime.utcnow().isoformat()
        self._idle_since = None
        self._ambient_collapsed = False
        logger.info("UI state updated: workspace=%s mode=%s task=%s",
                     self._state.workspace.value, self._state.mode.value, self._state.active_task)
        return self._state

    # -----------------------------------------------------------------------
    # Workspace Layout
    # -----------------------------------------------------------------------

    def get_layout(self, workspace: WorkspaceType) -> WorkspaceLayout:
        layout = WORKSPACE_LAYOUTS.get(workspace)
        if layout is None:
            raise HTTPException(status_code=404, detail=f"No layout defined for workspace '{workspace.value}'")
        panels = self._apply_focus_filter(layout.panels)
        adjusted = layout.model_copy(deep=True)
        adjusted.panels = panels
        return adjusted

    def _apply_focus_filter(self, panels: List[PanelDefinition]) -> List[PanelDefinition]:
        config = FOCUS_CONFIGS.get(self._focus.mode, FOCUS_CONFIGS[FocusMode.normal])
        ratio = config["visible_panels_ratio"]

        if ratio >= 1.0:
            for p in panels:
                if p.visibility == PanelVisibility.hidden:
                    p.visibility = PanelVisibility.visible
            return panels

        if ratio <= 0.1:
            for p in panels:
                if p.layer != Layer.orb:
                    p.visibility = PanelVisibility.hidden
            return panels

        visible_count = max(1, int(len(panels) * ratio))
        sorted_panels = sorted(panels, key=lambda p: p.order)
        for i, p in enumerate(sorted_panels):
            if p.layer in (Layer.system_shell, Layer.kernel_events, Layer.orb):
                continue
            p.visibility = PanelVisibility.visible if i < visible_count else PanelVisibility.hidden

        return sorted(sorted_panels, key=lambda p: p.order)

    # -----------------------------------------------------------------------
    # Intent Processing
    # -----------------------------------------------------------------------

    def process_intent(self, req: IntentRequest) -> IntentResponse:
        text_lower = req.text.lower().strip()

        target_workspace = req.workspace or self._detect_workspace(text_lower)
        intent_subtype = self._detect_intent_subtype(text_lower, target_workspace)

        panel_map = INTENT_PANEL_MAP.get(target_workspace, {})
        target_panels = panel_map.get(intent_subtype, panel_map.get("default", []))
        all_panel_ids = {p.id for p in WORKSPACE_LAYOUTS.get(target_workspace, WorkspaceLayout(workspace=target_workspace)).panels}

        panels_to_hide = list(all_panel_ids - set(target_panels))
        panels_to_show = target_panels.copy()

        orb_change = None
        focus_change = None
        layout_transforms: List[Dict[str, Any]] = []

        if intent_subtype == "debug":
            orb_change = OrbStateEnum.active
            layout_transforms.append({
                "panel": "ai_debugger",
                "animation": "slide_in_right",
                "duration_ms": 400,
            })
        elif intent_subtype in ("deep", "deep_dive"):
            focus_change = FocusMode.focus
            layout_transforms.append({
                "panel": "ai_explanation",
                "animation": "float_in",
                "duration_ms": 700,
            })
        elif intent_subtype == "focus":
            focus_change = FocusMode.focus
            panels_to_show = panel_map.get("focus", ["focus_timer", "task_list"])
            panels_to_hide = list(all_panel_ids - set(panels_to_show))

        suggestions = self._generate_contextual_suggestions(text_lower, target_workspace)

        self._state.workspace = target_workspace
        self._state.last_interaction = datetime.utcnow().isoformat()
        if focus_change:
            self._set_focus_mode(focus_change)

        logger.info("Intent processed: '%s' -> workspace=%s subtype=%s panels=%s",
                     req.text[:60], target_workspace.value, intent_subtype, panels_to_show)

        return IntentResponse(
            original_intent=req.text,
            target_workspace=target_workspace,
            panels_to_show=panels_to_show,
            panels_to_hide=panels_to_hide,
            orb_state_change=orb_change,
            focus_mode_change=focus_change,
            layout_transforms=layout_transforms,
            suggestions=suggestions,
        )

    @staticmethod
    def _detect_workspace(text: str) -> WorkspaceType:
        scored: Dict[WorkspaceType, int] = {ws: 0 for ws in WorkspaceType}
        for keyword, ws in INTENT_WORKSPACE_MAP.items():
            if keyword in text:
                scored[ws] = scored.get(ws, 0) + 1

        best = max(scored, key=scored.get) if any(scored.values()) else None
        return best or WorkspaceType.personal

    @staticmethod
    def _detect_intent_subtype(text: str, workspace: WorkspaceType) -> str:
        subtype_map: Dict[WorkspaceType, Dict[str, List[str]]] = {
            WorkspaceType.study: {
                "quiz": ["quiz", "test", "practice", "flashcard", "memorize"],
                "review": ["review", "go over", "recap", "summarize"],
                "deep": ["deep", "understand", "master", "comprehensive"],
            },
            WorkspaceType.coding: {
                "debug": ["debug", "bug", "error", "fix", "broken", "issue"],
                "architect": ["architect", "design", "structure", "pattern", "system"],
                "test": ["test", "coverage", "assert", "verify"],
            },
            WorkspaceType.learning: {
                "deep_dive": ["deep", "master", "comprehensive", "advanced"],
                "practice": ["practice", "exercise", "drill", "worksheet"],
                "explore": ["explore", "browse", "discover", "overview"],
            },
            WorkspaceType.personal: {
                "planning": ["plan", "goal", "objective", "strategy", " roadmap"],
                "review": ["review", "retrospective", "look back", "reflect"],
                "focus": ["focus", "concentrate", "deep work", "session"],
            },
        }

        ws_map = subtype_map.get(workspace, {})
        for subtype, keywords in ws_map.items():
            for keyword in keywords:
                if keyword in text:
                    return subtype
        return "default"

    # -----------------------------------------------------------------------
    # Contextual Suggestions
    # -----------------------------------------------------------------------

    def _generate_contextual_suggestions(self, text: str, workspace: WorkspaceType) -> List[SpotlightSuggestion]:
        suggestions: List[SpotlightSuggestion] = []

        workspace_suggestions: Dict[WorkspaceType, List[SpotlightSuggestion]] = {
            WorkspaceType.study: [
                SpotlightSuggestion(label="Generate Flashcards", icon="layers", action="study:flashcards"),
                SpotlightSuggestion(label="Start Quiz Session", icon="help-circle", action="study:quiz"),
                SpotlightSuggestion(label="Summarize Topic", icon="file-text", action="study:summarize"),
                SpotlightSuggestion(label="Focus Study Session", icon="target", action="study:focus"),
            ],
            WorkspaceType.coding: [
                SpotlightSuggestion(label="Run Code Analysis", icon="search", action="coding:analyze"),
                SpotlightSuggestion(label="Start Debugger", icon="bug", action="coding:debug"),
                SpotlightSuggestion(label="Git Status", icon="git-branch", action="coding:git_status"),
                SpotlightSuggestion(label="Open Terminal", icon="terminal", action="coding:terminal"),
            ],
            WorkspaceType.learning: [
                SpotlightSuggestion(label="Explore Knowledge Graph", icon="git-merge", action="learning:graph"),
                SpotlightSuggestion(label="Find Learning Resources", icon="book", action="learning:resources"),
                SpotlightSuggestion(label="Practice Quiz", icon="edit", action="learning:quiz"),
                SpotlightSuggestion(label="Track Progress", icon="trending-up", action="learning:progress"),
            ],
            WorkspaceType.personal: [
                SpotlightSuggestion(label="Plan Tomorrow", icon="calendar", action="personal:plan_tomorrow"),
                SpotlightSuggestion(label="Review Tasks", icon="check-square", action="personal:review_tasks"),
                SpotlightSuggestion(label="Focus Session", icon="clock", action="personal:focus_session"),
                SpotlightSuggestion(label="Weekly Overview", icon="bar-chart", action="personal:weekly_overview"),
            ],
        }

        suggestions = workspace_suggestions.get(workspace, workspace_suggestions[WorkspaceType.personal])

        if "urgent" in text or "asap" in text:
            suggestions.insert(0, SpotlightSuggestion(label="Flag as Urgent", icon="alert-triangle", action="system:flag_urgent"))
        if "help" in text or "what can" in text:
            suggestions.insert(0, SpotlightSuggestion(label="Show Help", icon="help-circle", action="system:help"))

        return suggestions[:6]

    # -----------------------------------------------------------------------
    # Orb System
    # -----------------------------------------------------------------------

    def get_orb_state(self) -> OrbState:
        self._update_orb_visuals()
        return self._orb

    def trigger_orb_notification(self, req: OrbNotifyRequest) -> OrbNotification:
        notification = OrbNotification(
            title=req.title,
            message=req.message,
            severity=req.severity,
            expires_at=(datetime.utcnow() + timedelta(seconds=req.expires_seconds)).isoformat(),
            actionable=req.actionable,
        )
        self._orb.notifications.append(notification)
        if len(self._orb.notifications) > 20:
            self._orb.notifications = self._orb.notifications[-15:]

        self._orb.state = req.severity
        if req.severity == OrbStateEnum.critical:
            self._orb.pulse_intensity = 0.7
            self._orb.glow_opacity = 0.6
        else:
            self._orb.pulse_intensity = 0.3
            self._orb.glow_opacity = 0.25

        self._orb.timer_remaining = float(req.expires_seconds)
        logger.info("Orb notification: [%s] %s", req.severity.value, req.title)
        return notification

    def dismiss_orb_notification(self, notification_id: str) -> bool:
        for n in self._orb.notifications:
            if n.id == notification_id:
                n.dismissed = True
                self._orb.notifications.remove(n)
                logger.info("Orb notification dismissed: %s", notification_id)

                if not self._orb.notifications:
                    self._orb.state = OrbStateEnum.idle
                    self._orb.pulse_intensity = 0.0
                    self._orb.glow_opacity = 0.05
                    self._orb.timer_remaining = 0.0
                return True
        return False

    def _update_orb_visuals(self) -> None:
        now = datetime.utcnow()
        active_notifications = [n for n in self._orb.notifications if not n.dismissed]

        if not active_notifications:
            if self._orb.state != OrbStateEnum.idle:
                self._orb.state = OrbStateEnum.idle
                self._orb.pulse_intensity = 0.0
                self._orb.glow_opacity = 0.05
                self._orb.timer_remaining = 0.0
            return

        active_notifications.sort(key=lambda n: n.created_at)
        latest = active_notifications[-1]
        expires = datetime.fromisoformat(latest.expires_at)
        remaining = max(0.0, (expires - now).total_seconds())

        self._orb.timer_remaining = remaining
        self._orb.state = latest.severity

        if remaining <= 0:
            self.dismiss_orb_notification(latest.id)
            return

        if latest.severity == OrbStateEnum.critical:
            self._orb.pulse_intensity = 0.7 + (0.3 * (1.0 - min(remaining / 30.0, 1.0)))
            self._orb.glow_opacity = 0.6
        else:
            fade = min(remaining / 30.0, 1.0)
            self._orb.pulse_intensity = 0.3 * fade
            self._orb.glow_opacity = 0.15 + (0.15 * fade)

    # -----------------------------------------------------------------------
    # Focus System
    # -----------------------------------------------------------------------

    def get_focus_state(self) -> FocusState:
        return self._focus

    def set_focus_mode(self, req: SetFocusModeRequest) -> FocusState:
        self._set_focus_mode(req.mode)
        if req.aggression_level is not None:
            self._focus.aggression_level = req.aggression_level
        return self._focus

    def _set_focus_mode(self, mode: FocusMode) -> None:
        config = FOCUS_CONFIGS.get(mode, FOCUS_CONFIGS[FocusMode.normal])
        prev = self._focus.mode
        self._focus.mode = mode
        self._focus.aggression_level = config["aggression"]
        self._focus.blocked_apps = config["blocked_apps"]

        if mode != FocusMode.normal and prev == FocusMode.normal:
            self._focus_start_time = time.monotonic()
            self._focus.active_since = datetime.utcnow().isoformat()
        elif mode == FocusMode.normal:
            self._focus_start_time = None
            self._focus.active_since = None

        self._state.mode = mode
        self._state.last_interaction = datetime.utcnow().isoformat()
        logger.info("Focus mode set: %s -> %s (aggression=%s)", prev.value, mode.value, config["aggression"].value)

    # -----------------------------------------------------------------------
    # Spotlight Suggestions
    # -----------------------------------------------------------------------

    def get_spotlight_suggestions(self) -> List[SpotlightSuggestion]:
        workspace = self._state.workspace
        suggestions = self._generate_contextual_suggestions("", workspace)

        global_suggestions = [
            SpotlightSuggestion(label="Open Spotlight", icon="command", action="system:spotlight", context={"shortcut": "Ctrl+Space"}),
            SpotlightSuggestion(label="Change Workspace", icon="grid", action="system:workspace_switcher"),
            SpotlightSuggestion(label="Adjust Focus Mode", icon="moon", action="system:focus_settings"),
            SpotlightSuggestion(label="System Settings", icon="settings", action="system:settings"),
            SpotlightSuggestion(label="View Notification History", icon="bell", action="system:notifications"),
        ]

        combined = suggestions + global_suggestions
        seen: set = set()
        unique: List[SpotlightSuggestion] = []
        for s in combined:
            if s.action not in seen:
                seen.add(s.action)
                unique.append(s)
        return unique[:10]

    # -----------------------------------------------------------------------
    # Ambient Behavior
    # -----------------------------------------------------------------------

    def ambient_tick(self, req: AmbientTickRequest) -> AmbientTickResponse:
        self._last_ambient_tick = time.monotonic()
        now = datetime.utcnow().isoformat()

        was_collapsed = self._ambient_collapsed
        current_layout = WORKSPACE_LAYOUTS.get(req.active_workspace or self._state.workspace)
        all_panels = [p.id for p in current_layout.panels] if current_layout else []

        hidden_panels: List[str] = []
        visible_panels: List[str] = []

        focus_adjustment: Optional[FocusMode] = None

        if req.idle_seconds >= DEEP_IDLE_TIMEOUT_SECONDS:
            self._ambient_collapsed = True
            self._state.orb_state = OrbStateEnum.idle
            for p in all_panels:
                hidden_panels.append(p)
            visible_panels = []
            logger.info("Ambient tick: deep idle (%ds), UI fully collapsed", req.idle_seconds)

        elif req.idle_seconds >= IDLE_TIMEOUT_SECONDS:
            self._ambient_collapsed = True
            if req.current_mode == FocusMode.normal:
                focus_adjustment = FocusMode.focus
            essential = ["spotlight_bar", "orb_indicator"]
            for p in all_panels:
                if p not in essential:
                    hidden_panels.append(p)
            visible_panels = essential
            self._state.orb_state = OrbStateEnum.idle
            logger.info("Ambient tick: idle (%ds), UI minimized", req.idle_seconds)

        else:
            if self._ambient_collapsed and req.idle_seconds < IDLE_TIMEOUT_SECONDS - ACTIVITY_RECOVERY_GRACE_SECONDS:
                self._ambient_collapsed = False
                visible_panels = all_panels
                hidden_panels = []

                if req.current_mode == FocusMode.focus and self._focus.mode == FocusMode.focus:
                    focus_adjustment = FocusMode.normal

                self._state.orb_state = OrbStateEnum.idle
                logger.info("Ambient tick: user active, UI restored")
            else:
                for p in all_panels:
                    visible_panels.append(p)

        if self._ambient_collapsed and not was_collapsed:
            self._state.last_interaction = now

        current_orb_state = self._orb.state

        return AmbientTickResponse(
            ui_collapsed=self._ambient_collapsed,
            hidden_panels=hidden_panels,
            visible_panels=visible_panels,
            orb_state=current_orb_state,
            focus_adjustment=focus_adjustment,
        )

    # -----------------------------------------------------------------------
    # Component Registry
    # -----------------------------------------------------------------------

    def list_components(self) -> List[ComponentState]:
        components: List[ComponentState] = []
        z_base = 100

        for layout in WORKSPACE_LAYOUTS.values():
            for panel in layout.panels:
                is_visible = self._is_component_visible(panel.id)
                z_map = {
                    Layer.orb: 5000,
                    Layer.context_panels: 4000,
                    Layer.workspace: 3000,
                    Layer.system_shell: 2000,
                    Layer.kernel_events: 1000,
                }
                z = z_map.get(panel.layer, 1000) + panel.order

                components.append(ComponentState(
                    id=f"{layout.workspace.value}::{panel.id}",
                    name=panel.name,
                    layer=panel.layer,
                    visibility=PanelVisibility.visible if is_visible else PanelVisibility.hidden,
                    position=panel.position,
                    z_index=z,
                    metadata={
                        "workspace": layout.workspace.value,
                        "order": panel.order,
                        "width": panel.width,
                        "height": panel.height,
                    },
                ))

        return components

    def _is_component_visible(self, panel_id: str) -> bool:
        config = FOCUS_CONFIGS.get(self._focus.mode, FOCUS_CONFIGS[FocusMode.normal])
        ratio = config["visible_panels_ratio"]
        if ratio >= 1.0:
            return True
        if self._ambient_collapsed:
            return panel_id in ("spotlight_bar", "orb_indicator")
        return True


# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="ICHIN OS Service 4 — UI + Interaction System",
    version="1.0.0",
    description="Dynamic cognitive environment that reshapes itself based on intent. Renders all system interfaces, controls motion + transitions, manages user input, workspace switching, AI Orb visibility + behavior, and Zoey-style ambient UI.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = UISystemEngine()


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse)
async def health():
    state = engine.get_ui_state()
    return HealthResponse(
        status="ok",
        service="ichin-ui-system",
        version="1.0.0",
        uptime=time.monotonic() - engine._start_time,
        current_workspace=state.workspace.value,
        current_focus_mode=state.mode.value,
        orb_state=engine._orb.state.value,
        visible_panels=len(state.visible_panels),
    )


# ---------------------------------------------------------------------------
# UI State Endpoints
# ---------------------------------------------------------------------------

@app.get("/ui/state", response_model=UIState)
async def get_ui_state():
    try:
        return engine.get_ui_state()
    except Exception as exc:
        logger.exception("Failed to get UI state")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/ui/state", response_model=UIState)
async def update_ui_state(body: UpdateUIStateRequest):
    try:
        return engine.update_ui_state(body)
    except Exception as exc:
        logger.exception("Failed to update UI state")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/ui/layout/{workspace}", response_model=WorkspaceLayout)
async def get_layout(workspace: WorkspaceType):
    try:
        return engine.get_layout(workspace)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to get layout for '%s'", workspace.value)
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/ui/intent", response_model=IntentResponse)
async def process_intent(body: IntentRequest):
    try:
        return engine.process_intent(body)
    except Exception as exc:
        logger.exception("Intent processing failed")
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# Orb Endpoints
# ---------------------------------------------------------------------------

@app.get("/ui/orb/state", response_model=OrbState)
async def get_orb_state():
    try:
        return engine.get_orb_state()
    except Exception as exc:
        logger.exception("Failed to get orb state")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/ui/orb/notify")
async def orb_notify(body: OrbNotifyRequest):
    try:
        notification = engine.trigger_orb_notification(body)
        return {
            "status": "notified",
            "notification_id": notification.id,
            "severity": body.severity.value,
            "expires_at": notification.expires_at,
        }
    except Exception as exc:
        logger.exception("Orb notification failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/ui/orb/dismiss")
async def orb_dismiss(body: DismissNotificationRequest):
    try:
        success = engine.dismiss_orb_notification(body.notification_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Notification '{body.notification_id}' not found")
        return {"status": "dismissed", "notification_id": body.notification_id}
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Orb dismiss failed")
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# Focus Endpoints
# ---------------------------------------------------------------------------

@app.get("/ui/focus/state", response_model=FocusState)
async def get_focus_state():
    try:
        return engine.get_focus_state()
    except Exception as exc:
        logger.exception("Failed to get focus state")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/ui/focus/mode", response_model=FocusState)
async def set_focus_mode(body: SetFocusModeRequest):
    try:
        return engine.set_focus_mode(body)
    except Exception as exc:
        logger.exception("Failed to set focus mode")
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# Spotlight Endpoints
# ---------------------------------------------------------------------------

@app.get("/ui/spotlight/suggestions", response_model=List[SpotlightSuggestion])
async def get_spotlight_suggestions():
    try:
        return engine.get_spotlight_suggestions()
    except Exception as exc:
        logger.exception("Failed to get spotlight suggestions")
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# Ambient Endpoints
# ---------------------------------------------------------------------------

@app.post("/ui/ambient/tick", response_model=AmbientTickResponse)
async def ambient_tick(body: AmbientTickRequest):
    try:
        return engine.ambient_tick(body)
    except Exception as exc:
        logger.exception("Ambient tick failed")
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# Component Endpoints
# ---------------------------------------------------------------------------

@app.get("/ui/components", response_model=List[ComponentState])
async def list_components():
    try:
        return engine.list_components()
    except Exception as exc:
        logger.exception("Failed to list components")
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("ui_system:app", host="0.0.0.0", port=8014, reload=True)
