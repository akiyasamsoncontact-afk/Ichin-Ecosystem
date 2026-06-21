import json
import os
import signal
import socket
import ssl
import threading

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CERT_FILE = os.path.join(SCRIPT_DIR, "..", "shared", "cert.pem")
KEY_FILE = os.path.join(SCRIPT_DIR, "..", "shared", "key.pem")
APPS_DIR = os.path.join(SCRIPT_DIR, "apps")
DEFAULT_PORT = 4892

ENCODING = "utf-8"


def _ssl_context():
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(CERT_FILE, KEY_FILE)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_3
    return ctx


def _get_reader(sock):
    if not hasattr(sock, '_reader'):
        sock._reader = sock.makefile('rb')
    return sock._reader


def _recv_line(sock):
    reader = _get_reader(sock)
    line = reader.readline()
    if not line:
        return None
    return line.decode(ENCODING).strip()


def _recv_json(sock):
    line = _recv_line(sock)
    if line is None:
        return None
    return json.loads(line)


from session import SessionManager
from static import StaticServer
from router import Router, MiddlewarePipeline, logging_middleware, rate_limit_middleware
from sandbox import SandboxManager, set_apps_dir
from realtime import RealtimeManager


class IchinD:
    def __init__(self, host="0.0.0.0", port=DEFAULT_PORT):
        self.host = host
        self.port = port
        self.sessions = SessionManager()
        self.static = StaticServer()
        self.router = Router()
        self.pipeline = MiddlewarePipeline()
        self.sandbox = SandboxManager()
        self.realtime = RealtimeManager()
        self._running = False
        self._app_routes = {}

    def setup(self):
        set_apps_dir(APPS_DIR)

        self.pipeline.use(logging_middleware)
        self.pipeline.use(rate_limit_middleware)

        self.router.add_route("GET", "/", self._handle_home)

        loaded = self.sandbox.load_apps()
        for app_name in loaded:
            sb = self.sandbox.get_app(app_name)
            routes = sb.get_routes()
            for route in routes:
                method = route.get("method", "GET")
                path = route.get("path", "/")
                handler_name = route.get("handler", "index")
                self.router.add_route(
                    method, path,
                    self._make_app_handler(app_name, handler_name, sb),
                )
            static_path = os.path.join(APPS_DIR, app_name, "static")
            if os.path.isdir(static_path):
                self.static.mount(app_name, static_path)
                self.router.add_route(
                    "GET", f"/{app_name}/static/*",
                    self._make_static_handler(app_name),
                )

        print(f"  Loaded apps: {loaded}")
        print(f"  Routes: {len(self.router._routes)}")

    def _make_app_handler(self, app_name, handler_name, sb):
        def handler(request, params, session):
            return sb.call(handler_name, request, params, session)
        return handler

    def _make_static_handler(self, app_name):
        def handler(request, params, session):
            path = request.get("path", "/")
            static_path = path.replace(f"/{app_name}/static/", "", 1)
            result = self.static.serve(app_name, static_path)
            if result:
                data, mime = result
                return {"status": 200, "body": {"_binary": True,
                        "data": data.hex(), "mime": mime}}
            return {"status": 404, "body": {"error": "File not found"}}
        return handler

    def _handle_home(self, request, params, session):
        return {"status": 200, "body": {
            "server": "IchinD/1.0",
            "status": "running",
            "session": session.session_id if session else None,
        }}

    def _handle_static(self, request, params, session):
        file_path = params.get("path", "")
        result = self.static.serve("_root", file_path)
        if result:
            data, mime = result
            return {"status": 200, "body": {"_binary": True,
                    "data": data.hex(), "mime": mime}}
        return {"status": 404, "body": {"error": "File not found"}}

    def _do_handshake(self, tls_conn):
        version = _recv_line(tls_conn)
        if not version or version != "ICHINP/1.0":
            tls_conn.sendall(b"505 VERSION-MISMATCH\n")
            return None
        _recv_line(tls_conn)
        _recv_line(tls_conn)
        tls_conn.sendall(
            b"100 ACCEPT\n"
            b"server-version: ichind/1.0\n"
            b"session-id: ichind-session\n"
            b"encryption: tls-1.3\n"
        )
        return True

    def _handle_client(self, tls_conn, addr):
        if not self._do_handshake(tls_conn):
            tls_conn.close()
            return

        sid = self.sessions.create(addr)
        session = self.sessions.get(sid)
        print(f"[{addr}] Session {sid[:8]} started")

        realtime_client = None

        while True:
            tls_conn.settimeout(30)
            try:
                raw = _recv_json(tls_conn)
                if raw is None:
                    break
            except socket.timeout:
                if realtime_client:
                    continue
                break
            except (json.JSONDecodeError, UnicodeDecodeError):
                resp = {"status": 400, "message": "BAD REQUEST",
                        "headers": {}, "body": {"error": "Invalid JSON"},
                        "session_id": sid}
                tls_conn.sendall((json.dumps(resp) + "\n").encode(ENCODING))
                continue
            except Exception:
                break

            method = raw.get("method", "GET").upper()
            path = raw.get("path", "/")
            req_body = raw.get("body", {})
            req_headers = raw.get("headers", {})

            request = {"method": method, "path": path,
                       "body": req_body, "headers": req_headers}

            if path.startswith("/_realtime/connect"):
                from realtime import RealtimeClient
                realtime_client = self.realtime.register(tls_conn, sid)
                resp_body = {"status": "connected",
                             "client_id": realtime_client.client_id}
                resp = {"status": 200, "message": "OK", "headers": {},
                        "body": resp_body, "session_id": sid}
                tls_conn.sendall((json.dumps(resp) + "\n").encode(ENCODING))
                self._realtime_loop(realtime_client, tls_conn, sid)
                break

            if path.startswith("/_realtime/send") and realtime_client:
                event = req_body.get("event", "message")
                data = req_body.get("data", {})
                target = req_body.get("target")
                if target:
                    self.realtime.send(target, event, data)
                else:
                    self.realtime.send(realtime_client.client_id, event, data)
                resp = {"status": 200, "message": "OK", "headers": {},
                        "body": {"sent": True}, "session_id": sid}
                tls_conn.sendall((json.dumps(resp) + "\n").encode(ENCODING))
                continue

            route, params = self.router.resolve(method, path)
            if not route:
                resp = {"status": 404, "message": "NOT FOUND",
                        "headers": {}, "body": {"error": "Route not found"},
                        "session_id": sid}
                tls_conn.sendall((json.dumps(resp) + "\n").encode(ENCODING))
                continue

            try:
                result = self.pipeline.run(request, params, session, route.handler)
                if isinstance(result, dict):
                    resp = {"status": result.get("status", 200),
                            "message": "OK",
                            "headers": {},
                            "body": result.get("body", {}),
                            "session_id": sid}
                else:
                    resp = {"status": 200, "message": "OK",
                            "headers": {}, "body": {"result": str(result)},
                            "session_id": sid}
            except Exception as e:
                resp = {"status": 500, "message": "INTERNAL ERROR",
                        "headers": {}, "body": {"error": str(e)},
                        "session_id": sid}

            try:
                tls_conn.sendall((json.dumps(resp) + "\n").encode(ENCODING))
            except Exception:
                break

        if realtime_client:
            self.realtime.unregister(realtime_client.client_id)
        self.sessions.delete(sid)
        try:
            tls_conn.close()
        except Exception:
            pass
        print(f"[{addr}] Session {sid[:8]} ended")

    def _realtime_loop(self, client, tls_conn, sid):
        while client.alive:
            tls_conn.settimeout(30)
            try:
                raw = _recv_json(tls_conn)
                if raw is None:
                    break
                self.realtime.handle_message(client.client_id, raw)
            except socket.timeout:
                continue
            except Exception:
                break

    def start(self):
        self.setup()

        ctx = _ssl_context()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(10)
        self._running = True
        print(f"IchinD on {self.host}:{self.port} (TLS 1.3)")

        signal.signal(signal.SIGINT, lambda s, f: self._shutdown())

        try:
            while self._running:
                conn, addr = sock.accept()
                try:
                    tls_conn = ctx.wrap_socket(conn, server_side=True)
                except ssl.SSLError:
                    conn.close()
                    continue
                t = threading.Thread(target=self._handle_client,
                                     args=(tls_conn, addr))
                t.daemon = True
                t.start()
        finally:
            sock.close()

    def _shutdown(self):
        print("\nShutting down...")
        self._running = False


if __name__ == "__main__":
    from router import logging_middleware

    server = IchinD()
    server.start()
