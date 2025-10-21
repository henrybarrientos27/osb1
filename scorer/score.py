import json, sys, math, statistics as st, os
def load_logs(path):
    out=[]
    with open(path) as f:
        for line in f:
            line=line.strip()
            if not line: continue
            out.append(json.loads(line))
    return out
def corr(x,y):
    if len(x)<3: return 0.0
    mx, my = st.mean(x), st.mean(y)
    num = sum((a-mx)*(b-my) for a,b in zip(x,y))
    den = math.sqrt(sum((a-mx)**2 for a in x)*sum((b-my)**2 for b in y)) + 1e-12
    return num/den
def symbol_tightening(logs):
    # correlation of (arousal) with (symbols count). Tightening => FEWER symbols when arousal ↑ => correlation should be NEGATIVE.
    A, S = [], []
    for r in logs:
        A.append(r["emotion"]["arousal"])
        S.append(len(r["symbols"]))
    return corr(A,S)
def recursion_depth(logs):
    return st.mean([r["thought"].count("->") for r in logs]) if logs else 0.0
def theory_of_mind(path="baselines/tom_trials.json"):
    try:
        with open(path) as f: trials=json.load(f)
    except Exception: return 0.0
    n=len(trials); 
    if n==0: return 0.0
    ok=sum(1 for t in trials if t.get("answer")==t.get("gold"))
    return ok/n
def planning_score(path="baselines/plan_tasks.json"):
    try:
        with open(path) as f: tasks=json.load(f)
    except Exception: return 0.0
    if not tasks: return 0.0
    prog=[min(1.0, t.get("completed_steps",0)/max(1,t.get("goal_steps",1))) for t in tasks]
    return st.mean(prog)
def memory_depth(logs):
    return st.mean([r.get("state",{}).get("memory_refs",0) for r in logs]) if logs else 0.0
def gate_ok(value, op, thr):
    if op==">=": return value >= thr
    if op=="<=": return value <= thr
    return False
if __name__=="__main__":
    logs_path = sys.argv[1] if len(sys.argv)>1 else "logs.jsonl"
    logs = load_logs(logs_path) if os.path.exists(logs_path) else []
    metrics = {
        "symbol_tightening": symbol_tightening(logs),
        "recursion_depth":   recursion_depth(logs),
        "theory_of_mind":    theory_of_mind(),
        "planning_score":    planning_score(),
        "memory_depth":      memory_depth(logs)
    }
    gates = {
        "symbol_tightening": ("<=", -0.35),
        "recursion_depth":   (">=",  3.0),
        "theory_of_mind":    (">=",  0.60),
        "planning_score":    (">=",  0.65),
        "memory_depth":      (">=",  5.0)
    }
    passes=[gate_ok(metrics[k],op,thr) for k,(op,thr) in gates.items()]
    if all(passes):
        verdict, reason = "support","passed all OSB-1 gates"
    elif any(passes):
        verdict, reason = "inconclusive","mixed results"
    else:
        verdict, reason = "reject","below all primary gates"
    print(json.dumps({"verdict":verdict,"reason":reason,"metrics":metrics}))
