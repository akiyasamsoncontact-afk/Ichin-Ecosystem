import os
import time
import mimetypes

DEFAULT_CACHE_TTL = 300
STATIC_DIRS = {}


class StaticCache:
    def __init__(self):
        self._entries = {}

    def get(self, path):
        entry = self._entries.get(path)
        if entry and time.time() < entry["expiry"]:
            return entry["data"], entry["mime"]
        return None

    def set(self, path, data, mime, ttl=DEFAULT_CACHE_TTL):
        self._entries[path] = {
            "data": data,
            "mime": mime,
            "expiry": time.time() + ttl,
        }

    def invalidate(self, path_prefix):
        keys = [k for k in self._entries if k.startswith(path_prefix)]
        for k in keys:
            del self._entries[k]


class StaticServer:
    def __init__(self):
        self.cache = StaticCache()
        self._dirs = {}

    def mount(self, app_name, path):
        self._dirs[app_name] = path

    def serve(self, app_name, file_path):
        base = self._dirs.get(app_name)
        if not base:
            return None

        safe_path = os.path.normpath(file_path).lstrip("/")
        full_path = os.path.join(base, safe_path)

        if not full_path.startswith(os.path.normpath(base)):
            return None

        if not os.path.isfile(full_path):
            return None

        cache_key = f"{app_name}:{file_path}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        with open(full_path, "rb") as f:
            data = f.read()

        mime, _ = mimetypes.guess_type(file_path)
        mime = mime or "application/octet-stream"

        if full_path.endswith(".ichin"):
            mime = "text/x-ichin"

        self.cache.set(cache_key, data, mime)
        return data, mime
