"""Regenerate the engagement's data artifacts from the public CFPB API.

Everything is public data from consumerfinance.gov; nothing is
redistributed here. Deterministic given the same API responses; the CFPB
database grows daily, so a fresh pull yields fresh complaints -- the
transcript in the README pins the run this repository records, not every
future pull.
"""
import json
import sqlite3
import subprocess
import urllib.parse
from collections import defaultdict
from pathlib import Path

BASE = "https://www.consumerfinance.gov/data-research/consumer-complaints/search/api/v1/"

def fetch(params):
    url = BASE + "?" + urllib.parse.urlencode(params)
    out = subprocess.run(["curl", "-sS", "--max-time", "120", url],
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout)["hits"]["hits"]

hits = fetch({"size": 1000, "has_narrative": "true"})
for product in ("Debt collection", "Checking or savings account",
                "Credit card", "Mortgage"):
    hits += fetch({"size": 250, "has_narrative": "true", "product": product})
hits += fetch({"size": 250, "has_narrative": "true",
               "company_response": "Closed with monetary relief"})

seen, rows = set(), []
for h in hits:
    s, cid = h["_source"], h["_id"]
    narrative = (s.get("complaint_what_happened") or "").strip()
    if cid in seen or len(narrative) < 80:
        continue
    seen.add(cid)
    if s.get("company_response") == "Untimely response":
        continue
    rows.append({"id": cid, "narrative": narrative[:3000],
                 "product": s.get("product"), "issue": s.get("issue"),
                 "response": s.get("company_response")})
rows.sort(key=lambda r: r["id"])

# fde samples refuses identical inputs with disagreeing labels -- rightly.
# 70 narratives in the first pull were byte-identical with different
# outcomes (redaction boilerplate): ambiguous ground truth, excluded.
by_text = defaultdict(set)
for r in rows:
    by_text[r["narrative"]].add(r["response"])
rows = [r for r in rows if len(by_text[r["narrative"]]) == 1]

by_class = defaultdict(list)
for r in rows:
    by_class[r["response"]].append(r)
golden, holdout = [], []
for cls, g_n, h_n in [("Closed with explanation", 50, 12),
                      ("Closed with non-monetary relief", 40, 10),
                      ("Closed with monetary relief", 30, 8)]:
    pool = by_class[cls]
    stride = max(1, len(pool) // (g_n + h_n))
    sample = pool[::stride][: g_n + h_n]
    golden += sample[:g_n]
    holdout += sample[g_n:]

def pair(r, pid):
    return {"id": pid, "verified": True, "input": r["narrative"],
            "output": {"decision": r["response"]}}

out = Path("engagement-prep")
out.mkdir(exist_ok=True)
with (out / "pairs.jsonl").open("w") as f:
    for n, r in enumerate(golden):
        f.write(json.dumps(pair(r, f"complaint-{n:03d}")) + "\n")
with (out / "holdout.jsonl").open("w") as f:
    for n, r in enumerate(holdout):
        f.write(json.dumps(pair(r, f"holdout-{n:03d}")) + "\n")

con = sqlite3.connect(out / "complaints.db")
con.execute("CREATE TABLE IF NOT EXISTS complaints "
            "(id TEXT PRIMARY KEY, narrative TEXT, product TEXT, "
            "issue TEXT, response TEXT)")
for r in rows:
    con.execute("INSERT OR REPLACE INTO complaints VALUES (?,?,?,?,?)",
                (r["id"], r["narrative"], r["product"], r["issue"], r["response"]))
con.commit()
print(f"golden {len(golden)}, holdout {len(holdout)}, db rows",
      con.execute("SELECT COUNT(*) FROM complaints").fetchone()[0])
