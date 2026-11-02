"""LangGraph orchestration: deterministic safety, real optional LLM RCA."""
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from data.scenarios import SCENARIOS, detect_incident, telemetry
from agents.llm import reason_about_incident
from agents.knowledge import retrieve_knowledge

class InvestigationState(TypedDict, total=False):
    scenario: str
    service: str
    incident: bool
    evidence: list[str]
    hypothesis: str
    recommendation: str
    risk: str
    decision: str
    trace: list[dict]
    use_ai: bool
    model: str
    ai_analysis: dict
    ai_error: str
    analysis_mode: str
    retrieved_knowledge: list[dict]
    retrieval_mode: str
    retrieval_error: str

def record(state, agent, detail):
    return {"trace": state.get("trace", []) + [{"agent": agent, "detail": detail}]}

def detect(state: InvestigationState):
    name = state["scenario"]
    incident = detect_incident(name)
    return {"service": SCENARIOS[name]["service"], "incident": incident,
            **record(state, "Detection Agent", f"Evaluated last six synthetic telemetry windows; sustained degradation: {incident}")}

def collect(state: InvestigationState):
    s = SCENARIOS[state["scenario"]]
    return {"evidence": s["evidence"], **record(state, "Observability Agent",
            f"Collected {len(s['evidence'])} synthetic evidence signals plus 12 telemetry samples")}

def retrieve(state: InvestigationState):
    scenario=SCENARIOS[state["scenario"]]
    query=f"{scenario['service']} {scenario['symptom']} " + " ".join(state.get("evidence",[]))
    if not state.get("use_ai",False):
        return {"retrieved_knowledge":[],"retrieval_mode":"Skipped (offline demo)",
                **record(state,"Knowledge Agent","Vector search skipped in offline demo")}
    try:
        docs=retrieve_knowledge(query,k=3)
        return {"retrieved_knowledge":docs,"retrieval_mode":"Live LangChain + Chroma",
                **record(state,"Knowledge Agent","Retrieved: "+", ".join(d["doc_id"] for d in docs))}
    except Exception as exc:
        return {"retrieved_knowledge":[],"retrieval_mode":"Unavailable","retrieval_error":str(exc),
                **record(state,"Knowledge Agent","Retrieval failed; no knowledge was supplied")}

def analyze(state: InvestigationState):
    s = SCENARIOS[state["scenario"]]
    if not state.get("use_ai", False):
        return {"hypothesis": s["hypothesis"], "analysis_mode": "Fixture (no AI call)",
                **record(state, "RCA Agent", "Predefined scenario hypothesis; AI not enabled")}
    try:
        df = telemetry(state["scenario"])
        samples = [{"time": str(row.time), "p95_latency_ms": float(row.p95_latency_ms),
                    "error_rate_pct": float(row.error_rate_pct)}
                   for row in df.itertuples(index=False)]
        analysis = reason_about_incident(
            state["scenario"], s["service"], s["symptom"], state["incident"],
            state["evidence"], samples, model=state.get("model", "gpt-4o-mini"), retrieved_knowledge=state.get("retrieved_knowledge",[]))
        return {"hypothesis": analysis["likely_cause"], "ai_analysis": analysis,
                "analysis_mode": "Live OpenAI LLM",
                **record(state, "AI RCA Agent", "OpenAI model analyzed 12 telemetry samples and scenario evidence; returned structured hypothesis and uncertainty")}
    except Exception as exc:
        # Do not silently pretend that a fixture is AI-generated.
        return {"hypothesis": s["hypothesis"], "analysis_mode": "Fallback fixture (AI failed)",
                "ai_error": str(exc),
                **record(state, "AI RCA Agent", "AI request failed. Displaying clearly labeled deterministic fallback.")}

def govern(state: InvestigationState):
    decision = "HOLD — no remediation warranted" if not state["incident"] else "REQUIRES HUMAN APPROVAL — no execution permitted"
    return {"recommendation": SCENARIOS[state["scenario"]]["recommendation"],
            "risk": "none" if not state["incident"] else "review required",
            "decision": decision,
            **record(state, "Governance Agent", decision + "; deterministic safety gate, no execution")}

def build_graph():
    graph = StateGraph(InvestigationState)
    graph.add_node("detect", detect)
    graph.add_node("collect", collect)
    graph.add_node("retrieve", retrieve)
    graph.add_node("analyze", analyze)
    graph.add_node("govern", govern)
    graph.add_edge(START, "detect")
    graph.add_edge("detect", "collect")
    graph.add_edge("collect", "retrieve")
    graph.add_edge("retrieve", "analyze")
    graph.add_edge("analyze", "govern")
    graph.add_edge("govern", END)
    return graph.compile()

def investigate(scenario: str, use_ai: bool = False, model: str = "gpt-4o-mini"):
    if scenario not in SCENARIOS:
        raise ValueError("Unknown scenario")
    return build_graph().invoke({"scenario": scenario, "trace": [], "use_ai": use_ai, "model": model})


def investigate_stream(scenario: str, use_ai: bool = False, model: str = "gpt-4o-mini"):
    """Yield (node_name, accumulated_state) after each actual LangGraph node completes."""
    if scenario not in SCENARIOS:
        raise ValueError("Unknown scenario")
    state = {"scenario": scenario, "trace": [], "use_ai": use_ai, "model": model}
    for update in build_graph().stream(state, stream_mode="updates"):
        for node, values in update.items():
            state.update(values)
            yield node, state.copy()
