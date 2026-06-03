import json
import os
import sys
import threading

APPS_DIR = None


def set_apps_dir(path):
    global APPS_DIR
    APPS_DIR = path


class Sandbox:
    def __init__(self, app_name):
        self.app_name = app_name
        self.app_dir = os.path.join(APPS_DIR, app_name) if APPS_DIR else None
        self._module = None
        self._routes = []
        self._lock = threading.Lock()

    def load(self):
        if not self.app_dir or not os.path.isdir(self.app_dir):
            return False

        route_file = os.path.join(self.app_dir, "route.json")
        main_file = os.path.join(self.app_dir, "main.py")

        if not os.path.exists(route_file):
            return False

        with open(route_file) as f:
            config = json.load(f)
        self._routes = config.get("routes", [])

        if os.path.exists(main_file):
            module_name = f"ichind_app_{self.app_name}"
            spec = None
            if module_name in sys.modules:
                del sys.modules[module_name]

            import importlib.util
            spec = importlib.util.spec_from_file_location(module_name, main_file)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = mod
                spec.loader.exec_module(mod)
                self._module = mod

        return True

    def get_routes(self):
        return list(self._routes)

    def get_handler(self, handler_name):
        if not self._module:
            return None
        return getattr(self._module, handler_name, None)

    def call(self, handler_name, request, params, session):
        handler = self.get_handler(handler_name)
        if not handler:
            return {"status": 500, "body": {"error": f"Handler not found: {handler_name}"}}
        try:
            result = handler(request, params, session)
            if isinstance(result, dict):
                return result
            return {"status": 200, "body": {"result": str(result)}}
        except Exception as e:
            return {"status": 500, "body": {"error": str(e)}}


class SandboxManager:
    def __init__(self):
        self._apps = {}
        self._lock = threading.Lock()

    def load_apps(self):
        if not APPS_DIR or not os.path.isdir(APPS_DIR):
            return []
        loaded = []
        for name in sorted(os.listdir(APPS_DIR)):
            app_dir = os.path.join(APPS_DIR, name)
            if not os.path.isdir(app_dir):
                continue
            sb = Sandbox(name)
            if sb.load():
                with self._lock:
                    self._apps[name] = sb
                loaded.append(name)
        return loaded

    def get_app(self, name):
        with self._lock:
            return self._apps.get(name)

    def reload(self, name):
        with self._lock:
            sb = Sandbox(name)
            if sb.load():
                self._apps[name] = sb
                return True
            return False
