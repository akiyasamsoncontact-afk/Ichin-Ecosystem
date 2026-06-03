import time
import uuid
import threading


class Session:
    def __init__(self, session_id, client_addr):
        self.session_id = session_id
        self.client_addr = client_addr
        self.created = time.time()
        self.last_active = time.time()
        self.data = {}
        self.realtime = False


class SessionManager:
    def __init__(self, timeout=300):
        self._sessions = {}
        self._lock = threading.Lock()
        self.timeout = timeout
        self._cleaner = threading.Thread(target=self._clean_loop, daemon=True)
        self._cleaner.start()

    def create(self, client_addr):
        with self._lock:
            sid = str(uuid.uuid4())
            self._sessions[sid] = Session(sid, client_addr)
            return sid

    def get(self, session_id):
        with self._lock:
            s = self._sessions.get(session_id)
            if s:
                s.last_active = time.time()
            return s

    def delete(self, session_id):
        with self._lock:
            return self._sessions.pop(session_id, None)

    def touch(self, session_id):
        s = self.get(session_id)
        if s:
            s.last_active = time.time()

    def _clean_loop(self):
        while True:
            time.sleep(60)
            now = time.time()
            with self._lock:
                stale = [sid for sid, s in self._sessions.items()
                         if now - s.last_active > self.timeout]
                for sid in stale:
                    del self._sessions[sid]
