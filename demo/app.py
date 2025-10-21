from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse, HTMLResponse, PlainTextResponse
import json, os, subprocess, pathlib
from jsonschema import validate, ValidationError

BASE = pathlib.Path(__file__).resolve().parent.parent
LOG_SCHEMA = json.loads((BASE / "spec" / "log_schema.json").read_text())

app = FastAPI()

INDEX = """<!doctype html><html><head><meta charset=utf-8>
<title>OSB-1</title>
<style>body{font-family:system-ui,Arial,sans-serif;max-width:760px;margin:40px auto;padding:0 16px}
.card{border:1px solid #ddd;border-radius:12px;padding:16px;box-shadow:0 1px 4px rgba(0,0,0,.06)}
h1{margin-top:0} code{background:#f6f8fa;padding:2px 6px;border-radius:6px}
table{width:100%;border-collapse:collapse;margin-top:12px}
th,td{padding:8px 6px;border-bottom:1px solid #eee;text-align:left}
.ok{color:#0a7a2e;font-weight:600}.bad{color:#b00020;font-weight:600}
</style></head><body><div class=card>
<h1>OSB-1 — Open Sentience Benchmark</h1>
<p>Use the buttons below: view <code>/result</code>, download a <code>/template</code>, or upload your <code>logs.jsonl</code> to <code>/score</code>.</p>
<p>
  <a href="/result" target="_blank">View latest result JSON</a> •
  <a href="/schema" target="_blank">Log schema</a> •
  <a href="/template" target="_blank">Template logs.jsonl</a>
</p>
<form id="f" enctype="multipart/form-data" method="post" action="/score">
  <input type="file" name="logs" accept=".jsonl,.txt,.json" required>
  <button type="submit">Upload & Score</button>
</form>
<pre id="out" style="white-space:pre-wrap;margin-top:16px"></pre>
<script>
document.getElementById("f").addEventListener("submit", async (e)=>{
  e.preventDefault();
  const fd = new FormData(e.target);
  const r = await fetch("/score", {method:"POST", body: fd});
  const t = await r.text();
  document.getElementById("out").textContent = t;
});
</script>
</div></body></html>"""

@app.get("/", response_class=HTMLResponse)
def home(): return INDEX

@app.get("/result")
def result():
    p = BASE / "result.json"
    if not p.exists(): return JSONResponse({"error":"result.json not found"}, status_code=404)
    return JSONResponse(json.loads(p.read_text()))

@app.get("/schema")
def schema(): return JSONResponse(LOG_SCHEMA)

@app.get("/template", response_class=PlainTextResponse)
def template():
    # 3 example lines users can copy/fill; each line is one JSON object
    tmpl = [
      {"agent_id":"A1","t":1,"state":{"memory_refs":5},"thought":"I->I->I->I","symbols":["s1","s2"],"emotion":{"valence":0.0,"arousal":0.9}},
      {"agent_id":"A1","t":2,"state":{"memory_refs":6},"thought":"I->I->I","symbols":["s1"],"emotion":{"valence":0.1,"arousal":0.8}},
      {"agent_id":"A1","t":3,"state":{"memory_refs":5},"thought":"I->I->I->I","symbols":[],"emotion":{"valence":0.0,"arousal":0.95}}
    ]
    return "\\n".join(json.dumps(x) for x in tmpl)

def validate_jsonl(path):
    errs=[]
    with open(path,"r") as f:
        for i,line in enumerate(f, start=1):
            line=line.strip()
            if not line: continue
            try:
                obj=json.loads(line)
                validate(instance=obj, schema=LOG_SCHEMA)
            except (json.JSONDecodeError, ValidationError) as e:
                errs.append(f"line {i}: {e}")
    return errs

@app.post("/score")
async def score(logs: UploadFile = File(...)):
    up = BASE / "logs_uploaded.jsonl"
    with open(up, "wb") as f:
        f.write(await logs.read())
    errs = validate_jsonl(up)
    if errs:
        return JSONResponse({"status":"invalid","errors":errs[:10]}, status_code=400)
    out = subprocess.check_output(["python3", str(BASE / "scorer" / "score.py"), str(up)])
    (BASE / "result.json").write_bytes(out)
    return PlainTextResponse(out.decode("utf-8"))
