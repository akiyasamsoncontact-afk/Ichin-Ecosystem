import json
import os
import ssl
import uuid

VERSION = "ICHINP/1.0"
PORT = 4889
ENCODING = "utf-8"

STATUS_CODES = {
    200: "OK",
    400: "BAD REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT FOUND",
    500: "INTERNAL ERROR",
}


class ICHINRequest:
    def __init__(self, method, path, headers=None, body=None, session_id=None):
        self.method = method
        self.path = path
        self.headers = headers or {}
        self.body = body or {}
        self.session_id = session_id

    def to_dict(self):
        return {
            "method": self.method,
            "path": self.path,
            "headers": self.headers,
            "body": self.body,
            "session_id": self.session_id or "",
        }

    def to_json(self):
        return json.dumps(self.to_dict(), separators=(",", ":"))

    @classmethod
    def from_dict(cls, d):
        return cls(
            method=d["method"],
            path=d["path"],
            headers=d.get("headers", {}),
            body=d.get("body", {}),
            session_id=d.get("session_id", ""),
        )


class ICHINResponse:
    def __init__(self, status, message=None, headers=None, body=None, session_id=None):
        self.status = status
        self.message = message or STATUS_CODES.get(status, "UNKNOWN")
        self.headers = headers or {}
        self.body = body or {}
        self.session_id = session_id

    def to_dict(self):
        return {
            "status": self.status,
            "message": self.message,
            "headers": self.headers,
            "body": self.body,
            "session_id": self.session_id or "",
        }

    def to_json(self):
        return json.dumps(self.to_dict(), separators=(",", ":"))

    @classmethod
    def from_dict(cls, d):
        return cls(
            status=d["status"],
            message=d.get("message", ""),
            headers=d.get("headers", {}),
            body=d.get("body", {}),
            session_id=d.get("session_id", ""),
        )


def create_ssl_context(server_side=False, certfile=None, keyfile=None, cafile=None):
    if server_side:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(certfile, keyfile)
    else:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        if cafile and os.path.exists(cafile):
            ctx.load_verify_locations(cafile)
        else:
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
    ctx.minimum_version = ssl.TLSVersion.TLSv1_3
    return ctx


def recv_line(sock):
    data = b""
    while True:
        ch = sock.recv(1)
        if not ch:
            return None
        data += ch
        if data.endswith(b"\n"):
            break
    return data.decode(ENCODING).strip()


def recv_json(sock):
    data = b""
    while True:
        ch = sock.recv(1)
        if not ch:
            return None
        data += ch
        if data.endswith(b"\n"):
            break
    return json.loads(data.decode(ENCODING).strip())
