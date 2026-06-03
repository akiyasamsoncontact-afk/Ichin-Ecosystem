def index(request, params, session):
    return {"status": 200, "body": {
        "app": "hello",
        "message": "Hello from IchinD!",
        "session": session.session_id[:8] if session else None,
    }}


def greet(request, params, session):
    name = params.get("name", "World")
    return {"status": 200, "body": {
        "message": f"Hello, {name}!",
        "params": params,
    }}


def echo(request, params, session):
    body = request.get("body", {})
    return {"status": 200, "body": {
        "echo": body,
        "method": request.get("method"),
    }}
