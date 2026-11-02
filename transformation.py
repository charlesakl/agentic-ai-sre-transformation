"""Transparent scenario-based SRE transformation planning. Not measured outcomes."""
from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class Scenario:
    monthly_incidents: int = 40
    baseline_mttr_min: int = 90
    target_mttr_min: int = 45
    baseline_noise_pct: int = 35
    target_noise_pct: int = 15
    baseline_toil_hours: int = 320
    target_toil_hours: int = 180
    hourly_loaded_cost: int = 85
    baseline_availability_pct: float = 99.90
    target_availability_pct: float = 99.95

def calculate(s: Scenario):
    if s.monthly_incidents < 0 or s.baseline_mttr_min <= 0 or s.target_mttr_min <= 0:
        raise ValueError("Incident count must be nonnegative and MTTR positive")
    if not all(0 <= x <= 100 for x in (s.baseline_noise_pct,s.target_noise_pct,s.baseline_availability_pct,s.target_availability_pct)):
        raise ValueError("Percentages must be between 0 and 100")
    if min(s.baseline_toil_hours,s.target_toil_hours,s.hourly_loaded_cost) < 0:
        raise ValueError("Hours and hourly cost must be nonnegative")
    mttr_pct=(s.baseline_mttr_min-s.target_mttr_min)/s.baseline_mttr_min*100
    hours_saved=s.baseline_toil_hours-s.target_toil_hours
    avoided_incident_hours=s.monthly_incidents*(s.baseline_mttr_min-s.target_mttr_min)/60
    # Noise reduction is percentage-point change in the assumed noisy alert share.
    return {
        "mttr_reduction_pct":round(mttr_pct,1),
        "toil_hours_saved_month":hours_saved,
        "toil_hours_saved_year":hours_saved*12,
        "toil_capacity_value_year":hours_saved*12*s.hourly_loaded_cost,
        "incident_hours_reduced_month":round(avoided_incident_hours,1),
        "noise_percentage_points":s.baseline_noise_pct-s.target_noise_pct,
        "availability_gain_pp":round(s.target_availability_pct-s.baseline_availability_pct,3),
        "baseline":asdict(s),
    }
