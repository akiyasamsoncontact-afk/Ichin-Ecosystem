Build a minimal, production-ready search engine for a closed ecosystem called “Ichin”.

Ichin is NOT the public internet. It is a controlled network where all websites are registered through a central registry (GurtDNS + GurtCA). There is no web crawling. All data is pre-registered and structured.

---

TECH STACK (STRICT):

Backend:
- Rust
- Axum framework

Database:
- SQLite (MVP only)

Frontend:
- Next.js (React)

No other frameworks unless absolutely necessary.

---

CORE GOAL:

Build a fast registry-based search engine that searches:
- registered sites
- pages inside sites
- metadata (tags, titles, descriptions)

---

DATA MODEL:

Site:
- id (integer)
- domain (string)
- name (string)
- description (string)
- verified (boolean)
- tags (string array)

Page:
- id (integer)
- site_id (foreign key)
- path (string)
- title (string)
- content (text)
- tags (string array)

---

SEARCH LOGIC:

When a user searches:
- Match query against:
  1. page title (highest priority)
  2. tags
  3. site name
  4. page content (lowest priority)

Ranking system:
- title match = +5
- tag match = +4
- site name match = +3
- content match = +1
- verified site bonus = +3

Return top results sorted by score.

---

API REQUIREMENT:

Create a REST API:

GET /search?q={query}

Response JSON:

{
  "query": "string",
  "results": [
    {
      "site": "domain.ichin",
      "title": "Page title",
      "path": "/path",
      "snippet": "short preview of content",
      "verified": true,
      "score": 0
    }
  ]
}

---

INDEXING SYSTEM:

- Build a simple inverted index:
  term → list of page IDs
- Store index in memory + persist in SQLite
- Update index whenever a site/page is registered or updated

---

IMPORTANT RULES:

- DO NOT implement web crawling
- DO NOT use vector embeddings or AI search
- DO NOT use external search APIs
- DO NOT over-engineer architecture
- DO NOT split into microservices

Keep it simple, deterministic, and fast.

---

OPTIONAL FEATURES (ONLY IF CORE WORKS):

- autocomplete suggestions
- tag filtering
- verified-only filter
- search caching
