import json
import socket

from ichinp import (
    VERSION, PORT, ENCODING,
    create_ssl_context, recv_line, recv_json,
)


class ICHINClient:
    def __init__(self, host="127.0.0.1", port=PORT, certfile=None):
        self.host = host
        self.port = port
        self.certfile = certfile
        self.session_id = None
        self.sock = None

    def connect(self, target_host="default.ichin", client_id="ichin-client/1.0"):
        ctx = create_ssl_context(server_side=False, certfile=self.certfile)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        tls_conn = ctx.wrap_socket(sock, server_hostname=self.host)
        tls_conn.connect((self.host, self.port))
        self.sock = tls_conn

        tls_conn.sendall(f"{VERSION}\n".encode(ENCODING))
        tls_conn.sendall(f"target-host: {target_host}\n".encode(ENCODING))
        tls_conn.sendall(f"client-id: {client_id}\n".encode(ENCODING))

        response = recv_line(tls_conn)
        if not response:
            raise ConnectionError("No handshake response")

        if response.startswith("505"):
            raise ConnectionError(f"Server rejected handshake: {response}")

        if response.startswith("100"):
            server_version = recv_line(tls_conn) or ""
            session_line = recv_line(tls_conn) or ""
            encryption_line = recv_line(tls_conn) or ""

            self.session_id = session_line.replace("session-id: ", "").strip()
            print(f"Connected. Session: {self.session_id}")
            return self.session_id

        raise ConnectionError(f"Unexpected handshake response: {response}")

    def request(self, method, path, headers=None, body=None):
        if not self.sock:
            raise RuntimeError("Not connected. Call connect() first.")

        req = {
            "method": method.upper(),
            "path": path,
            "headers": headers or {},
            "body": body or {},
            "session_id": self.session_id or "",
        }
        self.sock.sendall((json.dumps(req) + "\n").encode(ENCODING))

        raw = recv_json(self.sock)
        if raw is None:
            raise ConnectionError("Server closed connection")
        return raw

    def ping(self):
        return self.request("PING", "/")

    def echo(self, data):
        return self.request("ECHO", "/echo", body=data)

    def close(self):
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
            self.sock = None


def demo():
    client = ICHINClient()
    try:
        client.connect()
        print("→ PING /")
        resp = client.ping()
        print(f"  {resp['status']} {resp['message']}: {resp['body']}")

        print("→ ECHO /echo")
        resp = client.echo({"hello": "world"})
        print(f"  {resp['status']} {resp['message']}: {resp['body']}")

        print("→ TIME /time")
        resp = client.request("TIME", "/time")
        print(f"  {resp['status']} {resp['message']}: {resp['body']}")

    finally:
        client.close()


if __name__ == "__main__":
    demo()
