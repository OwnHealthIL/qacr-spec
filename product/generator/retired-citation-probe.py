# Probe, not yet a guard: does any data module's PROSE cite an FR identifier that is
# not a live requirement, outside a recognised history marker?
import re, json, subprocess, sys, os
DIR = "Generator"
live = set(json.loads(subprocess.check_output(
    ["node","-e","const s=[...require('./Generator/reqs-part1.js'),...require('./Generator/reqs-part2.js')];"
     "console.log(JSON.stringify(s.flatMap(x=>x.reqs.map(r=>r[0]))))"], text=True)))
manifest = json.load(open(os.path.join(DIR,"id-manifest.json")))["issued"]
HISTORY = re.compile(r"formerly|superseded|withdrawn|originally|consolidated|Appendix D", re.I)
bad = []
for mod in ["configs.js","review.js","epics.js","spta.js"]:
    for n, line in enumerate(open(os.path.join(DIR,mod), encoding="utf-8"), 1):
        for i in set(re.findall(r"FR-[A-Z]{3}-\d{3}", line)):
            if i in live: continue
            if HISTORY.search(line): continue
            bad.append((mod, n, i, manifest.get(i,"never issued"), line.strip()[:110]))
for b in bad:
    print(f"{b[0]}:{b[1]}  {b[2]} ({b[3]})\n    {b[4]}\n")
print(f"{len(bad)} prose citation(s) of a non-live requirement")
sys.exit(1 if bad else 0)
