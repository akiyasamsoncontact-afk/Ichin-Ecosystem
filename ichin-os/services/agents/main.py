import asyncio
import logging
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
logger = logging.getLogger("ichin.agents")

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SystemMode(str, Enum):
    normal = "normal"
    focus = "focus"
    deep_focus = "deep_focus"
    lock = "lock"


class ConflictStrategy(str, Enum):
    confidence = "confidence"
    risk_averse = "risk_averse"
    mode_rules = "mode_rules"
    weighted = "weighted"


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class AgentInput(BaseModel):
    request: str
    workspace: Optional[str] = None
    mode: SystemMode = SystemMode.normal
    memory_slice: Optional[Dict[str, Any]] = None
    agent_outputs: Optional[Dict[str, Any]] = None


class AgentOutput(BaseModel):
    agent_name: str
    recommendation: str
    reasoning: str
    confidence: float = Field(ge=0.0, le=1.0)
    risk_score: float = Field(ge=0.0, le=1.0)
    efficiency_score: float = Field(ge=0.0, le=1.0)
    dependencies: List[str] = Field(default_factory=list)

    @field_validator("confidence", "risk_score", "efficiency_score")
    @classmethod
    def validate_range(cls, v: float) -> float:
        return max(0.0, min(1.0, v))


class ReasonRequest(BaseModel):
    request: str
    workspace: Optional[str] = None
    mode: SystemMode = SystemMode.normal
    memory_slice: Optional[Dict[str, Any]] = None
    agent_outputs: Optional[Dict[str, Any]] = None


class OrchestrateRequest(BaseModel):
    request: str
    agents: Optional[List[str]] = None
    workspace: Optional[str] = None
    mode: SystemMode = SystemMode.normal
    memory_slice: Optional[Dict[str, Any]] = None


class ConflictResolveRequest(BaseModel):
    outputs: List[AgentOutput]
    strategy: ConflictStrategy = ConflictStrategy.weighted
    mode: SystemMode = SystemMode.normal
    workspace: Optional[str] = None


class AgentInfo(BaseModel):
    name: str
    description: str
    responsibilities: List[str]
    priority_factors: List[str]


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    uptime: float
    agent_count: int


# ---------------------------------------------------------------------------
# Base Agent
# ---------------------------------------------------------------------------

class BaseAgent:
    name: str = "base"
    description: str = ""
    responsibilities: List[str] = []
    priority_factors: List[str] = []
    risk_tolerance: float = 0.3

    async def process(self, inp: AgentInput) -> AgentOutput:
        raise NotImplementedError

    def _output(
        self,
        recommendation: str,
        reasoning: str,
        confidence: float,
        risk_score: float,
        efficiency_score: float = 0.5,
        dependencies: Optional[List[str]] = None,
    ) -> AgentOutput:
        return AgentOutput(
            agent_name=self.name,
            recommendation=recommendation,
            reasoning=reasoning,
            confidence=max(0.0, min(1.0, confidence)),
            risk_score=max(0.0, min(1.0, risk_score)),
            efficiency_score=max(0.0, min(1.0, efficiency_score)),
            dependencies=dependencies or [],
        )

    def _reject(self, reason: str = "No action needed", confidence: float = 0.3) -> AgentOutput:
        return self._output(
            recommendation="No action required from this agent",
            reasoning=reason,
            confidence=confidence,
            risk_score=0.02,
            efficiency_score=0.1,
        )


# ---------------------------------------------------------------------------
# Agent: Study
# ---------------------------------------------------------------------------

class StudyAgent(BaseAgent):
    name = "study"
    description = "Optimizes learning, retention, and academic performance through structured study techniques"
    responsibilities = [
        "generate quizzes",
        "break down complex topics",
        "create study schedules",
        "detect weak areas",
        "simulate exams",
        "convert content to flashcards",
    ]
    priority_factors = ["clarity", "speed", "depth"]

    async def process(self, inp: AgentInput) -> AgentOutput:
        req_lower = inp.request.lower()
        steps: List[str] = []
        findings: Dict[str, Any] = {}

        steps.append("Step 1: Parse request for study-related keywords and concepts")
        study_keywords = {
            "quiz": "quiz_generation",
            "flashcard": "flashcard_conversion",
            "schedule": "study_schedule",
            "exam": "exam_simulation",
            "practice": "practice_test",
            "review": "content_review",
            "memorize": "memory_retention",
            "understand": "concept_decomposition",
            "learn": "learning_path",
            "topic": "topic_breakdown",
            "subject": "subject_analysis",
            "weak": "weak_area_detection",
            "improve": "improvement_plan",
        }
        matched = {k: v for k, v in study_keywords.items() if k in req_lower}
        findings["detected_study_needs"] = list(matched.values()) if matched else ["general_study_guidance"]

        steps.append("Step 2: Analyze workspace context for relevant study domain")
        workspace_domain = (inp.workspace or "").lower()
        if workspace_domain in ("math", "mathematics", "science", "history", "language"):
            findings["study_domain"] = workspace_domain
        else:
            findings["study_domain"] = "general"

        steps.append("Step 3: Determine study approach based on request complexity")
        complexity = len(inp.request.split())
        if complexity > 50:
            findings["approach"] = "structured_decomposition"
            findings["recommended_technique"] = "concept_mapping"
        elif complexity > 20:
            findings["approach"] = "focused_practice"
            findings["recommended_technique"] = "active_recall"
        else:
            findings["approach"] = "quick_review"
            findings["recommended_technique"] = "spaced_repetition"

        steps.append("Step 4: Retrieve memory slice for past performance data")
        memory = inp.memory_slice or {}
        past_mastery = memory.get("study_mastery", {})
        findings["prior_mastery"] = past_mastery

        steps.append("Step 5: Generate study recommendation with confidence scoring")
        if matched:
            confidence_base = 0.75 + (len(matched) * 0.05)
            recommendation = (
                f"Generate {'/'.join(findings['detected_study_needs'])} "
                f"using {findings['recommended_technique']} in {workspace_domain or 'general'} domain"
            )
            confidence = min(confidence_base, 0.95)
            risk = 0.05
            efficiency = 0.7 + (len(matched) * 0.05)
        else:
            master_levels = list(past_mastery.values()) if isinstance(past_mastery, dict) else []
            if master_levels and any(m < 0.5 for m in master_levels):
                steps.append("Step 5a: Low mastery detected - proactive study reinforcement")
                recommendation = "Review weak areas based on prior mastery data"
                confidence = 0.65
                risk = 0.04
                efficiency = 0.6
            else:
                return self._reject("No study intent or weak areas detected in request")

        steps.append("Step 6: Validate against verified sources requirement")
        findings["source_verification"] = "required"
        dependencies = ["research"] if findings["detected_study_needs"] != ["general_study_guidance"] else []

        return self._output(
            recommendation=recommendation,
            reasoning="\n".join(steps) + f"\n\nFindings: {findings}",
            confidence=confidence,
            risk_score=risk,
            efficiency_score=min(efficiency, 0.95),
            dependencies=dependencies,
        )


# ---------------------------------------------------------------------------
# Agent: Coding
# ---------------------------------------------------------------------------

class CodingAgent(BaseAgent):
    name = "coding"
    description = "Software development, debugging, architecture design, and code quality analysis"
    responsibilities = [
        "code generation",
        "debugging",
        "refactoring",
        "architecture design",
        "performance optimization",
        "dependency analysis",
    ]
    priority_factors = ["correctness", "performance", "elegance"]

    async def process(self, inp: AgentInput) -> AgentOutput:
        req_lower = inp.request.lower()
        steps: List[str] = []
        findings: Dict[str, Any] = {}

        steps.append("Step 1: Identify programming context from request")
        coding_keywords = {
            "code": "code_generation",
            "debug": "debugging",
            "error": "error_analysis",
            "function": "function_implementation",
            "algorithm": "algorithm_design",
            "api": "api_development",
            "implement": "implementation",
            "refactor": "refactoring",
            "optimize": "optimization",
            "test": "testing",
            "bug": "bug_fix",
            "performance": "performance_tuning",
            "security": "security_review",
            "dependency": "dependency_analysis",
            "architecture": "architecture_design",
            "deploy": "deployment",
            "database": "database_design",
            "async": "async_patterns",
            "thread": "concurrency",
        }
        matched = {k: v for k, v in coding_keywords.items() if k in req_lower}
        findings["coding_needs"] = list(matched.values()) if matched else []

        steps.append("Step 2: Detect programming languages and frameworks mentioned")
        lang_patterns = {
            "python": "Python",
            "javascript": "JavaScript",
            "typescript": "TypeScript",
            "rust": "Rust",
            "java": "Java",
            "go": "Go",
            "c++": "C++",
            "react": "React",
            "node": "Node.js",
            "fastapi": "FastAPI",
            "django": "Django",
            "flask": "Flask",
            "sql": "SQL",
        }
        detected_langs = [v for k, v in lang_patterns.items() if k in req_lower]
        findings["detected_languages"] = detected_langs

        steps.append("Step 3: Analyze for security-sensitive patterns")
        security_patterns = [
            "password", "token", "secret", "injection", "xss", "csrf",
            "sudo", "exec(", "eval(", "shell", "raw_input",
        ]
        security_hits = [p for p in security_patterns if p in req_lower]
        if security_hits:
            findings["security_concerns"] = security_hits
            findings["requires_security_review"] = True

        steps.append("Step 4: Evaluate code complexity and recommend approach")
        word_count = len(inp.request.split())
        if word_count > 80:
            findings["complexity"] = "high"
            findings["approach"] = "modular_design"
        elif word_count > 30:
            findings["complexity"] = "medium"
            findings["approach"] = "structured_implementation"
        else:
            findings["complexity"] = "low"
            findings["approach"] = "direct_solution"

        steps.append("Step 5: Generate technical recommendation")
        if not findings["coding_needs"]:
            return self._reject("No programming-related content detected in request")

        confidence = min(0.7 + (len(matched) * 0.06), 0.95)
        if findings.get("requires_security_review"):
            confidence *= 0.9
            findings["recommendation_note"] = "Security review flagged - reducing confidence"

        risk_base = len(security_hits) * 0.12
        risk = min(risk_base + 0.08, 0.7)
        efficiency = min(0.6 + (len(matched) * 0.06), 0.9)

        deps = []
        if findings.get("requires_security_review"):
            deps.append("security")
        if "architecture" in findings["coding_needs"]:
            deps.append("research")

        return self._output(
            recommendation=(
                f"Apply {findings['approach']} for {', '.join(findings['coding_needs'])} "
                f"{'in ' + ', '.join(detected_langs) if detected_langs else ''}"
            ),
            reasoning="\n".join(steps) + f"\n\nFindings: {findings}",
            confidence=confidence,
            risk_score=risk,
            efficiency_score=min(efficiency, 0.95),
            dependencies=deps,
        )


# ---------------------------------------------------------------------------
# Agent: Learning
# ---------------------------------------------------------------------------

class LearningAgent(BaseAgent):
    name = "learning"
    description = "Builds structured knowledge systems from raw information using concept graph thinking"
    responsibilities = [
        "convert topics to learning paths",
        "generate courses",
        "connect concepts",
        "build progressive difficulty ladders",
    ]
    priority_factors = ["comprehension", "structure", "detail"]

    async def process(self, inp: AgentInput) -> AgentOutput:
        req_lower = inp.request.lower()
        steps: List[str] = []
        findings: Dict[str, Any] = {}

        steps.append("Step 1: Identify core topic and scope")
        topic_indicators = [
            "learn", "understand", "concept", "knowledge", "skill",
            "tutorial", "course", "resource", "topic", "subject",
            "overview", "introduction", "basics", "advanced",
            "fundamental", "principle", "theory", "framework",
        ]
        detected_indicators = [w for w in topic_indicators if w in req_lower]
        findings["learning_intent_detected"] = len(detected_indicators) > 0

        steps.append("Step 2: Map concept hierarchy")
        if not findings["learning_intent_detected"]:
            return self._reject("No learning intent detected in request")

        word_count = len(inp.request.split())
        if word_count > 60:
            findings["scope"] = "broad"
            findings["structure"] = "curriculum_design"
        elif word_count > 20:
            findings["scope"] = "focused"
            findings["structure"] = "learning_module"
        else:
            findings["scope"] = "narrow"
            findings["structure"] = "concept_explanation"

        steps.append("Step 3: Determine prerequisites and dependencies")
        findings["approach"] = "progressive_difficulty"
        findings["recommended_format"] = "learning_path"

        steps.append("Step 4: Reference other agent outputs for enrichment")
        other_outputs = inp.agent_outputs or {}
        if "study" in other_outputs:
            findings["study_integration"] = "available"
        if "research" in other_outputs:
            findings["research_support"] = "available"

        steps.append("Step 5: Generate learning structure recommendation")

        confidence = min(0.65 + (len(detected_indicators) * 0.04), 0.92)
        return self._output(
            recommendation=(
                f"Design {findings['structure']} with {findings['approach']} "
                f"for scope: {findings['scope']}"
            ),
            reasoning="\n".join(steps) + f"\n\nFindings: {findings}",
            confidence=confidence,
            risk_score=0.06,
            efficiency_score=min(0.6 + (len(detected_indicators) * 0.04), 0.85),
            dependencies=["research", "study"],
        )


# ---------------------------------------------------------------------------
# Agent: Productivity
# ---------------------------------------------------------------------------

class ProductivityAgent(BaseAgent):
    name = "productivity"
    description = "Optimizes execution of tasks and workflows through systems thinking and efficiency scoring"
    responsibilities = [
        "task breakdown",
        "scheduling",
        "workflow optimization",
        "priority ranking",
        "time estimation",
    ]
    priority_factors = ["efficiency", "simplicity", "completeness"]

    async def process(self, inp: AgentInput) -> AgentOutput:
        req_lower = inp.request.lower()
        steps: List[str] = []
        findings: Dict[str, Any] = {}

        steps.append("Step 1: Detect task and workflow signals")
        productivity_keywords = {
            "task": "task_identification",
            "todo": "todo_list",
            "deadline": "deadline_tracking",
            "priority": "priority_ranking",
            "schedule": "scheduling",
            "organize": "organization",
            "plan": "planning",
            "manage": "management",
            "time": "time_allocation",
            "efficient": "efficiency_analysis",
            "workflow": "workflow_optimization",
            "project": "project_planning",
            "goal": "goal_setting",
            "track": "progress_tracking",
            "automate": "automation_opportunity",
        }
        matched = {k: v for k, v in productivity_keywords.items() if k in req_lower}
        findings["productivity_needs"] = list(matched.values()) if matched else []

        steps.append("Step 2: Estimate task load and complexity")
        word_count = len(inp.request.split())
        task_count = sum(1 for line in inp.request.split(".") if any(
            w in line.lower()
            for w in ["task", "step", "item", "thing", "todo", "done", "complete"]
        ))
        findings["estimated_tasks"] = max(task_count, 1)
        findings["total_complexity"] = "high" if word_count > 80 else "medium" if word_count > 30 else "low"

        steps.append("Step 3: Check focus mode constraints")
        findings["current_mode"] = inp.mode.value
        if inp.mode in (SystemMode.deep_focus, SystemMode.lock):
            findings["mode_constraint"] = "productivity_scoring_applied"
        else:
            findings["mode_constraint"] = "full_productivity_range_available"

        steps.append("Step 4: Calculate efficiency baseline")
        if not findings["productivity_needs"]:
            return self._reject("No productivity or task signals detected")

        task_load = findings["estimated_tasks"]
        complexity_factor = {"low": 0.3, "medium": 0.6, "high": 0.9}
        base_efficiency = 0.7 - (complexity_factor.get(findings["total_complexity"], 0.5) * 0.2)
        base_efficiency += min(task_load * 0.03, 0.15)

        steps.append("Step 5: Generate productivity recommendation")
        recommendation = (
            f"Apply workflow optimization for {len(findings['productivity_needs'])} identified areas: "
            f"{', '.join(findings['productivity_needs'][:4])}. "
            f"Break down {task_load} task(s) with priority ranking."
        )

        return self._output(
            recommendation=recommendation,
            reasoning="\n".join(steps) + f"\n\nFindings: {findings}",
            confidence=min(0.65 + (len(matched) * 0.05), 0.9),
            risk_score=0.1,
            efficiency_score=min(max(base_efficiency, 0.3), 0.9),
            dependencies=["calendar"] if "scheduling" in findings["productivity_needs"] else [],
        )


# ---------------------------------------------------------------------------
# Agent: Focus
# ---------------------------------------------------------------------------

class FocusAgent(BaseAgent):
    name = "focus"
    description = "Attention management and distraction reduction with adaptive intervention levels"
    responsibilities = [
        "detect distractions",
        "suggest focus sessions",
        "enforce rules",
        "adjust aggression level",
        "recommend breaks",
    ]
    priority_factors = ["focus_stability", "productivity", "flexibility"]

    async def process(self, inp: AgentInput) -> AgentOutput:
        req_lower = inp.request.lower()
        steps: List[str] = []
        findings: Dict[str, Any] = {}

        steps.append("Step 1: Analyze current system mode")
        findings["current_mode"] = inp.mode.value

        steps.append("Step 2: Detect distraction signals")
        distraction_keywords = [
            "distract", "noise", "interrupt", "notification", "social",
            "break", "pause", "focus", "concentrate", "attention",
            "multitask", "switch", "stop", "block", "limit",
        ]
        distraction_hits = [w for w in distraction_keywords if w in req_lower]
        findings["distraction_signals"] = distraction_hits

        steps.append("Step 3: Calculate intervention aggression level")
        mode_aggression = {
            SystemMode.normal: 0.0,
            SystemMode.focus: 0.3,
            SystemMode.deep_focus: 0.7,
            SystemMode.lock: 1.0,
        }
        base_aggression = mode_aggression.get(inp.mode, 0.0)
        signal_boost = min(len(distraction_hits) * 0.1, 0.3)
        aggression = min(base_aggression + signal_boost, 1.0)
        findings["aggression_level"] = aggression

        steps.append("Step 4: Check for over-interruption risk")
        if inp.mode not in (SystemMode.deep_focus, SystemMode.lock) and aggression > 0.5:
            findings["over_interruption_warning"] = "Aggression exceeds safe threshold for current mode"
            aggression = min(aggression, 0.5)

        steps.append("Step 5: Determine if intervention is appropriate")
        if not distraction_hits and inp.mode == SystemMode.normal:
            return self._output(
                recommendation="Maintain current state — no focus intervention needed",
                reasoning="No distraction signals detected in normal mode",
                confidence=0.5,
                risk_score=0.05,
                efficiency_score=0.9,
            )

        if aggression > 0.6:
            recommendation = "Activate strong focus enforcement: block distractions, silence notifications, enter protected session"
        elif aggression > 0.3:
            recommendation = "Apply soft focus guidance: suggest single-tasking, mute non-essential notifications"
        else:
            recommendation = "No intervention — monitor for distraction patterns"

        if inp.mode in (SystemMode.deep_focus, SystemMode.lock):
            recommendation += " — DeepFocus/Lock mode active, intervention strength amplified"

        confidence = min(0.5 + (aggression * 0.4), 0.95)
        risk = 0.2 if aggression > 0.6 else 0.1
        efficiency = 0.9 - (aggression * 0.2)

        return self._output(
            recommendation=recommendation,
            reasoning="\n".join(steps) + f"\n\nFindings: {findings}",
            confidence=confidence,
            risk_score=risk,
            efficiency_score=max(efficiency, 0.4),
        )


# ---------------------------------------------------------------------------
# Agent: Security
# ---------------------------------------------------------------------------

class SecurityAgent(BaseAgent):
    name = "security"
    description = "System integrity, safety, and anomaly detection with strict rule-based logic"
    responsibilities = [
        "detect malicious patterns",
        "validate actions",
        "flag suspicious behavior",
        "monitor risks",
    ]
    priority_factors = ["safety", "correctness", "usability"]

    async def process(self, inp: AgentInput) -> AgentOutput:
        req_lower = inp.request.lower()
        steps: List[str] = []
        findings: Dict[str, Any] = {}

        steps.append("Step 1: Run pattern-based threat detection")
        high_risk_patterns = {
            "rm -rf": "destructive_filesystem",
            "DROP TABLE": "database_destruction",
            "format ": "disk_format",
            "shutdown": "system_shutdown",
            "reboot": "system_reboot",
            "sudo ": "privilege_escalation",
            "chmod 777": "permission_escalation",
            "eval(": "code_injection",
            "exec(": "code_injection",
            "__import__": "dynamic_import_abuse",
            "pickle.load": "deserialization_risk",
            "base64": "encoding_obfuscation",
        }
        high_risk_matches = {k: v for k, v in high_risk_patterns.items() if k in req_lower}

        steps.append("Step 2: Detect sensitive data exposure")
        sensitive_patterns = {
            "password": "credential_exposure",
            "secret": "secret_exposure",
            "token": "token_exposure",
            "api_key": "api_key_exposure",
            "private_key": "private_key_exposure",
            "connection_string": "connection_string_exposure",
        }
        sensitive_matches = {k: v for k, v in sensitive_patterns.items() if k in req_lower}

        steps.append("Step 3: Check mode-specific security posture")
        findings["mode_security_level"] = inp.mode.value
        if inp.mode == SystemMode.lock:
            findings["lock_mode_restrictions"] = [
                "entertainment_blocked",
                "social_media_blocked",
                "gaming_blocked",
                "execution_restricted",
            ]

        steps.append("Step 4: Calculate risk score")
        findings["high_risk_findings"] = list(high_risk_matches.values())
        findings["sensitive_findings"] = list(sensitive_matches.values())
        risk_score = min(
            (len(high_risk_matches) * 0.3)
            + (len(sensitive_matches) * 0.2)
            + (0.1 if inp.mode == SystemMode.lock else 0.0),
            0.95,
        )

        steps.append("Step 5: Generate security assessment")

        if high_risk_matches or sensitive_matches:
            confidence = min(0.8 + (len(high_risk_matches) * 0.08), 0.98)
            recommendation = f"SECURITY ALERT: Flagged {len(high_risk_matches)} high-risk and {len(sensitive_matches)} sensitive patterns"
            if high_risk_matches:
                recommendation += f". High risk: {', '.join(high_risk_matches.keys())}"
            if sensitive_matches:
                recommendation += f". Sensitive: {', '.join(sensitive_matches.keys())}"
        elif inp.mode == SystemMode.lock:
            confidence = 0.9
            recommendation = "Lock mode security posture active — no threats detected"
            risk_score = 0.15
        else:
            steps.append("Step 5a: Clean scan — no threats detected")
            return self._output(
                recommendation="No security concerns — request passes all checks",
                reasoning="Passed pattern-based threat detection and sensitive data scan with no flags",
                confidence=0.7,
                risk_score=0.05,
                efficiency_score=0.8,
            )

        return self._output(
            recommendation=recommendation,
            reasoning="\n".join(steps) + f"\n\nFindings: {findings}",
            confidence=confidence,
            risk_score=risk_score,
            efficiency_score=max(0.6 - (risk_score * 0.3), 0.3),
            dependencies=["focus"] if inp.mode in (SystemMode.deep_focus, SystemMode.lock) else [],
        )


# ---------------------------------------------------------------------------
# Agent: Calendar
# ---------------------------------------------------------------------------

class CalendarAgent(BaseAgent):
    name = "calendar"
    description = "Time management, scheduling, event detection, and conflict resolution"
    responsibilities = [
        "detect events in text",
        "propose calendar entries",
        "resolve conflicts",
        "optimize time distribution",
    ]
    priority_factors = ["accuracy", "convenience", "automation"]

    async def process(self, inp: AgentInput) -> AgentOutput:
        req_lower = inp.request.lower()
        steps: List[str] = []
        findings: Dict[str, Any] = {}

        steps.append("Step 1: Extract temporal signals from request")
        date_patterns = [
            "today", "tomorrow", "yesterday", "monday", "tuesday",
            "wednesday", "thursday", "friday", "saturday", "sunday",
            "january", "february", "march", "april", "may", "june",
            "july", "august", "september", "october", "november", "december",
            "next week", "this week", "next month", "this month",
        ]
        time_patterns = [
            "am", "pm", "o'clock", ":00", ":15", ":30", ":45",
            "morning", "afternoon", "evening", "night",
            "hour", "minute", "duration",
        ]
        event_keywords = [
            "meeting", "event", "appointment", "call", "session",
            "deadline", "due", "remind", "schedule", "book",
            "reserve", "plan", "block", "time",
        ]
        detected_dates = [w for w in date_patterns if w in req_lower]
        detected_times = [w for w in time_patterns if w in req_lower]
        detected_events = [w for w in event_keywords if w in req_lower]
        findings["temporal_signals"] = {
            "dates": detected_dates,
            "times": detected_times,
            "events": detected_events,
        }

        steps.append("Step 2: Check for conflicting events")
        other_outputs = inp.agent_outputs or {}
        if "productivity" in other_outputs:
            findings["productivity_integration"] = "available"

        steps.append("Step 3: Determine scheduling type")
        has_time = len(detected_times) > 0 or len(detected_dates) > 0
        has_event = len(detected_events) > 0

        if not has_time and not has_event:
            return self._reject("No temporal or event signals detected")

        if has_time and has_event:
            findings["scheduling_type"] = "exact_event"
            recommendations = "Propose calendar entry with specified time and date"
            confidence_base = 0.8
        elif has_event:
            findings["scheduling_type"] = "event_only"
            recommendations = "Detect suggested event — propose time optimization"
            confidence_base = 0.65
        else:
            findings["scheduling_type"] = "temporal_context"
            recommendations = "Note temporal context — no specific event detected"
            confidence_base = 0.5

        steps.append("Step 4: Estimate time distribution")
        findings["event_count"] = len(detected_events)
        findings["time_context"] = "rich" if len(detected_times) + len(detected_dates) > 3 else "limited"

        return self._output(
            recommendation=recommendations,
            reasoning="\n".join(steps) + f"\n\nFindings: {findings}",
            confidence=min(confidence_base + (len(detected_events) * 0.05), 0.92),
            risk_score=0.08,
            efficiency_score=min(0.5 + (len(detected_times) * 0.08) + (len(detected_dates) * 0.05), 0.9),
            dependencies=["productivity"],
        )


# ---------------------------------------------------------------------------
# Agent: Research
# ---------------------------------------------------------------------------

class ResearchAgent(BaseAgent):
    name = "research"
    description = "Gathers and synthesizes information with source-critical, evidence-based reasoning"
    responsibilities = [
        "search for information",
        "summarize findings",
        "cross-reference sources",
        "identify patterns",
        "provide citations",
    ]
    priority_factors = ["accuracy", "comprehensiveness", "speed"]

    async def process(self, inp: AgentInput) -> AgentOutput:
        req_lower = inp.request.lower()
        steps: List[str] = []
        findings: Dict[str, Any] = {}

        steps.append("Step 1: Identify research query and scope")
        research_indicators = [
            "what", "why", "how", "when", "where", "who",
            "research", "search", "find", "lookup", "investigate",
            "analyze", "explore", "tell me about", "information",
            "data", "source", "reference", "citation", "study",
            "evidence", "report", "summary", "overview",
        ]
        detected_indicators = [w for w in research_indicators if w in req_lower]
        findings["research_intent"] = len(detected_indicators) > 0

        steps.append("Step 2: Determine research depth needed")
        word_count = len(inp.request.split())
        if word_count > 80:
            findings["depth"] = "deep"
            findings["approach"] = "comprehensive_synthesis"
        elif word_count > 30:
            findings["depth"] = "moderate"
            findings["approach"] = "focused_analysis"
        else:
            findings["depth"] = "quick"
            findings["approach"] = "fast_fact_check"

        steps.append("Step 3: Cross-reference with other agent outputs")
        other_outputs = inp.agent_outputs or {}
        if "learning" in other_outputs:
            findings["learning_alignment"] = "available"
        if "study" in other_outputs:
            findings["study_alignment"] = "available"

        steps.append("Step 4: Plan source verification strategy")
        findings["verification_strategy"] = "cross_reference_multiple_sources"
        findings["citation_requirement"] = "required"

        if not findings["research_intent"]:
            return self._reject("No research intent detected in request")

        steps.append("Step 5: Generate research plan")

        confidence = min(0.6 + (len(detected_indicators) * 0.04), 0.9)
        return self._output(
            recommendation=(
                f"Conduct {findings['depth']} research using {findings['approach']} "
                f"with {findings['verification_strategy']}"
            ),
            reasoning="\n".join(steps) + f"\n\nFindings: {findings}",
            confidence=confidence,
            risk_score=0.07,
            efficiency_score=min(0.55 + (len(detected_indicators) * 0.04), 0.85),
            dependencies=["learning"],
        )


# ---------------------------------------------------------------------------
# Agent: Browser
# ---------------------------------------------------------------------------

class BrowserAgent(BaseAgent):
    name = "browser"
    description = "Controls browser automation: navigation, form filling, content extraction, multi-step research"
    responsibilities = [
        "navigate to URLs",
        "fill forms and click elements",
        "extract page content and metadata",
        "execute multi-step research workflows",
        "manage browser sessions and tabs",
        "enforce permission-based sandboxing",
    ]
    priority_factors = ["safety", "accuracy", "speed"]

    async def process(self, inp: AgentInput) -> AgentOutput:
        req_lower = inp.request.lower()
        steps: List[str] = []
        findings: Dict[str, Any] = {}

        steps.append("Step 1: Detect browser intent")
        browser_keywords = ["browse", "navigate", "open", "visit", "go to", "search",
                            "click", "fill", "extract", "scrape", "crawl", "research",
                            "find", "look up", "check", "load page", "url", "http"]
        detected = [w for w in browser_keywords if w in req_lower]
        findings["browser_intent"] = len(detected) > 0

        if not findings["browser_intent"]:
            return self._reject("No browser-related intent detected")

        steps.append("Step 2: Classify interaction level")
        passive = ["browse", "open", "visit", "go to", "load page"]
        active = ["click", "fill", "extract", "scrape", "search", "check"]
        destructive = ["delete", "remove", "modify", "change"]
        has_passive = any(w in req_lower for w in passive)
        has_active = any(w in req_lower for w in active)
        has_destructive = any(w in req_lower for w in destructive)
        if has_destructive:
            findings["interaction_level"] = "destructive"
            risk = 0.35
        elif has_active:
            findings["interaction_level"] = "active"
            risk = 0.20
        else:
            findings["interaction_level"] = "passive"
            risk = 0.08

        steps.append("Step 3: Determine browser action")
        actions = []
        if "navigate" in req_lower or "open" in req_lower or "go to" in req_lower or "visit" in req_lower:
            actions.append("navigate")
        if "fill" in req_lower or "type" in req_lower:
            actions.append("fill_form")
        if "click" in req_lower:
            actions.append("click")
        if "extract" in req_lower or "scrape" in req_lower:
            actions.append("extract_content")
        if "search" in req_lower:
            actions.append("search")
        if "research" in req_lower or "multi" in req_lower:
            actions.append("multi_step_research")
        if "screenshot" in req_lower:
            actions.append("screenshot")
        findings["actions"] = actions

        return self._output(
            recommendation=f"Execute browser {', '.join(actions)} in {findings['interaction_level']} mode",
            reasoning="\n".join(steps) + f"\n\nFindings: {findings}",
            confidence=0.88,
            risk_score=risk,
            efficiency_score=0.85,
            dependencies=["research"] if "research" in actions else [],
        )


# ---------------------------------------------------------------------------
# Agent: Voice
# ---------------------------------------------------------------------------

class VoiceAgent(BaseAgent):
    name = "voice"
    description = "Handles speech-to-text, text-to-speech, voice personality management, AI Orb state"
    responsibilities = [
        "convert speech to text (STT)",
        "generate speech from text (TTS)",
        "manage voice personalities and tones",
        "control AI Orb visual state",
        "stream audio responses",
        "enforce local-first audio processing",
    ]
    priority_factors = ["latency", "clarity", "privacy"]

    async def process(self, inp: AgentInput) -> AgentOutput:
        req_lower = inp.request.lower()
        steps: List[str] = []
        findings: Dict[str, Any] = {}

        steps.append("Step 1: Detect voice intent")
        voice_keywords = ["speak", "say", "read aloud", "listen", "voice", "talk",
                          "pronounce", "narrate", "audio", "speech", "transcribe",
                          "dictate", "record", "microphone", "orb", "personality"]
        detected = [w for w in voice_keywords if w in req_lower]
        findings["voice_intent"] = len(detected) > 0

        if not findings["voice_intent"]:
            return self._reject("No voice-related intent detected")

        steps.append("Step 2: Classify voice operation type")
        if any(w in req_lower for w in ["transcribe", "dictate", "record", "speech to text", "stt"]):
            findings["operation"] = "stt"
        elif any(w in req_lower for w in ["speak", "say", "read aloud", "text to speech", "tts", "narrate"]):
            findings["operation"] = "tts"
        else:
            findings["operation"] = "tts"
            detected.append("speak")

        steps.append("Step 3: Check personality selection")
        personalities = ["neutral", "warm", "professional", "energetic", "calm",
                         "socratic", "mentor", "friend"]
        selected = [p for p in personalities if p in req_lower]
        findings["personality"] = selected[0] if selected else "neutral"

        steps.append("Step 4: Determine delivery mode")
        if "orb" in req_lower or "visualize" in req_lower:
            findings["orb_state"] = "active"
        else:
            findings["orb_state"] = "idle"

        return self._output(
            recommendation=f"Execute {findings['operation']} with {findings['personality']} personality (orb: {findings['orb_state']})",
            reasoning="\n".join(steps) + f"\n\nFindings: {findings}",
            confidence=0.90,
            risk_score=0.10,
            efficiency_score=0.95,
        )


# ---------------------------------------------------------------------------
# Agent: Metasearch
# ---------------------------------------------------------------------------

class MetasearchAgent(BaseAgent):
    name = "metasearch"
    description = "Aggregates results across 15+ search engines: web, internal memory, knowledge graph, GitHub, and more"
    responsibilities = [
        "search across web search engines",
        "search internal memory and knowledge graph",
        "search GitHub and documentation sources",
        "deduplicate and rank results",
        "provide unified search results",
        "cache frequent queries",
    ]
    priority_factors = ["accuracy", "comprehensiveness", "speed"]

    async def process(self, inp: AgentInput) -> AgentOutput:
        req_lower = inp.request.lower()
        steps: List[str] = []
        findings: Dict[str, Any] = {}

        steps.append("Step 1: Detect search intent")
        search_keywords = ["search", "find", "lookup", "look up", "query", "seek",
                           "what is", "who is", "tell me about", "information on",
                           "results for", "search for", "find me"]
        detected = [w for w in search_keywords if w in req_lower]
        findings["search_intent"] = len(detected) > 0

        if not findings["search_intent"]:
            return self._reject("No search-related intent detected")

        steps.append("Step 2: Determine search scope")
        if any(w in req_lower for w in ["github", "code", "repository", "repo"]):
            findings["scope"] = "github"
        elif any(w in req_lower for w in ["memory", "remember", "note", "workspace"]):
            findings["scope"] = "internal"
        elif any(w in req_lower for w in ["graph", "relation", "concept", "knowledge"]):
            findings["scope"] = "knowledge_graph"
        else:
            findings["scope"] = "web"

        steps.append("Step 3: Select engines based on scope")
        if findings["scope"] == "github":
            findings["engines"] = ["github"]
        elif findings["scope"] == "internal":
            findings["engines"] = ["memory", "knowledge", "workspace"]
        elif findings["scope"] == "knowledge_graph":
            findings["engines"] = ["knowledge_graph"]
        else:
            findings["engines"] = ["duckduckgo", "wikipedia", "brave", "github", "reddit"]

        return self._output(
            recommendation=f"Search {findings['scope']} across {', '.join(findings['engines'])} engines",
            reasoning="\n".join(steps) + f"\n\nFindings: {findings}",
            confidence=0.92,
            risk_score=0.05,
            efficiency_score=0.90,
            dependencies=["research"],
        )


# ---------------------------------------------------------------------------
# Agent Registry
# ---------------------------------------------------------------------------

AGENT_REGISTRY: Dict[str, BaseAgent] = {
    "study": StudyAgent(),
    "coding": CodingAgent(),
    "learning": LearningAgent(),
    "productivity": ProductivityAgent(),
    "focus": FocusAgent(),
    "security": SecurityAgent(),
    "calendar": CalendarAgent(),
    "research": ResearchAgent(),
    "browser": BrowserAgent(),
    "voice": VoiceAgent(),
    "metasearch": MetasearchAgent(),
}

AGENT_DESCRIPTIONS: Dict[str, AgentInfo] = {
    name: AgentInfo(
        name=agent.name,
        description=agent.description,
        responsibilities=agent.responsibilities,
        priority_factors=agent.priority_factors,
    )
    for name, agent in AGENT_REGISTRY.items()
}

# ---------------------------------------------------------------------------
# Mode Weighting System
# ---------------------------------------------------------------------------

MODE_AGENT_WEIGHTS: Dict[SystemMode, Dict[str, float]] = {
    SystemMode.normal: {
        "productivity": 1.2,
        "study": 1.0,
        "coding": 1.0,
        "learning": 1.0,
        "research": 1.0,
        "focus": 0.7,
        "security": 1.0,
        "calendar": 0.9,
    },
    SystemMode.focus: {
        "focus": 1.2,
        "productivity": 1.1,
        "security": 1.1,
        "study": 1.0,
        "coding": 0.9,
        "learning": 0.9,
        "research": 0.9,
        "calendar": 0.7,
    },
    SystemMode.deep_focus: {
        "focus": 1.5,
        "security": 1.3,
        "productivity": 1.0,
        "study": 0.9,
        "coding": 0.8,
        "learning": 0.8,
        "research": 0.7,
        "calendar": 0.5,
    },
    SystemMode.lock: {
        "security": 1.5,
        "focus": 1.3,
        "productivity": 0.8,
        "study": 0.8,
        "coding": 0.7,
        "learning": 0.7,
        "research": 0.7,
        "calendar": 0.5,
    },
}

WORKSPACE_AGENT_WEIGHTS: Dict[str, Dict[str, float]] = {
    "study": {"study": 1.3, "learning": 1.2, "research": 1.1},
    "coding": {"coding": 1.3, "research": 1.1, "security": 1.1},
    "learning": {"learning": 1.3, "study": 1.2, "research": 1.1},
    "productivity": {"productivity": 1.3, "calendar": 1.1, "focus": 1.1},
    "research": {"research": 1.3, "learning": 1.2},
    "general": {"research": 1.0, "productivity": 1.0, "security": 1.0},
}

WORKSPACE_AGENT_MAP: Dict[str, List[str]] = {
    "study": ["study", "learning", "productivity", "focus", "research"],
    "coding": ["coding", "research", "productivity", "focus", "security"],
    "learning": ["learning", "study", "research", "productivity"],
    "productivity": ["productivity", "calendar", "focus", "research"],
    "research": ["research", "learning", "study", "productivity"],
    "general": ["research", "productivity", "focus", "security"],
}

# ---------------------------------------------------------------------------
# Agent Coordinator
# ---------------------------------------------------------------------------

class AgentCoordinator:
    @staticmethod
    def select_agents(request: str, workspace: Optional[str] = None, explicit: Optional[List[str]] = None) -> List[str]:
        if explicit:
            valid = [a for a in explicit if a in AGENT_REGISTRY]
            if len(valid) > 7:
                logger.warning("Requested %d agents, limiting to first 7", len(valid))
                valid = valid[:7]
            return valid

        req_lower = request.lower()
        candidate_agents: List[str] = []

        domain_signals = {
            "study": ["study", "learn", "quiz", "flashcard", "exam", "review", "memorize", "grade", "academic"],
            "coding": ["code", "debug", "program", "algorithm", "function", "api", "implement", "test", "script", "bug"],
            "learning": ["learn", "understand", "concept", "knowledge", "skill", "tutorial", "course", "resource", "topic"],
            "productivity": ["task", "todo", "schedule", "priority", "deadline", "organize", "plan", "workflow"],
            "focus": ["focus", "distract", "concentrate", "break", "interrupt", "attention", "noise", "block"],
            "security": ["security", "safe", "threat", "malicious", "virus", "permission", "access", "protect"],
            "calendar": ["calendar", "event", "meeting", "schedule", "appointment", "remind", "deadline", "date"],
            "research": ["what", "why", "how", "research", "search", "find", "lookup", "investigate", "analyze", "source"],
        }

        scores: Dict[str, float] = {}
        for agent_name, signals in domain_signals.items():
            score = sum(2 if f" {s} " in f" {req_lower} " else (1 if s in req_lower else 0) for s in signals)
            if score > 0:
                scores[agent_name] = score

        if not scores:
            return ["research", "productivity", "focus", "security"]

        sorted_agents = sorted(scores, key=scores.get, reverse=True)
        candidate_agents = sorted_agents[:7]

        ws_agents = WORKSPACE_AGENT_MAP.get(workspace or "general", [])
        for a in ws_agents:
            if a not in candidate_agents and len(candidate_agents) < 7:
                candidate_agents.append(a)
            if len(candidate_agents) >= 7:
                break

        return candidate_agents[:7]

    @staticmethod
    def detect_redundancy(request: str, selected: List[str]) -> Dict[str, Any]:
        overlaps = {
            ("study", "learning"): "Study and Learning agents overlap on educational content",
            ("coding", "learning"): "Coding and Learning agents overlap on technical learning",
            ("productivity", "calendar"): "Productivity and Calendar agents overlap on scheduling",
            ("research", "learning"): "Research and Learning agents overlap on information synthesis",
        }
        redundancies = []
        for (a, b), reason in overlaps.items():
            if a in selected and b in selected:
                redundancies.append({"agents": [a, b], "reason": reason})
        return {
            "redundancies_detected": len(redundancies),
            "details": redundancies,
            "selected_count": len(selected),
        }

    async def run_agents(
        self,
        agents: List[str],
        inp: AgentInput,
    ) -> List[AgentOutput]:
        agent_instances = [AGENT_REGISTRY[name] for name in agents if name in AGENT_REGISTRY]
        if not agent_instances:
            raise HTTPException(status_code=400, detail="No valid agents specified")

        async def run_with_fallback(agent: BaseAgent) -> AgentOutput:
            try:
                return await agent.process(inp)
            except Exception as exc:
                logger.exception("Agent '%s' failed", agent.name)
                return AgentOutput(
                    agent_name=agent.name,
                    recommendation="Error during agent processing",
                    reasoning=f"Agent raised exception: {exc}",
                    confidence=0.0,
                    risk_score=1.0,
                    efficiency_score=0.0,
                )

        tasks = [run_with_fallback(a) for a in agent_instances]
        return await asyncio.gather(*tasks)

    @staticmethod
    def resolve_conflicts(
        outputs: List[AgentOutput],
        strategy: ConflictStrategy,
        mode: SystemMode,
        workspace: Optional[str],
    ) -> List[AgentOutput]:
        if len(outputs) <= 1:
            return outputs

        mode_weights = MODE_AGENT_WEIGHTS.get(mode, {})
        ws_weights = WORKSPACE_AGENT_WEIGHTS.get(workspace or "general", {})

        if strategy == ConflictStrategy.confidence:
            return sorted(outputs, key=lambda o: o.confidence, reverse=True)

        if strategy == ConflictStrategy.risk_averse:
            return sorted(outputs, key=lambda o: (o.risk_score, -o.confidence))

        if strategy == ConflictStrategy.mode_rules:
            prioritized = []
            if mode == SystemMode.lock:
                prioritized = sorted(outputs, key=lambda o: (
                    -mode_weights.get(o.agent_name, 1.0),
                    -o.confidence,
                ))
            elif mode == SystemMode.deep_focus:
                prioritized = sorted(outputs, key=lambda o: (
                    -mode_weights.get(o.agent_name, 1.0),
                    -o.efficiency_score,
                ))
            else:
                prioritized = sorted(outputs, key=lambda o: (
                    -mode_weights.get(o.agent_name, 1.0),
                    -o.confidence,
                ))
            return prioritized

        if strategy == ConflictStrategy.weighted:
            scored = []
            for o in outputs:
                weight = mode_weights.get(o.agent_name, 1.0)
                weight *= ws_weights.get(o.agent_name, 1.0)
                composite = (o.confidence * weight * 0.5) - (o.risk_score * 0.3) + (o.efficiency_score * 0.2)
                scored.append((composite, o))

            scored.sort(key=lambda x: x[0], reverse=True)
            return [o for _, o in scored]

        return outputs


# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="ICHIN OS Service 2 — AI Agent System",
    version="1.0.0",
    description="8-agent reasoning system hosted on port 8012",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

coordinator = AgentCoordinator()
_start_time = time.monotonic()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        service="ichin-agents",
        version="1.0.0",
        uptime=time.monotonic() - _start_time,
        agent_count=len(AGENT_REGISTRY),
    )


@app.get("/agents", response_model=List[AgentInfo])
async def list_agents():
    return list(AGENT_DESCRIPTIONS.values())


@app.get("/agents/{agent_name}", response_model=AgentInfo)
async def get_agent(agent_name: str):
    agent = AGENT_DESCRIPTIONS.get(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    return agent


@app.post("/agents/{agent_name}/reason", response_model=AgentOutput)
async def reason_single(agent_name: str, body: ReasonRequest):
    agent = AGENT_REGISTRY.get(agent_name)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")

    inp = AgentInput(
        request=body.request,
        workspace=body.workspace,
        mode=body.mode,
        memory_slice=body.memory_slice,
        agent_outputs=body.agent_outputs,
    )
    try:
        return await agent.process(inp)
    except Exception as exc:
        logger.exception("Agent '%s' processing failed", agent_name)
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/agents/orchestrate")
async def orchestrate(body: OrchestrateRequest):
    try:
        agent_names = coordinator.select_agents(body.request, body.workspace, body.agents)
        if not agent_names:
            raise HTTPException(status_code=400, detail="No agents could be selected for this request")

        redundancy = coordinator.detect_redundancy(body.request, agent_names)

        inp = AgentInput(
            request=body.request,
            workspace=body.workspace,
            mode=body.mode,
            memory_slice=body.memory_slice,
        )

        outputs = await coordinator.run_agents(agent_names, inp)

        resolved = coordinator.resolve_conflicts(
            outputs,
            strategy=ConflictStrategy.weighted,
            mode=body.mode,
            workspace=body.workspace,
        )

        return {
            "agents_used": agent_names,
            "outputs": [o.model_dump() for o in outputs],
            "resolved_order": [o.agent_name for o in resolved],
            "redundancy_analysis": redundancy,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Orchestration failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/agents/conflict-resolve")
async def conflict_resolve(body: ConflictResolveRequest):
    try:
        resolved = coordinator.resolve_conflicts(
            body.outputs,
            strategy=body.strategy,
            mode=body.mode,
            workspace=body.workspace,
        )

        return {
            "strategy_used": body.strategy.value,
            "mode": body.mode.value,
            "workspace": body.workspace,
            "resolved_outputs": [o.model_dump() for o in resolved],
            "winner": resolved[0].model_dump() if resolved else None,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as exc:
        logger.exception("Conflict resolution failed")
        raise HTTPException(status_code=500, detail=str(exc))


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8012, reload=True)
