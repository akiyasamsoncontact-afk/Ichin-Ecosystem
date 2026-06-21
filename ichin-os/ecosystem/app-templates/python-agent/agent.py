"""ICHIN OS Python Agent Template

A template for building AI agents that integrate into the ICHIN OS
Council system. Connects to live ICHIN services:
  - Orchestrator (port 8011): /orchestrate
  - Memory Engine (port 8013): /memory/store, /memory/query
  - UI System (port 8014): /orb/notify
"""

import json
import os
from typing import Any
from urllib.request import Request, urlopen

ORCHESTRATOR_URL = os.getenv("ORCHESTRATOR_URL", "http://localhost:8011")
MEMORY_URL = os.getenv("MEMORY_URL", "http://localhost:8013")
UI_URL = os.getenv("UI_URL", "http://localhost:8014")


class IchinAgent:
    """Base class for ICHIN OS AI agents with live service integration."""

    def __init__(self, manifest_path: str = "manifest.json"):
        with open(manifest_path) as f:
            self.manifest = json.load(f)
        self.name = self.manifest["name"]
        self.id = self.manifest["id"]
        self.memory: dict[str, Any] = {}

    def _post(self, url: str, data: dict) -> dict:
        payload = json.dumps(data).encode()
        req = Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        with urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())

    async def on_activate(self, context: dict[str, Any]) -> None:
        """Called when the agent is activated in a workspace."""
        self.context = context
        print(f"[{self.name}] Activated in workspace: {context.get('workspace', 'unknown')}")

    async def on_deactivate(self) -> None:
        """Called when the agent is deactivated."""
        print(f"[{self.name}] Deactivated")

    async def process_task(self, task: dict[str, Any]) -> dict[str, Any]:
        """Process a task assigned by the Orchestrator or user."""
        raise NotImplementedError("Subclasses must implement process_task")

    async def query_ai(self, prompt: str, context: dict | None = None) -> str:
        """Send a query to the ICHIN AI system via the Orchestrator."""
        payload = {
            "request": prompt,
            "mode": "normal",
            "workspace": (context or {}).get("workspace", "system"),
        }
        try:
            result = self._post(f"{ORCHESTRATOR_URL}/orchestrate", payload)
            return result.get("result", "")
        except Exception as e:
            print(f"[{self.name}] Orchestrator call failed: {e}")
            return ""

    async def read_memory(self, key: str) -> Any:
        """Read from agent memory (local cache + memory engine)."""
        if key in self.memory:
            return self.memory[key]
        try:
            result = self._post(f"{MEMORY_URL}/memory/query", {"query": key, "workspace": "system"})
            return result
        except Exception:
            return None

    async def write_memory(self, key: str, value: Any) -> None:
        """Write to agent memory (local + memory engine)."""
        self.memory[key] = value
        try:
            self._post(f"{MEMORY_URL}/memory/store", {"key": key, "value": value, "type": "pattern", "workspace": "system"})
        except Exception as e:
            print(f"[{self.name}] Memory store failed: {e}")

    async def notify(self, message: str, state: str = "active") -> None:
        """Send a notification via the Orb system."""
        print(f"[{self.name}] Orb Notification [{state}]: {message}")
        try:
            self._post(f"{UI_URL}/orb/notify", {"message": message, "state": state, "source": self.name})
        except Exception as e:
            print(f"[{self.name}] Orb notify failed: {e}")


class StudyAssistantAgent(IchinAgent):
    """Example agent: study assistant that summarizes notes."""

    async def process_task(self, task: dict[str, Any]) -> dict[str, Any]:
        action = task.get("action", "")
        if action == "summarize":
            content = task.get("content", "")
            summary = await self.query_ai(f"Summarize: {content}")
            return {"result": "success", "summary": summary}
        elif action == "quiz":
            topic = task.get("topic", "")
            return {"result": "success", "questions": [f"Question about {topic}"]}
        return {"result": "error", "message": f"Unknown action: {action}"}


if __name__ == "__main__":
    import asyncio

    async def main():
        agent = StudyAssistantAgent()
        await agent.on_activate({"workspace": "study"})
        result = await agent.process_task({
            "action": "summarize",
            "content": "ICHIN OS is an AI-native operating system...",
        })
        print(json.dumps(result, indent=2))
        await agent.on_deactivate()

    asyncio.run(main())
