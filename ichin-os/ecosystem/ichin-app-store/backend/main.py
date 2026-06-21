import json
import os
import uuid
from datetime import datetime
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
DATA_FILE = os.path.join(DATA_DIR, "store.json")
os.makedirs(DATA_DIR, exist_ok=True)

# ICHIN service endpoints
ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:8011")
APP_RUNTIME_URL = os.getenv("APP_RUNTIME_URL", "http://localhost:8015")
MEMORY_ENGINE_URL = os.getenv("MEMORY_ENGINE_URL", "http://localhost:8013")

app = FastAPI(title="ICHIN App Store API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


# ─── Models ────────────────────────────────────────────────────────────────

class Permission(BaseModel):
    id: str
    name: str
    description: str
    granted: bool = False


class AppManifest(BaseModel):
    id: str
    name: str
    description: str
    version: str
    author: str
    icon: str
    category: str
    permissions: list[Permission]
    aiCompatibility: float
    workspaceIntegration: list[str]
    rating: float = 0.0
    aiTested: bool = False
    appType: str = "native"


class AppSubmission(BaseModel):
    name: str
    description: str
    version: str
    author: str
    icon: str = "default"
    category: str
    permissions: list[Permission]
    aiCompatibility: float = 0.0
    workspaceIntegration: list[str] = []
    appType: str = "native"
    manifestUrl: str = ""


class AppReview(BaseModel):
    id: str
    appId: str
    status: str
    securityScore: float
    sandboxScore: float
    performanceScore: float
    aiScore: float
    overallScore: float
    issues: list[str]
    timestamp: float


class AppRating(BaseModel):
    id: str
    appId: str
    userId: str
    score: int
    comment: str = ""
    timestamp: float


class InstallRecord(BaseModel):
    id: str
    appId: str
    installedAt: float
    status: str = "running"
    runtimeAppId: Optional[str] = None
    config: dict = {}
    lastUsed: Optional[float] = None


class AppCategory(BaseModel):
    id: str
    name: str
    description: str
    icon: str


class StoredApp(BaseModel):
    manifest: AppManifest
    screenshots: list[str] = []
    reviews: list[AppReview] = []
    ratings: list[AppRating] = []
    installs: int = 0


class StoreData(BaseModel):
    apps: dict[str, StoredApp] = {}
    installed: dict[str, InstallRecord] = {}
    categories: list[AppCategory] = []
    submissions: list[AppSubmission] = []


# ─── In-memory store with JSON persistence ─────────────────────────────────

store: StoreData = StoreData(
    categories=[
        AppCategory(id="productivity", name="Productivity", description="Boost your workflow", icon="zap"),
        AppCategory(id="study", name="Study Tools", description="Learn effectively", icon="book"),
        AppCategory(id="coding", name="Coding Tools", description="Development utilities", icon="code"),
        AppCategory(id="ai-agents", name="AI Agents", description="Intelligent assistants", icon="brain"),
        AppCategory(id="learning", name="Learning Modules", description="Expand knowledge", icon="graduation-cap"),
        AppCategory(id="system", name="System Extensions", description="Extend Ichin OS", icon="puzzle"),
    ]
)


def _save():
    with open(DATA_FILE, "w") as f:
        json.dump(store.model_dump(), f, indent=2, default=str)


def _load():
    global store
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            data = json.load(f)
            store = StoreData(**data)


_load()


@app.on_event("shutdown")
def _shutdown():
    _save()


# ─── Helpers ───────────────────────────────────────────────────────────────

def _map_permission_type(pid: str) -> str:
    mapping = {
        "AI_ACCESS": "ai_access",
        "MEMORY_READ": "memory_read",
        "FILE_ACCESS": "file_access",
        "NETWORK_ACCESS": "network_access",
        "WORKSPACE_INTEGRATION": "workspace_integration",
        "CALENDAR_ACCESS": "calendar_access",
        "NOTIFICATIONS_ACCESS": "notifications_access",
    }
    return mapping.get(pid, pid.lower())


def _map_app_type(at: str) -> str:
    mapping = {"native": "native", "web": "web", "external": "external"}
    return mapping.get(at, "native")


async def _call_app_runtime_install(manifest: AppManifest) -> Optional[str]:
    payload = {
        "manifest": {
            "name": manifest.name,
            "version": manifest.version,
            "app_type": _map_app_type(manifest.appType),
            "permissions": [
                {"type": _map_permission_type(p.id), "granted": p.granted, "user_approved": False}
                for p in manifest.permissions
            ],
            "ai_compatibility": str(manifest.aiCompatibility),
            "workspace_integration": ",".join(manifest.workspaceIntegration),
            "description": manifest.description,
        },
        "user_id": "app-store-user",
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(f"{APP_RUNTIME_URL}/app/install", json=payload)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("success"):
                return data["data"]["id"]
    return None


async def _call_app_runtime_terminate(runtime_app_id: str) -> bool:
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.post(f"{APP_RUNTIME_URL}/app/{runtime_app_id}/terminate")
        return resp.status_code == 200


async def _call_orchestrator_review(app_name: str, description: str) -> dict:
    prompt = f"Review this Ichin OS app for safety, quality, and AI compatibility.\nApp: {app_name}\nDescription: {description}"
    payload = {
        "request": prompt,
        "mode": "normal",
        "workspace": "system",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(f"{ORCHESTRATOR_URL}/orchestrate", json=payload)
        if resp.status_code == 200:
            return resp.json()
    return {"result": "", "confidence": 0.5, "agents_used": [], "risk_level": "medium"}


async def _call_memory_store(key: str, value: dict):
    payload = {"key": key, "value": value, "type": "structured", "workspace": "system"}
    async with httpx.AsyncClient(timeout=5) as client:
        try:
            await client.post(f"{MEMORY_ENGINE_URL}/memory/store", json=payload)
        except Exception:
            pass  # memory is optional


# ─── Endpoints ─────────────────────────────────────────────────────────────

@app.get("/api/store/apps")
def list_apps(
    category: Optional[str] = Query(None),
    workspace: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
):
    results = list(store.apps.values())
    if category:
        results = [a for a in results if a.manifest.category == category]
    if workspace:
        results = [a for a in results if workspace in a.manifest.workspaceIntegration]
    if search:
        q = search.lower()
        results = [a for a in results if q in a.manifest.name.lower() or q in a.manifest.description.lower()]
    return [
        {
            "id": a.manifest.id,
            "name": a.manifest.name,
            "description": a.manifest.description,
            "icon": a.manifest.icon,
            "category": a.manifest.category,
            "rating": a.manifest.rating,
            "version": a.manifest.version,
            "author": a.manifest.author,
            "aiCompatibility": a.manifest.aiCompatibility,
            "aiTested": a.manifest.aiTested,
            "installs": a.installs,
        }
        for a in results
    ]


@app.get("/api/store/apps/{app_id}")
def get_app(app_id: str):
    if app_id not in store.apps:
        raise HTTPException(404, "App not found")
    a = store.apps[app_id]
    return {
        "manifest": a.manifest.model_dump(),
        "screenshots": a.screenshots,
        "reviews": [r.model_dump() for r in a.reviews],
        "ratings": {"average": a.manifest.rating, "count": len(a.ratings)},
        "installs": a.installs,
    }


@app.post("/api/store/apps/{app_id}/install")
async def install_app(app_id: str):
    if app_id not in store.apps:
        raise HTTPException(404, "App not found")
    if app_id in store.installed:
        raise HTTPException(409, "Already installed")

    manifest = store.apps[app_id].manifest
    runtime_id = await _call_app_runtime_install(manifest)

    record = InstallRecord(
        id=str(uuid.uuid4()),
        appId=app_id,
        runtimeAppId=runtime_id,
        installedAt=datetime.now().timestamp(),
        status="running" if runtime_id else "pending",
    )
    store.installed[app_id] = record
    store.apps[app_id].installs += 1

    await _call_memory_store(f"app_install_{app_id}", {
        "app": manifest.name,
        "category": manifest.category,
        "installed_at": record.installedAt,
        "runtime_id": runtime_id,
    })

    return {
        "id": record.id,
        "appId": app_id,
        "status": record.status,
        "runtimeAppId": runtime_id,
        "permissions": [p.model_dump() for p in manifest.permissions],
    }


@app.post("/api/store/apps/{app_id}/uninstall")
async def uninstall_app(app_id: str):
    if app_id not in store.installed:
        raise HTTPException(404, "App not installed")

    record = store.installed[app_id]
    if record.runtimeAppId:
        await _call_app_runtime_terminate(record.runtimeAppId)

    del store.installed[app_id]

    await _call_memory_store(f"app_uninstall_{app_id}", {
        "app": store.apps[app_id].manifest.name if app_id in store.apps else "unknown",
        "uninstalled_at": datetime.now().timestamp(),
    })

    return {"status": "uninstalled", "appId": app_id}


@app.get("/api/store/installed")
def list_installed():
    result = []
    for app_id, rec in store.installed.items():
        if app_id in store.apps:
            a = store.apps[app_id]
            result.append({"installRecord": rec.model_dump(), "manifest": a.manifest.model_dump()})
    return result


@app.get("/api/store/categories")
def list_categories():
    return [c.model_dump() for c in store.categories]


@app.post("/api/store/apps")
def submit_app(submission: AppSubmission):
    app_id = submission.name.lower().replace(" ", "-") + "-" + str(uuid.uuid4())[:8]
    manifest = AppManifest(
        id=app_id,
        name=submission.name,
        description=submission.description,
        version=submission.version,
        author=submission.author,
        icon=submission.icon,
        category=submission.category,
        permissions=submission.permissions,
        aiCompatibility=submission.aiCompatibility,
        workspaceIntegration=submission.workspaceIntegration,
        appType=submission.appType,
    )
    store.apps[app_id] = StoredApp(manifest=manifest)
    store.submissions.append(submission)
    return {"id": app_id, "status": "submitted", "message": "App submitted for review"}


@app.post("/api/store/apps/{app_id}/review")
async def review_app(app_id: str):
    if app_id not in store.apps:
        raise HTTPException(404, "App not found")
    manifest = store.apps[app_id].manifest

    # Call orchestrator for AI-powered review
    ai_review = await _call_orchestrator_review(manifest.name, manifest.description)

    # Combine AI review with static checks
    issues = []
    security_score = 0.0
    for p in manifest.permissions:
        if p.id in ("FILE_ACCESS", "NETWORK_ACCESS"):
            security_score += 0.5
        else:
            security_score += 1.0
    security_score = min(security_score / max(len(manifest.permissions), 1), 1.0) * 10

    sandbox_score = 8.5 if manifest.permissions else 10.0

    ai_score = manifest.aiCompatibility * 10
    if manifest.aiCompatibility < 0.3:
        issues.append("Low AI compatibility")

    performance_score = 7.0
    if manifest.aiCompatibility < 0.3:
        issues.append("Consider adding AI integration")

    # Incorporate orchestrator confidence
    ai_confidence = ai_review.get("confidence", 0.5)
    if ai_confidence < 0.3:
        issues.append("Low AI review confidence")

    overall = (security_score + sandbox_score + performance_score + ai_score) / 4
    status = "approved" if overall >= 6.0 and not any("security" in i.lower() for i in issues) else "needs_review"

    review = AppReview(
        id=str(uuid.uuid4()),
        appId=app_id,
        status=status,
        securityScore=round(security_score, 1),
        sandboxScore=round(sandbox_score, 1),
        performanceScore=round(performance_score, 1),
        aiScore=round(ai_score, 1),
        overallScore=round(overall, 1),
        issues=issues,
        timestamp=datetime.now().timestamp(),
    )
    store.apps[app_id].reviews.append(review)
    manifest.aiTested = status == "approved"

    await _call_memory_store(f"app_review_{app_id}", {
        "app": manifest.name,
        "status": status,
        "overall_score": overall,
        "orchestrator_confidence": ai_confidence,
    })

    return review.model_dump()


@app.get("/api/store/apps/{app_id}/reviews")
def get_reviews(app_id: str):
    if app_id not in store.apps:
        raise HTTPException(404, "App not found")
    return [r.model_dump() for r in store.apps[app_id].reviews]


@app.post("/api/store/apps/{app_id}/rate")
def rate_app(app_id: str, rating: AppRating):
    if app_id not in store.apps:
        raise HTTPException(404, "App not found")
    r = AppRating(
        id=str(uuid.uuid4()),
        appId=app_id,
        userId=rating.userId,
        score=max(1, min(5, rating.score)),
        comment=rating.comment,
        timestamp=datetime.now().timestamp(),
    )
    store.apps[app_id].ratings.append(r)
    scores = [rat.score for rat in store.apps[app_id].ratings]
    store.apps[app_id].manifest.rating = round(sum(scores) / len(scores), 1)
    return r.model_dump()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8021)
