"""Live-website authorization gate (P16, SEC-11, seo/website-work): BeyondSEO `edit apply|rollback` changes real sites
over FTP/SFTP. Each needs an explicit, per-task authorization recorded in this project only: who asked, which site,
which task, why, and an expiry. Credentials are never stored here (connection files stay where the user keeps them).
"""
import secrets
from datetime import datetime, timedelta, timezone

from ..events import emit
from ..isolation.locks import project_lock
from ..project.state import checked, read_yaml, write_yaml

FILE = "seo-authorizations.yaml"
DEFAULT_HOURS = 2


class AuthorizationError(PermissionError):
    pass


def _path(project):
    return checked(project, project.state_dir / FILE, "write")


def _now():
    return datetime.now(timezone.utc)


def grant(project, *, site: str, task: str, reason: str, hours: int = DEFAULT_HOURS, granted_by="user") -> dict:
    if not (site and task and reason and reason.strip()):
        raise AuthorizationError("authorization needs --site, --task and --reason")
    entry = {"id": "AUTH-" + secrets.token_hex(4), "site": site, "task": task, "reason": reason.strip(),
             "granted_by": granted_by, "granted_at": _now().isoformat(timespec="seconds"),
             "expires_at": (_now() + timedelta(hours=hours)).isoformat(timespec="seconds"), "used": []}
    with project_lock(project, "seo-auth"):
        data = read_yaml(_path(project)) or {"schema_version": 1, "authorizations": []}
        data["authorizations"].append(entry)
        write_yaml(_path(project), data)
    emit(project, "STATE_UPDATED", severity="medium", capabilities=["seo/website-work"],
         details={"authorization": entry["id"], "site": site, "task": task})
    return entry


def require(project, auth_id: str | None, *, action: str, site: str | None = None) -> dict:
    """The valid, unexpired authorization for this live-site action, or AuthorizationError. Use is logged."""
    if not auth_id:
        raise AuthorizationError(f"edit {action} changes a live website: authorize it first "
                                 "(`agylite seo authorize --site <site> --task <T-id> --reason \"…\"`) and pass "
                                 "--authorization <id>")
    with project_lock(project, "seo-auth"):
        data = read_yaml(_path(project)) or {"authorizations": []}
        entry = next((a for a in data["authorizations"] if a["id"] == auth_id), None)
        if entry is None:
            raise AuthorizationError(f"unknown authorization {auth_id} for this project")
        if datetime.fromisoformat(entry["expires_at"]) < _now():
            raise AuthorizationError(f"authorization {auth_id} expired at {entry['expires_at']}")
        if site and entry["site"] != site:
            raise AuthorizationError(f"authorization {auth_id} is for {entry['site']}, not {site}")
        entry["used"].append({"action": action, "at": _now().isoformat(timespec="seconds")})
        write_yaml(_path(project), data)
    return entry
