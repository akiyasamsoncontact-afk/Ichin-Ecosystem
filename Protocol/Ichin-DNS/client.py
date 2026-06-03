import json
import socket
import ssl

from ichindns import (
    DEFAULT_PORT, ROOT_ZONE, VALID_TYPES,
    verify_signature,
)

ENCODING = "utf-8"


def create_ssl_context():
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
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


class IchinDNSClient:
    def __init__(self, host="127.0.0.1", port=DEFAULT_PORT):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        ctx = create_ssl_context()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        tls_conn = ctx.wrap_socket(sock, server_hostname=self.host)
        tls_conn.connect((self.host, self.port))
        self.sock = tls_conn

        tls_conn.sendall(b"ICHINP/1.0\n")
        tls_conn.sendall(b"target-host: dns.ichin\n")
        tls_conn.sendall(b"client-id: ichindns-cli/1.0\n")

        response = recv_line(tls_conn)
        if not response or response.startswith("505"):
            raise ConnectionError(f"Handshake rejected: {response}")
        recv_line(tls_conn)
        recv_line(tls_conn)
        recv_line(tls_conn)

    def _send_request(self, method, path, body):
        req = {
            "method": method,
            "path": path,
            "headers": {},
            "body": body,
            "session_id": "dns-query",
        }
        self.sock.sendall((json.dumps(req) + "\n").encode(ENCODING))
        raw = recv_json(self.sock)
        if raw is None:
            raise ConnectionError("Connection closed")
        sig = raw.get("headers", {}).get("x-ichindns-sig", "")
        result = raw.get("body", {})
        if sig and not verify_signature(result, sig):
            print("  ⚠  Response signature invalid")
        return result

    def query(self, domain, type_="A"):
        return self._send_request("QUERY", "/dns/query",
                                  {"query": domain, "type": type_.upper()})

    def register(self, type_, host, value, ttl=3600):
        return self._send_request("REGISTER", "/dns/register",
                                  {"type": type_.upper(), "host": host,
                                   "value": value, "ttl": ttl})

    def list_records(self, domain):
        return self._send_request("LIST", "/dns/list",
                                  {"domain": domain})

    def delete(self, domain, type_=None):
        body = {"domain": domain}
        if type_:
            body["type"] = type_.upper()
        return self._send_request("DELETE", "/dns/delete", body)

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None


def demo():
    import sys

    client = IchinDNSClient()
    try:
        client.connect()
        print("Connected to IchinDNS\n")

        client.register("A", "site.ichin", "10.0.0.1")
        client.register("AAAA", "site.ichin", "::1")
        client.register("TXT", "site.ichin", "verification=ichin-ca")
        client.register("ICHIN", "app.ichin", "ichinp://10.0.0.1:4889/app")
        client.register("CNAME", "blog.ichin", "site.ichin")
        print("Registered seed records\n")

        tests = [
            ("site.ichin", "A"),
            ("site.ichin", "AAAA"),
            ("site.ichin", "TXT"),
            ("app.ichin", "ICHIN"),
            ("blog.ichin", "A"),
            ("unknown.ichin", "A"),
        ]

        for domain, type_ in tests:
            result = client.query(domain, type_)
            status = result.get("status", "ERR")
            records = result.get("records", [])
            print(f"  {domain} ({type_}): {status}")
            for r in records:
                print(f"    → {r['type']} {r['value']}")

    except ConnectionError as e:
        print(f"Error: {e}")
        return 1
    finally:
        client.close()

    print("\nDemo complete.")
    return 0


if __name__ == "__main__":
    sys.exit(demo())
