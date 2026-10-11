"""SEO evidence model (P16, spec §28.2): every SEO statement carries one label, decided by what was captured.

FACT         directly observed in a complete, usable capture (presence or absence)
OBSERVATION  seen in a usable but partial capture (positive observations survive a partial capture)
INFERENCE    a conclusion drawn from at least one FACT/OBSERVATION
HYPOTHESIS   a prediction or an interpretation with no observed basis
UNKNOWN      could not be inspected (failed/partial capture for an absence claim, or no capture)

Capture quality comes from BeyondSEO's own `capture_quality` (evidence.py in the bundled runtime); this module only
applies the labelling rules to its output so the rule is testable without the runtime.
"""
LABELS = ("FACT", "OBSERVATION", "INFERENCE", "HYPOTHESIS", "UNKNOWN")
CLAIMS = ("presence", "absence", "metric", "interpretation", "prediction")


def label(claim: str, quality: dict | None = None, basis=()) -> dict:
    """Label one claim. `quality` = BeyondSEO capture_quality(page); `basis` = labels the claim is derived from."""
    if claim not in CLAIMS:
        raise ValueError(f"claim must be one of {CLAIMS}")
    if claim == "prediction":
        return {"label": "HYPOTHESIS", "why": "a prediction is never observed"}
    if claim == "interpretation":
        observed = [b for b in basis if b in ("FACT", "OBSERVATION")]
        return ({"label": "INFERENCE", "why": f"derived from {len(observed)} observed statement(s)"} if observed else
                {"label": "HYPOTHESIS", "why": "no observed basis"})
    q = quality or {}
    limits = list(q.get("limits") or [])
    if not q.get("usable"):
        return {"label": "UNKNOWN", "why": "could not be inspected: " + ("; ".join(limits) or "no usable capture")}
    if claim == "absence":
        if q.get("absence_supported"):
            return {"label": "FACT", "why": "complete capture; absence observed"}
        return {"label": "UNKNOWN", "why": "could not be inspected completely: " + "; ".join(limits)}
    if limits:
        return {"label": "OBSERVATION", "why": "seen in a partial capture: " + "; ".join(limits)}
    return {"label": "FACT", "why": "seen in a complete capture"}


def render(statement: str, result: dict) -> str:
    return f"[{result['label']}] {statement} — {result['why']}"
