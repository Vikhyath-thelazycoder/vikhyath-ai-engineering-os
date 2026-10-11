"""Change impact (spec §55) derived from a route result, the located phase and the touched paths."""

NO_TEST_TYPES = ("DOCUMENTATION_CHANGE", "PLAN_CHANGE")
DEPLOY_CAPS = ("engineering/release", "engineering/migration", "testing/release-verification")
DOC_IMPACT = {
    "NEW_FEATURE": ["docs/FEATURES.md", "docs/SYSTEM_WORKFLOW.md"],
    "FEATURE_CHANGE": ["docs/FEATURES.md"],
    "SECURITY_CHANGE": ["docs/SECURITY.md"],
    "DESIGN_CHANGE": ["docs/DESIGN.md"],
    "INFRA_CHANGE": ["docs/TRD.md"],
    "PLAN_CHANGE": ["docs/IMPLEMENTATION_PLAN.md"],
}


def impact(route, phase=None, paths=()):
    """All twelve §55 fields. Booleans carry a reason so the plan row and the user see why."""
    caps = [c["id"] for c in route["capabilities"]] + [d["id"] for d in route["dependencies"]]
    ct = route["change_type"]
    domains = list(dict.fromkeys(c.split("/", 1)[0] for c in caps))

    def flag(cond, reason):
        return {"required": bool(cond), "reason": reason if cond else None}

    security = flag(ct == "SECURITY_CHANGE" or any(c in caps for c in ("engineering/security", "testing/security")),
                    "security change" if ct == "SECURITY_CHANGE" else "security capability routed")
    design = flag(ct == "DESIGN_CHANGE" or "design" in domains, "design capability routed")
    testing = flag(ct not in NO_TEST_TYPES, f"{ct} requires tests")
    performance = flag(ct == "PERFORMANCE_CHANGE" or "engineering/performance" in caps, "performance capability routed")
    deployment = flag(ct == "INFRA_CHANGE" or any(c in caps for c in DEPLOY_CAPS), "release/migration work")
    docs = list(DOC_IMPACT.get(ct, []))
    if "engineering/architecture" in caps:
        docs.append("docs/ARCHITECTURE.md")
    rollback = ("data migration: needs a down-migration or backup" if "engineering/migration" in caps
                else "infrastructure change: keep the previous deployment" if ct == "INFRA_CHANGE"
                else "revert the task's commits")
    deps = list(dict.fromkeys((phase or {}).get("dependencies", []) + [d["id"] for d in route["dependencies"]]))
    return {
        "change_type": ct,
        "affected_domain": domains,
        "affected_subdomain": caps,
        "affected_phase": (phase or {}).get("phase_id"),
        "affected_files": list(paths) or list((phase or {}).get("affected_paths", [])),
        "dependencies": deps,
        "security_impact": security,
        "design_impact": design,
        "testing_impact": testing,
        "performance_impact": performance,
        "deployment_impact": deployment,
        "documentation_impact": list(dict.fromkeys(docs)),
        "rollback_impact": rollback,
    }
