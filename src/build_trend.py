"""Build docs/trend.html — per-model-per-harness score over time.

Reads every snapshot and renders, for a chosen benchmark and model, one line
per harness across snapshot dates. No build step: data is inlined. With one
snapshot the lines are single points; the page becomes useful as history
accumulates from the daily cron.
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pandas as pd

from snapshot import load_history

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"


def build_payload() -> dict:
    hist = load_history()
    if hist.empty:
        return {"updated": date.today().isoformat(), "benchmarks": {}}
    rate = hist[hist["score_unit"] == "rate"]
    benches: dict[str, dict] = {}
    for bench, grp in rate.groupby("benchmark"):
        # keep only models seen under >=2 harnesses (trend only means something there)
        multi = grp.groupby("model")["scaffold"].nunique()
        grp = grp[grp["model"].isin(multi[multi >= 2].index)]
        if grp.empty:
            continue
        benches[bench] = {
            "models": sorted(grp["model"].unique()),
            "harnesses": sorted(grp["scaffold"].unique()),
            "series": {
                m: {
                    h: [[r["date"], round(float(r["score"]), 3)]
                        for r in sub.to_dict("records")]
                    for h, sub in sub.groupby("scaffold")
                }
                for m, sub in grp.groupby("model")
            },
        }
    return {"updated": date.today().isoformat(), "benchmarks": benches}


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Trend — agent-harness-evals benchmark history</title>
<meta name="description" content="Score trends over time for models and agent harnesses across benchmarks — historical view of the agent-harness-evals matrix.">
<link rel="canonical" href="https://alloevil.github.io/agent-harness-evals/trend.html">
<meta property="og:type" content="website">
<meta property="og:url" content="https://alloevil.github.io/agent-harness-evals/trend.html">
<meta property="og:title" content="Trend — agent-harness-evals benchmark history">
<meta property="og:description" content="Score trends over time for models and agent harnesses across benchmarks.">
<meta name="twitter:card" content="summary">
<style>
:root { --bg:#0d1117; --fg:#e6edf3; --dim:#8b949e; --line:#21262d; --accent:#58a6ff; }
body { margin:0; background:var(--bg); color:var(--fg); font:15px/1.5 -apple-system,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; }
main { max-width:960px; margin:0 auto; padding:2rem 1.5rem 4rem; }
h1 { font-size:1.4rem; } h1 a { color:inherit; text-decoration:none; }
label { display:block; color:var(--dim); font-size:.85rem; margin:.6rem 0 .2rem; }
select { background:var(--line); color:var(--fg); border:1px solid var(--line);
  border-radius:6px; padding:.4rem .6rem; font-size:.9rem; max-width:100%; }
svg { display:block; margin-top:1.5rem; width:100%; }
.note { color:var(--dim); font-size:.85rem; }
footer { color:var(--dim); font-size:.85rem; margin-top:2rem; } footer a { color:var(--accent); }
</style>
</head>
<body>
<main>
<h1><a href="https://github.com/alloevil/agent-harness-evals">agent-harness-evals</a> — trend</h1>
<p class="note">Score over snapshot dates, one line per harness. <a href="index.html">Back to matrix</a>.</p>
<label for="bench">benchmark</label><select id="bench"></select>
<label for="model">model</label><select id="model"></select>
<div id="chart"></div>
<footer>Snapshots from the daily cron · <a href="https://github.com/alloevil/agent-harness-evals">source</a></footer>
</main>
<script id="data" type="application/json">__DATA__</script>
<script>
const D = JSON.parse(document.getElementById('data').textContent);
const benchSel = document.getElementById('bench'), modelSel = document.getElementById('model');
Object.keys(D.benchmarks).forEach(n => {
  const o = document.createElement('option'); o.value = n; o.textContent = n; benchSel.appendChild(o);
});
function fillModels() {
  modelSel.innerHTML = '';
  D.benchmarks[benchSel.value].models.forEach(n => {
    const o = document.createElement('option'); o.value = n; o.textContent = n; modelSel.appendChild(o);
  });
}
function chart(bench, model) {
  const series = D.benchmarks[bench].series[model];
  const dates = [...new Set(Object.values(series).flat().map(p => p[0]))].sort();
  const vals = Object.values(series).flat().map(p => p[1]);
  const lo = Math.min(...vals), hi = Math.max(...vals), pad = (hi-lo)||1;
  const W = 900, H = 360, ml = 48, mr = 16, mt = 16, mb = 40;
  const x = d => ml + (dates.length===1 ? (W-ml-mr)/2 : dates.indexOf(d)*(W-ml-mr)/(dates.length-1));
  const y = v => mt + (H-mt-mb) * (1 - (v-lo)/pad);
  let g = `<svg viewBox="0 0 ${W} ${H}">`;
  for (let i=0;i<=4;i++) { const yy = mt+(H-mt-mb)*i/4, vv = hi - pad*i/4;
    g += `<line x1="${ml}" y1="${yy}" x2="${W-mr}" y2="${yy}" stroke="#21262d"/>`+
         `<text x="${ml-6}" y="${yy+4}" fill="#8b949e" font-size="11" text-anchor="end">${vv.toFixed(2)}</text>`; }
  dates.forEach(d => { const xx = x(d);
    g += `<text x="${xx}" y="${H-mb+16}" fill="#8b949e" font-size="10" text-anchor="middle">${d.slice(5)}</text>`; });
  const palette = ['#58a6ff','#3fb950','#d29922','#f778ba','#a371f7','#79c0ff','#56d4dd'];
  Object.entries(series).forEach(([h, pts], i) => {
    const pts2 = pts.slice().sort((a,b)=>a[0]<b[0]?-1:1);
    const d = pts2.map(p => `${x(p[0])},${y(p[1])}`).join(' ');
    const c = palette[i % palette.length];
    g += `<polyline points="${d}" fill="none" stroke="${c}" stroke-width="2"/>`;
    pts2.forEach(p => g += `<circle cx="${x(p[0])}" cy="${y(p[1])}" r="3" fill="${c}"/>`);
  });
  // legend
  let ly = mt;
  Object.keys(series).forEach((h,i) => {
    g += `<rect x="${W-mr-130}" y="${ly}" width="10" height="10" fill="${palette[i%palette.length]}"/>`+
         `<text x="${W-mr-114}" y="${ly+9}" fill="#e6edf3" font-size="11">${h}</text>`; ly += 15;
  });
  document.getElementById('chart').innerHTML = g + '</svg>';
}
benchSel.onchange = () => { fillModels(); chart(benchSel.value, modelSel.value); };
modelSel.onchange = () => chart(benchSel.value, modelSel.value);
if (Object.keys(D.benchmarks).length) { fillModels(); chart(benchSel.value, modelSel.value); }
else { document.getElementById('chart').innerHTML = '<p class="note">No snapshots yet — run the pipeline once and the daily cron will accumulate history.</p>'; }
</script>
</body>
</html>
"""


def build_trend() -> Path:
    DOCS.mkdir(exist_ok=True)
    payload = build_payload()
    html = TEMPLATE.replace("__DATA__", json.dumps(payload, separators=(",", ":")))
    dest = DOCS / "trend.html"
    dest.write_text(html)
    print(f"trend: {dest} ({dest.stat().st_size/1024:.0f} KB, "
          f"{len(payload['benchmarks'])} benchmarks)")
    return dest


if __name__ == "__main__":
    build_trend()
