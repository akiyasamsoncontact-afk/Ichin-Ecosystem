import json
import os
import socket
import ssl
import threading

from ichindns import (
    DEFAULT_PORT, ROOT_ZONE, VALID_TYPES,
    Record, Registry, Cache, Resolver, sign_response,
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REGISTRY_FILE = os.path.join(SCRIPT_DIR, "registry.json")
CERT_FILE = os.path.join(SCRIPT_DIR, "..", "shared", "cert.pem")
KEY_FILE = os.path.join(SCRIPT_DIR, "..", "shared", "key.pem")

ENCODING = "utf-8"


def create_ssl_context():
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    ctx.load_cert_chain(CERT_FILE, KEY_FILE)
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


class IchinDNSServer:
    def __init__(self, host="0.0.0.0", port=DEFAULT_PORT):
        self.host = host
        self.port = port
        self.registry = Registry(seed_file=REGISTRY_FILE)
        self.cache = Cache()
        self.resolver = Resolver(self.registry, self.cache)

    def _handshake(self, tls_conn):
        version = recv_line(tls_conn)
        if not version or version != "ICHINP/1.0":
            tls_conn.sendall(b"505 VERSION-MISMATCH\n")
            return None
        recv_line(tls_conn)
        recv_line(tls_conn)
        tls_conn.sendall(
            b"100 ACCEPT\n"
            b"server-version: ichindns/1.0\n"
            b"session-id: dns-query\n"
            b"encryption: tls-1.3\n"
        )
        return True

    def _handle_query(self, body):
        domain = body.get("query", "").strip()
        type_ = body.get("type", "A").upper()
        if type_ not in VALID_TYPES:
            type_ = "A"
        if not domain:
            return {"status": "ERR_INVALID", "records": []}
        status, records = self.resolver.resolve(domain, type_)
        return {
            "status": status,
            "records": [r.to_dict() for r in records] if status == "OK" else [],
        }

    def _handle_register(self, body):
        type_ = body.get("type", "").upper()
        host = body.get("host", "").strip().lower()
        value = body.get("value", "").strip()
        ttl = body.get("ttl", 3600)

        if type_ not in VALID_TYPES or not host or not value:
            return {"status": "ERR_INVALID"}
        record = Record(type_, host, value, ttl)
        result = self.registry.register(record)
        if result == "OK":
            self.cache.invalidate(host)
            self.registry.save(REGISTRY_FILE)
        return {"status": result}

    def _handle_list(self, body):
        domain = body.get("domain", "").strip().lower()
        if not domain:
            return {"status": "ERR_INVALID", "records": []}
        records = self.registry.lookup(domain)
        return {"status": "OK", "records": [r.to_dict() for r in records]}

    def _handle_delete(self, body):
        domain = body.get("domain", "").strip().lower()
        type_ = body.get("type", "").upper() or None
        if not domain:
            return {"status": "ERR_INVALID"}
        result = self.registry.delete(domain, type_)
        if result == "OK":
            self.cache.invalidate(domain)
            self.registry.save(REGISTRY_FILE)
        return {"status": result}

    def _handle_request(self, tls_conn, body):
        method = body.get("method", "QUERY").upper()
        path = body.get("path", "/dns/query")
        req_body = body.get("body", {})

        if path == "/dns/query" and method == "QUERY":
            result = self._handle_query(req_body)
        elif path == "/dns/register" and method == "REGISTER":
            result = self._handle_register(req_body)
        elif path == "/dns/list" and method == "LIST":
            result = self._handle_list(req_body)
        elif path == "/dns/delete" and method == "DELETE":
            result = self._handle_delete(req_body)
        else:
            result = {"status": "NOT_FOUND"}

        signature = sign_response(result)

        resp = {
            "status": 200,
            "message": "OK",
            "headers": {"x-ichindns-sig": signature},
            "body": result,
            "session_id": "dns-query",
        }
        tls_conn.sendall((json.dumps(resp) + "\n").encode(ENCODING))

    def _handle_client(self, tls_conn, addr):
        if not self._handshake(tls_conn):
            tls_conn.close()
            return
        print(f"[{addr}] DNS session started")

        while True:
            tls_conn.settimeout(30)
            try:
                raw = recv_json(tls_conn)
                if raw is None:
                    break
                self._handle_request(tls_conn, raw)
            except socket.timeout:
                break
            except (json.JSONDecodeError, UnicodeDecodeError):
                resp = {"status": 400, "message": "BAD REQUEST",
                        "headers": {}, "body": {"status": "ERR_INVALID"},
                        "session_id": "dns-query"}
                tls_conn.sendall((json.dumps(resp) + "\n").encode(ENCODING))
            except Exception:
                break

        tls_conn.close()
        print(f"[{addr}] DNS session ended")

    def start(self):
        ctx = create_ssl_context()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(5)
        print(f"IchinDNS server on {self.host}:{self.port} (TLS 1.3)")

        try:
            while True:
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
        except KeyboardInterrupt:
            self.registry.save(REGISTRY_FILE)
            print("\nSaved. Shutting down.")
        finally:
            sock.close()


if __name__ == "__main__":
    server = IchinDNSServer()
    server.start()
