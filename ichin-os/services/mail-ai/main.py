import asyncio
import json
import logging
import os
import time
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ichin.mail-ai")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
INBOX_FILE = os.path.join(DATA_DIR, "inbox.json")
RULES_FILE = os.path.join(DATA_DIR, "rules.json")
os.makedirs(DATA_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class EmailCategory(str, Enum):
    primary = "primary"
    social = "social"
    promotions = "promotions"
    updates = "updates"
    forums = "forums"
    spam = "spam"
    draft = "draft"
    sent = "sent"
    archive = "archive"
    trash = "trash"


class EmailPriority(str, Enum):
    critical = "critical"
    high = "high"
    normal = "normal"
    low = "low"
    none = "none"


class ActionItemStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"
    delegated = "delegated"


class SenderRelationship(str, Enum):
    known = "known"
    trusted = "trusted"
    frequent = "frequent"
    unknown = "unknown"
    blocked = "blocked"


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class EmailAddress(BaseModel):
    name: str = ""
    address: str


class EmailMessage(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message_id: str = ""
    thread_id: str = ""
    from_address: EmailAddress
    to: List[EmailAddress] = []
    cc: List[EmailAddress] = []
    bcc: List[EmailAddress] = []
    subject: str = ""
    body_text: str = ""
    body_html: str = ""
    received_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    category: EmailCategory = EmailCategory.primary
    priority: EmailPriority = EmailPriority.normal
    labels: List[str] = []
    read: bool = False
    flagged: bool = False
    attachments: List[Dict[str, Any]] = []
    size_bytes: int = 0
    snippet: str = ""
    ai_summary: Optional[str] = None
    ai_action_items: List[Dict[str, Any]] = []
    ai_suggested_reply: Optional[str] = None
    ai_category: Optional[str] = None
    sender_relationship: SenderRelationship = SenderRelationship.unknown
    processed_at: Optional[str] = None


class EmailThread(BaseModel):
    id: str
    subject: str
    participants: List[EmailAddress] = []
    messages: List[str] = []
    last_message_at: str = ""
    message_count: int = 0
    unread_count: int = 0
    category: EmailCategory = EmailCategory.primary
    priority: EmailPriority = EmailPriority.normal
    ai_summary: Optional[str] = None
    ai_action_items: List[Dict[str, Any]] = []
    ai_suggested_reply: Optional[str] = None


class ProcessingRequest(BaseModel):
    emails: List[EmailMessage] = []
    auto_categorize: bool = True
    auto_prioritize: bool = True
    auto_summarize: bool = True
    extract_actions: bool = True
    suggest_replies: bool = True
    enable_rules: bool = True


class ProcessingResponse(BaseModel):
    processed_count: int
    categorized: int = 0
    prioritized: int = 0
    summarized: int = 0
    actions_extracted: int = 0
    replies_suggested: int = 0
    rules_applied: int = 0
    processing_time_ms: float = 0.0
    emails: List[EmailMessage] = []


class CategorizationResult(BaseModel):
    category: EmailCategory
    confidence: float = 0.0
    labels: List[str] = []


class SummaryResult(BaseModel):
    summary: str
    key_points: List[str] = []
    sentiment: str = "neutral"
    action_items: List[Dict[str, Any]] = []


class RuleDefinition(BaseModel):
    id: str
    name: str
    description: str = ""
    conditions: Dict[str, Any]
    actions: Dict[str, Any]
    enabled: bool = True
    priority: int = 0
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class SuggestReplyRequest(BaseModel):
    email: EmailMessage
    style: str = "professional"
    max_length: int = 500
    include_context: bool = True


class SuggestReplyResponse(BaseModel):
    reply: str
    style: str
    confidence: float = 0.0


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    uptime: float
    inbox_size: int
    rules_count: int


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
# AI Email Processor
# ---------------------------------------------------------------------------

class AIEmailProcessor:
    def __init__(self):
        self._inbox: Dict[str, EmailMessage] = {}
        self._threads: Dict[str, EmailThread] = {}
        self._rules: Dict[str, RuleDefinition] = {}
        self._load()

    def _load(self) -> None:
        for e_data in _load_json(INBOX_FILE, []):
            try:
                email = EmailMessage(**e_data)
                self._inbox[email.id] = email
            except Exception as exc:
                logger.warning("Skipping invalid email: %s", exc)
        for r_data in _load_json(RULES_FILE, []):
            try:
                rule = RuleDefinition(**r_data)
                self._rules[rule.id] = rule
            except Exception as exc:
                logger.warning("Skipping invalid rule: %s", exc)
        logger.info("Loaded %d emails, %d rules", len(self._inbox), len(self._rules))

    def _persist_inbox(self) -> None:
        _save_json(INBOX_FILE, [e.model_dump(mode="json") for e in self._inbox.values()])

    def _persist_rules(self) -> None:
        _save_json(RULES_FILE, [r.model_dump(mode="json") for r in self._rules.values()])

    # -------------------------------------------------------------------
    # Classification
    # -------------------------------------------------------------------

    def categorize(self, email: EmailMessage) -> CategorizationResult:
        subj_lower = email.subject.lower()
        body_lower = email.body_text.lower()
        combined = f"{subj_lower} {body_lower}"

        spam_indicators = ["unsubscribe", "click here", "limited time", "act now", "free money", "congratulations", "you won", "prize", "lottery", "investment opportunity"]
        spam_score = sum(2 for w in spam_indicators if w in combined)

        if spam_score >= 6:
            return CategorizationResult(category=EmailCategory.spam, confidence=min(0.5 + spam_score * 0.05, 0.95), labels=["spam", "unsolicited"])

        social_indicators = ["facebook", "twitter", "linkedin", "instagram", "social", "friend request", "connection", "follow", "like", "comment", "share"]
        promo_indicators = ["sale", "discount", "offer", "deal", "promo", "coupon", "save", "buy", "shop", "order", "cart"]
        update_indicators = ["notification", "update", "alert", "change", "status", "report", "activity", "digest", "weekly"]
        forum_indicators = ["reply", "comment", "thread", "forum", "discussion", "group", "community", "subscribed"]

        if any(w in combined for w in social_indicators):
            return CategorizationResult(category=EmailCategory.social, confidence=0.7, labels=["social"])
        if any(w in combined for w in promo_indicators):
            return CategorizationResult(category=EmailCategory.promotions, confidence=0.75, labels=["promotion"])
        if any(w in combined for w in update_indicators):
            return CategorizationResult(category=EmailCategory.updates, confidence=0.7, labels=["update"])
        if any(w in combined for w in forum_indicators):
            return CategorizationResult(category=EmailCategory.forums, confidence=0.65, labels=["forum"])

        work_indicators = ["meeting", "project", "deadline", "invoice", "contract", "proposal", "report", "review", "task", "action required", "asap", "urgent", "follow-up"]
        if any(w in combined for w in work_indicators) or email.from_address.address.endswith((".com", ".org")):
            return CategorizationResult(category=EmailCategory.primary, confidence=0.6, labels=["work"])

        return CategorizationResult(category=EmailCategory.primary, confidence=0.4, labels=[])

    def prioritize(self, email: EmailMessage) -> EmailPriority:
        subj_lower = email.subject.lower()
        body_lower = email.body_text.lower()
        combined = f"{subj_lower} {body_lower}"

        critical_indicators = ["urgent", "critical", "emergency", "asap", "immediately", "deadline passed", "security", "breach", "account suspended"]
        high_indicators = ["deadline", "required", "action required", "important", "review needed", "approval", "final notice", "overdue"]

        if any(w in combined for w in critical_indicators):
            return EmailPriority.critical
        if any(w in combined for w in high_indicators):
            return EmailPriority.high

        if email.from_address.name:
            trusted_names = {"ceo", "founder", "lead", "manager", "director", "vp", "chief"}
            if any(t in email.from_address.name.lower() for t in trusted_names):
                return EmailPriority.high

        if email.flagged:
            return EmailPriority.high

        return EmailPriority.normal

    # -------------------------------------------------------------------
    # Summarization
    # -------------------------------------------------------------------

    def summarize(self, email: EmailMessage) -> SummaryResult:
        body = email.body_text or email.body_html
        if not body:
            return SummaryResult(summary="", key_points=[], sentiment="neutral")

        body_clean = body[:2000]

        sentences = [s.strip() for s in body_clean.replace("\n", " ").split(".") if s.strip()]
        if not sentences:
            return SummaryResult(summary=body_clean[:200], key_points=[], sentiment="neutral")

        key_points = []
        for s in sentences[:5]:
            s_lower = s.lower()
            if any(w in s_lower for w in ["important", "key", "critical", "note", "remember", "action", "required", "deadline", "urgent"]):
                key_points.append(s[:200])
            elif any(w in s_lower for w in ["please", "need", "would like", "request", "ask"]):
                key_points.append(s[:200])

        summary = sentences[0][:300] if sentences else body_clean[:200]
        if len(sentences) > 1:
            summary += ". " + sentences[1][:300]

        sentiment_keywords = {
            "positive": ["great", "excellent", "happy", "pleased", "thank", "appreciate", "good", "wonderful", "amazing", "delighted"],
            "negative": ["unfortunately", "sorry", "problem", "issue", "concern", "complaint", "dissatisfied", "error", "failed", "wrong"],
            "urgent": ["urgent", "critical", "emergency", "deadline", "asap", "immediately"],
        }
        sentiment_scores = {}
        for sent_type, words in sentiment_keywords.items():
            score = sum(1 for w in words if w in body_lower)
            if score > 0:
                sentiment_scores[sent_type] = score
        sentiment = max(sentiment_scores, key=sentiment_scores.get) if sentiment_scores else "neutral"

        return SummaryResult(
            summary=summary[:500],
            key_points=key_points[:5],
            sentiment=sentiment,
            action_items=self._extract_action_items(body_clean),
        )

    # -------------------------------------------------------------------
    # Action Item Extraction
    # -------------------------------------------------------------------

    def _extract_action_items(self, text: str) -> List[Dict[str, Any]]:
        action_items = []
        patterns = [
            (r"(?:please|kindly|can you|could you|need you to|would you)\s+(.+?)(?:\.|;|$)", ActionItemStatus.pending),
            (r"(?:I will|I'll|I'm going to|going to)\s+(.+?)(?:\.|;|$)", ActionItemStatus.pending),
            (r"(?:deadline|due date|by|before)\s+(.+?)(?:\.|;|$)", ActionItemStatus.pending),
        ]

        for pattern, status in patterns:
            import re
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches[:3]:
                action_text = match.strip()[:200] if isinstance(match, str) else match[0].strip()[:200]
                if action_text:
                    action_items.append({
                        "id": str(uuid.uuid4()),
                        "text": action_text,
                        "status": status.value,
                        "priority": "medium",
                        "source": "email",
                    })
        return action_items

    # -------------------------------------------------------------------
    # Suggested Replies
    # -------------------------------------------------------------------

    def suggest_reply(self, req: SuggestReplyRequest) -> SuggestReplyResponse:
        email = req.email
        body = email.body_text or ""

        reply_templates = {
            "professional": "Dear {name},\n\nThank you for your email regarding {subject}. ",
            "casual": "Hi {name},\n\nThanks for reaching out about {subject}. ",
            "formal": "Dear {name},\n\nI hope this message finds you well. ",
        }

        template = reply_templates.get(req.style, reply_templates["professional"])
        name = email.from_address.name or email.from_address.address.split("@")[0]

        body_lower = body.lower()
        reply_body = ""

        if "question" in body_lower or any(w in body_lower for w in ["?", "what", "how", "why", "when", "where"]):
            reply_body = "In response to your questions, I would like to provide the following information. "
        elif any(w in body_lower for w in ["meeting", "schedule", "appointment"]):
            reply_body = "Regarding the scheduling request, I have reviewed the proposed times and would like to suggest an alternative. "
        elif any(w in body_lower for w in ["problem", "issue", "error", "bug"]):
            reply_body = "I have received your report and I am looking into this matter. I will get back to you shortly with an update. "
        elif any(w in body_lower for w in ["request", "approval", "review"]):
            reply_body = "I have received your request and it is currently under review. I will follow up once a decision has been made. "
        else:
            reply_body = "I have received your message and will respond in detail shortly. "

        closing = {
            "professional": "\n\nBest regards,\nAI Mail Assistant",
            "casual": "\n\nCheers,\nAI Mail Assistant",
            "formal": "\n\nRespectfully,\nAI Mail Assistant",
        }

        reply = template.format(name=name, subject=email.subject[:100]) + reply_body + closing.get(req.style, "")
        if len(reply) > req.max_length:
            reply = reply[:req.max_length] + "..."

        return SuggestReplyResponse(
            reply=reply,
            style=req.style,
            confidence=0.75,
        )

    # -------------------------------------------------------------------
    # Rules Engine
    # -------------------------------------------------------------------

    def apply_rules(self, email: EmailMessage) -> EmailMessage:
        for rule in sorted(self._rules.values(), key=lambda r: r.priority, reverse=True):
            if not rule.enabled:
                continue
            if self._evaluate_conditions(email, rule.conditions):
                email = self._apply_actions(email, rule.actions)
                logger.info("Rule '%s' applied to email %s", rule.name, email.id)
        return email

    def _evaluate_conditions(self, email: EmailMessage, conditions: Dict[str, Any]) -> bool:
        for key, value in conditions.items():
            if key == "from_contains" and isinstance(value, str):
                if value.lower() not in email.from_address.address.lower() and value.lower() not in (email.from_address.name or "").lower():
                    return False
            elif key == "subject_contains" and isinstance(value, str):
                if value.lower() not in email.subject.lower():
                    return False
            elif key == "body_contains" and isinstance(value, str):
                if value.lower() not in email.body_text.lower():
                    return False
            elif key == "has_attachments":
                if bool(email.attachments) != bool(value):
                    return False
            elif key == "priority" and isinstance(value, str):
                if email.priority.value != value:
                    return False
        return True

    def _apply_actions(self, email: EmailMessage, actions: Dict[str, Any]) -> EmailMessage:
        if "category" in actions:
            try:
                email.category = EmailCategory(actions["category"])
            except ValueError:
                pass
        if "labels" in actions and isinstance(actions["labels"], list):
            email.labels.extend(actions["labels"])
        if "read" in actions:
            email.read = bool(actions["read"])
        if "flag" in actions:
            email.flagged = bool(actions["flag"])
        if "priority" in actions:
            try:
                email.priority = EmailPriority(actions["priority"])
            except ValueError:
                pass
        return email

    # -------------------------------------------------------------------
    # Processing Pipeline
    # -------------------------------------------------------------------

    async def process(self, req: ProcessingRequest) -> ProcessingResponse:
        start = time.monotonic()
        stats = {"categorized": 0, "prioritized": 0, "summarized": 0, "actions_extracted": 0, "replies_suggested": 0, "rules_applied": 0}

        processed_emails = []
        for email in req.emails:
            email.processed_at = datetime.utcnow().isoformat()

            if req.enable_rules:
                email = self.apply_rules(email)
                stats["rules_applied"] += 1

            if req.auto_categorize:
                categorization = self.categorize(email)
                email.category = categorization.category
                email.ai_category = categorization.category.value
                email.labels = list(set(email.labels + categorization.labels))
                stats["categorized"] += 1

            if req.auto_prioritize:
                email.priority = self.prioritize(email)
                stats["prioritized"] += 1

            if req.auto_summarize:
                summary = self.summarize(email)
                email.ai_summary = summary.summary
                stats["summarized"] += 1

            if req.extract_actions:
                actions = self._extract_action_items(f"{email.subject}\n{email.body_text}")
                email.ai_action_items = actions
                stats["actions_extracted"] += len(actions)

            if req.suggest_replies and email.category != EmailCategory.spam:
                suggest_req = SuggestReplyRequest(email=email, style="professional")
                reply = self.suggest_reply(suggest_req)
                email.ai_suggested_reply = reply.reply
                stats["replies_suggested"] += 1

            self._inbox[email.id] = email
            processed_emails.append(email)

        self._persist_inbox()

        return ProcessingResponse(
            processed_count=len(processed_emails),
            **stats,
            processing_time_ms=(time.monotonic() - start) * 1000,
            emails=processed_emails,
        )


# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="ICHIN OS Service — AI Mail Processor",
    version="1.0.0",
    description="AI-powered email processing: categorization, prioritization, summarization, action items, and smart replies",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

processor = AIEmailProcessor()
_start_time = time.monotonic()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        service="ichin-mail-ai",
        version="1.0.0",
        uptime=time.monotonic() - _start_time,
        inbox_size=len(processor._inbox),
        rules_count=len(processor._rules),
    )


@app.post("/process", response_model=ProcessingResponse)
async def process_emails(body: ProcessingRequest):
    try:
        return await processor.process(body)
    except Exception as exc:
        logger.exception("Email processing failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/categorize", response_model=CategorizationResult)
async def categorize_email(body: EmailMessage):
    try:
        return processor.categorize(body)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/prioritize")
async def prioritize_email(body: EmailMessage):
    try:
        return {"priority": processor.prioritize(body).value}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/summarize", response_model=SummaryResult)
async def summarize_email(body: EmailMessage):
    try:
        return processor.summarize(body)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/suggest-reply", response_model=SuggestReplyResponse)
async def suggest_reply(body: SuggestReplyRequest):
    try:
        return processor.suggest_reply(body)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/inbox")
async def list_inbox(category: Optional[str] = None, limit: int = 50, unread_only: bool = False):
    emails = list(processor._inbox.values())
    if category:
        try:
            cat = EmailCategory(category)
            emails = [e for e in emails if e.category == cat]
        except ValueError:
            pass
    if unread_only:
        emails = [e for e in emails if not e.read]
    emails.sort(key=lambda e: e.received_at, reverse=True)
    return [e.model_dump() for e in emails[:limit]]


@app.get("/email/{email_id}")
async def get_email(email_id: str):
    email = processor._inbox.get(email_id)
    if not email:
        raise HTTPException(status_code=404, detail=f"Email '{email_id}' not found")
    return email.model_dump()


@app.delete("/email/{email_id}")
async def delete_email(email_id: str):
    if email_id not in processor._inbox:
        raise HTTPException(status_code=404, detail=f"Email '{email_id}' not found")
    del processor._inbox[email_id]
    processor._persist_inbox()
    return {"status": "deleted", "email_id": email_id}


# ---------------------------------------------------------------------------
# Rules Endpoints
# ---------------------------------------------------------------------------

@app.post("/rules")
async def create_rule(body: RuleDefinition):
    if body.id in processor._rules:
        raise HTTPException(status_code=409, detail=f"Rule '{body.id}' already exists")
    processor._rules[body.id] = body
    processor._persist_rules()
    return body.model_dump()


@app.get("/rules")
async def list_rules():
    return [r.model_dump() for r in processor._rules.values()]


@app.get("/rule/{rule_id}")
async def get_rule(rule_id: str):
    rule = processor._rules.get(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail=f"Rule '{rule_id}' not found")
    return rule.model_dump()


@app.delete("/rule/{rule_id}")
async def delete_rule(rule_id: str):
    if rule_id not in processor._rules:
        raise HTTPException(status_code=404, detail=f"Rule '{rule_id}' not found")
    del processor._rules[rule_id]
    processor._persist_rules()
    return {"status": "deleted", "rule_id": rule_id}


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8060, reload=True)
