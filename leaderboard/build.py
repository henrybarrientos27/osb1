import json, pathlib, csv, html
BASE=pathlib.Path(__file__).resolve().parents[1]
SUB=BASE/"submissions"; LD=BASE/"leaderboard"; LD.mkdir(exist_ok=True)
rows=[]
for p in sorted(SUB.glob("*.json")):
    try:
        obj=json.loads(p.read_text())
        sc=obj.get("score",{})
        m=sc.get("metrics",{})
        rows.append({
          "file":p.name,
          "ts":obj.get("meta",{}).get("ts",""),
          "verdict":sc.get("verdict",""),
          "symbol_tightening":m.get("symbol_tightening"),
          "recursion_depth":m.get("recursion_depth"),
          "theory_of_mind":m.get("theory_of_mind"),
          "planning_score":m.get("planning_score"),
          "memory_depth":m.get("memory_depth"),
          "rank_key": (m.get("planning_score",0)+m.get("theory_of_mind",0)+m.get("memory_depth",0)) - (m.get("symbol_tightening",0) or 0)
        })
    except Exception:
        pass
rows.sort(key=lambda r: r["rank_key"], reverse=True)
# CSV
with open(LD/"board.csv","w",newline="") as f:
    w=csv.writer(f)
    w.writerow(["rank","file","ts","verdict","symbol_tightening","recursion_depth","theory_of_mind","planning_score","memory_depth"])
    for i,r in enumerate(rows,1):
        w.writerow([i,r["file"],r["ts"],r["verdict"],r["symbol_tightening"],r["recursion_depth"],r["theory_of_mind"],r["planning_score"],r["memory_depth"]])
# HTML
def td(x): 
    if isinstance(x,float): return f"{x:.3f}"
    return html.escape(str(x))
table="".join(f"<tr><td>{i+1}</td><td>{td(r[file])}</td><td>{td(r[ts])}</td><td>{td(r[verdict])}</td><td>{td(r[symbol_tightening])}</td><td>{td(r[recursion_depth])}</td><td>{td(r[theory_of_mind])}</td><td>{td(r[planning_score])}</td><td>{td(r[memory_depth])}</td></tr>" for i,r in enumerate(rows))
(LD/"index.html").write_text(f"""<!doctype html><meta charset=utf-8><title>OSB-1 Leaderboard</title>
<style>body{{font-family:system-ui,Arial;max-width:1000px;margin:40px auto}} table{{border-collapse:collapse;width:100%}}th,td{{border:1px solid #ddd;padding:6px}} th{{background:#f6f8fa}}</style>
<h1>OSB-1 Leaderboard</h1>
<p>CSV: <a href="/leaderboard.csv">/leaderboard.csv</a></p>
<table><tr><th>Rank</th><th>File</th><th>Timestamp</th><th>Verdict</th><th>Symbol Tightening</th><th>Recursion</th><th>ToM</th><th>Planning</th><th>Memory</th></tr>{table}</table>
""")
print("leaderboard built")
