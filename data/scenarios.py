"""Deterministic synthetic demo data; not sourced from any bank."""
from datetime import datetime, timedelta
import pandas as pd

SCENARIOS = {
    "Payment API latency": {
        "service": "payments-api", "severity": "SEV2",
        "symptom": "p95 latency and HTTP 5xx rates increased after a deployment.",
        "hypothesis": "Connection-pool exhaustion following deployment v2.4.1.",
        "evidence": ["Deployment v2.4.1 at 10:12", "Connection utilization 96%", "Timeouts increased after deployment"],
        "recommendation": "Review deployment diff and consider an approved rollback.",
        "latency": [180, 190, 205, 270, 620, 980, 1200, 1160, 1120, 1080, 1010, 950],
        "errors": [0.2, 0.2, 0.3, 0.5, 2.1, 4.6, 8.4, 8.0, 7.6, 6.8, 6.2, 5.5],
    },
    "Kubernetes CrashLoopBackOff": {
        "service": "customer-profile", "severity": "SEV2",
        "symptom": "Pods restart repeatedly and readiness is degraded.",
        "hypothesis": "Memory limit exhaustion; investigate OOMKilled exit code 137.",
        "evidence": ["Restart count increased", "Last termination: OOMKilled / 137", "Memory usage approached configured limit"],
        "recommendation": "Inspect memory regression and resource settings before approved change.",
        "latency": [150, 155, 160, 170, 260, 440, 710, 690, 740, 680, 650, 610],
        "errors": [0.1, 0.1, 0.2, 0.3, 1.0, 3.2, 6.5, 5.9, 7.0, 5.5, 4.9, 4.4],
    },
    "Database saturation": {
        "service": "accounts-api", "severity": "SEV2",
        "symptom": "Database wait times and API timeouts increased.",
        "hypothesis": "Database connections saturated under elevated concurrency.",
        "evidence": ["DB active connections 98% of limit", "Queue wait time elevated", "API timeout rate tracks DB waits"],
        "recommendation": "Inspect expensive queries and connection utilization; propose reviewed mitigation.",
        "latency": [130, 135, 150, 210, 400, 690, 930, 990, 1040, 980, 910, 880],
        "errors": [0.1, 0.2, 0.2, 0.6, 1.3, 3.5, 5.6, 6.2, 6.8, 6.0, 5.1, 4.6],
    },
    "False-positive alert": {
        "service": "catalog-api", "severity": "INFO",
        "symptom": "One isolated latency spike without sustained SLO impact.",
        "hypothesis": "Transient measurement spike; insufficient evidence for incident remediation.",
        "evidence": ["Single p95 outlier", "5xx rate remains below 1%", "No correlated change or sustained degradation"],
        "recommendation": "Do not remediate. Continue monitoring and review alert thresholds.",
        "latency": [140, 145, 148, 150, 450, 155, 145, 148, 146, 144, 147, 143],
        "errors": [0.1, 0.1, 0.2, 0.1, 0.3, 0.2, 0.1, 0.1, 0.2, 0.1, 0.1, 0.1],
    },
}

def telemetry(name: str) -> pd.DataFrame:
    s = SCENARIOS[name]
    start = datetime(2026, 10, 27, 10, 0)
    return pd.DataFrame({
        "time": [start + timedelta(minutes=5*i) for i in range(len(s["latency"]))],
        "p95_latency_ms": s["latency"],
        "error_rate_pct": s["errors"],
    })

def detect_incident(name: str) -> bool:
    """Illustrative rule: sustained degradation in last six samples."""
    df = telemetry(name)
    tail = df.tail(6)
    return bool((tail["p95_latency_ms"] > 500).sum() >= 3 and
                (tail["error_rate_pct"] > 2).sum() >= 3)
