"""`vikhyath dashboard` (P23, spec §31–32, D-043): a loopback-only, read-only HTTP server, started on demand.

No daemon: the process exits after `sleep_after_minutes` without a page poll (DASHBOARD_SLEEPING) or on Ctrl+C.
"""
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from ..events import emit
from .api import Office

STATIC = Path(__file__).with_name("static")
TYPES = {".html": "text/html; charset=utf-8", ".js": "text/javascript; charset=utf-8", ".css": "text/css; charset=utf-8"}
HOST = "127.0.0.1"


def make_handler(office: Office, touch):
    routes = {"/api/agents": office.agents, "/api/activity": office.activity, "/api/state": office.state,
              "/api/hosts": office.hosts, "/api/runtimes": office.runtimes}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):   # quiet: the terminal shows only the URL
            pass

        def _send(self, code, body: bytes, ctype):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self' 'unsafe-inline'")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            touch()
            path = urlparse(self.path).path
            if path in routes:
                try:
                    body = json.dumps(routes[path](), ensure_ascii=False, default=str).encode()
                    return self._send(200, body, "application/json")
                except Exception as exc:   # noqa: BLE001 - one broken panel must not take the page down
                    return self._send(500, json.dumps({"error": str(exc)}).encode(), "application/json")
            name = "index.html" if path in ("/", "") else path.lstrip("/")
            f = (STATIC / name).resolve()
            if f.parent != STATIC.resolve() or not f.is_file() or f.suffix not in TYPES:
                return self._send(404, b"not found", "text/plain")
            return self._send(200, f.read_bytes(), TYPES[f.suffix])

        def do_POST(self):   # read-only
            self._send(405, b"read-only", "text/plain")

    return Handler


class Dashboard:
    def __init__(self, project, *, port=0, demo=False, sleep_after=None):
        self.office = Office(project, demo=demo)
        self.sleep_after = (sleep_after if sleep_after is not None
                            else self.office.layout.get("sleep_after_minutes", 10) * 60)
        self.last = time.monotonic()
        self.httpd = ThreadingHTTPServer((HOST, port), make_handler(self.office, self._touch))
        self.reason = None

    def _touch(self):
        self.last = time.monotonic()

    @property
    def url(self):
        return f"http://{HOST}:{self.httpd.server_address[1]}/"

    def _watch(self):
        while self.reason is None:
            time.sleep(min(5, max(0.05, self.sleep_after / 4)))
            if time.monotonic() - self.last > self.sleep_after:
                self.reason = "idle"
                self.httpd.shutdown()

    def serve(self):
        project = self.office.project
        emit(project, "DASHBOARD_STARTED", details={"url": self.url, "demo": self.office.demo})
        threading.Thread(target=self._watch, daemon=True).start()
        try:
            self.httpd.serve_forever(poll_interval=0.2)
        except KeyboardInterrupt:
            self.reason = "stopped"
        finally:
            self.httpd.server_close()
            emit(project, "DASHBOARD_SLEEPING", details={"reason": self.reason or "stopped"})
        return self.reason
