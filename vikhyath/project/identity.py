"""Project identity (doc 14 §1, D-011): `project_id = sha256(realpath(root) + "\\n" + normalized origin)[:16]`.

Computed by the core from the filesystem, never taken from model output. Reads `.git` directly (no subprocess) so
identity costs a few small file reads.
"""
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

from ..paths import vikhyath_home

_SCP = re.compile(r"^(?:[\w.-]+@)?([\w.-]+):(?!/)(.+)$")


def _git_dir(root: Path) -> Path | None:
    dot = root / ".git"
    if dot.is_dir():
        return dot
    if dot.is_file():   # worktree or submodule: "gitdir: <path>"
        text = dot.read_text(encoding="utf-8", errors="ignore").strip()
        if text.startswith("gitdir:"):
            gd = Path(text[7:].strip())
            return (root / gd).resolve() if not gd.is_absolute() else gd
    return None


def find_root(start: Path | None = None) -> Path:
    """Nearest ancestor containing `.git`; otherwise the start directory itself."""
    here = (start or Path.cwd()).resolve()
    for d in (here, *here.parents):
        if (d / ".git").exists():
            return d
    return here


def _common_dir(git_dir: Path) -> Path:
    common = git_dir / "commondir"
    if common.is_file():
        c = Path(common.read_text(encoding="utf-8").strip())
        return (git_dir / c).resolve() if not c.is_absolute() else c
    return git_dir


def origin_url(root: Path) -> str:
    """Normalized `remote.origin.url`: no scheme, credentials or `.git`, lowercase host; "" when absent."""
    gd = _git_dir(root)
    if gd is None:
        return ""
    config = _common_dir(gd) / "config"
    if not config.is_file():
        return ""
    section, url = None, ""
    for line in config.read_text(encoding="utf-8", errors="ignore").splitlines():
        s = line.strip()
        if s.startswith("["):
            section = s
        elif section == '[remote "origin"]' and s.replace(" ", "").startswith("url="):
            url = s.split("=", 1)[1].strip()
            break
    return normalize_origin(url)


def normalize_origin(url: str) -> str:
    if not url:
        return ""
    url = url.strip()
    m = _SCP.match(url)
    if m and "://" not in url:
        host, path = m.group(1), m.group(2)
    else:
        rest = url.split("://", 1)[-1]
        rest = rest.split("@", 1)[-1]          # drop credentials
        host, _, path = rest.partition("/")
        host = host.split(":", 1)[0]           # drop port
    path = path.strip("/")
    if path.endswith(".git"):
        path = path[:-4]
    return f"{host.lower()}/{path}"


def current_branch(root: Path) -> str | None:
    gd = _git_dir(root)
    head = gd / "HEAD" if gd else None
    if not head or not head.is_file():
        return None
    text = head.read_text(encoding="utf-8", errors="ignore").strip()
    return text.split("refs/heads/", 1)[-1] if text.startswith("ref:") else text[:12]


def compute_id(root: Path, origin: str) -> str:
    return hashlib.sha256(f"{root.resolve()}\n{origin}".encode()).hexdigest()[:16]


@dataclass(frozen=True)
class ProjectRef:
    """Explicit project handle passed to every core API (doc 14 §3: no "current project" singleton)."""
    root: Path
    project_id: str
    origin: str
    home: Path

    @property
    def data_dir(self) -> Path:
        """Machine-local, regenerable data: $VIKHYATH_HOME/projects/<project_id>/ (cache, events, sessions)."""
        return self.home / "projects" / self.project_id

    @property
    def state_dir(self) -> Path:
        """Project-owned compact state: <project>/.vikhyath/ (D-011)."""
        return self.root / ".vikhyath"

    @property
    def name(self) -> str:
        return self.root.name


def detect(start: Path | None = None, home: Path | None = None) -> ProjectRef:
    root = find_root(start)
    origin = origin_url(root)
    return ProjectRef(root=root, project_id=compute_id(root, origin), origin=origin, home=home or vikhyath_home())
