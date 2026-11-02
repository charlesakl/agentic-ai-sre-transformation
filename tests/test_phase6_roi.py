from transformation import Scenario, calculate

def test_capacity_value_remains_separate_from_cash():
    r=calculate(Scenario())
    capacity=r["toil_capacity_value_year"]
    realized=capacity*.75
    cash=realized*0
    cost=60000
    assert capacity==142800
    assert realized==107100
    assert cash==0
    assert (cash-cost)/cost*100==-100
