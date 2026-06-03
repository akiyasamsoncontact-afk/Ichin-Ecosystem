import json
import socket
import threading
import uuid
from datetime import datetime, timedelta

from ichinp import (
    VERSION, PORT, STATUS_CODES, ENCODING,
    create_ssl_context, recv_line, recv_json,
)


class ICHINServer:
    def __init__(self, certfile="cert.pem", keyfile="key.pem",
                 host="0.0.0.0", port=PORT, idle_timeout=60):
        self.certfile = certfile
        self.keyfile = keyfile
        self.host = host
        self.port = port
        self.idle_timeout = idle_timeout
        self.sessions = {}
        self.routes = {}

    def route(self, method, path):
        def wrapper(handler):
            self.routes[(method.upper(), path)] = handler
            return handler
        return wrapper

    def _handle_client(self, tls_conn, addr):
        version = recv_line(tls_conn)
        if not version:
            tls_conn.close()
            return

        target_host = recv_line(tls_conn) or ""
        client_id = recv_line(tls_conn) or ""

        if version != VERSION:
            tls_conn.sendall(f"505 VERSION-MISMATCH\n".encode(ENCODING))
            tls_conn.close()
            print(f"[{addr}] Rejected: version mismatch ({version})")
            return

        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "host": target_host,
            "client_id": client_id,
            "addr": addr,
            "created": datetime.now(),
        }

        tls_conn.sendall(
            f"100 ACCEPT\n"
            f"server-version: ichind/1.0\n"
            f"session-id: {session_id}\n"
            f"encryption: tls-1.3\n"
            .encode(ENCODING)
        )
        print(f"[{addr}] Accepted → session {session_id}")

        self._request_loop(tls_conn, session_id, addr)
        self.sessions.pop(session_id, None)
        tls_conn.close()
        print(f"[{addr}] Disconnected")

    def _request_loop(self, tls_conn, session_id, addr):
        while True:
            tls_conn.settimeout(self.idle_timeout)
            try:
                raw = recv_json(tls_conn)
                if raw is None:
                    break
            except socket.timeout:
                print(f"[{addr}] Idle timeout")
                break
            except (json.JSONDecodeError, UnicodeDecodeError):
                resp = {"status": 400, "message": "BAD REQUEST",
                        "headers": {}, "body": {}, "session_id": session_id}
                tls_conn.sendall((json.dumps(resp) + "\n").encode(ENCODING))
                continue
            except Exception:
                break

            method = raw.get("method", "GET").upper()
            path = raw.get("path", "/")
            body = raw.get("body", {})
            headers = raw.get("headers", {})

            handler = self.routes.get((method, path))
            if not handler:
                resp = {"status": 404, "message": "NOT FOUND",
                        "headers": {}, "body": {}, "session_id": session_id}
            else:
                try:
                    result = handler(body, headers, session_id)
                    resp = {"status": 200, "message": "OK",
                            "headers": {}, "body": result, "session_id": session_id}
                except Exception as e:
                    resp = {"status": 500, "message": "INTERNAL ERROR",
                            "headers": {}, "body": {"error": str(e)},
                            "session_id": session_id}

            try:
                tls_conn.sendall((json.dumps(resp) + "\n").encode(ENCODING))
            except Exception:
                break

    def start(self):
        ctx = create_ssl_context(server_side=True,
                                 certfile=self.certfile,
                                 keyfile=self.keyfile)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(5)
        print(f"ICHINP server listening on {self.host}:{self.port} (TLS 1.3)")

        try:
            while True:
                conn, addr = sock.accept()
                try:
                    tls_conn = ctx.wrap_socket(conn, server_side=True)
                except ssl.SSLError as e:
                    print(f"[{addr}] TLS handshake failed: {e}")
                    conn.close()
                    continue
                t = threading.Thread(target=self._handle_client,
                                     args=(tls_conn, addr))
                t.daemon = True
                t.start()
        except KeyboardInterrupt:
            print("\nShutting down...")
        finally:
            sock.close()


if __name__ == "__main__":
    import ssl

    server = ICHINServer()

    @server.route("PING", "/")
    def ping(body, headers, session_id):
        return {"reply": "pong", "session": session_id}

    @server.route("ECHO", "/echo")
    def echo(body, headers, session_id):
        return body

    @server.route("TIME", "/time")
    def time_handler(body, headers, session_id):
        return {"server_time": datetime.now().isoformat()}

    server.start()
