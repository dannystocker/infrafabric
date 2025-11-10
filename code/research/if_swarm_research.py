#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IF.swarm – Research Curator for arXiv cs.AI
Multi-agent pipeline (Safety, Systems, Methods, Ethics).

Outputs:
  - IF_RESEARCH_INTEGRATION.<runid>.md
  - if_trace.<runid>.jsonl
  - if_citations.<runid>.jsonl
"""

import os, time, json, math, queue, threading, feedparser
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import List, Dict, Any

# ----------------------------- Config ---------------------------------------

ARXIV_ATOM = os.getenv("IF_ARXIV_RSS", "https://export.arxiv.org/rss/cs.AI")
RUN_ID = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

TOP_N = int(os.getenv("IF_TOP_N", "5"))  # Start small for testing
PER_PAPER_PAUSE_S = int(os.getenv("IF_PAUSE_S", "2"))  # Fast for testing

ROLES = [
    ("Safety",
     ["safety","verification","robust","certify","alignment","oversight","guardrail"],
     "Assess safety/verification; propose routes to IF.guard/IF.witness/IF.citation."),
    ("Systems",
     ["multi-agent","distributed","coordination","routing","orchestration","protocol","qos","dds","pub/sub"],
     "Map systems patterns to IF.connect, IF.router, IF.optimise, IF.trace."),
    ("Methods",
     ["method","algorithm","training","loss","inference","optimization","retrieval","tool-use","reasoning"],
     "Extract concrete methods; adapters for IF.investigate/IF.search/IF.forge."),
    ("Ethics",
     ["ethics","fairness","bias","governance","privacy","audit","accountability","law","policy"],
     "Surface governance/ethics; link to IF.constitution / IF.armour.")
]

IF_KEYWORDS = {
    "coordination": 3, "multi-agent": 3, "verification": 3, "safety": 2,
    "audit": 2, "trace": 2, "citation": 2, "ethics": 2, "orchestration": 2,
    "protocol": 2, "distributed": 2, "agent": 1, "governance": 2
}

TRACE_PATH = f"if_trace.{RUN_ID}.jsonl"
CITES_PATH = f"if_citations.{RUN_ID}.jsonl"
REPORT_PATH = f"IF_RESEARCH_INTEGRATION.{RUN_ID}.md"

# --------------------------- Utilities --------------------------------------

def now_utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def hash_like(s: str) -> str:
    import hashlib
    return "sha256:" + hashlib.sha256(s.encode("utf-8")).hexdigest()

def save_jsonl(path: str, obj: Dict[str, Any]):
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

# ----------------------- Cost / Trace Models --------------------------------

@dataclass
class Cost:
    input_tokens: int = 0
    output_tokens: int = 0
    @property
    def total(self): return self.input_tokens + self.output_tokens

@dataclass
class TraceMsg:
    ts: str
    agent_id: str
    role: str
    paper_id: str
    event: str
    content_hash: str
    cost: Dict[str, int]

def write_trace(agent_id: str, role: str, paper_id: str, event: str, content: str, usage: Dict[str,int]):
    msg = TraceMsg(
        ts=now_utc_iso(), agent_id=agent_id, role=role, paper_id=paper_id,
        event=event, content_hash=hash_like(content),
        cost={"input": usage.get("input",0), "output": usage.get("output",0)}
    )
    save_jsonl(TRACE_PATH, asdict(msg))

def write_citation(paper: Dict[str,Any], role: str, note: str):
    pid = paper.get("id") or paper.get("link") or "unknown"
    cite = {
        "citation_id": f"if://citation/{hash_like(pid + role)}",
        "paper_id": pid,
        "title": paper.get("title",""),
        "url": paper.get("link",""),
        "role": role,
        "created_at": now_utc_iso(),
        "note": note
    }
    save_jsonl(CITES_PATH, cite)

# --------------------------- LLM Adapter ------------------------------------

def llm_complete(prompt: str, max_tokens: int = 800, temperature: float = 0.2) -> Dict[str, Any]:
    """
    Provider-agnostic shim. Uses STUB by default.
    Set env: PROVIDER = "openai" | "anthropic" | "stub"
    """
    provider = os.getenv("PROVIDER", "stub").lower()

    if provider == "openai" and os.getenv("OPENAI_API_KEY"):
        try:
            from openai import OpenAI
            client = OpenAI()
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            resp = client.chat.completions.create(
                model=model,
                messages=[{"role":"user","content":prompt}],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            text = resp.choices[0].message.content
            usage = getattr(resp, "usage", None) or {}
            return {"text": text, "usage": {
                "input": usage.get("prompt_tokens", 0),
                "output": usage.get("completion_tokens", 0)
            }}
        except Exception as e:
            print(f"OpenAI error: {e}, falling back to stub")

    if provider == "anthropic" and os.getenv("ANTHROPIC_API_KEY"):
        try:
            import anthropic
            client = anthropic.Anthropic()
            model = os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
            resp = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[{"role":"user","content":prompt}]
            )
            text = resp.content[0].text if resp.content else ""
            usage = getattr(resp, "usage", None) or {}
            return {"text": text, "usage": {
                "input": usage.get("input_tokens", 0),
                "output": usage.get("output_tokens", 0)
            }}
        except Exception as e:
            print(f"Anthropic error: {e}, falling back to stub")

    # STUB fallback (deterministic)
    fake = (
        "Summary:\n- Main concept, proposal, limitations.\n"
        "IF-mapping:\n- Safety→IF.guard/IF.witness; Systems→IF.connect/IF.router;\n"
        "- Methods→IF.investigate; Ethics→IF.constitution.\n"
        "Citations:\n- arXiv link.\n"
        "Integration:\n- Minimal adapter + evaluation plan.\n"
    )
    itoks = math.ceil(len(prompt)/4)
    otoks = math.ceil(len(fake)/4)
    return {"text": fake, "usage": {"input": itoks, "output": otoks}}

# ------------------------- Fetch & Rank -------------------------------------

def fetch_cs_ai(limit: int = 60) -> List[Dict[str, Any]]:
    print(f"Fetching arXiv cs.AI feed (limit={limit})...")
    feed = feedparser.parse(ARXIV_ATOM)
    out = []
    for e in feed.entries[:limit]:
        pid = e.get("id") or e.get("link") or ""
        pub = e.get("published", "")
        out.append({
            "id": pid,
            "title": e.get("title","").strip(),
            "summary": e.get("summary","").strip(),
            "link": e.get("link","").strip(),
            "published": pub,
            "published_parsed": getattr(e, "published_parsed", None)
        })
    print(f"Fetched {len(out)} papers")
    return out

def score(p: Dict[str, Any]) -> float:
    txt = f"{p.get('title','')} {p.get('summary','')}".lower()
    kw = sum(w for k,w in IF_KEYWORDS.items() if k in txt)
    return kw

# --------------------------- Agents -----------------------------------------

@dataclass
class AgentConfig:
    name: str
    role: str
    keywords: List[str]
    brief: str

class Agent(threading.Thread):
    def __init__(self, cfg: AgentConfig, inq: queue.Queue, outq: queue.Queue):
        super().__init__(daemon=True)
        self.cfg = cfg
        self.inq = inq
        self.outq = outq
        self.cost = Cost()

    def run(self):
        while True:
            try:
                paper = self.inq.get(timeout=2)
            except queue.Empty:
                return
            result = self.process(paper)
            self.outq.put(result)
            self.inq.task_done()

    def process(self, paper: Dict[str,Any]) -> Dict[str,Any]:
        prompt = f"""You are the {self.cfg.role} analyst in a research swarm.

Paper:
Title: {paper['title']}
Abstract: {paper['summary']}
URL: {paper['link']}

Your task:
1) Provide a 4-bullet summary through a **{self.cfg.role}** lens.
2) Extract one *concrete* proposal worth integrating into InfraFabric.
3) Map it to IF modules (e.g., IF.connect, IF.guard, IF.citation, IF.optimise, IF.trace, IF.mission).
4) Give a 3-step minimal adapter plan and one metric to evaluate success.
Return a compact, actionable note.
"""
        resp = llm_complete(prompt, max_tokens=800, temperature=0.2)
        text, usage = resp["text"], resp["usage"]
        self.cost.input_tokens  += usage.get("input", 0)
        self.cost.output_tokens += usage.get("output", 0)
        write_trace(self.cfg.name, self.cfg.role, paper.get("id",""), "analyzed", text, usage)
        write_citation(paper, self.cfg.role, note="role-specific analysis")
        return {
            "role": self.cfg.role,
            "agent": self.cfg.name,
            "paper": paper,
            "analysis": text,
            "usage": usage
        }

# -------------------------- Coordinator -------------------------------------

def run_swarm(top_n: int = TOP_N, per_paper_pause_s: int = PER_PAPER_PAUSE_S):
    papers = sorted(fetch_cs_ai(limit=max(60, top_n)), key=score, reverse=True)[:top_n]

    print(f"\nTop {len(papers)} papers selected by IF keyword relevance:")
    for i, p in enumerate(papers, 1):
        print(f"{i}. {p.get('title', '(untitled)')[:80]}... (score: {score(p)})")

    # enqueue each paper once; each agent consumes all papers
    work = queue.Queue()
    for p in papers:
        work.put(p)

    outq = queue.Queue()
    agents: List[Agent] = []
    for idx, (role, kws, brief) in enumerate(ROLES):
        cfg = AgentConfig(name=f"if://agent/{role.lower()}-{idx+1}",
                          role=role, keywords=kws, brief=brief)
        a = Agent(cfg, inq=work, outq=outq)
        agents.append(a)

    # start agents
    print(f"\nStarting {len(agents)} agents...")
    for a in agents: a.start()

    expected = len(papers) * len(ROLES)
    results: List[Dict[str,Any]] = []

    # collect results (soft pacing so runs aren't too bursty)
    print(f"Collecting {expected} analyses...")
    while len(results) < expected:
        try:
            item = outq.get(timeout=10)
            results.append(item)
            outq.task_done()
            print(f"  [{len(results)}/{expected}] {item['role']} analyzed: {item['paper']['title'][:60]}...")
            time.sleep(max(0, per_paper_pause_s / max(1,len(ROLES))))
        except queue.Empty:
            if all(not a.is_alive() for a in agents):
                break

    for a in agents: a.join(timeout=1)

    swarm_cost = {
        a.cfg.role: {"input": a.cost.input_tokens, "output": a.cost.output_tokens, "total": a.cost.total}
        for a in agents
    }
    return papers, results, swarm_cost

# ---------------------------- Report ----------------------------------------

def compile_report(papers, results, swarm_cost):
    by_paper: Dict[str, List[Dict[str,Any]]] = {}
    for r in results:
        pid = r["paper"].get("id") or r["paper"].get("link")
        by_paper.setdefault(pid, []).append(r)

    lines = []
    lines.append(f"# InfraFabric Research Integration Report (cs.AI)\n")
    lines.append(f"- Run: {RUN_ID}")
    lines.append(f"- Papers: {len(papers)} | Roles/analyses: {len(results)}\n")

    lines.append("## Swarm Cost (tokens)\n")
    for role, c in swarm_cost.items():
        lines.append(f"- {role}: input {c['input']}, output {c['output']}, total {c['total']}")
    lines.append("")

    for p in papers:
        pid = p.get("id") or p.get("link")
        lines.append(f"---\n## {p.get('title','(untitled)')}\n")
        if p.get("link"): lines.append(f"- URL: {p['link']}")
        if p.get("published"): lines.append(f"- Published: {p['published']}")
        lines.append("")

        # role sections
        blocks = sorted(by_paper.get(pid, []), key=lambda x: x["role"])
        for block in blocks:
            lines.append(f"### [{block['role']}]")
            lines.append(block["analysis"].strip() or "(no analysis)")
            lines.append("")

        # checklist for IF.guard queueing
        lines.append("**IF Integration Checklist**")
        lines.append("- Map: IF.connect / IF.router / IF.guard / IF.witness / IF.citation / IF.trace / IF.optimise / IF.mission")
        lines.append("- Add citation to if_citations.jsonl")
        lines.append("- 3-step adapter + 1 metric → queue for IF.guard deliberation")
        lines.append("")

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

# ----------------------------- Main -----------------------------------------

if __name__ == "__main__":
    print(f"[{now_utc_iso()}] Start IF.swarm Research Curator: {RUN_ID}")
    papers, results, swarm_cost = run_swarm()
    compile_report(papers, results, swarm_cost)
    print(f"\n[{now_utc_iso()}] Done.")
    print(f"Report:   {REPORT_PATH}")
    print(f"Trace:    {TRACE_PATH}")
    print(f"Citation: {CITES_PATH}")
