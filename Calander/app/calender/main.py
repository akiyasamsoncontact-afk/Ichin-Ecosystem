import json
import urllib.request
import urllib.error

BACKEND_URL = "http://127.0.0.1:3002/api"


def _proxy(method, path, body=None):
    url = f"{BACKEND_URL}{path}"
    data = json.dumps(body).encode("utf-8") if body else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={"Content-Type": "application/json"} if data else {}
    )
    try:
        with urllib.request.urlopen(req) as resp:
            return {"status": resp.status, "body": json.loads(resp.read().decode("utf-8"))}
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        return {"status": e.code, "body": json.loads(body) if body else {"error": str(e)}}
    except urllib.error.URLError:
        return {"status": 503, "body": {"success": False, "error": "Backend unavailable"}}


def health(request, params, session):
    return _proxy("GET", "/tasks")


def get_tasks(request, params, session):
    return _proxy("GET", "/tasks")


def create_task(request, params, session):
    return _proxy("POST", "/tasks", request.get("body", {}))


def update_task(request, params, session):
    task_id = params.get("id")
    return _proxy("PUT", f"/tasks/{task_id}", request.get("body", {}))


def delete_task(request, params, session):
    task_id = params.get("id")
    return _proxy("DELETE", f"/tasks/{task_id}")
