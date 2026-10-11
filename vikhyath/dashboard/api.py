"""Read-only JSON for the Agent Office (P23, D-043). Built only from existing state: registry, project state, plan
index, event log, evidence, adapters and runtimes. Nothing here writes; everything is scoped to one project."""
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from .. import __version__
from ..events import read
from ..paths import current_bundle, vikhyath_home
from . import agents as office

DEMO_EVENTS = Path(__file__).with_name("demo_events.json")


def capability_sources():
    from ..registry import generate
    bundle = current_bundle()
    reg = (generate.load_registry(bundle) if bundle else None) or generate.plan_registry()
    return {cid: e.get("source_repositories", []) for cid, e in reg["capabilities"].items()}


class Office:
    """One project's view. `demo=True` replays bundled sample events (progressively) instead of the event log."""

    def __init__(self, project, demo=False, root=None):
        self.project = project
        self.demo = demo
        self.layout = office.load_layout(root)
        self.sources = capability_sources()
        self.started = time.monotonic()
        self._cache = {}

    def events(self, limit=500):
        if not self.demo:
            return read(self.project, limit=limit)
        sample = json.loads(DEMO_EVENTS.read_text(encoding="utf-8"))
        n = min(len(sample), 1 + int((time.monotonic() - self.started) / 2.5) % (len(sample) + 4))
        now = datetime.now(timezone.utc)
        out = []
        for i, rec in enumerate(sample[:n]):   # restamp so the replay is always "now"
            ts = datetime.fromtimestamp(now.timestamp() - (n - i) * 2.5, timezone.utc)
            out.append({**rec, "ts": ts.isoformat(timespec="milliseconds"), "severity": rec.get("severity", "info")})
        return out

    def agents(self):
        ev = self.events()
        return {"seats": office.derive(self.layout, ev, self.sources), "rooms": self.layout["rooms"],
                "demo": self.demo, "at": datetime.now(timezone.utc).isoformat(timespec="seconds")}

    def activity(self, limit=40):
        return {"items": office.activity(self.events(), limit), "demo": self.demo}

    def state(self):
        from ..project import plan_index, state as pstate
        from ..project.identity import current_branch
        from ..verify import policy
        st = pstate.load_state(self.project)
        index = plan_index.load_index(self.project, st) if st else None
        phase = next((p for p in (index or {}).get("phases", []) if p["phase_id"] == (index or {}).get("current_phase")),
                     None)
        bundle = current_bundle()
        return {"os_version": __version__, "project": self.project.name, "project_id": self.project.project_id,
                "branch": current_branch(self.project.root), "bundle": bundle.name if bundle else None,
                "stage": (st or {}).get("stage"), "phase": phase and f"{phase['phase_id']} {phase['phase_name']}",
                "phase_status": phase and phase["status"], "verification_mode": policy.MODE,
                "last_verification": ((st or {}).get("verification") or {}).get("last"), "demo": self.demo}

    def _cached(self, key, fn, ttl=60):
        hit = self._cache.get(key)
        if hit and time.monotonic() - hit[0] < ttl:
            return hit[1]
        val = fn()
        self._cache[key] = (time.monotonic(), val)
        return val

    def hosts(self):
        from ..adapters import all_adapters
        return self._cached("hosts", lambda: {"hosts": [{k: a.status()[k] for k in ("host", "status", "installed")}
                                                        for a in all_adapters()]})

    def runtimes(self):
        def collect():
            from ..runtimes import brag, graphify, seo, uiux, unlazy
            home, bundle = vikhyath_home(), current_bundle()
            rows = [graphify.health(home, bundle), unlazy.health(home), uiux.health(bundle), seo.health(home, bundle),
                    brag.health(home, bundle)]
            return {"runtimes": [{"runtime": r["runtime"], "status": r["status"], "version": r.get("version")}
                                 for r in rows]}
        return self._cached("runtimes", collect)
