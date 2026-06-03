import json
import os
import socket
import ssl
import threading

from ichinca import (
    CA_PORT, CHALLENGE_TAG,
    RootCA, CertStore, CRL,
    IchinDNSClient, VerificationEngine, CertificateValidator,
    ROOT_KEY_FILE, ROOT_CERT_FILE, CERT_STORE_FILE, CRL_FILE,
)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
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


class IchinCAServer:
    def __init__(self, host="0.0.0.0", port=CA_PORT):
        self.host = host
        self.port = port
        self.root_ca = RootCA()
        self.cert_store = CertStore()
        self.crl = CRL()
        self.dns_client = IchinDNSClient()
        self.verifier = VerificationEngine(self.dns_client)
        self.validator = CertificateValidator(self.root_ca, self.crl)
        self._ensure_root_ca()

    def _ensure_root_ca(self):
        if self.root_ca.exists():
            self.root_ca.load()
            print(f"Root CA loaded: {ROOT_CERT_FILE}")
        else:
            self.root_ca.generate()
            self.root_ca.save()
            print(f"Root CA generated and saved")

    def _handshake(self, tls_conn):
        version = recv_line(tls_conn)
        if not version or version != "ICHINP/1.0":
            tls_conn.sendall(b"505 VERSION-MISMATCH\n")
            return None
        recv_line(tls_conn)
        recv_line(tls_conn)
        tls_conn.sendall(
            b"100 ACCEPT\n"
            b"server-version: ichinca/1.0\n"
            b"session-id: ca-session\n"
            b"encryption: tls-1.3\n"
        )
        return True

    def _handle_request_cert(self, body):
        domain = body.get("domain", "").strip().lower()
        public_key = body.get("public_key", "").strip()

        if not domain or not domain.endswith(".ichin"):
            return {"status": "ERROR", "message": "Invalid domain"}
        if not public_key:
            return {"status": "ERROR", "message": "Public key required"}

        import uuid
        import time
        from datetime import datetime, timezone

        pending = {
            "domain": domain,
            "public_key": public_key,
            "issuer": "pending",
            "issued_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "expires_at": "",
            "serial_number": "pending-" + uuid.uuid4().hex[:8],
            "signature": "",
        }
        self.cert_store.add(pending)
        self.cert_store.save()

        challenge_value = self.verifier.create_challenge(domain)

        return {
            "status": "pending_verification",
            "challenge": challenge_value,
            "domain": domain,
            "instructions": (
                f"Publish TXT record: {challenge_value} on {domain} "
                f"via IchinDNS, then call verify_domain"
            ),
        }

    def _handle_verify(self, body):
        domain = body.get("domain", "").strip().lower()

        if not domain:
            return {"status": "ERROR", "message": "Domain required"}

        store_certs = self.cert_store.get_by_domain(domain)
        if not store_certs:
            return {"status": "ERROR", "message": f"No pending request for {domain}"}

        pending = store_certs[-1]
        if pending.get("signature"):
            return {"status": "already_issued"}

        if not self.verifier.verify(domain):
            return {
                "status": "verification_failed",
                "message": (
                    f"TXT challenge not found for {domain}. "
                    f"Ensure the record '{CHALLENGE_TAG}=<token>' is published."
                ),
            }

        cert = self.root_ca.sign_certificate(domain, pending["public_key"])
        self.cert_store.remove(pending["serial_number"])
        self.cert_store.add(cert)
        self.cert_store.save()

        return {
            "status": "issued",
            "certificate": cert,
        }

    def _handle_check_cert(self, body):
        serial = body.get("serial", "").strip()
        domain = body.get("domain", "").strip().lower()

        cert = None
        if serial:
            cert = self.cert_store.get_by_serial(serial)
        elif domain:
            certs = self.cert_store.get_by_domain(domain)
            cert = certs[-1] if certs else None

        if not cert:
            return {"status": "NOT_FOUND", "valid": False}

        errors = self.validator.validate(cert, domain)

        if cert.get("issuer") == "IchinCA Root" and cert.get("domain") == "IchinCA Root":
            errors = []

        return {
            "status": "OK" if not errors else "INVALID",
            "valid": len(errors) == 0,
            "errors": errors,
            "certificate": cert,
        }

    def _handle_revoke(self, body):
        serial = body.get("serial", "").strip()
        reason = body.get("reason", "unspecified")

        if not serial:
            return {"status": "ERROR", "message": "Serial required"}

        cert = self.cert_store.get_by_serial(serial)
        if not cert:
            return {"status": "NOT_FOUND"}

        self.crl.revoke(serial, reason)
        self.crl.save()
        return {"status": "revoked", "serial": serial}

    def _handle_get_crl(self, body):
        return {
            "status": "OK",
            "revoked": self.crl.list_all(),
        }

    def _handle_get_root(self, body):
        return {
            "status": "OK",
            "root_certificate": self.root_ca.certificate,
        }

    def _handle_request(self, tls_conn, body):
        action = body.get("body", {}).get("action", "").strip()
        req_body = body.get("body", {})

        actions = {
            "request_cert": self._handle_request_cert,
            "verify_domain": self._handle_verify,
            "check_cert": self._handle_check_cert,
            "revoke_cert": self._handle_revoke,
            "get_crl": self._handle_get_crl,
            "get_root_cert": self._handle_get_root,
        }

        handler = actions.get(action)
        if not handler:
            result = {"status": "ERROR", "message": f"Unknown action: {action}"}
        else:
            result = handler(req_body)

        resp = {
            "status": 200,
            "message": "OK",
            "headers": {},
            "body": result,
            "session_id": "ca-session",
        }
        tls_conn.sendall((json.dumps(resp) + "\n").encode(ENCODING))

    def _handle_client(self, tls_conn, addr):
        if not self._handshake(tls_conn):
            tls_conn.close()
            return
        print(f"[{addr}] CA session started")

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
                        "session_id": "ca-session"}
                tls_conn.sendall((json.dumps(resp) + "\n").encode(ENCODING))
            except Exception:
                break

        tls_conn.close()
        print(f"[{addr}] CA session ended")

    def start(self):
        ctx = create_ssl_context()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((self.host, self.port))
        sock.listen(5)
        print(f"IchinCA server on {self.host}:{self.port} (TLS 1.3)")

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
            self.cert_store.save()
            self.crl.save()
            print("\nSaved. Shutting down.")
        finally:
            sock.close()


if __name__ == "__main__":
    server = IchinCAServer()
    server.start()
