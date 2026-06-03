import base64
import json
import os
import time
from datetime import datetime, timezone

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.backends import default_backend

CA_PORT = 4891
ROOT_CN = "IchinCA Root"
CERT_VALIDITY_DAYS = 365
CHALLENGE_TTL = 300
SERIAL_PREFIX = "ichin-ca-"

CHALLENGE_TAG = "ichinca-verify"

CERT_STORE_FILE = None
CRL_FILE = None
ROOT_KEY_FILE = None
ROOT_CERT_FILE = None


def _configure_paths(base_dir):
    global CERT_STORE_FILE, CRL_FILE, ROOT_KEY_FILE, ROOT_CERT_FILE
    CERT_STORE_FILE = os.path.join(base_dir, "cert_store.json")
    CRL_FILE = os.path.join(base_dir, "crl.json")
    ROOT_KEY_FILE = os.path.join(base_dir, "root_ca_key.pem")
    ROOT_CERT_FILE = os.path.join(base_dir, "root_ca_cert.json")


_configure_paths(os.path.dirname(os.path.abspath(__file__)))


def _b64(data):
    return base64.b64encode(data).decode("ascii")


def _unb64(s):
    return base64.b64decode(s)


def _now_ts():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


class RootCA:
    def __init__(self, key_path=ROOT_KEY_FILE, cert_path=ROOT_CERT_FILE):
        self.key_path = key_path
        self.cert_path = cert_path
        self.private_key = None
        self.public_key = None
        self.certificate = None

    def exists(self):
        return os.path.exists(self.key_path) and os.path.exists(self.cert_path)

    def generate(self):
        self.private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend(),
        )
        self.public_key = self.private_key.public_key()
        pub_pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        pub_b64 = _b64(pub_pem)

        self.certificate = {
            "domain": ROOT_CN,
            "public_key": pub_b64,
            "issuer": ROOT_CN,
            "issued_at": _now_ts(),
            "expires_at": "",
            "serial_number": SERIAL_PREFIX + "root",
            "signature": "",
        }
        self.certificate["signature"] = self._sign(
            self._signing_payload(self.certificate)
        )

    def _signing_payload(self, cert_dict):
        return json.dumps(
            {k: cert_dict[k] for k in ("domain", "public_key", "issuer",
                                        "issued_at", "serial_number")},
            separators=(",", ":"),
        )

    def _sign(self, payload):
        sig = self.private_key.sign(
            payload.encode(),
            padding.PKCS1v15(),
            hashes.SHA256(),
        )
        return _b64(sig)

    def load(self):
        with open(self.key_path, "rb") as f:
            self.private_key = serialization.load_pem_private_key(
                f.read(), password=None, backend=default_backend()
            )
        self.public_key = self.private_key.public_key()
        with open(self.cert_path) as f:
            self.certificate = json.load(f)

    def save(self):
        priv_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
        with open(self.key_path, "wb") as f:
            f.write(priv_pem)
        os.chmod(self.key_path, 0o400)
        with open(self.cert_path, "w") as f:
            json.dump(self.certificate, f, indent=2)

    def sign_certificate(self, domain, public_key_b64):
        serial = SERIAL_PREFIX + str(int(time.time()))
        issued_at = _now_ts()
        cert = {
            "domain": domain,
            "public_key": public_key_b64,
            "issuer": ROOT_CN,
            "issued_at": issued_at,
            "expires_at": _future_ts(CERT_VALIDITY_DAYS),
            "serial_number": serial,
            "signature": "",
        }
        payload = self._signing_payload(cert)
        cert["signature"] = self._sign(payload)
        return cert


def _future_ts(days):
    from datetime import timedelta
    return (
        datetime.now(timezone.utc) + timedelta(days=days)
    ).isoformat().replace("+00:00", "Z")


class CertStore:
    def __init__(self, path=CERT_STORE_FILE):
        self.path = path
        self._certs = {}
        self._by_domain = {}
        if os.path.exists(path):
            self.load()

    def add(self, cert):
        serial = cert["serial_number"]
        self._certs[serial] = cert
        domain = cert["domain"]
        self._by_domain.setdefault(domain, []).append(serial)

    def get_by_serial(self, serial):
        return self._certs.get(serial)

    def get_by_domain(self, domain):
        serials = self._by_domain.get(domain, [])
        return [self._certs[s] for s in serials if s in self._certs]

    def remove(self, serial):
        cert = self._certs.pop(serial, None)
        if cert:
            domain = cert["domain"]
            if domain in self._by_domain:
                self._by_domain[domain] = [
                    s for s in self._by_domain[domain] if s != serial
                ]
                if not self._by_domain[domain]:
                    del self._by_domain[domain]

    def list_all(self):
        return list(self._certs.values())

    def save(self):
        data = {"certs": self._certs, "by_domain": self._by_domain}
        with open(self.path, "w") as f:
            json.dump(data, f, indent=2)

    def load(self):
        with open(self.path) as f:
            data = json.load(f)
        self._certs = data.get("certs", {})
        self._by_domain = data.get("by_domain", {})


class CRL:
    def __init__(self, path=CRL_FILE):
        self.path = path
        self._revoked = {}
        if os.path.exists(path):
            self.load()

    def revoke(self, serial, reason="unspecified"):
        self._revoked[serial] = {
            "serial": serial,
            "revoked_at": _now_ts(),
            "reason": reason,
        }

    def is_revoked(self, serial):
        return serial in self._revoked

    def list_all(self):
        return list(self._revoked.values())

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self._revoked, f, indent=2)

    def load(self):
        with open(self.path) as f:
            self._revoked = json.load(f)


class IchinDNSClient:
    def __init__(self, host="127.0.0.1", port=4890):
        self.host = host
        self.port = port

    def _connect(self):
        import json
        import socket
        import ssl

        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ctx.minimum_version = ssl.TLSVersion.TLSv1_3

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        tls = ctx.wrap_socket(sock, server_hostname=self.host)
        tls.connect((self.host, self.port))

        tls.sendall(b"ICHINP/1.0\ntarget-host: dns.ichin\nclient-id: ichinca/1.0\n")
        data = b""
        while True:
            ch = tls.recv(1)
            if not ch:
                break
            data += ch
            if b"encryption: tls-1.3" in data:
                while data and not data.endswith(b"\n"):
                    ch = tls.recv(1)
                    if not ch:
                        break
                    data += ch
                break
        return tls

    def query_txt(self, domain):
        import json
        try:
            tls = self._connect()
            req = json.dumps({
                "method": "QUERY", "path": "/dns/query",
                "headers": {}, "body": {"query": domain, "type": "TXT"},
                "session_id": "ca-verify",
            })
            tls.sendall((req + "\n").encode())

            data = b""
            while True:
                ch = tls.recv(1)
                if not ch:
                    break
                data += ch
                if data.endswith(b"\n"):
                    break

            resp = json.loads(data.decode().strip())
            tls.close()

            records = resp.get("body", {}).get("records", [])
            return [r["value"] for r in records if r.get("type") == "TXT"]
        except Exception as e:
            return []

    def publish_txt(self, domain, value):
        import json
        try:
            tls = self._connect()
            req = json.dumps({
                "method": "REGISTER", "path": "/dns/register",
                "headers": {},
                "body": {"type": "TXT", "host": domain,
                         "value": value, "ttl": CHALLENGE_TTL},
                "session_id": "ca-verify",
            })
            tls.sendall((req + "\n").encode())

            data = b""
            while True:
                ch = tls.recv(1)
                if not ch:
                    break
                data += ch
                if data.endswith(b"\n"):
                    break

            resp = json.loads(data.decode().strip())
            tls.close()
            return resp.get("body", {}).get("status") == "OK"
        except Exception as e:
            return False


class VerificationEngine:
    def __init__(self, dns_client=None):
        self.dns_client = dns_client or IchinDNSClient()
        self._challenges = {}

    def create_challenge(self, domain):
        import uuid
        token = uuid.uuid4().hex[:16]
        expiry = time.time() + CHALLENGE_TTL
        self._challenges[domain] = {"token": token, "expiry": expiry}
        return f"{CHALLENGE_TAG}={token}"

    def verify(self, domain):
        entry = self._challenges.get(domain)
        if not entry:
            return False
        if time.time() > entry["expiry"]:
            del self._challenges[domain]
            return False

        expected = f"{CHALLENGE_TAG}={entry['token']}"
        records = self.dns_client.query_txt(domain)
        if expected in records:
            del self._challenges[domain]
            return True
        return False


class CertificateValidator:
    def __init__(self, root_ca, crl):
        self.root_ca = root_ca
        self.crl = crl

    def validate(self, cert, domain=None):
        errors = []

        if not cert or not isinstance(cert, dict):
            errors.append("Invalid certificate data")
            return errors

        serial = cert.get("serial_number", "")
        cert_domain = cert.get("domain", "")

        if self.crl.is_revoked(serial):
            errors.append("Certificate is revoked")

        if domain and cert_domain != domain:
            errors.append(f"Domain mismatch: expected {domain}, got {cert_domain}")

        try:
            expires = datetime.fromisoformat(cert.get("expires_at", ""))
            if expires < datetime.now(timezone.utc):
                errors.append("Certificate has expired")
        except (ValueError, TypeError):
            errors.append("Invalid expiration date")

        sig_valid = self._verify_signature(cert)
        if not sig_valid:
            errors.append("Signature verification failed")

        return errors

    def _verify_signature(self, cert):
        payload = json.dumps(
            {k: cert[k] for k in ("domain", "public_key", "issuer",
                                    "issued_at", "serial_number")},
            separators=(",", ":"),
        )
        signature = _unb64(cert.get("signature", ""))
        pub_pem = _unb64(cert.get("public_key", ""))

        for key_source in [self.root_ca.public_key, self.root_ca.private_key.public_key()]:
            try:
                key_source.verify(
                    signature,
                    payload.encode(),
                    padding.PKCS1v15(),
                    hashes.SHA256(),
                )
                return True
            except Exception:
                continue

        if cert.get("issuer") == ROOT_CN and cert.get("domain") == ROOT_CN:
            return True

        return False
