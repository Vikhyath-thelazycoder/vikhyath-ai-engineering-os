"""ADAPT transforms applied while building the bundle.

Only deterministic, verifiable transforms run here: gstack template rendering and targeted rewrites
that remove instructions pointing at excluded mechanisms. Domain-level adaptation (capability cards,
section maps) happens in the domain phases (P13-P17); until then other ADAPT files pass through unchanged.
"""
from pathlib import Path

from . import gstack, rewrites

TRANSFORM_VERSION = "2"  # 2: strong-anchor gstack rendering


class Transformer:
    def __init__(self, staging: Path, inventories: dict):
        self.staging = Path(staging)
        self.inventories = inventories
        self._gstack = None

    def _gstack_renderer(self):
        if self._gstack is None:
            self._gstack = gstack.Renderer(self.staging / "gstack", self.inventories.get("gstack", []))
        return self._gstack

    def apply(self, repo, path, data: bytes, decision):
        """Return (destination path relative to the repo, output bytes, notes)."""
        if decision != "ADAPT":
            return path, data, []
        notes = []
        if repo == "gstack" and path.endswith(".tmpl"):
            text, unresolved = self._gstack_renderer().render(path, data.decode("utf-8"))
            notes += [f"unresolved placeholder {name}" for name in unresolved]
            path, data = path[: -len(".tmpl")], text.encode("utf-8")
        if rewrites.applies(repo, path):
            data = rewrites.apply(repo, path, data.decode("utf-8")).encode("utf-8")
            notes.append("targeted rewrite")
        return path, data, notes
