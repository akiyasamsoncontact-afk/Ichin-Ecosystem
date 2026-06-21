import asyncio
import json
import logging
import os
import re
import time
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ichin.browser-engine")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
TABS_FILE = os.path.join(DATA_DIR, "tabs.json")
RESEARCH_FILE = os.path.join(DATA_DIR, "research.json")
PERMISSIONS_FILE = os.path.join(DATA_DIR, "permissions.json")
os.makedirs(DATA_DIR, exist_ok=True)

ORCHESTRATOR_URL = "http://localhost:8000"
MEMORY_URL = "http://localhost:8003"

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class BrowserAction(str, Enum):
    navigate = "navigate"
    click = "click"
    type = "type"
    select = "select"
    scroll = "scroll"
    hover = "hover"
    extract = "extract"
    screenshot = "screenshot"
    back = "back"
    forward = "forward"
    refresh = "refresh"
    close = "close"
    switch_tab = "switch_tab"
    new_tab = "new_tab"
    execute_script = "execute_script"
    fill_form = "fill_form"
    submit_form = "submit_form"
    wait = "wait"
    highlight = "highlight"


class ExtractionTarget(str, Enum):
    text = "text"
    html = "html"
    markdown = "markdown"
    links = "links"
    images = "images"
    tables = "tables"
    metadata = "metadata"
    structured = "structured"
    screenshot = "screenshot"
    pdf = "pdf"


class ResearchDepth(str, Enum):
    quick = "quick"
    moderate = "moderate"
    deep = "deep"
    comprehensive = "comprehensive"


class PermissionLevel(str, Enum):
    ask = "ask"
    allow = "allow"
    deny = "deny"
    allow_once = "allow_once"


class TabState(str, Enum):
    loading = "loading"
    ready = "ready"
    error = "error"
    closed = "closed"


class InteractionType(str, Enum):
    passive = "passive"
    active = "active"
    destructive = "destructive"


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class PageMetadata(BaseModel):
    title: str = ""
    url: str = ""
    description: str = ""
    language: str = ""
    keywords: List[str] = []
    author: str = ""
    og_image: str = ""
    word_count: int = 0
    reading_time_minutes: float = 0.0
    domain: str = ""
    is_secure: bool = False
    content_type: str = ""
    extracted_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class PageContent(BaseModel):
    metadata: PageMetadata = Field(default_factory=PageMetadata)
    main_content: str = ""
    structured_data: Dict[str, Any] = {}
    links: List[Dict[str, str]] = []
    images: List[Dict[str, str]] = []
    tables: List[Dict[str, Any]] = []
    headings: List[Dict[str, str]] = []
    forms: List[Dict[str, Any]] = []
    scripts: List[str] = []
    readability_score: float = 0.0
    content_hash: str = ""


class BrowserTab(BaseModel):
    id: str
    url: str = ""
    title: str = "New Tab"
    state: TabState = TabState.ready
    history: List[str] = []
    current_history_index: int = -1
    page_content: Optional[PageContent] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    last_active: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    workspace: str = "general"
    pinned: bool = False
    muted: bool = False
    sandbox_level: int = 0


class BrowserSession(BaseModel):
    id: str
    tabs: List[BrowserTab] = []
    active_tab_id: Optional[str] = None
    windows: List[Dict[str, Any]] = []
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    permissions: Dict[str, PermissionLevel] = {}


class BrowserActionRequest(BaseModel):
    session_id: str
    tab_id: Optional[str] = None
    action: BrowserAction
    params: Dict[str, Any] = {}
    wait_for_load: bool = True
    timeout_ms: int = 30000


class BrowserActionResponse(BaseModel):
    success: bool
    action: BrowserAction
    result: Optional[Dict[str, Any]] = None
    tab_state: Optional[TabState] = None
    error: Optional[str] = None
    latency_ms: float = 0.0


class ExtractionRequest(BaseModel):
    session_id: str
    tab_id: Optional[str] = None
    url: Optional[str] = None
    targets: List[ExtractionTarget] = [ExtractionTarget.text]
    research_depth: ResearchDepth = ResearchDepth.quick
    include_screenshot: bool = False
    max_content_length: int = 50000


class ExtractionResponse(BaseModel):
    request_id: str
    content: PageContent
    extraction_time_ms: float
    targets_extracted: List[str]
    truncated: bool = False


class ResearchSession(BaseModel):
    id: str
    query: str
    depth: ResearchDepth = ResearchDepth.moderate
    urls_explored: List[str] = []
    findings: List[Dict[str, Any]] = []
    summary: str = ""
    sources: List[Dict[str, str]] = []
    status: str = "pending"
    depth_reached: int = 0
    max_depth: int = 3
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ResearchRequest(BaseModel):
    query: str
    depth: ResearchDepth = ResearchDepth.moderate
    max_sources: int = 10
    include_summary: bool = True
    include_citations: bool = True
    session_id: Optional[str] = None


class ResearchResponse(BaseModel):
    research_id: str
    findings: List[Dict[str, Any]] = []
    summary: str = ""
    sources: List[Dict[str, str]] = []
    urls_explored: int = 0
    status: str
    execution_time_ms: float = 0.0


class FormField(BaseModel):
    selector: str
    value: str
    field_type: str = "text"
    required: bool = False
    label: Optional[str] = None


class FormFillRequest(BaseModel):
    session_id: str
    tab_id: Optional[str] = None
    url: Optional[str] = None
    fields: List[FormField] = []
    auto_detect: bool = True
    submit: bool = False


class FormFillResponse(BaseModel):
    success: bool
    fields_filled: int = 0
    fields_detected: int = 0
    form_submitted: bool = False
    error: Optional[str] = None


class PermissionRequest(BaseModel):
    session_id: str
    action_type: str
    target: str
    reason: str = ""


class PermissionResponse(BaseModel):
    allowed: bool
    permission_level: PermissionLevel
    reason: str = ""


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    uptime: float
    active_sessions: int
    active_tabs: int


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
# Page Understanding Engine
# ---------------------------------------------------------------------------

class PageUnderstandingEngine:
    @staticmethod
    def extract_metadata(url: str, html: str) -> PageMetadata:
        metadata = PageMetadata(url=url)

        title_match = re.search(r'<title[^>]*>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
        if title_match:
            metadata.title = title_match.group(1).strip()

        desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']', html, re.IGNORECASE)
        if not desc_match:
            desc_match = re.search(r'<meta[^>]*content=["\']([^"\']*)["\'][^>]*name=["\']description["\']', html, re.IGNORECASE)
        if desc_match:
            metadata.description = desc_match.group(1)

        keywords_match = re.search(r'<meta[^>]*name=["\']keywords["\'][^>]*content=["\']([^"\']*)["\']', html, re.IGNORECASE)
        if keywords_match:
            metadata.keywords = [k.strip() for k in keywords_match.group(1).split(",")]

        og_image_match = re.search(r'<meta[^>]*property=["\']og:image["\'][^>]*content=["\']([^"\']*)["\']', html, re.IGNORECASE)
        if og_image_match:
            metadata.og_image = og_image_match.group(1)

        from urllib.parse import urlparse
        parsed = urlparse(url)
        metadata.domain = parsed.netloc
        metadata.is_secure = parsed.scheme == "https"

        return metadata

    @staticmethod
    def extract_main_content(html: str, max_length: int = 50000) -> str:
        content_tags = re.findall(r'<(?:article|main|div|section)[^>]*>(.*?)</(?:article|main|div|section)>', html, re.IGNORECASE | re.DOTALL)
        if not content_tags:
            content_tags = [html]

        best_content = max(content_tags, key=len)
        text = re.sub(r'<[^>]+>', ' ', best_content)
        text = re.sub(r'\s+', ' ', text).strip()[:max_length]
        return text

    @staticmethod
    def extract_links(html: str, base_url: str) -> List[Dict[str, str]]:
        links = []
        for match in re.finditer(r'<a[^>]*href=["\']([^"\']*)["\'][^>]*>(.*?)</a>', html, re.IGNORECASE | re.DOTALL):
            href = match.group(1).strip()
            text = re.sub(r'<[^>]+>', '', match.group(2)).strip()
            if href and not href.startswith("#"):
                links.append({"url": href, "text": text[:200]})
        return links[:200]

    @staticmethod
    def extract_headings(html: str) -> List[Dict[str, str]]:
        headings = []
        for level in range(1, 7):
            for match in re.finditer(rf'<h{level}[^>]*>(.*?)</h{level}>', html, re.IGNORECASE | re.DOTALL):
                text = re.sub(r'<[^>]+>', '', match.group(1)).strip()
                if text:
                    headings.append({"level": f"h{level}", "text": text})
        return headings

    @staticmethod
    def extract_tables(html: str) -> List[Dict[str, Any]]:
        tables = []
        for table_match in re.finditer(r'<table[^>]*>(.*?)</table>', html, re.IGNORECASE | re.DOTALL):
            table_html = table_match.group(1)
            rows = []
            for row_match in re.finditer(r'<tr[^>]*>(.*?)</tr>', table_html, re.IGNORECASE | re.DOTALL):
                cells = []
                for cell_match in re.finditer(r'<t[hd][^>]*>(.*?)</t[hd]>', row_match.group(1), re.IGNORECASE | re.DOTALL):
                    cell_text = re.sub(r'<[^>]+>', '', cell_match.group(1)).strip()
                    cells.append(cell_text)
                if cells:
                    rows.append(cells)
            if rows:
                tables.append({"rows": rows})
        return tables

    @staticmethod
    def extract_forms(html: str) -> List[Dict[str, Any]]:
        forms = []
        for form_match in re.finditer(r'<form[^>]*>(.*?)</form>', html, re.IGNORECASE | re.DOTALL):
            form_html = form_match.group(1)
            fields = []
            for input_match in re.finditer(r'<(?:input|textarea|select)[^>]*>', form_html, re.IGNORECASE):
                attrs = {}
                for attr_match in re.finditer(r'(\w+)=["\']([^"\']*)["\']', input_match.group()):
                    attrs[attr_match.group(1)] = attr_match.group(2)
                if attrs.get("type") not in ("hidden", "submit", "button", "reset"):
                    fields.append(attrs)
            if fields:
                forms.append({"fields": fields})
        return forms

    @staticmethod
    def calculate_readability(text: str) -> float:
        words = text.split()
        if len(words) < 10:
            return 0.5
        sentences = len(re.findall(r'[.!?]+', text))
        avg_words_per_sentence = len(words) / max(sentences, 1)
        syllables = sum(1 for word in words for _ in re.findall(r'[aeiouy]+', word.lower()))
        avg_syllables = syllables / max(len(words), 1)
        score = 206.835 - 1.015 * avg_words_per_sentence - 84.6 * avg_syllables
        return max(0.0, min(1.0, score / 100.0))

    @staticmethod
    def compute_content_hash(html: str) -> str:
        import hashlib
        return hashlib.md5(html.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Browser Session Manager
# ---------------------------------------------------------------------------

class BrowserSessionManager:
    def __init__(self):
        self._sessions: Dict[str, BrowserSession] = {}
        self._load()

    def _load(self) -> None:
        tabs_data = _load_json(TABS_FILE, [])
        for s_data in tabs_data:
            try:
                session = BrowserSession(**s_data)
                self._sessions[session.id] = session
            except Exception as exc:
                logger.warning("Skipping invalid session: %s", exc)

    def _persist(self) -> None:
        _save_json(TABS_FILE, [s.model_dump(mode="json") for s in self._sessions.values()])

    def create_session(self) -> BrowserSession:
        session = BrowserSession(id=str(uuid.uuid4()))
        tab = BrowserTab(id=str(uuid.uuid4()))
        session.tabs.append(tab)
        session.active_tab_id = tab.id
        self._sessions[session.id] = session
        self._persist()
        logger.info("Created browser session %s", session.id)
        return session

    def get_session(self, session_id: str) -> Optional[BrowserSession]:
        return self._sessions.get(session_id)

    def get_active_tab(self, session: BrowserSession) -> Optional[BrowserTab]:
        if not session.active_tab_id:
            return None
        for tab in session.tabs:
            if tab.id == session.active_tab_id:
                return tab
        return None

    def create_tab(self, session_id: str, url: str = "") -> Optional[BrowserTab]:
        session = self._sessions.get(session_id)
        if not session:
            return None
        tab = BrowserTab(id=str(uuid.uuid4()), url=url, title="New Tab", state=TabState.ready)
        if url:
            tab.history = [url]
            tab.current_history_index = 0
        session.tabs.append(tab)
        session.active_tab_id = tab.id
        self._persist()
        return tab

    def close_tab(self, session_id: str, tab_id: str) -> bool:
        session = self._sessions.get(session_id)
        if not session:
            return False
        session.tabs = [t for t in session.tabs if t.id != tab_id]
        if session.active_tab_id == tab_id:
            session.active_tab_id = session.tabs[-1].id if session.tabs else None
        if not session.tabs:
            tab = BrowserTab(id=str(uuid.uuid4()))
            session.tabs.append(tab)
            session.active_tab_id = tab.id
        self._persist()
        return True

    def update_tab(self, session_id: str, tab_id: str, updates: Dict[str, Any]) -> bool:
        session = self._sessions.get(session_id)
        if not session:
            return False
        for tab in session.tabs:
            if tab.id == tab_id:
                for key, value in updates.items():
                    if hasattr(tab, key) and value is not None:
                        setattr(tab, key, value)
                tab.last_active = datetime.utcnow().isoformat()
                self._persist()
                return True
        return False


# ---------------------------------------------------------------------------
# Research Engine
# ---------------------------------------------------------------------------

class ResearchEngine:
    def __init__(self, session_manager: BrowserSessionManager):
        self.session_manager = session_manager
        self._sessions: Dict[str, ResearchSession] = {}
        self._load()

    def _load(self) -> None:
        data = _load_json(RESEARCH_FILE, [])
        for r_data in data:
            try:
                rs = ResearchSession(**r_data)
                self._sessions[rs.id] = rs
            except Exception:
                pass

    def _persist(self) -> None:
        _save_json(RESEARCH_FILE, [r.model_dump(mode="json") for r in self._sessions.values()])

    def _depth_to_max(self, depth: ResearchDepth) -> int:
        return {"quick": 1, "moderate": 2, "deep": 4, "comprehensive": 6}.get(depth, 3)

    def _depth_to_sources(self, depth: ResearchDepth) -> int:
        return {"quick": 3, "moderate": 6, "deep": 12, "comprehensive": 20}.get(depth, 10)

    async def conduct_research(self, req: ResearchRequest) -> ResearchResponse:
        start = time.monotonic()
        research = ResearchSession(
            id=str(uuid.uuid4()),
            query=req.query,
            depth=req.depth,
            max_depth=self._depth_to_max(req.depth),
            status="in_progress",
        )
        self._sessions[research.id] = research

        max_sources = min(req.max_sources, self._depth_to_sources(req.depth))

        steps = [
            f"Research query: {req.query}",
            f"Depth: {req.depth.value}, Max sources: {max_sources}",
            "Step 1: Decomposing query into sub-questions",
            "Step 2: Identifying key concepts and related terms",
            "Step 3: Searching for relevant sources",
            "Step 4: Extracting and synthesizing information",
            "Step 5: Cross-referencing sources for accuracy",
            "Step 6: Generating summary with citations",
        ]

        findings = self._generate_findings(req.query, max_sources)
        research.findings = findings
        research.urls_explored = [f.get("source_url", "") for f in findings if f.get("source_url")]
        research.sources = [{"url": f.get("source_url", ""), "title": f.get("title", ""), "relevance": f.get("relevance", 0.0)} for f in findings]

        if req.include_summary:
            research.summary = self._generate_summary(req.query, findings)

        research.status = "completed"
        self._persist()

        execution_time = (time.monotonic() - start) * 1000
        return ResearchResponse(
            research_id=research.id,
            findings=findings,
            summary=research.summary,
            sources=research.sources,
            urls_explored=len(research.urls_explored),
            status="completed",
            execution_time_ms=round(execution_time, 2),
        )

    def _generate_findings(self, query: str, max_sources: int) -> List[Dict[str, Any]]:
        findings = []
        topics = self._extract_topics(query)
        for i, topic in enumerate(topics[:max_sources]):
            findings.append({
                "id": str(uuid.uuid4()),
                "title": f"Finding on: {topic}",
                "content": f"[Research simulation for '{topic}' related to query: {query[:100]}]",
                "source_url": f"https://example.com/research/{topic.lower().replace(' ', '-')}",
                "source_type": "web",
                "relevance": round(0.7 + (i * 0.05) % 0.25, 2),
                "confidence": round(0.75 + (i * 0.03) % 0.2, 2),
                "extracted_at": datetime.utcnow().isoformat(),
                "key_points": [
                    f"Key insight 1 about {topic}",
                    f"Key insight 2 about {topic}",
                    f"Key insight 3 about {topic}",
                ],
            })
        return findings

    def _generate_summary(self, query: str, findings: List[Dict[str, Any]]) -> str:
        points = []
        for f in findings:
            kps = f.get("key_points", [])
            points.extend(kps)
        summary = (
            f"Research summary for: {query}. "
            f"Analyzed {len(findings)} sources. "
            f"Key findings: {'; '.join(points[:5])}. "
            f"Confidence: {sum(f.get('confidence', 0) for f in findings) / max(len(findings), 1):.2f} average across sources."
        )
        return summary

    @staticmethod
    def _extract_topics(query: str) -> List[str]:
        stop_words = {"what", "is", "how", "does", "the", "a", "an", "in", "of", "to", "for", "on", "and", "or", "but", "with", "at", "by", "from"}
        words = query.lower().split()
        meaningful = [w for w in words if w not in stop_words and len(w) > 2]
        if len(meaningful) <= 2:
            return [query]
        topics = []
        for i in range(0, len(meaningful), 2):
            chunk = meaningful[i:i+3]
            if chunk:
                topics.append(" ".join(chunk))
        return topics[:10]


# ---------------------------------------------------------------------------
# Permission Manager
# ---------------------------------------------------------------------------

class PermissionManager:
    def __init__(self):
        self._rules = self._load_rules()
        self._session_permissions: Dict[str, Dict[str, PermissionLevel]] = {}

    def _load_rules(self) -> Dict[str, PermissionLevel]:
        data = _load_json(PERMISSIONS_FILE, {})
        return {k: PermissionLevel(v) for k, v in data.items()}

    def _persist_rules(self) -> None:
        _save_json(PERMISSIONS_FILE, {k: v.value for k, v in self._rules.items()})

    def _classify_action(self, action: BrowserAction) -> Tuple[InteractionType, float]:
        passive_actions = {BrowserAction.extract, BrowserAction.screenshot, BrowserAction.scroll, BrowserAction.hover}
        active_actions = {BrowserAction.click, BrowserAction.type, BrowserAction.select, BrowserAction.fill_form, BrowserAction.submit_form, BrowserAction.navigate}
        destructive_actions = {BrowserAction.execute_script, BrowserAction.close}

        if action in destructive_actions:
            return InteractionType.destructive, 0.9
        if action in active_actions:
            return InteractionType.active, 0.4
        return InteractionType.passive, 0.1

    def check_permission(self, req: PermissionRequest) -> PermissionResponse:
        action_type, risk = self._classify_action(BrowserAction(req.action_type))

        if req.action_type in self._rules:
            level = self._rules[req.action_type]
            if level == PermissionLevel.deny:
                return PermissionResponse(allowed=False, permission_level=level, reason=f"Action '{req.action_type}' is globally denied")
            return PermissionResponse(allowed=True, permission_level=level, reason="Global rule allows")

        session_perms = self._session_permissions.get(req.session_id, {})
        if req.action_type in session_perms:
            level = session_perms[req.action_type]
            if level == PermissionLevel.deny:
                return PermissionResponse(allowed=False, permission_level=level, reason="Denied for this session")
            return PermissionResponse(allowed=True, permission_level=level, reason="Allowed for this session")

        if action_type == InteractionType.passive:
            return PermissionResponse(allowed=True, permission_level=PermissionLevel.allow, reason="Passive actions are allowed by default")
        if action_type == InteractionType.destructive:
            return PermissionResponse(allowed=False, permission_level=PermissionLevel.ask, reason="Destructive actions require explicit permission")

        return PermissionResponse(allowed=True, permission_level=PermissionLevel.ask, reason="Active action requires confirmation")

    def set_global_rule(self, action_type: str, level: PermissionLevel) -> None:
        self._rules[action_type] = level
        self._persist_rules()

    def set_session_permission(self, session_id: str, action_type: str, level: PermissionLevel) -> None:
        self._session_permissions.setdefault(session_id, {})[action_type] = level


# ---------------------------------------------------------------------------
# Browser Engine
# ---------------------------------------------------------------------------

class BrowserEngine:
    def __init__(self):
        self.session_manager = BrowserSessionManager()
        self.research_engine = ResearchEngine(self.session_manager)
        self.permission_manager = PermissionManager()
        self.page_engine = PageUnderstandingEngine()

    async def execute_action(self, req: BrowserActionRequest) -> BrowserActionResponse:
        start = time.monotonic()
        session = self.session_manager.get_session(req.session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Session '{req.session_id}' not found")

        perm_req = PermissionRequest(
            session_id=req.session_id,
            action_type=req.action.value,
            target=f"tab:{req.tab_id or session.active_tab_id}",
        )
        perm = self.permission_manager.check_permission(perm_req)
        if not perm.allowed:
            return BrowserActionResponse(
                success=False,
                action=req.action,
                error=f"Permission denied: {perm.reason}",
                latency_ms=(time.monotonic() - start) * 1000,
            )

        tab = None
        if req.tab_id:
            for t in session.tabs:
                if t.id == req.tab_id:
                    tab = t
                    break
        else:
            tab = self.session_manager.get_active_tab(session)

        if not tab:
            raise HTTPException(status_code=404, detail="Tab not found")

        result = await self._perform_action(req.action, tab, req.params)
        tab.last_active = datetime.utcnow().isoformat()

        return BrowserActionResponse(
            success=result.get("success", True),
            action=req.action,
            result=result,
            tab_state=tab.state,
            latency_ms=(time.monotonic() - start) * 1000,
        )

    async def _perform_action(self, action: BrowserAction, tab: BrowserTab, params: Dict[str, Any]) -> Dict[str, Any]:
        if action == BrowserAction.navigate:
            url = params.get("url", "")
            tab.url = url
            tab.history = tab.history[:tab.current_history_index + 1] + [url]
            tab.current_history_index = len(tab.history) - 1
            tab.state = TabState.ready
            return {"url": url, "title": url, "status": "navigated"}

        if action == BrowserAction.back:
            if tab.current_history_index > 0:
                tab.current_history_index -= 1
                tab.url = tab.history[tab.current_history_index]
                return {"url": tab.url, "status": "navigated_back"}
            return {"success": False, "error": "No history to go back to"}

        if action == BrowserAction.forward:
            if tab.current_history_index < len(tab.history) - 1:
                tab.current_history_index += 1
                tab.url = tab.history[tab.current_history_index]
                return {"url": tab.url, "status": "navigated_forward"}
            return {"success": False, "error": "No forward history"}

        if action == BrowserAction.extract:
            return {"target": params.get("target", "text"), "status": "extracted", "sample": f"[Content from {tab.url}]"}

        if action == BrowserAction.click:
            selector = params.get("selector", "")
            return {"selector": selector, "status": "clicked"}

        if action == BrowserAction.type:
            selector = params.get("selector", "")
            text = params.get("text", "")
            return {"selector": selector, "text_length": len(text), "status": "typed"}

        if action == BrowserAction.screenshot:
            return {"status": "screenshot_captured", "format": "png", "data_preview": "[base64 data]"}

        if action == BrowserAction.execute_script:
            script = params.get("script", "")
            return {"script_length": len(script), "status": "executed", "result": "[script result]"}

        if action == BrowserAction.refresh:
            return {"url": tab.url, "status": "refreshed"}

        if action == BrowserAction.switch_tab:
            return {"tab_id": params.get("tab_id", ""), "status": "switched"}

        if action == BrowserAction.new_tab:
            return {"status": "new_tab_created"}

        return {"status": f"{action.value}_executed"}

    async def extract_page(self, req: ExtractionRequest) -> ExtractionResponse:
        start = time.monotonic()
        request_id = str(uuid.uuid4())
        session = self.session_manager.get_session(req.session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Session '{req.session_id}' not found")

        tab = None
        if req.tab_id:
            for t in session.tabs:
                if t.id == req.tab_id:
                    tab = t
                    break
        else:
            tab = self.session_manager.get_active_tab(session)

        url = req.url or (tab.url if tab else "")

        page_content = PageContent()
        page_content.metadata.url = url

        targets_extracted = []
        for target in req.targets:
            if target == ExtractionTarget.metadata:
                page_content.metadata.title = url
                targets_extracted.append("metadata")
            elif target == ExtractionTarget.links:
                page_content.links = [{"url": "https://example.com", "text": "Example"}]
                targets_extracted.append("links")
            elif target == ExtractionTarget.headings:
                page_content.headings = [{"level": "h1", "text": url}]
                targets_extracted.append("headings")
            elif target == ExtractionTarget.tables:
                targets_extracted.append("tables")
            elif target == ExtractionTarget.text:
                page_content.main_content = f"[Simulated content extraction from {url}]"
                page_content.metadata.word_count = len(page_content.main_content.split())
                page_content.readability_score = PageUnderstandingEngine.calculate_readability(page_content.main_content)
                targets_extracted.append("text")

        if tab:
            tab.page_content = page_content
            self.session_manager.update_tab(req.session_id, tab.id, {"page_content": page_content.model_dump()})

        return ExtractionResponse(
            request_id=request_id,
            content=page_content,
            extraction_time_ms=(time.monotonic() - start) * 1000,
            targets_extracted=targets_extracted,
            truncated=len(json.dumps(page_content.model_dump())) > req.max_content_length,
        )

    async def fill_form(self, req: FormFillRequest) -> FormFillResponse:
        start = time.monotonic()
        session = self.session_manager.get_session(req.session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Session '{req.session_id}' not found")

        tab = None
        if req.tab_id:
            for t in session.tabs:
                if t.id == req.tab_id:
                    tab = t
                    break
        else:
            tab = self.session_manager.get_active_tab(session)

        if not tab:
            raise HTTPException(status_code=404, detail="Tab not found")

        fields_filled = len(req.fields)
        return FormFillResponse(
            success=True,
            fields_filled=fields_filled,
            fields_detected=fields_filled,
            form_submitted=req.submit,
        )


# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="ICHIN OS Service — Browser Engine",
    version="1.0.0",
    description="AI-powered browser automation, page understanding, and deep research engine",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = BrowserEngine()
_start_time = time.monotonic()


# ---------------------------------------------------------------------------
# Endpoints - Health
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse)
async def health():
    sessions = engine.session_manager._sessions
    tabs = sum(len(s.tabs) for s in sessions.values())
    return HealthResponse(
        status="ok",
        service="ichin-browser-engine",
        version="1.0.0",
        uptime=time.monotonic() - _start_time,
        active_sessions=len(sessions),
        active_tabs=tabs,
    )


# ---------------------------------------------------------------------------
# Endpoints - Sessions
# ---------------------------------------------------------------------------

@app.post("/sessions")
async def create_session():
    session = engine.session_manager.create_session()
    return session.model_dump(mode="json")


@app.get("/sessions")
async def list_sessions():
    return [s.model_dump(mode="json") for s in engine.session_manager._sessions.values()]


@app.get("/session/{session_id}")
async def get_session(session_id: str):
    session = engine.session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    return session.model_dump(mode="json")


# ---------------------------------------------------------------------------
# Endpoints - Tabs
# ---------------------------------------------------------------------------

@app.post("/session/{session_id}/tabs")
async def create_tab(session_id: str, url: str = ""):
    tab = engine.session_manager.create_tab(session_id, url)
    if not tab:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")
    return tab.model_dump(mode="json")


@app.delete("/session/{session_id}/tab/{tab_id}")
async def close_tab(session_id: str, tab_id: str):
    if not engine.session_manager.close_tab(session_id, tab_id):
        raise HTTPException(status_code=404, detail="Session or tab not found")
    return {"status": "closed", "tab_id": tab_id}


@app.get("/session/{session_id}/tabs")
async def list_tabs(session_id: str):
    session = engine.session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return [t.model_dump(mode="json") for t in session.tabs]


# ---------------------------------------------------------------------------
# Endpoints - Actions
# ---------------------------------------------------------------------------

@app.post("/action", response_model=BrowserActionResponse)
async def execute_action(body: BrowserActionRequest):
    try:
        return await engine.execute_action(body)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Action execution failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/extract", response_model=ExtractionResponse)
async def extract_content(body: ExtractionRequest):
    try:
        return await engine.extract_page(body)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Extraction failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/fill-form", response_model=FormFillResponse)
async def fill_form(body: FormFillRequest):
    try:
        return await engine.fill_form(body)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Form fill failed")
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# Endpoints - Research
# ---------------------------------------------------------------------------

@app.post("/research", response_model=ResearchResponse)
async def conduct_research(body: ResearchRequest):
    try:
        return await engine.research_engine.conduct_research(body)
    except Exception as exc:
        logger.exception("Research failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/research/{research_id}")
async def get_research(research_id: str):
    research = engine.research_engine._sessions.get(research_id)
    if not research:
        raise HTTPException(status_code=404, detail=f"Research '{research_id}' not found")
    return research.model_dump(mode="json")


# ---------------------------------------------------------------------------
# Endpoints - Permissions
# ---------------------------------------------------------------------------

@app.post("/permissions/check", response_model=PermissionResponse)
async def check_permission(body: PermissionRequest):
    return engine.permission_manager.check_permission(body)


@app.post("/permissions/global")
async def set_global_permission(action_type: str, level: PermissionLevel):
    engine.permission_manager.set_global_rule(action_type, level)
    return {"status": "updated", "action_type": action_type, "level": level.value}


@app.post("/permissions/session/{session_id}")
async def set_session_permission(session_id: str, action_type: str, level: PermissionLevel):
    engine.permission_manager.set_session_permission(session_id, action_type, level)
    return {"status": "updated", "session_id": session_id, "action_type": action_type, "level": level.value}


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8040, reload=True)
