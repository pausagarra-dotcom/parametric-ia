# SP-8: servidor HTTP minim DINS de Rhino 9 (s'executa amb run_python o RhinoCode).
# Manté obert el .gh de la textura 03 en memoria (no es desa ni es modifica) i respon a:
#   GET /ping                  -> {"ok": true}
#   GET /set?name=DEPTH&v=0.5  -> canvia el slider, resol i torna temps i nombre de vertexs
#   GET /stop                  -> atura el servidor
# El calcul es fa al fil principal de Rhino (InvokeOnUiThread); el servidor espera el resultat.
import json, threading, time, System, Rhino
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
import scriptcontext as sc

PORT = 8765
GH_PATH = r"H:\Mi unidad\PARAMETRIC IA_New_shot\textures\03_organica_quadres\grasshopper\superficie_organica_quadres.gh"

Rhino.RhinoApp.GetPlugInObject("Grasshopper")
from Grasshopper.Kernel import GH_DocumentIO
from Grasshopper.Kernel.Special import GH_NumberSlider

state = {}


def open_doc():
    io = GH_DocumentIO(); io.Open(GH_PATH)
    d = io.Document; d.Enabled = True
    state["doc"] = d
    state["sliders"] = {o.NickName: o for o in d.Objects if isinstance(o, GH_NumberSlider)}
    t = time.time(); d.NewSolution(True); state["t_first"] = time.time() - t


def on_ui(fn):
    box = {}; ev = threading.Event(); t0 = time.time()
    def run():
        box["wait_ui_s"] = round(time.time() - t0, 3)
        try:
            box["r"] = fn()
        except Exception as e:
            box["r"] = {"error": repr(e)}
        box["t_done"] = time.time()
        ev.set()
    Rhino.RhinoApp.InvokeOnUiThread(System.Action(run))
    ev.wait(60)
    r = box.get("r", {"error": "timeout"})
    r["wait_ui_s"] = box.get("wait_ui_s")
    r["after_done_s"] = round(time.time() - box.get("t_done", time.time()), 3)
    r["server_total_s"] = round(time.time() - t0, 3)
    return r


def do_set(name, v):
    s = state["sliders"][name]; d = state["doc"]
    t = time.time()
    d.Enabled = False                       # sense aixo, canviar el valor ja llanca una solucio i despres se'n feia una altra
    s.Slider.Value = System.Decimal(float(v)); s.ExpireSolution(False)
    d.Enabled = True
    d.NewSolution(False); dt = time.time() - t
    if not state.get("count"):
        return {"solve_s": round(dt, 3)}
    nv = 0
    for o in state["doc"].Objects:
        vd = getattr(o, "VolatileData", None)
        if vd is None or not hasattr(o, "Sources"):
            continue
        for g in vd.AllData(True):
            m = getattr(g, "Value", None)
            if isinstance(m, Rhino.Geometry.Mesh) and o.Recipients.Count == 0:
                nv += m.Vertices.Count
    return {"solve_s": round(dt, 3), "mesh_vertices_out": nv}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass
    def do_GET(self):
        u = urlparse(self.path); q = parse_qs(u.query)
        if u.path == "/ping":
            r = {"ok": True}
        elif u.path == "/set":
            r = on_ui(lambda: do_set(q["name"][0], q["v"][0]))
        elif u.path == "/stop":
            r = {"stopping": True}
            threading.Thread(target=self.server.shutdown).start()
        else:
            r = {"error": "unknown"}
        b = json.dumps(r).encode()
        self.send_response(200); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)


old = sc.sticky.get("sp8_server")
if old:
    try:
        old.shutdown(); old.server_close()
    except Exception:
        pass
open_doc()
srv = HTTPServer(("127.0.0.1", PORT), H)
sc.sticky["sp8_server"] = srv
threading.Thread(target=srv.serve_forever, daemon=True).start()
print(json.dumps({"listening": PORT, "t_first_solve_s": round(state["t_first"], 2), "sliders": len(state["sliders"])}))
