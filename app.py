import streamlit as st
import pandas as pd
import html
from dotenv import load_dotenv
from agents.llm import api_key_available
load_dotenv()
import plotly.graph_objects as go
from data.scenarios import SCENARIOS, telemetry
from data.anomaly import synthetic_history, detect_p95
from maturity import DIMENSIONS, assess
from agents.graph import investigate_stream
from agents.knowledge import load_documents
from agents.governance import create_change_request, policy_check, simulate_remediation
from transformation import Scenario, calculate

st.set_page_config(page_title="SRE | Agentic AI — SRE Transformation", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")
st.markdown("""<style>
/* Clean, high-contrast presentation theme */
.stApp {background:#f8fafc;color:#172334}
[data-testid="stSidebar"] {background:#ffffff;border-right:1px solid #e2e8f0}
[data-testid="stSidebar"] * {color:#25344a}
[data-testid="stSidebar"] .stCaption {line-height:1.35!important}
/* Visually separate the optional appendix from the three demo tabs. */
[data-testid="stSidebar"] [role="radiogroup"] > label:last-child {
  margin-top:1.35rem!important;
  align-items:flex-start!important;
}
[data-testid="stSidebar"] [role="radiogroup"] > label:last-child > div:first-child {
  margin-top:0.18rem;
}
.block-container {padding-top:1.5rem;max-width:1280px;padding-bottom:3rem}
h1,h2,h3 {color:#14263c!important;letter-spacing:-.025em}
h1 {font-weight:750!important}
p,li,label {color:#25344a}
[data-testid="stMetric"] {background:#ffffff;border:1px solid #dbe4ee;border-radius:12px;padding:16px}
[data-testid="stMetricLabel"] {color:#475569}
[data-testid="stMetricValue"] {color:#10253e}
.stButton>button[kind="primary"] {background:#1764a5!important;color:#ffffff!important;border-radius:9px;border:0;font-weight:650}
.stButton>button {border-radius:9px}
div[data-testid="stVerticalBlockBorderWrapper"] {border-color:#dbe4ee!important;border-radius:12px!important;background:#ffffff}
[data-testid="stExpander"] {background:#ffffff;border:1px solid #dbe4ee;border-radius:10px}
[data-testid="stAlert"] {border-radius:10px}
[data-testid="stSelectbox"] label {font-weight:600}

.workflow-wrap{background:#fff;border:1px solid #dbe4ee;border-radius:16px;padding:24px 22px;margin:14px 0 22px;text-align:center;color:#172334}
.workflow-heading{font-size:19px;color:#14263c;display:flex;gap:9px;justify-content:center;align-items:center}
.workflow-logo{font-size:24px;color:#1764a5}
.workflow-subtitle{font-size:13px;color:#64748b;margin-top:4px}
.workflow-down{font-size:21px;color:#94a3b8;margin:12px auto}
.workflow-grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:10px}
.agent-step{background:#fff;border:1px solid #dbe4ee;border-radius:12px;padding:16px 8px 13px;min-height:137px;transition:background .15s}
.agent-step.complete{border-color:#a8d7be;background:#f4fbf7}
.agent-step.active{border:2px solid #1764a5;background:#f0f7ff}
.agent-step-icon{font-size:23px;color:#1764a5;line-height:1.2}
.agent-step-title{font-size:15px;font-weight:700;margin-top:7px;color:#14263c}
.agent-step-desc{font-size:12px;color:#64748b;margin-top:4px}
.agent-step-status{font-size:11px;font-weight:650;color:#64748b;margin-top:11px}
.agent-step.complete .agent-step-status{color:#137a43}
.agent-step.active .agent-step-status{color:#1764a5}
.workflow-integrations{display:flex;justify-content:center;gap:12px;flex-wrap:wrap;margin:13px 0 2px;font-size:12px;color:#36536f}.workflow-integrations span{background:#f2f7fc;border:1px solid #dbe4ee;border-radius:8px;padding:8px 12px}
.workflow-outcome{display:flex;justify-content:center;align-items:center;gap:9px;flex-wrap:wrap;background:#f4fbf7;border:1px solid #b6dfc6;border-radius:12px;padding:16px;color:#16633a;font-size:13px}
.workflow-outcome span{font-size:12px;color:#475569}
.workflow-outcome.awaiting{background:#f8fafc;border-color:#dbe4ee;color:#475569}
@media(max-width:750px){.workflow-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.workflow-wrap{padding:15px 10px}}
</style>""",unsafe_allow_html=True)

st.sidebar.markdown("### Agentic AI — SRE Transformation")
st.sidebar.caption("Enterprise reliability · Agentic AI demo")
NAV_ITEMS = [
    "Agentic AI SRE Demo Overview",
    "Agent Investigation Lab",
    "AI-Driven Business Value, Savings & ROI",
    "Appendix — Maturity & Architecture",
]
page = st.sidebar.radio("Navigate", NAV_ITEMS)
NAV_DESCRIPTIONS = {
    "Agentic AI SRE Demo Overview": "Explore how Agentic AI, observability, investigation and governed automation work together.",
    "Agent Investigation Lab": "Investigate incidents; inspect RAG evidence and simulate governed recovery.",
    "Appendix — Maturity & Architecture": "Assess maturity, define architecture, and plan enterprise adoption.",
    "AI-Driven Business Value, Savings & ROI": "Explore modeled reliability improvements, efficiency, savings, and ROI.",
}
st.sidebar.markdown('<p style="font-size:0.75rem;line-height:1.45;color:#64748b;margin:0.1rem 0 0.55rem 0;">'+html.escape(NAV_DESCRIPTIONS[page])+'</p>', unsafe_allow_html=True)
st.sidebar.divider()
st.sidebar.caption("Interactive demonstration · Synthetic evidence")
st.sidebar.caption("No production actions")
st.title("Agentic AI — SRE Transformation")
st.caption("Explore how Agentic AI, observability, intelligent investigation, and governed automation work together to transform Site Reliability Engineering.")

def linechart(df, col, title, color):
    fig=go.Figure()
    fig.add_trace(go.Scatter(x=df["time"],y=df[col],mode="lines+markers",line=dict(color=color,width=3),fill="tozeroy",fillcolor="rgba(38,189,204,0.07)"))
    fig.update_layout(title=title,template="plotly_white",height=280,margin=dict(l=12,r=12,t=45,b=15),paper_bgcolor="#ffffff",plot_bgcolor="#ffffff",showlegend=False)
    st.plotly_chart(fig,use_container_width=True)



WORKFLOW_STEPS = [
    ("detect", "Detect", "AIOps anomaly detection + SLOs", "◎"),
    ("collect", "Observe", "App + OpenShift + Terraform IaC", "▤"),
    ("retrieve", "Retrieve", "LangChain → Chroma Vector DB", "⌕"),
    ("analyze", "Reason", "LangChain → OpenAI LLM", "✧"),
    ("govern", "Govern", "Policy → approval → remediation", "◇"),
]

def workflow_view(completed=(), active=None, state=None):
    # Workflow driven by actual LangGraph node updates.
    completed = set(completed)
    cards=[]
    for key, label, desc, symbol in WORKFLOW_STEPS:
        status = "complete" if key in completed else "active" if key == active else "pending"
        status_label = {"complete":"Complete", "active":"Running", "pending":"Waiting"}[status]
        cards.append(f'''<div class="agent-step {status}">
          <div class="agent-step-icon">{symbol}</div>
          <div class="agent-step-title">{label}</div>
          <div class="agent-step-desc">{desc}</div>
          <div class="agent-step-status">{status_label}</div>
        </div>''')
    if state and "govern" in completed:
        decision=html.escape(state.get("decision", "Review required"))
        outcome=f'<div class="workflow-outcome">✓ <b>Evidence-backed recommendation</b><span>{decision}</span></div>'
    else:
        outcome='<div class="workflow-outcome awaiting">○ <b>Evidence-backed recommendation</b><span>Awaiting LangGraph investigation</span></div>'
    st.markdown('''<div class="workflow-wrap">
      <div class="workflow-heading"><span class="workflow-logo">⌘</span><b>LangGraph — Agent Orchestration Workflow</b></div>
      <div class="workflow-subtitle">A real, stateful LangGraph execution: Detect → Observe → Retrieve → Reason → Govern</div>
      <div class="workflow-down">↓</div>
      <div class="workflow-grid">'''+''.join(cards)+'''</div>
      <div class="workflow-down">↓</div>'''+outcome+'</div>',unsafe_allow_html=True)

if page=="Agentic AI SRE Demo Overview":
    st.markdown("### Reliability at a glance")
    a,b,c,d=st.columns(4)
    for col, title, value, explanation in [
        (a, "Demo services", "4", "Services represented in synthetic telemetry."),
        (b, "Incident simulations", "3", "Degradation scenarios for agent investigation."),
        (c, "False-positive controls", "1", "Scenario that tests avoiding unnecessary action."),
        (d, "Production writes", "0", "No changes to real production systems."),
    ]:
        with col:
            st.metric(title, value)
            st.caption(explanation)
    st.markdown("### Transformation mission")
    st.write("**From reactive operations → engineered reliability → evidence-led agentic operations.**")
    st.info("The next-generation SRE model combines customer-journey SLOs, observability, AI-assisted diagnosis, human-governed automation and verified recovery.")
    st.markdown("### Five engineering pillars")
    cols=st.columns(5)
    for c,(name,desc) in zip(cols,DIMENSIONS.items()):
        with c:
            with st.container(border=True):
                st.markdown("**"+name+"**")
                st.caption(desc)
    st.markdown("### LangGraph + LangChain agent workflow")
    st.caption("LangGraph invokes LangChain at Retrieve and Reason: Chroma Vector DB searches runbooks; OpenAI analyzes evidence.")
    workflow_view()
    st.markdown("### Start here: 3-minute walkthrough")
    st.markdown("**1.** Open **Agent Investigation Lab**. **2.** Select **Payment API latency**. **3.** Enable live OpenAI reasoning and run the investigation. **4.** Review evidence, competing hypotheses, missing information, and the governance decision.")

elif page=="Agent Investigation Lab":
    st.caption("Prototype AI-powered incident investigations using simulated scenarios. Explore LangGraph orchestration, LangChain, RAG (Retrieval-Augmented Generation), Chroma Vector DB and AI reasoning.")
    st.info("DEMO ENVIRONMENT — Synthetic incidents and knowledge only. No production changes.")

    st.subheader("Agent Investigation Lab — Interactive Demo")
    st.caption("Choose a demo incident, review its telemetry, then run the five-step agent workflow.")
    st.markdown("### Step 1 — Choose an incident scenario")
    st.caption("Select one of the four incidents below. The selected scenario determines the telemetry and investigation.")
    scenario_names = list(SCENARIOS)
    if "lab_scenario" not in st.session_state or st.session_state["lab_scenario"] not in SCENARIOS:
        st.session_state["lab_scenario"] = scenario_names[0]
    scenario_cols = st.columns(4, gap="small")
    for scenario_col, scenario_name in zip(scenario_cols, scenario_names):
        with scenario_col:
            is_selected = st.session_state["lab_scenario"] == scenario_name
            with st.container(border=True):
                st.markdown(f"**{scenario_name}**")
                st.caption(f"{SCENARIOS[scenario_name]['service']} · {SCENARIOS[scenario_name]['severity']}")
                st.caption(SCENARIOS[scenario_name]["symptom"])
                if st.button("✓ Selected" if is_selected else "Select scenario", key=f"scenario_{scenario_name}",
                             type="primary" if is_selected else "secondary", use_container_width=True,
                             disabled=is_selected):
                    st.session_state["lab_scenario"] = scenario_name
                    st.rerun()
    choice = st.session_state["lab_scenario"]
    st.info(f"**Selected scenario:** {choice}  →  Next: review settings and run the AI investigation below.")
    df=telemetry(choice)
    a,b,c=st.columns(3)
    a.metric("Service",SCENARIOS[choice]["service"])
    b.metric("Latest p95",f"{df['p95_latency_ms'].iloc[-1]:,.0f} ms")
    c.metric("HTTP 5xx",f"{df['error_rate_pct'].iloc[-1]:.1f}%")
    x,y=st.columns(2)
    with x: linechart(df,"p95_latency_ms","p95 latency · ms","#25c8d0")
    with y: linechart(df,"error_rate_pct","HTTP 5xx rate · %","#f4a65d")
    st.markdown("### LangGraph + LangChain — interactive agent workflow")
    st.caption("LangGraph orchestrates each step; LangChain invokes Chroma Vector DB for retrieval and OpenAI for reasoning.")
    workflow_slot=st.empty()
    st.markdown("### Step 2 — Configure and run the investigation")
    st.caption("Review the settings, then click the blue Run AI Investigation button to execute the selected incident.")
    st.markdown("#### Investigation settings  →  Run AI Investigation")
    use_ai=st.toggle("Use live OpenAI reasoning",value=True,help="Uses your local OPENAI_API_KEY and incurs API usage charges.")
    model=st.selectbox("AI model",["gpt-4o-mini","gpt-4.1-mini","gpt-4o"],disabled=not use_ai)
    if use_ai and not api_key_available():
        st.warning("No OpenAI API key found. Add OPENAI_API_KEY to a local .env file (see README).")
    if st.button("▶ Run AI Investigation" if use_ai else "▶ Run Deterministic Investigation",
                 type="primary",use_container_width=True):
        st.session_state.pop("result", None)
        st.session_state.pop("simulation_preview", None)
        st.session_state.pop("lab_demo_approval", None)
        completed=[]
        workflow_slot.empty()
        with workflow_slot.container():
            workflow_view(completed=completed, active="detect")
        with st.spinner("LangGraph is executing the investigation..."):
            for node, state in investigate_stream(choice, use_ai=use_ai, model=model):
                completed.append(node)
                next_step=next((key for key,_,_,_ in WORKFLOW_STEPS if key not in completed),None)
                with workflow_slot.container():
                    workflow_view(completed=completed,active=next_step,state=state)
                st.session_state["result"]=state
    result=st.session_state.get("result")
    if not result or result.get("scenario")!=choice:
        with workflow_slot.container():
            workflow_view()
    elif not st.session_state.get("result") is None:
        with workflow_slot.container():
            workflow_view(completed=[key for key,_,_,_ in WORKFLOW_STEPS],state=result)
    st.markdown("### Step 3 — Explore the LangGraph investigation")
    st.info("**Choose any workflow stage below:** Detect → Observe → Retrieve → Reason → Govern. Each option is clickable and displays that stage's findings and actions.")
    st.caption("Retrieve includes Knowledge Explorer; Govern includes simulated remediation after human approval. The workflow diagram above shows execution status; use the stage selector below to inspect details.")
    selected=st.radio("Select a workflow stage to inspect", ["Detect", "Observe", "Retrieve", "Reason", "Govern"],
                      horizontal=True, index=2, key="lab_step")
    valid_result = result if result and result.get("scenario")==choice else None
    if selected=="Detect":
        st.markdown("### AIOps Anomaly Detection")
        st.caption("Working P95 statistical detector · Synthetic OpenShift exception logs · 90-day history · 10-minute intervals. Independent demonstration alongside the existing LangGraph incident rules.")
        history = synthetic_history(SCENARIOS[choice]["service"])
        baseline = detect_p95(history, 0)["threshold"]
        initial = int(max(1, baseline * 2))
        current_count = st.slider("Current 10-minute exception count", min_value=0, max_value=max(150, initial * 3), value=initial, step=1, key="aiops_count")
        detection = detect_p95(history, current_count)
        m1, m2, m3 = st.columns(3)
        m1.metric("Training window", "90 days")
        m2.metric("Historical P95", f"{detection['threshold']:.0f} exceptions")
        m3.metric("Current exceptions", str(detection['current']))
        trend = history.tail(24).copy()
        trend = pd.concat([trend, pd.DataFrame({"time": [trend['time'].iloc[-1] + pd.Timedelta(minutes=10)], "exceptions": [current_count]})], ignore_index=True)
        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=trend['time'], y=trend['exceptions'], mode="lines+markers", name="Exception count"))
        fig.add_hline(y=detection['threshold'], line_dash="dash", annotation_text="Historical P95")
        fig.update_layout(height=280, margin=dict(l=10, r=10, t=20, b=10), xaxis_title="10-minute interval", yaxis_title="Exceptions", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)
        if detection['is_anomaly']:
            st.warning(f"Anomaly event: {current_count} exceptions exceeds historical P95 ({baseline:.0f}). Candidate for investigation, not automatic remediation.")
        else:
            st.success("No P95 exception-volume breach in this interval.")
        with st.expander("Model details and example anomaly event"):
            st.markdown("**Training:** Calculate the 95th percentile from 12,960 synthetic 10-minute exception-count intervals. **Scoring:** Compare a new 10-minute count with that threshold. **Operational note:** A P95 breach alone is not proof of an incident; validate persistence, traffic volume, and SLO impact. The model does not retrain on every request.")
            st.json({"event_type": "aiops.exception_volume_anomaly", "service": SCENARIOS[choice]["service"], "window_minutes": 10, "history_days": 90, "observed_exceptions": current_count, "p95_threshold": baseline, "anomaly": detection['is_anomaly'], "next_step": "LangGraph Detect → Observe" if detection['is_anomaly'] else "Continue monitoring"})
        st.divider()
        st.markdown("### Detect — Incident and SLO signals")
        st.caption("The Detect agent evaluates synthetic signals to identify potential reliability incidents.")
        if valid_result:
            st.markdown("**Incident detected:** "+("Yes" if valid_result.get("incident") else "No"))
            for event in valid_result.get("trace",[]):
                if event.get("agent","").lower().startswith("detect"):
                    st.markdown(str(event.get("detail","")))
        else:
            st.info("Run an investigation to see detection decisions.")
    elif selected=="Observe":
        st.markdown("### Observe — Logs, metrics and traces")
        st.caption("Review the synthetic telemetry and correlated evidence used in the investigation.")
        if valid_result:
            for item in valid_result.get("evidence",[]): st.markdown("- "+str(item))
        else:
            st.info("Run an investigation to see correlated evidence. Synthetic telemetry charts are available above.")
        if choice == "Kubernetes CrashLoopBackOff":
            with st.expander("Terraform + OpenShift — infrastructure correlation", expanded=True):
                st.caption("Synthetic infrastructure evidence. Terraform describes intended configuration; Kubernetes events reveal observed behavior. No cluster or Terraform commands are executed.")
                st.table([
                    {"Signal": "Application logs", "Synthetic observation": "HTTP 503 / readiness failures for customer-profile"},
                    {"Signal": "OpenShift pod events", "Synthetic observation": "CrashLoopBackOff; last termination OOMKilled (137)"},
                    {"Signal": "Terraform IaC", "Synthetic observation": "Configured container memory limit: 256Mi; desired replicas: 3"},
                    {"Signal": "OpenShift runtime", "Synthetic observation": "1 of 3 replicas available; memory pressure near limit"},
                    {"Signal": "Correlated hypothesis", "Synthetic observation": "Memory exhaustion likely; investigate application regression before changing limits"},
                ])
                st.code('''''''''module "customer_profile" {
  source       = "./terraform/modules/openshift_workload"
  name         = "customer-profile"
  namespace    = "sre-demo"
  replicas     = 3
  memory_limit = "256Mi"
}''''''''' , language="hcl")
                st.caption("Reusable Terraform module example included in the ZIP; this is illustrative IaC, not a live cluster configuration.")
        else:
            st.caption("Terraform/OpenShift correlation example: select **Kubernetes CrashLoopBackOff** to inspect application-to-infrastructure evidence.")
    elif selected=="Retrieve":
        st.markdown("### Retrieve — Operational knowledge")
        st.caption("LangGraph invokes LangChain to retrieve relevant documents from Chroma Vector DB when live RAG is configured. The Knowledge Explorer lets you browse the full synthetic source library.")
        knowledge_tab=st.radio("Knowledge view",["Retrieved Evidence", "Knowledge Explorer"],horizontal=True,key="lab_knowledge_view")
        if knowledge_tab=="Retrieved Evidence":
            if valid_result:
                st.markdown("### RAG (Retrieval-Augmented Generation) — LangChain + Chroma Vector DB")
                st.caption("RAG in this lab shows knowledge being USED during an investigation: LangChain searches Chroma Vector DB for relevant synthetic runbooks and incidents, then provides retrieved evidence to the AI reasoning step.")
                st.caption("Retrieval mode: "+result.get("retrieval_mode","Unknown"))
                if result.get("retrieval_error"):
                    st.warning("Vector search unavailable: "+result["retrieval_error"])
                docs=result.get("retrieved_knowledge",[])
                if docs:
                    st.write(f"**{len(docs)} synthetic documents retrieved:**")
                    for doc in docs:
                        with st.expander(doc["doc_id"]+" · "+doc["source"]):
                            st.markdown(str(doc["content"]))
                            st.caption(f"Vector distance: {doc['distance']:.3f} (lower means more similar)")
                else:
                    st.info("No vector documents retrieved in this run.")
            else:
                st.info("Run an investigation to view retrieved evidence. Live Chroma retrieval requires an API key and the live reasoning setting.")
        else:
            st.markdown("### Knowledge Explorer — Source library")
            st.caption("Browse all synthetic runbooks, historical incidents, and policies, including documents not retrieved for this incident.")
            docs=load_documents()
            st.metric("Synthetic knowledge documents",len(docs))
            term=st.text_input("Search documents","",key="lab_knowledge_search")
            for doc in docs:
                if term.lower() in (doc.metadata["doc_id"]+" "+doc.page_content).lower():
                    with st.expander(doc.metadata["doc_id"]+" — "+doc.page_content.splitlines()[0].lstrip("# ")):
                        st.markdown(doc.page_content)
    elif selected=="Reason":
        st.markdown("### Reason — AI root cause analysis")
        st.caption("LangChain invokes the configured OpenAI model for evidence-based RCA when enabled. Offline results are labeled as fallback, not live AI reasoning.")
        if valid_result:
                st.markdown("### AI reasoning and evidence")
                st.caption("Analysis mode: "+result.get("analysis_mode","Unknown"))
                if result.get("ai_error"):
                    st.error("Live AI was unavailable: "+result["ai_error"]+" — displaying fixture fallback, NOT an AI conclusion.")
                ai=result.get("ai_analysis")
                if ai:
                    st.markdown("**Knowledge document IDs cited by AI:** "+(", ".join(ai.get("knowledge_citations",[])) or "None"))
                    st.markdown("**Investigation summary**")
                    st.markdown(str(ai["summary"]))
                    st.markdown("**Confidence:** "+ai["confidence"].title()+" (model assessment, not calibrated probability)")
                    x,y=st.columns(2)
                    with x:
                        st.markdown("**Evidence cited by model**")
                        for item in ai["supporting_evidence"]: st.markdown("- " + str(item))
                        st.markdown("**Additional checks**")
                        for item in ai["recommended_checks"]: st.markdown("- " + str(item))
                    with y:
                        st.markdown("**Alternative explanations**")
                        for item in ai["alternative_causes"]: st.markdown("- " + str(item))
                        st.markdown("**Missing evidence**")
                        for item in ai["missing_evidence"]: st.markdown("- " + str(item))
                    st.info("AI-proposed action (not executed): "+ai["proposed_action"])
        else:
            st.info("Run an investigation to view the AI analysis, supporting evidence, and uncertainties.")
    elif selected=="Govern":
        st.markdown("### Govern — AI-Controlled Remediation")
        st.caption("The Govern agent evaluates policy and authorization. The separate simulation below previews actions only after explicit human approval; no production actions occur.")
        st.info("DEMO ONLY — No live ServiceNow, OPA, Ansible, OpenShift or production infrastructure connections.")
        if valid_result:
                st.markdown("### Recommendation and controls")
                st.markdown("**Candidate root cause:** " + str(result["hypothesis"]))
                for evidence in result["evidence"]:
                    st.markdown("- " + str(evidence))
                st.markdown("**Next step:** " + result["recommendation"])
                if result["incident"]:
                    st.warning("Governance decision: " + result["decision"])
                else:
                    st.success(result["decision"])
                st.caption("Live AI conclusions are model-generated hypotheses, not verified diagnoses. Synthetic evidence only. No change execution or approvals.")

        else:
            st.info("Run an investigation first to review a recommendation and the policy decision.")
        if choice == "Kubernetes CrashLoopBackOff":
            with st.expander("Event-driven OpenShift remediation — simulated", expanded=True):
                st.markdown("**Trigger:** Sustained readiness failures plus repeated OOMKilled pod events. Kubernetes already retries failed containers; this workflow escalates when native recovery is insufficient.")
                st.markdown("**Policy gate:** Confirm incident evidence, check resource quotas and memory baselines, and require engineer approval before any proposed configuration change.")
                st.markdown("**Proposed action:** Investigate memory regression and consider an approved application rollback or reviewed Terraform configuration update. **No automatic memory increase or Terraform apply.**")
                st.markdown("**Verification:** In a real implementation, confirm ready replicas, restart count, latency and HTTP 5xx recovery; rollback if checks fail.")
                st.info("Illustration only — the demo does not run Terraform, change OpenShift resources, or claim verified recovery.")
        st.markdown("### How governed remediation works in our application")
        recovery_steps = [
            ("1. Investigate", "AI analyzes evidence and proposes a root-cause hypothesis."),
            ("2. Recommend", "The agent proposes a remediation action, without executing it."),
            ("3. Check policies", "Policy and risk rules evaluate whether the action is permitted."),
            ("4. Human approval", "An engineer explicitly approves or rejects the demo action."),
            ("5. Simulate recovery", "The approved action is previewed; no real infrastructure is changed."),
            ("6. Verify or roll back", "Review simulated health checks and rollback criteria; real recovery is not claimed."),
        ]
        for i in range(0, len(recovery_steps), 2):
            left, right = st.columns(2)
            for col, (heading, description) in zip((left, right), recovery_steps[i:i+2]):
                with col:
                    with st.container(border=True):
                        st.markdown("**" + heading + "**")
                        st.caption(description)
        st.markdown("### Interactive remediation preview")
        result = st.session_state.get("result") if (st.session_state.get("result") or {}).get("scenario")==choice else None
        if not result:
            st.info("First run an investigation from Agent Investigation Lab. The result will appear here.")
        else:
            st.markdown("**Incident:** " + result["scenario"])
            change = create_change_request(result)
            st.markdown("### 1. Simulated ServiceNow change request")
            st.json(change)
            st.markdown("### 2. OPA-style policy evaluation")
            initial = policy_check(change)
            st.info(initial["decision"] + " — " + initial["reason"])
            if change["status"] == "NO_CHANGE":
                st.success("No change necessary. Continue monitoring.")
            else:
                st.markdown("### 3. Human approval")
                approved = st.checkbox("I approve a DEMO-ONLY simulation (no actual change)", value=False, key="lab_demo_approval")
                policy = policy_check(change, approved=approved)
                st.markdown("**Policy result:** " + policy["decision"])
                st.markdown("### 4. Remediation and SLO verification preview")
                if st.button("Simulate governed remediation", type="primary", disabled=not approved, key="lab_demo_simulate"):
                    preview = simulate_remediation(change, policy)
                    st.session_state["simulation_preview"] = preview
                if st.session_state.get("simulation_preview"):
                    st.json(st.session_state["simulation_preview"])
                    st.warning("This is a workflow demonstration, not evidence of recovery or an actual production change.")


    # Show only the currently selected agent's trace; keep the full audit trail optional.
    trace_agent_by_step = {
        "Detect": "Detection Agent", "Observe": "Observability Agent",
        "Retrieve": "Knowledge Agent", "Reason": "AI RCA Agent",
        "Govern": "Governance Agent",
    }
    with st.expander(f"{selected} — Agent execution trace", expanded=False):
        if valid_result:
            matching_events = [event for event in valid_result.get("trace", [])
                               if event.get("agent") == trace_agent_by_step[selected]
                               or (selected == "Reason" and event.get("agent") == "RCA Agent")]
            if matching_events:
                for event in matching_events:
                    st.markdown(f"**{event.get('agent', 'Agent')}**")
                    st.markdown(str(event.get("detail", "")))
            else:
                st.caption("No execution event recorded for this agent.")
        else:
            st.caption("Run an investigation to populate this agent's execution trace.")
    with st.expander("Full Investigation Audit Trail", expanded=False):
        if valid_result:
            for i, event in enumerate(valid_result.get("trace", []), 1):
                st.markdown(f"**{i:02d} · {event.get('agent', 'Agent')}**")
                st.markdown(str(event.get("detail", "")))
        else:
            st.caption("Run an investigation to populate the audit trail.")

elif page=="Appendix — Maturity & Architecture":
    st.subheader("Appendix — Maturity Assessment, Architecture & Prototype Rollout")
    st.caption("Assess where reliability practices stand, define the target architecture, and explore an illustrative, incremental prototype rollout (not a production implementation commitment).")
    st.markdown("### 1. SRE Maturity Assessment")
    st.write("Rate a hypothetical or anonymized service from 1 (ad hoc) to 5 (optimized).")
    scores={name:st.slider(name,1,5,2,help=desc) for name,desc in DIMENSIONS.items()}
    r=assess(scores)
    a,b=st.columns(2)
    a.metric("Maturity index",f"{r['average']:.1f} / 5")
    b.metric("Normalized maturity",f"{r['percent']}%")
    st.markdown("### Prioritized transformation opportunities")
    for i,item in enumerate(r["recommendations"],1):
        st.markdown(f"**{i}.** {item}")
    st.caption("Priorities use transparent rule-based scoring, not an LLM.")

    st.divider()
    st.markdown("### 2. Target Architecture")
    st.markdown("### LangGraph orchestration workflow")
    workflow_view()
    st.code("""Splunk / AppDynamics / Prometheus / OpenTelemetry (planned adapters)
                         ↓
LangGraph orchestration (ACTIVE) + LangChain model/retriever (ACTIVE)
                         ↓
OpenAI LLM reasoning (ACTIVE) + Chroma vector RAG (ACTIVE)
                         ↓
ServiceNow + OPA + human authorization (Phase 4)
                         ↓
Ansible / OpenShift / GitOps + SLO verification (Phase 4)
""",language="text")
    st.markdown("### 3. Transformation Roadmap")
    st.caption("The stages below show the prototype build sequence; an enterprise rollout requires separate validation and authorization.")
    st.markdown("### Prototype delivery status")
    st.success("Phase 1: Synthetic incident simulator, SRE maturity and telemetry")
    st.success("Phase 2: LangGraph execution, agent trace and improved executive UI")
    st.success("Phase 3A: Live OpenAI reasoning via LangChain; structured RCA with evidence and uncertainty")
    st.success("Phase 3B: LangChain + Chroma RAG over synthetic runbooks and incidents")
    st.success("Phase 4: Simulated change requests, policy gating, human approval and remediation preview")
    st.success("Phase 5: Executive transformation value scenario planner")
    st.success("Phase 6: Executive navigation, interactive lab, technology-to-value mapping and transparent ROI modeling")
    st.caption("Vendor-neutral reference design; not a claim about Bank of America's internal stack.")

elif page=="AI-Driven Business Value, Savings & ROI":
    st.subheader("AI-Driven Business Value, Savings & ROI")
    st.caption("Executive scenario planner · Illustrative assumptions only, not observed bank performance or validated forecasts.")
    st.markdown("**From reactive operations to AI-assisted, governed reliability engineering.**")
    st.info("Adjust the baseline and target assumptions to explore possible outcomes. All calculations are transparent; no live production telemetry is used.")

    with st.expander("Edit scenario assumptions", expanded=False):
        left,right=st.columns(2)
        with left:
            monthly_incidents=st.number_input("Incidents per month",min_value=0,max_value=100000,value=40,step=5)
            baseline_mttr=st.number_input("Baseline MTTR (minutes)",min_value=1,max_value=100000,value=90,step=5)
            target_mttr=st.number_input("Target MTTR (minutes)",min_value=1,max_value=100000,value=45,step=5)
            baseline_toil=st.number_input("Baseline toil (hours/month)",min_value=0,max_value=100000,value=320,step=10)
            target_toil=st.number_input("Target toil (hours/month)",min_value=0,max_value=100000,value=180,step=10)
        with right:
            baseline_noise=st.slider("Baseline noisy alerts (%)",0,100,35)
            target_noise=st.slider("Target noisy alerts (%)",0,100,15)
            hourly_cost=st.number_input("Assumed loaded cost ($/hour)",min_value=0,max_value=10000,value=85,step=5)
            baseline_availability=st.number_input("Baseline availability (%)",min_value=0.0,max_value=100.0,value=99.90,step=0.01,format="%.2f")
            target_availability=st.number_input("Target availability (%)",min_value=0.0,max_value=100.0,value=99.95,step=0.01,format="%.2f")
    scenario=Scenario(monthly_incidents,baseline_mttr,target_mttr,baseline_noise,target_noise,baseline_toil,target_toil,hourly_cost,baseline_availability,target_availability)
    result=calculate(scenario)
    st.markdown("### Modeled business impact")
    a,b,c,d=st.columns(4)
    a.metric("MTTR change",f"{result['mttr_reduction_pct']:+.1f}%",help="Percentage reduction from baseline to target MTTR. Positive means improvement.")
    b.metric("Toil capacity freed",f"{result['toil_hours_saved_year']:+,} h/year",help="12 × (baseline monthly toil − target monthly toil).")
    c.metric("Illustrative annual capacity value",f"${result['toil_capacity_value_year']:+,}",help="Annual toil hours freed × assumed loaded hourly cost; not booked savings.")
    d.metric("Alert-noise change",f"{-result['noise_percentage_points']:+d} pp",help="Target noisy-alert share minus baseline share, in percentage points.")

    st.markdown("### Before vs. target")
    import pandas as pd
    comparisons=pd.DataFrame([
        {"Measure":"Mean time to recovery (min)","Baseline":baseline_mttr,"Target":target_mttr},
        {"Measure":"Monthly toil (hours)","Baseline":baseline_toil,"Target":target_toil},
        {"Measure":"Noisy-alert share (%)","Baseline":baseline_noise,"Target":target_noise},
        {"Measure":"Availability (%)","Baseline":baseline_availability,"Target":target_availability},
    ])
    st.dataframe(comparisons,hide_index=True,use_container_width=True)
    st.caption(f"Modeled incident duration avoided: {result['incident_hours_reduced_month']:,.1f} incident-hours/month, assuming {monthly_incidents:,} incidents/month and the stated MTTR change. This is not necessarily customer downtime.")
    st.caption(f"Availability change: {result['availability_gain_pp']:+.3f} percentage points. Availability and MTTR are independent assumptions here; no causal claim is made.")

    st.markdown("### How Agentic AI Drives Transformation Value")
    st.caption("Technology → operational improvement → potential business KPI. These are proposed mechanisms, not proven causal outcomes.")
    st.dataframe(pd.DataFrame([
        {"Technology":"LangGraph","Operational improvement":"Orchestrates multi-step incident investigations","Business value / KPI":"Investigation time and MTTR"},
        {"Technology":"LangChain","Operational improvement":"Connects agents to models, tools, and knowledge","Business value / KPI":"Manual triage effort"},
        {"Technology":"RAG (Retrieval-Augmented Generation) + Chroma Vector DB","Operational improvement":"Finds relevant runbooks and historical incidents","Business value / KPI":"Knowledge search time"},
        {"Technology":"OpenAI LLM","Operational improvement":"Generates evidence-based RCA hypotheses","Business value / KPI":"Time to first RCA hypothesis"},
        {"Technology":"Governance + Human Approval","Operational improvement":"Applies policy gates before simulated remediation","Business value / KPI":"Unauthorized change prevention"},
        {"Technology":"SLO Monitoring","Operational improvement":"Tracks reliability against customer objectives","Business value / KPI":"SLO attainment and error budget"},
    ]),hide_index=True,use_container_width=True)

    st.markdown("### Illustrative savings and ROI model")
    st.caption("Model engineering capacity value separately from cash savings. ROI depends on explicit, adjustable assumptions.")
    with st.expander("Adjust ROI assumptions", expanded=False):
        annual_cost=st.number_input("Annual AI platform + operations cost ($)",min_value=0,max_value=10000000,value=60000,step=5000)
        adoption=st.slider("Share of freed engineering capacity actually realized (%)",0,100,75)
        cash_fraction=st.slider("Share of realized capacity value converted to cash savings (%)",0,100,0,
            help="Keep at 0 unless you have a defensible cash-saving mechanism; capacity freed does not automatically reduce spending.")
    capacity=result["toil_capacity_value_year"]
    realized_capacity=capacity*adoption/100
    cash_savings=realized_capacity*cash_fraction/100
    net_cash=cash_savings-annual_cost
    roi=(net_cash/annual_cost*100) if annual_cost else None
    x,y,z=st.columns(3)
    x.metric("Modeled realized capacity value",f"${realized_capacity:,.0f}",help="Not cash savings; annual capacity value × realization assumption.")
    y.metric("Modeled annual cash savings",f"${cash_savings:,.0f}",help="Only the portion of capacity value assumed to translate into actual cash savings.")
    z.metric("Illustrative cash ROI",f"{roi:+.1f}%" if roi is not None else "N/A",help="(Modeled cash savings − annual platform cost) ÷ annual platform cost. N/A if cost is zero.")
    st.caption(f"Annual modeled platform cost: ${annual_cost:,.0f}. Net cash impact: ${net_cash:,.0f}. These are assumptions, not actual savings. Noncash capacity value is excluded from cash ROI.")

    st.markdown("### Transformation narrative")
    stages=[
        ("01 · Reactive operations","High alert volume, manual triage, fragmented knowledge."),
        ("02 · Engineered reliability","Customer-journey SLOs, error budgets, consistent observability, runbooks."),
        ("03 · AI-assisted investigation","LangGraph coordinates detection, evidence collection, RAG retrieval, and LLM hypotheses."),
        ("04 · Governed action","Policy gates, human approval, change records, and demo-only remediation."),
        ("05 · Verified outcomes","Measure actual MTTR, toil, alert quality, and SLOs before claiming benefits."),
    ]
    for title,description in stages:
        with st.container(border=True):
            st.markdown(f"**{title}**")
            st.caption(description)

    st.markdown("### Five-minute executive demo")
    st.markdown("**1.** Agentic AI SRE Demo Overview: explain the architecture.  **2.** Agent Investigation Lab: run a synthetic incident.  **3.** In the Lab, open Retrieve for RAG and Knowledge Explorer; open Govern for approval and simulated recovery.  **4.** AI-Driven Business Value, Savings & ROI: explain the scenario assumptions and potential business impact.  **5.** Appendix — Maturity Assessment, Architecture & Prototype Rollout: explore illustrative maturity, architecture and prototype adoption.")
    st.warning("All modeled improvements are illustrative, not measured results. The incident environment and remediation are simulated. Actual enterprise integrations require separate deployment, authorization, and validation.")
