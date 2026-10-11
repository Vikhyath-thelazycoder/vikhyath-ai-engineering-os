"""Secret redaction (spec §78–79): applied to every event before it is written and to anything echoed back.

Values are replaced with `[REDACTED:<type>]`. Dictionary keys that name a secret (password, token, api_key, …) have
their whole value redacted; free text is scanned for well-known credential shapes.
"""
import re

PATTERNS = [   # (type, regex) — order matters: specific shapes before generic key=value
    ("private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----", re.S)),
    ("authorization", re.compile(r"(?i)(\bauthorization\s*[:=]\s*)(?:bearer|basic|token)?\s*[^\s\"',;]+")),
    ("bearer", re.compile(r"(?i)\bbearer\s+[A-Za-z0-9._~+/=-]{8,}")),
    ("url-credentials", re.compile(r"(?i)\b([a-z][a-z0-9+.-]*://)[^\s:/@]+:[^\s@/]+@")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}")),
    ("aws-access-key", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("github-token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,})\b")),
    ("slack-token", re.compile(r"\bxox[abposr]-[A-Za-z0-9-]{10,}")),
    ("anthropic-key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}")),
    ("stripe-key", re.compile(r"\b(?:sk|rk|pk)_(?:live|test)_[A-Za-z0-9]{10,}")),
    ("openai-key", re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{20,}")),
    ("google-api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b")),
    ("secret-assignment", re.compile(
        r"(?i)\b([A-Z0-9_]*(?:password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key|private[_-]?key|"
        r"client[_-]?secret|credentials?)[A-Z0-9_]*)(\s*[:=]\s*)(\"[^\"]*\"|'[^']*'|[^\s,;&]+)")),
]
SENSITIVE_KEY = re.compile(r"(?i)(password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key|private[_-]?key|"
                           r"authorization|cookie|credential|session[_-]?secret|client[_-]?secret)")
SAFE_KEYS = {"est_tokens", "tokens", "token_cost_estimate", "max_tokens", "sent_tokens", "bundled_tokens"}


def redact_text(text: str) -> str:
    for kind, rx in PATTERNS:
        if kind == "authorization":
            text = rx.sub(lambda m, k=kind: f"{m.group(1)}[REDACTED:{k}]", text)
        elif kind == "url-credentials":
            text = rx.sub(lambda m, k=kind: f"{m.group(1)}[REDACTED:{k}]@", text)
        elif kind == "secret-assignment":
            text = rx.sub(lambda m, k=kind: m.group(0) if "[REDACTED:" in m.group(3)
                          else f"{m.group(1)}{m.group(2)}[REDACTED:{k}]", text)
        else:
            text = rx.sub(f"[REDACTED:{kind}]", text)
    return text


def redact(value, key: str | None = None):
    """Recursively redact a JSON-like value."""
    if (key and key not in SAFE_KEYS and SENSITIVE_KEY.search(key) and isinstance(value, (str, int, float))
            and not isinstance(value, bool) and value != ""):
        return "[REDACTED:sensitive-key]"
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, dict):
        return {k: redact(v, str(k)) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [redact(v) for v in value]
    return value
