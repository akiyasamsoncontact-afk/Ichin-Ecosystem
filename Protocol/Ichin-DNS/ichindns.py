import hashlib
import hmac
import json
import os
import time
import threading

# --- Constants ---

DEFAULT_PORT = 4890
ROOT_ZONE = ".ichin"
DEFAULT_TTL = 3600
SECRET_KEY = os.environ.get("ICHINDNS_SECRET", "ichin-dns-dev-secret")

VALID_TYPES = {"A", "AAAA", "CNAME", "TXT", "ICHIN"}

# --- Data Models ---


class Record:
    def __init__(self, type_, host, value, ttl=DEFAULT_TTL):
        self.type = type_
        self.host = host.lower()
        self.value = value
        self.ttl = ttl

    def to_dict(self):
        return {"type": self.type, "host": self.host,
                "value": self.value, "ttl": self.ttl}

    @classmethod
    def from_dict(cls, d):
        return cls(d["type"], d["host"], d["value"], d.get("ttl", DEFAULT_TTL))


class Registry:
    def __init__(self, seed_file=None, auto_approve=True):
        self.auto_approve = auto_approve
        self._lock = threading.Lock()
        self._domains = {}  # domain.lower() → [Record, ...]
        self._pending = {}  # for manual approval mode

        if seed_file and os.path.exists(seed_file):
            self.load(seed_file)

    def register(self, record, force=False):
        with self._lock:
            key = record.host
            if not self.auto_approve and not force:
                self._pending.setdefault(key, []).append(record)
                return "PENDING"

            if key in self._domains:
                existing = self._domains[key]
                for r in existing:
                    if r.type == record.type:
                        return "CONFLICT"
                existing.append(record)
            else:
                self._domains[key] = [record]
            self._clean_cname_ptrs()
            return "OK"

    def delete(self, domain, type_=None):
        with self._lock:
            key = domain.lower()
            if key not in self._domains:
                return "NXDOMAIN"
            if type_:
                self._domains[key] = [r for r in self._domains[key]
                                      if r.type != type_]
                if not self._domains[key]:
                    del self._domains[key]
            else:
                del self._domains[key]
            self._clean_cname_ptrs()
            return "OK"

    def lookup(self, domain):
        with self._lock:
            key = domain.lower()
            return list(self._domains.get(key, []))

    def list_all(self):
        with self._lock:
            result = {}
            for domain, records in self._domains.items():
                result[domain] = [r.to_dict() for r in records]
            return result

    def _clean_cname_ptrs(self):
        pass

    def save(self, path):
        with self._lock:
            data = {}
            for domain, records in self._domains.items():
                data[domain] = [r.to_dict() for r in records]
            with open(path, "w") as f:
                json.dump(data, f, indent=2)

    def load(self, path):
        with open(path) as f:
            data = json.load(f)
        with self._lock:
            for domain, records in data.items():
                self._domains[domain] = [Record.from_dict(r) for r in records]


class Cache:
    def __init__(self):
        self._lock = threading.Lock()
        self._entries = {}  # (domain, type) → (records, expiry)

    def get(self, domain, type_):
        with self._lock:
            key = (domain.lower(), type_)
            if key in self._entries:
                records, expiry = self._entries[key]
                if time.time() < expiry:
                    return records
                del self._entries[key]
            return None

    def set(self, domain, type_, records, ttl=DEFAULT_TTL):
        with self._lock:
            key = (domain.lower(), type_)
            self._entries[key] = (records, time.time() + ttl)

    def invalidate(self, domain):
        with self._lock:
            keys = [k for k in self._entries if k[0] == domain.lower()]
            for k in keys:
                del self._entries[k]

    def clear(self):
        with self._lock:
            self._entries.clear()


class Resolver:
    def __init__(self, registry, cache=None):
        self.registry = registry
        self.cache = cache or Cache()

    def resolve(self, domain, type_="A", depth=0):
        if depth > 16:
            return "ERR_LOOP", []

        domain = domain.lower().rstrip(".")
        if not domain:
            return "NXDOMAIN", []

        cached = self.cache.get(domain, type_)
        if cached is not None:
            return "OK", cached

        records = self.registry.lookup(domain)
        matched = [r for r in records if r.type == type_]

        if matched:
            ttl = matched[0].ttl
            self.cache.set(domain, type_, matched, ttl)
            return "OK", matched

        cnames = [r for r in records if r.type == "CNAME"]
        if cnames:
            target = cnames[0].value
            status, result = self.resolve(target, type_, depth + 1)
            if status == "OK":
                self.cache.set(domain, type_, result, cnames[0].ttl)
            return status, result

        return "NXDOMAIN", []


def sign_response(data, secret=SECRET_KEY):
    payload = json.dumps(data, separators=(",", ":"))
    sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return sig


def verify_signature(data, signature, secret=SECRET_KEY):
    expected = sign_response(data, secret)
    return hmac.compare_digest(expected, signature)
