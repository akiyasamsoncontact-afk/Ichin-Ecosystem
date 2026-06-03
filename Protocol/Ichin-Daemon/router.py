import re
import time


class Route:
    def __init__(self, method, pattern, handler, middleware=None):
        self.method = method.upper()
        self.handler = handler
        self.middleware = middleware or []
        self.param_names = []
        self.regex = self._compile(pattern)

    def _compile(self, pattern):
        parts = pattern.strip("/").split("/") if pattern.strip("/") else []
        regex_parts = []
        for part in parts:
            if part.startswith(":"):
                self.param_names.append(part[1:])
                regex_parts.append(r"([^/]+)")
            else:
                regex_parts.append(re.escape(part))
        pattern_str = "^/" + "/".join(regex_parts) + "$" if regex_parts else "^/$"
        return re.compile(pattern_str)

    def match(self, method, path):
        if self.method != method.upper():
            return None
        m = self.regex.match(path)
        if not m:
            return None
        params = dict(zip(self.param_names, m.groups()))
        return params


class Router:
    def __init__(self):
        self._routes = []
        self._global_middleware = []

    def add_global_middleware(self, middleware):
        self._global_middleware.append(middleware)

    def add_route(self, method, pattern, handler, middleware=None):
        self._routes.append(Route(method, pattern, handler, middleware))

    def resolve(self, method, path):
        for route in self._routes:
            params = route.match(method, path)
            if params is not None:
                return route, params
        return None, None


class MiddlewarePipeline:
    def __init__(self):
        self._middleware = []

    def use(self, middleware):
        self._middleware.append(middleware)

    def run(self, request, params, session, handler):
        context = {
            "request": request,
            "params": params,
            "session": session,
            "handler": handler,
            "response": None,
        }

        def execute(index):
            if context["response"] is not None:
                return context["response"]
            if index < len(self._middleware):
                mw = self._middleware[index]
                return mw(context, lambda: execute(index + 1))
            return handler(request, params, session)

        return execute(0)


def logging_middleware(ctx, next_fn):
    start = time.time()
    req = ctx["request"]
    method = req.get("method", "?")
    path = req.get("path", "?")
    result = next_fn()
    duration = (time.time() - start) * 1000
    status = result.get("status", result) if isinstance(result, dict) else "?"
    print(f"  [{method}] {path} → {status} ({duration:.0f}ms)")
    return result


def rate_limit_middleware(ctx, next_fn):
    session = ctx.get("session")
    if session and hasattr(session, "data"):
        hits = session.data.get("rate_hits", 0) + 1
        session.data["rate_hits"] = hits
        if hits > 100:
            return {"status": 429, "message": "TOO MANY REQUESTS",
                    "headers": {}, "body": {"error": "Rate limit exceeded"}}
    return next_fn()
