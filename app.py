"""
OpenDeepResearcher — Full Production App
Milestone 1: Foundation (LM Studio + Tavily + dotenv)
Milestone 2: Core agents (Planner → Searcher → Writer via LangGraph)
Milestone 3: UI + Session Memory (MemorySaver, thread tracking, chat persistence)
Milestone 4: Report generation (structured output, citations, timestamps, PDF/MD export)
"""

import streamlit as st
import os
import uuid
import json
from datetime import datetime
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, Annotated, List
import operator

from agents.planner import Planner
from agents.searcher import Searcher
from agents.writer import Writer
load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────────────────────────────────────
MAX_TURNS   = 10
CHATS_FILE  = "chats.json"   # persistent thread storage across restarts

# ─────────────────────────────────────────────────────────────────────────────
#  Page config
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="OpenDeepResearcher",
    page_icon="◎",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
#  CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500&display=swap');

:root {
    --bg:      #111110;
    --bg2:     #1a1917;
    --bg3:     #222120;
    --border:  rgba(255,255,255,0.08);
    --border2: rgba(255,255,255,0.14);
    --txt:     #e8e4de;
    --txt2:    #888580;
    --txt3:    #555250;
    --accent:  #d4884a;
    --accent2: #a86a34;
    --green:   #4a9e6e;
    --red:     #c05050;
    --blue:    #5b8dd9;
    --mono:    'IBM Plex Mono', monospace;
    --sans:    'IBM Plex Sans', sans-serif;
    --r:       8px;
}
body {
    font-size: 16px !important;
}
html,body,[class*="css"],.stApp {
    font-family: var(--sans) !important;
    background:  var(--bg) !important;
    color:       var(--txt) !important;
}
#MainMenu,footer,header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background:   var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] .stButton > button {
    background:    var(--bg3) !important;
    color:         var(--txt) !important;
    border:        1px solid var(--border) !important;
    border-radius: var(--r) !important;
    font-family:   var(--sans) !important;
    font-size:     0.8rem !important;
    font-weight:   400 !important;
    padding:       8px 12px !important;
    width:         100% !important;
    text-align:    left !important;
    transition:    all .15s !important;
    margin-bottom: 2px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background:   var(--bg) !important;
    border-color: var(--border2) !important;
}

/* new thread button override */
.new-thread-wrap .stButton > button {
    background:  var(--accent) !important;
    color:       #fff !important;
    border:      none !important;
    font-weight: 500 !important;
    margin-bottom: 12px !important;
}
.new-thread-wrap .stButton > button:hover { background: var(--accent2) !important; }

/* ── Sidebar elements ── */
.agent-hdr {
    display: flex; align-items: center; gap: 10px;
    padding: 2px 0 16px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 14px;
}
.agent-orb {
    width: 30px; height: 30px;
    border: 1.5px solid var(--accent);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; color: var(--accent);
    flex-shrink: 0;
}
.agent-name { font-size: 0.86rem; font-weight: 500; color: var(--txt); }
.agent-ver  { font-size: 0.67rem; color: var(--txt3); font-family: var(--mono); }

.sec-lbl {
    font-size: 0.62rem; font-weight: 500;
    text-transform: uppercase; letter-spacing: 1.5px;
    color: var(--txt3); padding: 10px 0 5px;
    font-family: var(--mono);
}
.thread-row {
    padding: 7px 10px; border-radius: var(--r);
    font-size: 0.79rem; color: var(--txt2);
    border: 1px solid transparent;
    margin-bottom: 2px;
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    transition: all .12s;
}
.thread-row:hover { background: var(--bg3); border-color: var(--border); color: var(--txt); }
.thread-row.active { background: var(--bg3); border-color: var(--accent); color: var(--txt); }
.thread-meta { font-size: 0.63rem; color: var(--txt3); font-family: var(--mono); margin-top: 1px; }

.mem-badge {
    display: inline-flex; align-items: center; gap: 5px;
    background: var(--bg3); border: 1px solid var(--border);
    border-radius: 20px; padding: 3px 9px;
    font-size: 0.69rem; color: var(--txt2); font-family: var(--mono);
    margin-bottom: 8px;
}
.mem-badge .dot { width: 5px; height: 5px; border-radius: 50%; background: var(--green); }

.stat-blk { padding-top: 14px; border-top: 1px solid var(--border); }
.stat-row { display: flex; align-items: center; gap: 7px; font-size: 0.72rem; color: var(--txt3); padding: 3px 0; font-family: var(--mono); }
.sdot { width: 5px; height: 5px; border-radius: 50%; flex-shrink: 0; }
.sdot.ok  { background: var(--green); }
.sdot.err { background: var(--red); }

/* ── Top bar ── */
.topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 28px; border-bottom: 1px solid var(--border);
    background: var(--bg);
}
.thread-pill { display: flex; align-items: center; gap: 8px; font-size: 0.77rem; font-family: var(--mono); color: var(--txt2); }
.tid-badge   { background: var(--bg3); border: 1px solid var(--border); border-radius: 4px; padding: 3px 8px; font-size: 0.69rem; color: var(--accent); font-family: var(--mono); }
.turn-count  { font-size: 0.69rem; font-family: var(--mono); color: var(--txt3); }

/* ── Messages ── */
.msg {
    display: flex; gap: 14px; align-items: flex-start;
    padding: 18px 0; border-bottom: 1px solid var(--border);
    animation: msgIn .22s ease;
}
@keyframes msgIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
.msg:last-child { border-bottom: none; }

.msg-icon {
    width: 28px; height: 28px; border-radius: 50%; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-family: var(--mono); margin-top: 2px;
}
.msg-icon.u { background: var(--bg3); border: 1px solid var(--border2); color: var(--txt2); }
.msg-icon.a { background: var(--bg3); border: 1.5px solid var(--accent); color: var(--accent); font-size: 13px; }

.msg-body { flex: 1; min-width: 0; }
.msg-role { font-size: 0.67rem; font-family: var(--mono); color: var(--txt3); margin-bottom: 6px; text-transform: uppercase; letter-spacing: 1px; }
.msg-text {
    font-size: 1.05rem !important;
    line-height: 1.75;
    color: var(--txt);
}

.ctx-tag {
    display: inline-flex; align-items: center; gap: 4px;
    background: rgba(212,136,74,0.1); border: 1px solid rgba(212,136,74,0.22);
    border-radius: 4px; padding: 2px 7px;
    font-size: 0.63rem; color: var(--accent); font-family: var(--mono);
    margin-bottom: 8px;
}

/* plan block */
.plan-blk {
    background: var(--bg2); border: 1px solid var(--border);
    border-left: 2px solid var(--accent);
    border-radius: var(--r); padding: 10px 14px; margin-bottom: 12px;
}
.blk-lbl { font-size: 0.61rem; font-family: var(--mono); color: var(--txt3); text-transform: uppercase; letter-spacing: 1.3px; margin-bottom: 7px; }
.plan-q {
    font-size: 0.95rem !important;
    color: var(--txt2);
    padding: 2px 0;
    display: flex;
    gap: 7px;
    line-height: 1.4;
}
.plan-q::before { content: "›"; color: var(--accent); flex-shrink: 0; }

/* summary */
.summary {
    font-size: 1.1rem !important;
    line-height: 1.8 !important;
    color: var(--txt);
    margin-bottom: 12px;
    white-space: pre-wrap;
}

/* sources */
.src-row { display: flex; flex-wrap: wrap; gap: 5px; margin-top: 5px; }
.src-chip {
    display: inline-flex; align-items: center; gap: 4px;
    background: var(--bg2); border: 1px solid var(--border);
    border-radius: 4px; padding: 3px 9px;
    font-size: 0.85rem !important;color: var(--txt2); font-family: var(--mono);
    text-decoration: none; max-width: 260px;
    overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
    transition: all .12s;
}
.src-chip:hover { border-color: var(--border2); color: var(--txt); }
.src-chip::before { content: "→"; opacity: .5; flex-shrink: 0; }

/* report block (milestone 4) */
.report-blk {
    background: var(--bg2); border: 1px solid var(--border);
    border-left: 2px solid var(--blue);
    border-radius: var(--r); padding: 10px 14px; margin-top: 12px;
}

/* thinking indicator */
.think-blk {
    background: var(--bg2); border: 1px solid var(--border);
    border-left: 2px solid var(--accent);
    border-radius: var(--r); padding: 12px 14px; flex: 1;
}
.think-hdr { display: flex; align-items: center; gap: 8px; font-size: 0.72rem; font-family: var(--mono); color: var(--txt2); margin-bottom: 10px; }
.dots span { display: inline-block; width: 3px; height: 3px; background: var(--accent); border-radius: 50%; animation: bl 1.2s ease-in-out infinite; margin-right: 2px; }
.dots span:nth-child(2) { animation-delay: .2s; }
.dots span:nth-child(3) { animation-delay: .4s; }
@keyframes bl { 0%,80%,100% { opacity: .2; } 40% { opacity: 1; } }
.step { display: flex; align-items: center; gap: 8px; font-size: 0.78rem; font-family: var(--mono); color: var(--txt3); padding: 3px 0; }
.step.active { color: var(--accent); }
.step.done   { color: var(--txt2); }
.step-i { width: 14px; text-align: center; flex-shrink: 0; }
.pbar  { height: 1px; background: var(--border); margin-top: 12px; overflow: hidden; border-radius: 1px; }
.pfill { height: 100%; background: var(--accent); transition: width .5s ease; border-radius: 1px; }

/* ── Input ── */
.input-frame { background: transparent; padding: 20px 20px 40px; display: flex; flex-direction: column; align-items: center; margin-top: 20px; }

/* The stForm itself acts as the pill search box */
[data-testid="stForm"] {
    background: var(--bg2) !important; 
    border: 1px solid var(--border) !important;
    border-radius: 28px !important;
    width: 100% !important; max-width: 680px !important;
    margin: 0 auto !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
    padding: 2px 6px 2px 20px !important;
    transition: box-shadow .2s, border-color .2s;
}
[data-testid="stForm"]:hover, [data-testid="stForm"]:focus-within {
    box-shadow: 0 4px 16px rgba(0,0,0,0.3) !important;
    border-color: var(--accent) !important;
}

.stTextInput > div > div > input {
    background: transparent !important; border: none !important;
    box-shadow: none !important; padding: 12px 14px 12px 0 !important;
    font-size: 1.05rem !important; color: var(--txt) !important;
    font-family: var(--sans) !important;
    caret-color: var(--accent) !important;
}
.stTextInput > div > div > input::placeholder { color: var(--txt3) !important; font-weight: 300 !important; }
[data-baseweb="input"], [data-baseweb="base-input"] { background: transparent !important; border: none !important; }

[data-testid="stForm"] button {
    background: var(--accent) !important; color: #ffffff !important;
    border: 1px solid var(--accent) !important; border-radius: 50% !important;
    font-family: var(--sans) !important; font-size: 1.25rem !important;
    font-weight: 500 !important; padding: 0 !important;
    height: 40px !important; width: 40px !important;
    margin: 0 0 0 auto !important; transition: all .15s !important;
    display: flex !important; align-items: center !important; justify-content: center !important;
}
[data-testid="stForm"] button:hover { 
    background: #4a7ec2 !important; color: #ffffff !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.15) !important; 
    border: 1px solid #4a7ec2 !important;
}

.input-footer { display: flex; justify-content: center; align-items: center; padding: 16px 12px 0; font-size: 0.72rem; color: var(--txt3); font-family: var(--mono); gap: 12px; }
.mi-dot { width: 5px; height: 5px; border-radius: 50%; background: var(--green); display: inline-block; animation: pulse 2s ease-in-out infinite; }
@keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: .3; } }

/* Clean popover button */
div[data-testid="stPopover"] > button {
    background: transparent !important;
    border: none !important;
    color: var(--txt3) !important;
    font-size: 0.85rem !important;
    font-family: var(--mono) !important;
    box-shadow: none !important;
    padding: 4px 0 !important;
    display: block !important;
    margin: 4px auto 0 !important;
}
div[data-testid="stPopover"] > button:hover {
    color: var(--txt) !important;
    text-decoration: underline !important;
    background: transparent !important;
}
.disclaimer { text-align: center; font-size: 0.67rem; color: var(--txt3); font-family: var(--mono); margin-top: 6px; max-width: 860px; margin-left: auto; margin-right: auto; }

/* ── Download buttons ── */
.stDownloadButton > button {
    background: var(--bg3) !important; color: var(--txt2) !important;
    border: 1px solid var(--border2) !important; border-radius: 6px !important;
    font-family: var(--mono) !important; font-size: 0.73rem !important;
    padding: 5px 12px !important; transition: all .15s !important;
}
.stDownloadButton > button:hover { border-color: var(--accent) !important; color: var(--accent) !important; }

/* ── Welcome ── */
.welcome-wrap { display: flex; flex-direction: column; align-items: center; padding: 60px 24px 32px; gap: 24px; text-align: center; }
.welcome-orb {
    width: 54px; height: 54px; border-radius: 50%;
    border: 1.5px solid var(--accent);
    display: flex; align-items: center; justify-content: center;
    font-size: 22px; color: var(--accent);
    animation: orbPulse 3s ease-in-out infinite;
}
@keyframes orbPulse { 0%,100% { box-shadow: 0 0 0 0 rgba(212,136,74,.3); } 50% { box-shadow: 0 0 0 12px rgba(212,136,74,0); } }
.welcome-title { font-size: 1.55rem; font-weight: 300; color: var(--txt); letter-spacing: -0.3px; line-height: 1.3; }
.welcome-title span { color: var(--accent); }
.welcome-sub { font-size: 0.85rem; color: var(--txt2); max-width: 400px; line-height: 1.7; }
div[data-testid="stHorizontalBlock"] .stButton > button {
    background: var(--bg2) !important; color: var(--txt) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--r) !important;
    font-family: var(--sans) !important; font-size: 0.82rem !important;
    font-weight: 400 !important; padding: 12px 14px !important;
    text-align: left !important; line-height: 1.5 !important;
    height: auto !important; min-height: 64px !important;
    white-space: pre-wrap !important;
    transition: all .15s !important; width: 100% !important; margin: 0 !important;
}
div[data-testid="stHorizontalBlock"] .stButton > button:hover {
    border-color: var(--accent) !important; background: var(--bg3) !important;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-thumb { background: var(--bg3); border-radius: 2px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  LangGraph state definition
# ─────────────────────────────────────────────────────────────────────────────
class ResearchState(TypedDict):
    messages: Annotated[List, operator.add]
    topic:    str
    plan:     List[str]
    results:  List[dict]
    summary:  str
    report:   str
    turn:     int


# ─────────────────────────────────────────────────────────────────────────────
#  Cached resources
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_memory():
    return MemorySaver()

@st.cache_resource
def get_agents():
    return Planner(), Searcher(), Writer()


# ─────────────────────────────────────────────────────────────────────────────
#  Build LangGraph pipeline
# ─────────────────────────────────────────────────────────────────────────────
def build_graph():
    planner, searcher, writer = get_agents()
    memory = get_memory()

    def planner_node(state: ResearchState) -> dict:
        ctx = _history_ctx(state.get("messages", []))
        queries = planner.plan(state["topic"], history_context=ctx)
        return {"plan": queries}

    def searcher_node(state: ResearchState) -> dict:
        results = searcher.search_many(state.get("plan", []))
        return {"results": results}

    def writer_node(state: ResearchState) -> dict:
        ctx     = _history_ctx(state.get("messages", []))
        summary = writer.summarize(state["topic"], state.get("results", []), history_context=ctx)
        # Milestone 4: also generate full structured report
        report  = writer.generate_full_report(
            state["topic"],
            state.get("plan", []),
            state.get("results", []),
            summary,
        )
        new_msgs = [
            HumanMessage(content=state["topic"]),
            AIMessage(content=summary),
        ]
        return {
            "summary":  summary,
            "report":   report,
            "turn":     state.get("turn", 0) + 1,
            "messages": new_msgs,
        }

    g = StateGraph(ResearchState)
    g.add_node("planner",  planner_node)
    g.add_node("searcher", searcher_node)
    g.add_node("writer",   writer_node)
    g.add_edge(START,     "planner")
    g.add_edge("planner", "searcher")
    g.add_edge("searcher","writer")
    g.add_edge("writer",   END)
    return g.compile(checkpointer=memory)


def _history_ctx(messages: list, n: int = 6) -> str:
    """Format last n messages as context string."""
    ctx = ""
    for m in messages[-n:]:
        role = "User" if isinstance(m, HumanMessage) else "Agent"
        ctx += f"{role}: {m.content[:250]}\n"
    return ctx


# ─────────────────────────────────────────────────────────────────────────────
#  Chat persistence (chats.json)
# ─────────────────────────────────────────────────────────────────────────────
def load_chats() -> dict:
    if os.path.exists(CHATS_FILE):
        try:
            with open(CHATS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def save_chats(threads: dict):
    # Strip non-serializable objects before saving
    serializable = {}
    for tid, tdata in threads.items():
        serializable[tid] = {
            "title":    tdata["title"],
            "created":  tdata["created"],
            "turn":     tdata["turn"],
            "messages": [
                m for m in tdata["messages"]
                if m["role"] in ("user", "assistant")
            ],
        }
    try:
        with open(CHATS_FILE, "w", encoding="utf-8") as f:
            json.dump(serializable, f, indent=2, ensure_ascii=False)
    except Exception:
        pass


# ─────────────────────────────────────────────────────────────────────────────
#  Session state init
# ─────────────────────────────────────────────────────────────────────────────
def init():
    if "threads" not in st.session_state:
        st.session_state.threads = load_chats()
    if "active_thread" not in st.session_state:
        st.session_state.active_thread = None
    if "pending" not in st.session_state:
        st.session_state.pending = None
    if "graph" not in st.session_state:
        st.session_state.graph = build_graph()

init()
tv_ok = bool(os.getenv("TAVILY_API_KEY"))


def new_thread() -> str:
    tid = str(uuid.uuid4())[:8]
    st.session_state.threads[tid] = {
        "title":    "New research",
        "created":  datetime.now().strftime("%H:%M"),
        "turn":     0,
        "messages": [],
    }
    st.session_state.active_thread = tid
    save_chats(st.session_state.threads)
    return tid


def active_data():
    tid = st.session_state.active_thread
    return st.session_state.threads.get(tid) if tid else None


# ─────────────────────────────────────────────────────────────────────────────
#  Research runner
# ─────────────────────────────────────────────────────────────────────────────
def run_research(topic: str, thread_id: str, status_box) -> dict:

    def show(s1, s2, s3, pct):
        ic = {"wait": "○", "active": "◉", "done": "✓"}
        cl = {"wait": "step", "active": "step active", "done": "step done"}
        status_box.markdown(f"""
        <div class="msg" style="padding:14px 0">
          <div class="msg-icon a">◎</div>
          <div class="think-blk">
            <div class="think-hdr">processing
              <div class="dots"><span></span><span></span><span></span></div>
            </div>
            <div class="{cl[s1]}"><span class="step-i">{ic[s1]}</span> planning queries</div>
            <div class="{cl[s2]}"><span class="step-i">{ic[s2]}</span> searching web</div>
            <div class="{cl[s3]}"><span class="step-i">{ic[s3]}</span> writing report</div>
            <div class="pbar"><div class="pfill" style="width:{pct}%"></div></div>
          </div>
        </div>""", unsafe_allow_html=True)

    show("active", "wait", "wait", 5)

    # Build existing message history for LangGraph continuity
    thread_data = st.session_state.threads.get(thread_id, {})
    existing_msgs = []
    for m in thread_data.get("messages", []):
        if m["role"] == "user":
            existing_msgs.append(HumanMessage(content=m["content"]))
        elif m["role"] == "assistant":
            existing_msgs.append(AIMessage(content=m.get("data", {}).get("summary", "")))

    config = {"configurable": {"thread_id": thread_id}}

    show("active", "wait", "wait", 15)
    result = st.session_state.graph.invoke(
        {
            "messages": existing_msgs,
            "topic":    topic,
            "plan":     [],
            "results":  [],
            "summary":  "",
            "report":   "",
            "turn":     thread_data.get("turn", 0),
        },
        config=config,
    )
    show("done", "done", "done", 100)
    status_box.empty()

    return {
        "topic":   topic,
        "queries": result.get("plan", []),
        "sources": result.get("results", []),
        "summary": result.get("summary", ""),
        "report":  result.get("report", ""),
        "turn":    result.get("turn", 1),
        "ts":      datetime.now().strftime("%H:%M · %d %b %Y"),
    }


# ─────────────────────────────────────────────────────────────────────────────
#  Main area
# ─────────────────────────────────────────────────────────────────────────────
tdata = active_data()
tid   = st.session_state.active_thread
turns = tdata.get("turn", 0) if tdata else 0

st.markdown(f"""
<div class="topbar">
  <div class="thread-pill">
    <span>thread</span>
    <span class="tid-badge">{tid or "—"}</span>
    <span class="turn-count">{turns} / {MAX_TURNS} turns</span>
  </div>
  <div style="font-size:.71rem;font-family:var(--mono);color:var(--txt3)">
    {os.getenv('LM_STUDIO_MODEL','qwen2.5-7b-instruct')} · {datetime.now().strftime('%d %b %Y')}
  </div>
</div>""", unsafe_allow_html=True)

st.markdown('<div style="max-width:880px;margin:0 auto;padding:0 28px">', unsafe_allow_html=True)

# ── Welcome screen ────────────────────────────────────────────────────────────
if not tdata or not tdata["messages"]:
    st.markdown("<br><br><br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div class="welcome-wrap">
      <div class="welcome-orb">◎</div>
      <div>
        <div class="welcome-title">Research <span>Agent</span></div>
        <div class="welcome-sub" style="margin-top:8px">
          Every prompt builds on the last. The agent remembers your full thread context,
          searches the web, and generates a citable structured report.
        </div>
      </div>
    </div>""", unsafe_allow_html=True)



# ── Thread messages ───────────────────────────────────────────────────────────
else:
    for i, msg in enumerate(tdata["messages"]):
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="msg">
              <div class="msg-icon u">you</div>
              <div class="msg-body">
                <div class="msg-role">user · turn {msg.get('turn', '')}</div>
                <div class="msg-text">{msg['content']}</div>
              </div>
            </div>""", unsafe_allow_html=True)

          
            

        elif msg["role"] == "assistant":
            d       = msg["data"]
            ctx_tag = '<div class="ctx-tag">◎ context from memory</div>' if i > 1 else ""
            
            plan_html = ""
            if d.get("queries"):
                qs = "".join(f'<div class="plan-q">{q}</div>' for q in d["queries"])
                plan_html = f'<div class="plan-blk"><div class="blk-lbl">Research Plan</div>{qs}</div>'

            seen, chips = set(), ""
            for s in d.get("sources", []):
                url   = s.get("url", "")
                title = s.get("title", url)[:52].replace("<", "").replace(">", "")
                if url and url not in seen:
                    seen.add(url)
                    safe_url = url.replace('"', '')
                    chips += f'<a href="{safe_url}" class="src-chip" style="color:var(--txt2); text-decoration:none; padding:4px 10px; background:var(--bg2); border:1px solid var(--border); border-radius:6px; font-size:0.85rem;" target="_blank">{title}</a>'

            srcs_html = ""
            if chips:
                srcs_html = f"""<div style="margin-top:20px;">
<div class="blk-lbl">🔗 Sources ({len(seen)} cited)</div>
<div class="src-row" style="display:flex; flex-wrap:wrap; gap:8px;">{chips}</div>
</div>"""

            st.markdown(f"""
<div class="msg" style="border-bottom:none; padding-bottom:5px;">
  <div class="msg-icon a">◎</div>
  <div class="msg-body">
    <div class="msg-role" style="margin-bottom:8px;">agent · turn {d.get('turn','')} · {d.get('ts','')}</div>
{ctx_tag}
{plan_html}
  </div>
</div>""", unsafe_allow_html=True)

            st.markdown(f"""
<div style="margin-left:42px; border-bottom:1px solid var(--border); padding-bottom:24px;">

{d.get("summary", "")}

{srcs_html}

</div>
""", unsafe_allow_html=True)

            # Milestone 4 — Download report buttons
            report_md = d.get("report", "")
            if report_md:
                dl1, dl2, _ = st.columns([1, 1, 4])
                with dl1:
                    st.download_button(
                        "⬇ Download .md",
                        data=report_md.encode("utf-8"),
                        file_name=f"report_{d.get('turn','')}.md",
                        mime="text/markdown",
                        key=f"dl_md_{i}",
                    )
                with dl2:
                    # Plain text export as .txt fallback (PDF needs fpdf2)
                    st.download_button(
                        "⬇ Download .txt",
                        data=report_md.encode("utf-8"),
                        file_name=f"report_{d.get('turn','')}.txt",
                        mime="text/plain",
                        key=f"dl_txt_{i}",
                    )

    if turns >= MAX_TURNS:
        st.warning(f"This thread has reached {MAX_TURNS} turns. Start a new thread to keep memory sharp.")

st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  Input bar
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="input-frame">', unsafe_allow_html=True)

with st.form("chat_form", clear_on_submit=True):
    c1, c2 = st.columns([5, 1], vertical_alignment="center")
    with c1:
        user_input = st.text_input(
            "q", "",
            placeholder="Search Research Agent or type a prompt...",
            label_visibility="collapsed",
        )
    with c2:
        submitted = st.form_submit_button("↑")

st.markdown(f"""
<div class="input-footer">
  <div style="display:flex;align-items:center;gap:6px">
    <div class="mi-dot"></div>
    memory active · {turns} / {MAX_TURNS} turns
  </div>
</div>""", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

c_left, c_mid, c_right = st.columns([3, 2, 3])
with c_mid:
    with st.popover("📜 Recent Threads", use_container_width=True):
        if st.button("＋  New thread", key="new_thread_btn_pop"):
            new_thread()
            st.rerun()

        if st.session_state.threads:
            for tid_, tdata_ in reversed(list(st.session_state.threads.items())):
                active_str = " (Active)" if tid_ == st.session_state.active_thread else ""
                label_ = tdata_["title"][:40] + ("…" if len(tdata_["title"]) > 40 else "")
                turns_ = tdata_.get("turn", 0)

                st.markdown(f"**{label_}**{active_str}  \n*{tdata_['created']} · {turns_}/{MAX_TURNS} turns*")

                col_a, col_b = st.columns([3, 1])
                with col_a:
                    if st.button("Open", key=f"open_{tid_}"):
                        st.session_state.active_thread = tid_
                        st.rerun()
                with col_b:
                    if st.button("✕", key=f"del_{tid_}"):
                        del st.session_state.threads[tid_]
                        if st.session_state.active_thread == tid_:
                            st.session_state.active_thread = None
                        save_chats(st.session_state.threads)
                        st.rerun()
                st.markdown("---")
        else:
            st.write("No recent threads.")
st.markdown(
    '<div class="disclaimer">agent may make mistakes · verify critical findings · '
    'chats saved to chats.json · memory resets on server restart</div>',
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
#  Handle topic submission
# ─────────────────────────────────────────────────────────────────────────────
def handle(topic: str):
    t_id = st.session_state.active_thread or new_thread()
    td   = st.session_state.threads[t_id]
    cur  = td["turn"] + 1

    if td["turn"] == 0:
        td["title"] = topic[:38]

    td["messages"].append({"role": "user", "content": topic, "turn": cur})

    status_box = st.empty()
    try:
        result       = run_research(topic, t_id, status_box)
        result["turn"] = cur
        td["messages"].append({"role": "assistant", "data": result})
        td["turn"] = cur
        save_chats(st.session_state.threads)   # persist after each turn
    except Exception as e:
        status_box.empty()
        st.error(
            f"Agent error: {e}\n\n"
            "Check:\n"
            "• LM Studio is running on port 1234\n"
            "• A model is loaded in LM Studio\n"
            "• TAVILY_API_KEY is set in .env"
        )
    st.rerun()


if st.session_state.pending:
    t = st.session_state.pending
    st.session_state.pending = None
    handle(t)

if submitted and user_input.strip():
    handle(user_input.strip())
