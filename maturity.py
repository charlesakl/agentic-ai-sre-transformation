"""Simple transparent SRE maturity assessment, not an industry certification."""
DIMENSIONS = {
    "SLOs and error budgets": "Defined customer-journey SLIs, objectives and error-budget decisions",
    "Observability": "Actionable metrics, logs, traces and service dependency visibility",
    "Incident response": "Clear on-call ownership, playbooks and learning reviews",
    "Toil automation": "Repeatable tasks measured and automated with controls",
    "Resilience": "Game days, failover testing and validated recovery objectives",
}

def assess(scores: dict) -> dict:
    if set(scores) != set(DIMENSIONS):
        raise ValueError("Provide one score for each maturity dimension.")
    if any(not isinstance(v, int) or not 1 <= v <= 5 for v in scores.values()):
        raise ValueError("Scores must be integers from 1 to 5.")
    average = sum(scores.values()) / len(scores)
    priorities = sorted(scores, key=lambda k: (scores[k], k))[:3]
    return {"average": round(average, 2), "percent": round(average / 5 * 100),
            "priorities": priorities,
            "recommendations": [
                f"{name}: {DIMENSIONS[name]}. Establish a baseline, owner and measurable 30-day improvement."
                for name in priorities
            ]}
