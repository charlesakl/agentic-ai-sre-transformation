from transformation import Scenario, calculate
import pytest

def test_default_scenario():
    r=calculate(Scenario())
    assert r["mttr_reduction_pct"]==50
    assert r["toil_hours_saved_year"]==1680
    assert r["toil_capacity_value_year"]==142800
    assert r["noise_percentage_points"]==20
    assert r["incident_hours_reduced_month"]==30

def test_no_improvement():
    r=calculate(Scenario(target_mttr_min=90,target_toil_hours=320,target_noise_pct=35,target_availability_pct=99.90))
    assert r["mttr_reduction_pct"]==0
    assert r["toil_hours_saved_year"]==0

def test_invalid_input():
    with pytest.raises(ValueError):
        calculate(Scenario(baseline_mttr_min=0))
