import json
import socket
import ssl
import sys

ENCODING = "utf-8"
CA_PORT = 4891


def _ssl_context(cafile=None):
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    if cafile and os.path.exists(cafile):
        ctx.load_verify_locations(cafile)
    else:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
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


class IchinCAClient:
    def __init__(self, host="127.0.0.1", port=CA_PORT):
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        ctx = _ssl_context()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        tls = ctx.wrap_socket(sock, server_hostname=self.host)
        tls.connect((self.host, self.port))
        self.sock = tls

        tls.sendall(b"ICHINP/1.0\ntarget-host: ca.ichin\nclient-id: ichinca-cli/1.0\n")
        resp = _recv_line(tls)
        if not resp or resp.startswith("505"):
            raise ConnectionError(f"Handshake rejected: {resp}")
        for _ in range(3):
            _recv_line(tls)

    def _send(self, body):
        req = {
            "method": "ACTION",
            "path": "/ca/action",
            "headers": {},
            "body": body,
            "session_id": "ca-session",
        }
        self.sock.sendall((json.dumps(req) + "\n").encode(ENCODING))
        raw = _recv_json(self.sock)
        if raw is None:
            raise ConnectionError("Connection closed")
        return raw.get("body", {})

    def request_cert(self, domain, public_key):
        return self._send({
            "action": "request_cert",
            "domain": domain,
            "public_key": public_key,
        })

    def verify_domain(self, domain):
        return self._send({
            "action": "verify_domain",
            "domain": domain,
        })

    def check_cert(self, serial=None, domain=None):
        body = {"action": "check_cert"}
        if serial:
            body["serial"] = serial
        if domain:
            body["domain"] = domain
        return self._send(body)

    def revoke_cert(self, serial, reason="unspecified"):
        return self._send({
            "action": "revoke_cert",
            "serial": serial,
            "reason": reason,
        })

    def get_crl(self):
        return self._send({"action": "get_crl"})

    def get_root_cert(self):
        return self._send({"action": "get_root_cert"})

    def close(self):
        if self.sock:
            self.sock.close()
            self.sock = None


def demo():
    import sys

    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.backends import default_backend

    service_key = rsa.generate_private_key(65537, 2048, default_backend())
    pub_pem = service_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    import base64
    pub_b64 = base64.b64encode(pub_pem).decode("ascii")

    client = IchinCAClient()
    try:
        client.connect()
        print("Connected to IchinCA\n")

        r = client.request_cert("site.ichin", pub_b64)
        print(f"1. Request cert: {r['status']}")
        challenge = r.get("challenge", "")
        print(f"   Challenge: {challenge}")

        from ichinca import IchinDNSClient
        dns = IchinDNSClient()
        dns.publish_txt("site.ichin", challenge)

        from time import sleep
        sleep(0.5)

        r = client.verify_domain("site.ichin")
        print(f"2. Verify domain: {r['status']}")
        cert = r.get("certificate", {})
        if cert:
            print(f"   Serial : {cert.get('serial_number')}")
            print(f"   Domain : {cert.get('domain')}")
            print(f"   Issuer : {cert.get('issuer')}")
            print(f"   Expires: {cert.get('expires_at')}")

        r = client.check_cert(domain="site.ichin")
        print(f"3. Check cert: {r['status']}, valid={r.get('valid')}")

        serial = cert.get("serial_number", "")
        r = client.revoke_cert(serial)
        print(f"4. Revoke: {r['status']} (serial={serial})")

        r = client.check_cert(domain="site.ichin")
        print(f"5. Check after revoke: valid={r.get('valid')}, errors={r.get('errors')}")

        r = client.get_crl()
        print(f"6. CRL entries: {len(r.get('revoked', []))}")

        r = client.get_root_cert()
        print(f"7. Root CA: {r.get('root_certificate', {}).get('domain')}")

    except ConnectionError as e:
        print(f"Error: {e}")
        return 1
    finally:
        client.close()

    print("\nDemo complete.")
    return 0


if __name__ == "__main__":
    sys.exit(demo())
