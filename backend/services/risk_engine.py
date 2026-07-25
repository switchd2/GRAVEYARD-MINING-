from typing import Any


def inject_risk_annotations(
    phases: list[dict[str, Any]],
    clusters: list[dict[str, Any]],
    dependency_reports: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """
    Annotates roadmap phases with risk checkpoints derived from dead repo failure clusters and dependency reports.
    """
    annotated_phases = []

    # Map high risk dependencies
    vulnerable_pkgs = [r["package_name"] for r in dependency_reports if r.get("vulnerability_count", 0) > 0 or r.get("supply_chain_risk") in ["HIGH", "CRITICAL"]]

    for phase in phases:
        p_num = phase.get("phase_number", 1)
        checkpoints = []

        # Phase 1: Stack & Auth setup risks
        if p_num == 1:
            if vulnerable_pkgs:
                checkpoints.append({
                    "title": "Dependency Supply Chain Alert",
                    "risk_level": "HIGH",
                    "warning": f"Detected vulnerable/risky packages in initial stack: {', '.join(vulnerable_pkgs[:3])}.",
                    "prevention_strategy": "Lock dependency versions explicitly and scan packages with Snyk/OSV before writing initial schema.",
                    "evidence_repos": ["Package registry security advisories"]
                })

        # Phase 2 & 3: Architectural complexity & Scope Creep
        if p_num in [2, 3]:
            for cluster in clusters:
                checkpoints.append({
                    "title": f"Graveyard Pattern: {cluster.get('cluster_name')}",
                    "risk_level": cluster.get("risk_level", "HIGH"),
                    "warning": cluster.get("description"),
                    "prevention_strategy": "Maintain strict MVP boundaries. Implement feature flags and isolate custom abstractions behind interfaces.",
                    "evidence_repos": cluster.get("affected_repos", [])
                })

        # Phase 4 & 5: Maintenance & Debt
        if p_num in [4, 5]:
            low_maint = [r["package_name"] for r in dependency_reports if r.get("maintenance_score", 1.0) < 0.5]
            if low_maint:
                checkpoints.append({
                    "title": "Unmaintained Dependency Decay Risk",
                    "risk_level": "MEDIUM",
                    "warning": f"Packages like {', '.join(low_maint)} have low maintenance scores and may block future updates.",
                    "prevention_strategy": "Prepare fallback wrappers or plan to replace unmaintained libraries before launch.",
                    "evidence_repos": ["Dead repo maintenance telemetry"]
                })
            else:
                checkpoints.append({
                    "title": "Maintainer Velocity & Community Friction",
                    "risk_level": "MEDIUM",
                    "warning": "Similar repositories died from lack of community contribution guidelines and complex onboarding.",
                    "prevention_strategy": "Document dev setup in 1-click Docker or standard scripts. Write concise CONTRIBUTING.md.",
                    "evidence_repos": [r for c in clusters for r in c.get("affected_repos", [])][:2]
                })

        # Ensure at least 1 risk checkpoint per phase
        if not checkpoints:
            checkpoints.append({
                "title": "Feature Scope Expansion Watchpoint",
                "risk_level": "LOW",
                "warning": "Premature optimization and non-critical integrations slow down launch velocity.",
                "prevention_strategy": "Focus strictly on user-validated deliverables before adding secondary tools.",
                "evidence_repos": []
            })

        phase_copy = dict(phase)
        phase_copy["risk_checkpoints"] = checkpoints
        annotated_phases.append(phase_copy)

    return annotated_phases
