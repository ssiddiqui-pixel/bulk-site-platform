"""Local dashboard: paste up to 10 domains -> build 10 sites -> download one ZIP.
Run:  ANTHROPIC_API_KEY=sk-... python3 dashboard/app.py   (then open http://localhost:5001)"""
import os, sys, threading, traceback, time
from flask import Flask, request, jsonify, send_file, Response

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pipeline

app = Flask(__name__)
OUT = os.path.join(HERE, "output"); os.makedirs(OUT, exist_ok=True)
JOBS = {}   # job_id -> {state, log:[], sites:[], error, zip, qa}

def log(job, msg): JOBS[job]["log"].append(msg)

def run_job(job, domains, api_key):
    J = JOBS[job]
    try:
        J["state"]="running"; log(job, f"Assigning a unique manifest for {len(domains)} site(s)…")
        manifest = pipeline.assign_manifest(domains)
        slugs = [s["slug"] for s in manifest["sites"]]
        J["sites"] = [{"brand":s["brand"],"slug":s["slug"],"domain":s["domain"],
                       "layout":s["layout"],"voice":s["voice"],"status":"queued"} for s in manifest["sites"]]
        for i, s in enumerate(manifest["sites"]):
            J["sites"][i]["status"]="writing"; log(job, f"Writing copy for {s['brand']} ({i+1}/{len(slugs)})…")
            data = pipeline.gen_content(s, api_key)
            pipeline.write_content_files(s, data)
            J["sites"][i]["status"]="building"; log(job, f"Building {s['brand']}…")
            pipeline.build_site(s["slug"])
            J["sites"][i]["status"]="done"
        log(job, "Running the QA gate across the batch…")
        code, out = pipeline.run_qa(); J["qa"] = {"passed": code==0, "report": out}
        log(job, "QA passed ✓" if code==0 else "QA reported issues (see report)")
        log(job, "Packaging ZIP…")
        zp = os.path.join(OUT, f"{job}.zip"); pipeline.zip_batch(slugs, zp); J["zip"]=zp
        pipeline.commit_registry(manifest)
        J["state"]="done"; log(job, "Done — your ZIP is ready to download.")
    except Exception as ex:
        J["state"]="error"; J["error"]=str(ex); log(job, f"ERROR: {ex}")
        traceback.print_exc()

@app.route("/api/build", methods=["POST"])
def build():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return jsonify(error="ANTHROPIC_API_KEY is not set. Export it and restart the app."), 400
    domains = [d.strip() for d in (request.json.get("domains") or []) if d.strip()][:10]
    if not domains: return jsonify(error="Enter at least one domain."), 400
    job = f"batch-{int(time.time())}"
    JOBS[job] = {"state":"queued","log":[],"sites":[],"error":None,"zip":None,"qa":None}
    threading.Thread(target=run_job, args=(job, domains, api_key), daemon=True).start()
    return jsonify(job_id=job)

@app.route("/api/status/<job>")
def status(job):
    J = JOBS.get(job)
    if not J: return jsonify(error="unknown job"), 404
    return jsonify(state=J["state"], log=J["log"], sites=J["sites"], error=J["error"],
                   qa=J["qa"], download=(f"/download/{job}" if J["zip"] else None))

@app.route("/download/<job>")
def download(job):
    J = JOBS.get(job)
    if not J or not J["zip"]: return "not ready", 404
    return send_file(J["zip"], as_attachment=True, download_name=f"{job}.zip")

@app.route("/")
def home():
    return Response(PAGE, mimetype="text/html")

PAGE = r"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Bulk Site Builder</title><style>
:root{--p:#6C4AB6;--s:#8D72E1;--bg:#0f0b1a;--card:#1a1430;--ink:#efeaff;--muted:#a99fc4;--line:#2c2447;--ok:#31c48d;--err:#f77}
*{box-sizing:border-box;margin:0;padding:0}body{font-family:system-ui,sans-serif;background:radial-gradient(900px 500px at 80% -10%,#241a44,var(--bg));color:var(--ink);min-height:100vh;padding:32px 20px}
.wrap{max-width:920px;margin:0 auto}
h1{font-size:1.9rem;letter-spacing:-.02em}.sub{color:var(--muted);margin:6px 0 26px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:22px}@media(max-width:760px){.grid{grid-template-columns:1fr}}
.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:22px}
label{font-weight:600;font-size:.9rem;display:block;margin-bottom:8px}
textarea{width:100%;min-height:230px;background:#120e24;border:1px solid var(--line);border-radius:10px;color:var(--ink);padding:12px 14px;font:14px/1.6 ui-monospace,monospace;resize:vertical}
.hint{color:var(--muted);font-size:.8rem;margin-top:8px}
button{background:linear-gradient(135deg,var(--p),var(--s));color:#fff;border:0;border-radius:999px;padding:13px 24px;font-weight:700;font-size:.95rem;cursor:pointer;margin-top:16px;width:100%}
button:disabled{opacity:.5;cursor:not-allowed}
.dl{display:inline-block;background:var(--ok);color:#062;border-radius:999px;padding:13px 24px;font-weight:800;text-decoration:none;margin-top:8px}
.row{display:flex;align-items:center;gap:10px;padding:9px 0;border-bottom:1px solid var(--line);font-size:.9rem}
.row:last-child{border:0}.badge{margin-left:auto;font-size:.72rem;font-weight:700;padding:3px 10px;border-radius:999px;background:#2c2447;color:var(--muted)}
.badge.done{background:rgba(49,196,141,.16);color:var(--ok)}.badge.writing,.badge.building{background:rgba(141,114,225,.2);color:#cbb8ff}
.log{background:#120e24;border:1px solid var(--line);border-radius:10px;padding:14px;font:12.5px/1.7 ui-monospace,monospace;color:#c9c0e6;max-height:230px;overflow:auto;white-space:pre-wrap}
.status{font-size:.85rem;color:var(--muted);margin-top:10px}
.err{color:var(--err)}.mut{color:var(--muted)}.tag{font-size:.72rem;color:var(--muted)}
.qa{margin-top:12px;font-weight:700}.qa.ok{color:var(--ok)}.qa.bad{color:var(--err)}
</style></head><body><div class="wrap">
<h1>🎰 Bulk Social-Gaming Site Builder</h1>
<p class="sub">Paste up to 10 domains (one per line). Each becomes a unique 21+ free-to-play site — distinct theme, palette, layout, voice & games — then download them all as one ZIP.</p>
<div class="grid">
<div class="card"><label>Domains (one per line, max 10)</label>
<textarea id="domains" placeholder="echo-arcade.com&#10;playwave-studio.com&#10;pixel-grove.io&#10;lumen-play.com&#10;nimbus-games.gg"></textarea>
<div class="hint">The brand name is derived from each domain, and the real domain is stamped into every page's SEO (canonical, sitemap, robots).</div>
<button id="go">Build sites</button>
<div class="status" id="keynote"></div></div>
<div class="card"><label>Progress</label>
<div id="sites"><p class="mut" style="font-size:.9rem">Sites will appear here as they build.</p></div>
<div class="qa" id="qa"></div>
<div id="dlwrap"></div>
<div class="log" id="log" style="margin-top:12px;display:none"></div></div>
</div></div>
<script>
const $=id=>document.getElementById(id);let poll=null;
$('go').onclick=async()=>{
  const domains=$('domains').value.split('\n').map(s=>s.trim()).filter(Boolean).slice(0,10);
  if(!domains.length){$('keynote').innerHTML='<span class="err">Enter at least one domain.</span>';return;}
  $('go').disabled=true;$('keynote').textContent='Starting…';$('log').style.display='block';$('log').textContent='';$('qa').textContent='';$('dlwrap').innerHTML='';
  const r=await fetch('/api/build',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({domains})});
  const j=await r.json();
  if(j.error){$('keynote').innerHTML='<span class="err">'+j.error+'</span>';$('go').disabled=false;return;}
  $('keynote').textContent='Job '+j.job_id+' running…';
  poll=setInterval(()=>refresh(j.job_id),1500);refresh(j.job_id);
};
async function refresh(job){
  const r=await fetch('/api/status/'+job);const j=await r.json();
  if(j.sites&&j.sites.length){$('sites').innerHTML=j.sites.map(s=>
    `<div class="row"><span>${s.brand}</span><span class="tag">${s.layout} · ${s.voice}</span><span class="badge ${s.status}">${s.status}</span></div>`).join('');}
  $('log').textContent=(j.log||[]).join('\n');$('log').scrollTop=$('log').scrollHeight;
  if(j.qa){$('qa').className='qa '+(j.qa.passed?'ok':'bad');$('qa').textContent=j.qa.passed?'✓ QA gate passed':'⚠ QA reported issues';}
  if(j.state==='done'){clearInterval(poll);$('go').disabled=false;$('keynote').textContent='Finished.';
    if(j.download)$('dlwrap').innerHTML='<a class="dl" href="'+j.download+'">⬇ Download ZIP ('+j.sites.length+' sites)</a>';}
  if(j.state==='error'){clearInterval(poll);$('go').disabled=false;$('keynote').innerHTML='<span class="err">'+(j.error||'failed')+'</span>';}
}
fetch('/api/status/__none__').then(()=>{});
</script></body></html>"""

if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5001"))
    print(f"\n  Bulk Site Builder → http://localhost:{port}\n  API key set: {'yes' if os.environ.get('ANTHROPIC_API_KEY') else 'NO (export ANTHROPIC_API_KEY first)'}\n")
    app.run(host="127.0.0.1", port=port, debug=False, threaded=True)
