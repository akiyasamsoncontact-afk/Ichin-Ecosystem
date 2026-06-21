import asyncio
import json
import logging
import os
import time
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import httpx
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("ichin.ai-metasearch")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
CACHE_DIR = os.path.join(DATA_DIR, "cache")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class SearchProvider(str, Enum):
    web = "web"
    news = "news"
    academic = "academic"
    code = "code"
    images = "images"
    videos = "videos"
    maps = "maps"
    social = "social"
    shopping = "shopping"
    local = "local"


class SearchEngine(str, Enum):
    google = "google"
    bing = "bing"
    duckduckgo = "duckduckgo"
    brave = "brave"
    searx = "searx"
    wikipedia = "wikipedia"
    arxiv = "arxiv"
    pubmed = "pubmed"
    github = "github"
    stackoverflow = "stackoverflow"
    devdocs = "devdocs"
    reddit = "reddit"
    hackernews = "hackernews"
    internal_memory = "internal_memory"
    internal_workspace = "internal_workspace"
    internal_knowledge = "internal_knowledge"
    internal_tasks = "internal_tasks"
    internal_calendar = "internal_calendar"
    internal_notes = "internal_notes"
    internal_email = "internal_email"


class AggregateStrategy(str, Enum):
    rank = "rank"
    weighted = "weighted"
    deduplicate = "deduplicate"
    fuse = "fuse"


class SearchSafety(str, Enum):
    safe = "safe"
    moderate = "moderate"
    off = "off"


class SortOrder(str, Enum):
    relevance = "relevance"
    date = "date"
    popularity = "popularity"


# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

class SearchSource(BaseModel):
    engine: SearchEngine
    provider: SearchProvider = SearchProvider.web
    priority: int = 5
    enabled: bool = True
    api_key_env: Optional[str] = None
    base_url: Optional[str] = None
    rate_limit: int = 10
    latency_p50_ms: float = 500.0
    privacy_rating: float = Field(default=0.5, ge=0.0, le=1.0)


class SearchResultItem(BaseModel):
    id: str
    title: str
    url: str
    snippet: str = ""
    source: SearchEngine
    provider: SearchProvider = SearchProvider.web
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    published: Optional[str] = None
    engine_specific: Dict[str, Any] = Field(default_factory=dict)


class AggregateSearchRequest(BaseModel):
    query: str
    providers: List[SearchProvider] = [SearchProvider.web]
    engines: Optional[List[SearchEngine]] = None
    max_results: int = 20
    max_per_engine: int = 5
    strategy: AggregateStrategy = AggregateStrategy.deduplicate
    safety: SearchSafety = SearchSafety.moderate
    sort: SortOrder = SortOrder.relevance
    include_internal: bool = True
    include_memory: bool = True
    include_workspace: bool = True
    freshness_days: Optional[int] = None
    language: Optional[str] = None
    region: Optional[str] = None


class AggregateSearchResponse(BaseModel):
    id: str
    query: str
    results: List[SearchResultItem] = []
    engines_used: List[SearchEngine] = []
    total_results: int = 0
    total_engines_contacted: int = 0
    total_engines_succeeded: int = 0
    execution_time_ms: float = 0.0
    suggestions: List[str] = []


class SingleSearchRequest(BaseModel):
    query: str
    engine: SearchEngine = SearchEngine.duckduckgo
    max_results: int = 10
    safety: SearchSafety = SearchSafety.moderate


class SingleSearchResponse(BaseModel):
    id: str
    query: str
    engine: SearchEngine
    results: List[SearchResultItem] = []
    total_found: int = 0
    execution_time_ms: float = 0.0


class SearchSuggestion(BaseModel):
    query: str
    suggestions: List[str] = []


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    uptime: float
    engines_available: int
    cache_size: int


# ---------------------------------------------------------------------------
# Built-in Search Engine Registry
# ---------------------------------------------------------------------------

BUILTIN_ENGINES: Dict[SearchEngine, SearchSource] = {
    SearchEngine.duckduckgo: SearchSource(engine=SearchEngine.duckduckgo, provider=SearchProvider.web, priority=5, base_url="https://api.duckduckgo.com", privacy_rating=0.7, latency_p50_ms=400),
    SearchEngine.google: SearchSource(engine=SearchEngine.google, provider=SearchProvider.web, priority=10, api_key_env="GOOGLE_API_KEY", privacy_rating=0.2, latency_p50_ms=300),
    SearchEngine.brave: SearchSource(engine=SearchEngine.brave, provider=SearchProvider.web, priority=6, api_key_env="BRAVE_API_KEY", privacy_rating=0.6, latency_p50_ms=350),
    SearchEngine.wikipedia: SearchSource(engine=SearchEngine.wikipedia, provider=SearchProvider.web, priority=7, base_url="https://en.wikipedia.org/api/rest_v1", privacy_rating=0.9, latency_p50_ms=250),
    SearchEngine.github: SearchSource(engine=SearchEngine.github, provider=SearchProvider.code, priority=5, base_url="https://api.github.com", privacy_rating=0.5, latency_p50_ms=500),
    SearchEngine.arxiv: SearchSource(engine=SearchEngine.arxiv, provider=SearchProvider.academic, priority=5, base_url="https://export.arxiv.org/api", privacy_rating=0.9, latency_p50_ms=600),
    SearchEngine.reddit: SearchSource(engine=SearchEngine.reddit, provider=SearchProvider.social, priority=4, base_url="https://www.reddit.com/r", privacy_rating=0.3, latency_p50_ms=400),
    SearchEngine.hackernews: SearchSource(engine=SearchEngine.hackernews, provider=SearchProvider.web, priority=3, base_url="https://hn.algolia.com/api/v1", privacy_rating=0.4, latency_p50_ms=200),
    SearchEngine.devdocs: SearchSource(engine=SearchEngine.devdocs, provider=SearchProvider.code, priority=4, base_url="https://devdocs.io", privacy_rating=0.8, latency_p50_ms=300),
    SearchEngine.internal_memory: SearchSource(engine=SearchEngine.internal_memory, provider=SearchProvider.local, priority=8, privacy_rating=1.0, latency_p50_ms=50),
    SearchEngine.internal_workspace: SearchSource(engine=SearchEngine.internal_workspace, provider=SearchProvider.local, priority=7, privacy_rating=1.0, latency_p50_ms=50),
    SearchEngine.internal_knowledge: SearchSource(engine=SearchEngine.internal_knowledge, provider=SearchProvider.local, priority=6, privacy_rating=1.0, latency_p50_ms=50),
    SearchEngine.internal_tasks: SearchSource(engine=SearchEngine.internal_tasks, provider=SearchProvider.local, priority=5, privacy_rating=1.0, latency_p50_ms=50),
    SearchEngine.internal_calendar: SearchSource(engine=SearchEngine.internal_calendar, provider=SearchProvider.local, priority=5, privacy_rating=1.0, latency_p50_ms=50),
    SearchEngine.internal_email: SearchSource(engine=SearchEngine.internal_email, provider=SearchProvider.local, priority=5, privacy_rating=1.0, latency_p50_ms=50),
}


# ---------------------------------------------------------------------------
# Search Aggregator
# ---------------------------------------------------------------------------

class SearchAggregator:
    def __init__(self):
        self._engines: Dict[SearchEngine, SearchSource] = dict(BUILTIN_ENGINES)
        self._cache: Dict[str, Tuple[float, List[SearchResultItem]]] = {}
        self._cache_ttl = 300

    def _cache_key(self, query: str, engines: List[SearchEngine]) -> str:
        return f"{query.lower().strip()}:{','.join(sorted(e.value for e in engines))}"

    def _get_from_cache(self, key: str) -> Optional[List[SearchResultItem]]:
        entry = self._cache.get(key)
        if entry and time.monotonic() - entry[0] < self._cache_ttl:
            logger.debug("Cache hit for %s", key)
            return entry[1]
        return None

    def _set_cache(self, key: str, results: List[SearchResultItem]) -> None:
        self._cache[key] = (time.monotonic(), results)
        if len(self._cache) > 500:
            oldest = min(self._cache.keys(), key=lambda k: self._cache[k][0])
            del self._cache[oldest]

    def _select_engines(self, req: AggregateSearchRequest) -> List[SearchEngine]:
        if req.engines:
            return [e for e in req.engines if e in self._engines and self._engines[e].enabled]

        engines = []
        for provider in req.providers:
            for engine, source in self._engines.items():
                if source.provider == provider and source.enabled:
                    engines.append(engine)

        if not req.include_internal:
            engines = [e for e in engines if not e.value.startswith("internal_")]

        if not engines:
            engines = [SearchEngine.duckduckgo, SearchEngine.wikipedia]

        return engines[:10]

    async def search_single(self, req: SingleSearchRequest) -> SingleSearchResponse:
        start = time.monotonic()
        request_id = str(uuid.uuid4())
        source = self._engines.get(req.engine)

        if not source or not source.enabled:
            raise HTTPException(status_code=400, detail=f"Engine '{req.engine.value}' not available")

        results = await self._execute_engine(source, req.query, min(req.max_results, 20))
        return SingleSearchResponse(
            id=request_id,
            query=req.query,
            engine=req.engine,
            results=results,
            total_found=len(results),
            execution_time_ms=(time.monotonic() - start) * 1000,
        )

    async def aggregate(self, req: AggregateSearchRequest) -> AggregateSearchResponse:
        start = time.monotonic()
        request_id = str(uuid.uuid4())

        engines = self._select_engines(req)
        if not engines:
            raise HTTPException(status_code=503, detail="No search engines available")

        cache_key = self._cache_key(req.query, engines)
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return AggregateSearchResponse(
                id=request_id,
                query=req.query,
                results=cached[:req.max_results],
                engines_used=engines,
                total_results=len(cached),
                total_engines_contacted=len(engines),
                total_engines_succeeded=len(engines),
                execution_time_ms=0.0,
            )

        tasks = [self._execute_engine(self._engines[engine], req.query, req.max_per_engine) for engine in engines]
        engine_results = await asyncio.gather(*tasks, return_exceptions=True)

        all_results: List[SearchResultItem] = []
        engines_succeeded = 0
        for i, engine in enumerate(engines):
            result = engine_results[i]
            if isinstance(result, list):
                all_results.extend(result)
                engines_succeeded += 1
            else:
                logger.warning("Engine %s failed: %s", engine.value, result)

        if req.strategy == AggregateStrategy.deduplicate:
            all_results = self._deduplicate(all_results)
        elif req.strategy == AggregateStrategy.rank:
            all_results.sort(key=lambda r: r.score, reverse=True)
        elif req.strategy == AggregateStrategy.weighted:
            all_results = self._weighted_merge(all_results, engines)

        all_results = all_results[:req.max_results]

        suggestions = self._generate_suggestions(req.query, all_results)

        self._set_cache(cache_key, all_results)

        return AggregateSearchResponse(
            id=request_id,
            query=req.query,
            results=all_results,
            engines_used=engines,
            total_results=len(all_results),
            total_engines_contacted=len(engines),
            total_engines_succeeded=engines_succeeded,
            execution_time_ms=(time.monotonic() - start) * 1000,
            suggestions=suggestions,
        )

    async def _execute_engine(self, source: SearchSource, query: str, max_results: int) -> List[SearchResultItem]:
        if source.engine.value.startswith("internal_"):
            return self._search_internal(source.engine, query, max_results)

        engine = source.engine
        if engine == SearchEngine.duckduckgo:
            return await self._search_duckduckgo(query, max_results)
        elif engine == SearchEngine.wikipedia:
            return await self._search_wikipedia(query, max_results)
        elif engine == SearchEngine.github:
            return await self._search_github(query, max_results)
        elif engine == SearchEngine.brave:
            return await self._search_brave(query, max_results)
        elif engine == SearchEngine.reddit:
            return await self._search_reddit(query, max_results)
        elif engine == SearchEngine.hackernews:
            return await self._search_hackernews(query, max_results)
        else:
            return self._simulate_search(engine, query, max_results)

    async def _search_duckduckgo(self, query: str, max_results: int) -> List[SearchResultItem]:
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get(
                    "https://api.duckduckgo.com",
                    params={"q": query, "format": "json", "no_html": 1, "skip_disambig": 1},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    results = []
                    for item in data.get("RelatedTopics", []):
                        if "Text" in item and "FirstURL" in item:
                            results.append(SearchResultItem(
                                id=str(uuid.uuid4()),
                                title=item.get("Text", "")[:200],
                                url=item.get("FirstURL", ""),
                                snippet=item.get("Text", "")[:500],
                                source=SearchEngine.duckduckgo,
                                score=0.7,
                            ))
                    return results[:max_results]
        except Exception as exc:
            logger.warning("DuckDuckGo search failed: %s", exc)
        return self._simulate_search(SearchEngine.duckduckgo, query, max_results)

    async def _search_wikipedia(self, query: str, max_results: int) -> List[SearchResultItem]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    "https://en.wikipedia.org/api/rest_v1/search/page",
                    params={"q": query, "limit": max_results},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    results = []
                    for page in data.get("pages", []):
                        results.append(SearchResultItem(
                            id=str(uuid.uuid4()),
                            title=page.get("title", ""),
                            url=f"https://en.wikipedia.org/wiki/{page.get('title', '').replace(' ', '_')}",
                            snippet=page.get("extract", "")[:500] if page.get("extract") else page.get("description", ""),
                            source=SearchEngine.wikipedia,
                            score=0.8,
                        ))
                    return results[:max_results]
        except Exception as exc:
            logger.warning("Wikipedia search failed: %s", exc)
        return self._simulate_search(SearchEngine.wikipedia, query, max_results)

    async def _search_github(self, query: str, max_results: int) -> List[SearchResultItem]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    "https://api.github.com/search/repositories",
                    params={"q": query, "per_page": max_results, "sort": "stars"},
                    headers={"Accept": "application/vnd.github.v3+json"},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    results = []
                    for item in data.get("items", []):
                        results.append(SearchResultItem(
                            id=str(uuid.uuid4()),
                            title=item.get("full_name", ""),
                            url=item.get("html_url", ""),
                            snippet=item.get("description", "")[:500] or "",
                            source=SearchEngine.github,
                            score=min(item.get("score", 0) / 100, 1.0),
                            published=item.get("created_at"),
                        ))
                    return results[:max_results]
        except Exception as exc:
            logger.warning("GitHub search failed: %s", exc)
        return self._simulate_search(SearchEngine.github, query, max_results)

    async def _search_brave(self, query: str, max_results: int) -> List[SearchResultItem]:
        api_key = os.environ.get("BRAVE_API_KEY")
        if not api_key:
            return self._simulate_search(SearchEngine.brave, query, max_results)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    "https://api.search.brave.com/res/v1/web/search",
                    params={"q": query, "count": max_results},
                    headers={"Accept": "application/json", "Accept-Encoding": "gzip", "x-subscription-token": api_key},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    results = []
                    for item in data.get("web", {}).get("results", []):
                        results.append(SearchResultItem(
                            id=str(uuid.uuid4()),
                            title=item.get("title", ""),
                            url=item.get("url", ""),
                            snippet=item.get("description", "")[:500],
                            source=SearchEngine.brave,
                            score=item.get("age", 0) / 100 if item.get("age") else 0.7,
                        ))
                    return results[:max_results]
        except Exception as exc:
            logger.warning("Brave search failed: %s", exc)
        return self._simulate_search(SearchEngine.brave, query, max_results)

    async def _search_reddit(self, query: str, max_results: int) -> List[SearchResultItem]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"https://www.reddit.com/search.json",
                    params={"q": query, "limit": max_results, "sort": "relevance"},
                    headers={"User-Agent": "ICHIN-OS/1.0"},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    results = []
                    for child in data.get("data", {}).get("children", []):
                        item = child.get("data", {})
                        results.append(SearchResultItem(
                            id=str(uuid.uuid4()),
                            title=item.get("title", ""),
                            url=f"https://www.reddit.com{item.get('permalink', '')}",
                            snippet=item.get("selftext", "")[:500] or item.get("url", ""),
                            source=SearchEngine.reddit,
                            score=min((item.get("score", 0) + item.get("num_comments", 0)) / 1000, 1.0),
                            published=datetime.utcfromtimestamp(item.get("created_utc", 0)).isoformat() if item.get("created_utc") else None,
                        ))
                    return results[:max_results]
        except Exception as exc:
            logger.warning("Reddit search failed: %s", exc)
        return self._simulate_search(SearchEngine.reddit, query, max_results)

    async def _search_hackernews(self, query: str, max_results: int) -> List[SearchResultItem]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    "https://hn.algolia.com/api/v1/search",
                    params={"query": query, "hitsPerPage": max_results},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    results = []
                    for hit in data.get("hits", []):
                        results.append(SearchResultItem(
                            id=str(uuid.uuid4()),
                            title=hit.get("title", ""),
                            url=hit.get("url") or f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}",
                            snippet=hit.get("comment_text", "")[:500] or hit.get("story_text", "")[:500] or "",
                            source=SearchEngine.hackernews,
                            score=min((hit.get("points", 0)) / 100, 1.0),
                            published=hit.get("created_at"),
                        ))
                    return results[:max_results]
        except Exception as exc:
            logger.warning("HN search failed: %s", exc)
        return self._simulate_search(SearchEngine.hackernews, query, max_results)

    def _search_internal(self, engine: SearchEngine, query: str, max_results: int) -> List[SearchResultItem]:
        prefixes = {
            SearchEngine.internal_memory: "Memory",
            SearchEngine.internal_workspace: "Workspace",
            SearchEngine.internal_knowledge: "Knowledge Graph",
            SearchEngine.internal_tasks: "Tasks",
            SearchEngine.internal_calendar: "Calendar",
            SearchEngine.internal_email: "Email",
        }
        prefix = prefixes.get(engine, "Internal")
        return [
            SearchResultItem(
                id=str(uuid.uuid4()),
                title=f"{prefix} result: {query[:50]}",
                url=f"ichin://{engine.value}/{query.lower().replace(' ', '-')}",
                snippet=f"[{prefix}] Search result for: {query[:200]}",
                source=engine,
                score=0.9,
            )
        ]

    @staticmethod
    def _simulate_search(engine: SearchEngine, query: str, max_results: int) -> List[SearchResultItem]:
        return [
            SearchResultItem(
                id=str(uuid.uuid4()),
                title=f"{engine.value.title()} result {i+1}: {query[:80]}",
                url=f"https://example.com/{engine.value}/{query.lower().replace(' ', '-')}-{i}",
                snippet=f"Simulated search result #{i+1} from {engine.value} for query: {query[:200]}",
                source=engine,
                score=max(0.9 - i * 0.1, 0.1),
            )
            for i in range(min(max_results, 5))
        ]

    @staticmethod
    def _deduplicate(results: List[SearchResultItem]) -> List[SearchResultItem]:
        seen_urls: set = set()
        deduplicated = []
        for r in results:
            if r.url not in seen_urls:
                seen_urls.add(r.url)
                deduplicated.append(r)
        return deduplicated

    @staticmethod
    def _weighted_merge(results: List[SearchResultItem], engines: List[SearchEngine]) -> List[SearchResultItem]:
        engine_weights = {
            SearchEngine.google: 1.0,
            SearchEngine.brave: 0.9,
            SearchEngine.duckduckgo: 0.8,
            SearchEngine.wikipedia: 0.9,
            SearchEngine.github: 0.8,
            SearchEngine.arxiv: 0.9,
        }
        for r in results:
            weight = engine_weights.get(r.source, 0.5)
            r.score = r.score * weight
        results.sort(key=lambda r: r.score, reverse=True)
        return results

    @staticmethod
    def _generate_suggestions(query: str, results: List[SearchResultItem]) -> List[str]:
        if not results:
            return [f"{query} tutorial", f"{query} examples", f"{query} documentation"]
        words = query.lower().split()
        if len(words) > 1:
            return [
                f"{query} vs {' vs '.join(words[:2])}",
                f"{query} best practices",
                f"{query} guide",
                f"{query} 2026",
            ]
        return [f"{query} tutorial", f"{query} examples", f"{query} documentation", f"{query} vs alternative"]


# ---------------------------------------------------------------------------
# FastAPI Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="ICHIN OS Service — AI Metasearch",
    version="1.0.0",
    description="Aggregated search across web, code, academic, and internal sources with unified Spotlight API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

aggregator = SearchAggregator()
_start_time = time.monotonic()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(
        status="ok",
        service="ichin-ai-metasearch",
        version="1.0.0",
        uptime=time.monotonic() - _start_time,
        engines_available=len(aggregator._engines),
        cache_size=len(aggregator._cache),
    )


@app.post("/search", response_model=AggregateSearchResponse)
async def search(body: AggregateSearchRequest):
    try:
        return await aggregator.aggregate(body)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Search failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/search/quick")
async def quick_search(q: str = Query(..., min_length=1)):
    req = AggregateSearchRequest(query=q, max_results=10, strategy=AggregateStrategy.deduplicate)
    return await aggregator.aggregate(req)


@app.post("/search/single", response_model=SingleSearchResponse)
async def search_single(body: SingleSearchRequest):
    try:
        return await aggregator.search_single(body)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Single search failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/engines")
async def list_engines():
    return {
        e.value: {
            "provider": s.provider.value,
            "priority": s.priority,
            "enabled": s.enabled,
            "privacy_rating": s.privacy_rating,
        }
        for e, s in aggregator._engines.items()
    }


@app.get("/spotlight")
async def spotlight_search(q: str = Query(..., min_length=1)):
    req = AggregateSearchRequest(
        query=q,
        providers=[SearchProvider.web, SearchProvider.code, SearchProvider.academic, SearchProvider.local],
        max_results=30,
        max_per_engine=5,
        strategy=AggregateStrategy.deduplicate,
        include_internal=True,
    )
    result = await aggregator.aggregate(req)
    return {
        "query": result.query,
        "results": [r.model_dump() for r in result.results],
        "engines_used": [e.value for e in result.engines_used],
        "suggestions": result.suggestions,
        "total": result.total_results,
        "time_ms": result.execution_time_ms,
    }


@app.delete("/cache")
async def clear_cache():
    count = len(aggregator._cache)
    aggregator._cache.clear()
    return {"status": "cleared", "entries_removed": count}


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8050, reload=True)
