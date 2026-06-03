import json
import threading
import time
import uuid

ENCODING = "utf-8"


class RealtimeClient:
    def __init__(self, conn, session_id):
        self.conn = conn
        self.session_id = session_id
        self.client_id = str(uuid.uuid4())
        self.connected_at = time.time()
        self.alive = True


class RealtimeManager:
    def __init__(self):
        self._clients = {}
        self._lock = threading.Lock()
        self._event_handlers = {}

    def register(self, conn, session_id):
        client = RealtimeClient(conn, session_id)
        with self._lock:
            self._clients[client.client_id] = client
        self._emit("client.connect", {"client_id": client.client_id,
                                       "session_id": session_id})
        return client

    def unregister(self, client_id):
        with self._lock:
            client = self._clients.pop(client_id, None)
        if client:
            client.alive = False
            self._emit("client.disconnect", {"client_id": client_id})

    def on(self, event, handler):
        self._event_handlers[event] = handler

    def _emit(self, event, data):
        handler = self._event_handlers.get(event)
        if handler:
            try:
                handler(event, data)
            except Exception:
                pass

    def send(self, client_id, event, data):
        with self._lock:
            client = self._clients.get(client_id)
        if not client or not client.alive:
            return False
        msg = {"event": event, "data": data, "type": "realtime"}
        try:
            client.conn.sendall((json.dumps(msg) + "\n").encode(ENCODING))
            return True
        except Exception:
            self.unregister(client_id)
            return False

    def broadcast(self, event, data, exclude=None):
        with self._lock:
            targets = list(self._clients.items())
        for cid, client in targets:
            if exclude and cid == exclude:
                continue
            self.send(cid, event, data)

    def handle_message(self, client_id, payload):
        self._emit("client.message", {
            "client_id": client_id,
            "payload": payload,
        })
