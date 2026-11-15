# SP-8: client que mesura el servidor de dins de Rhino (sp8_servidor_rhino.py).
# Entorn: C:\dev\venvs\textura -> python -I sp8_client.py
import json, time, os, urllib.request

BASE = "http://127.0.0.1:8765"


def get(path):
    t = time.time()
    with urllib.request.urlopen(BASE + path, timeout=120) as r:
        data = json.loads(r.read())
    return data, time.time() - t


res = {}
pings = [get("/ping")[1] * 1000 for _ in range(20)]
res["ping_ms"] = {"min": round(min(pings), 2), "median": round(sorted(pings)[10], 2)}
calls = []
for v in (0.3, 0.5, 0.4, 0.35, 0.45):
    d, dt = get("/set?name=DEPTH&v=%s" % v)
    calls.append({"total_s": round(dt, 3), "rhino_solve_s": d.get("solve_s"), "error": d.get("error")})
res["DEPTH"] = calls
res["overhead_ms_median"] = round(sorted((c["total_s"] - (c["rhino_solve_s"] or 0)) * 1000 for c in calls)[2], 1)
print(json.dumps(res, indent=1))
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sp8_servidor.json"), "w"), indent=1)
