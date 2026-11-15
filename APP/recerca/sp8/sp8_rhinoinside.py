# SP-8: Rhino 9 dins del proces de Python (Rhino.Inside CPython, paquet rhinoinside).
# Mesura: temps de carrega, temps d'una crida simple i temps de recalcul de la textura 03 (el .gh
# s'obre en memoria, no es desa ni es modifica). Entorn: C:\dev\venvs\textura -> python -I sp8_rhinoinside.py
import time, json, os, sys
T0 = time.time()
import rhinoinside
RHINO = r"C:\Program Files\Rhino 9\System"
res = {}
# rhinoinside 0.8.2 busca .NET 9 per a Rhino 9; en aquest equip nomes hi ha .NET 10: forcem el runtime instal·lat
F = rhinoinside._DotNetFramework
def _find(self, runtimes):
    c = [rt for rt in runtimes if rt.name == "Microsoft.WindowsDesktop.App"]
    return sorted(c, key=lambda s: s.version)[-1]
F._DotNetFramework__find_runtime_spec = _find
rhinoinside.load(RHINO, "net9.0")
import System  # noqa
import Rhino  # noqa
T1 = time.time(); res["t_load_rhino_s"] = round(T1 - T0, 2)
res["rhino_version"] = str(Rhino.RhinoApp.Version)
t = time.time()
for _ in range(1000):
    Rhino.Geometry.Point3d(1, 2, 3).DistanceTo(Rhino.Geometry.Point3d(4, 5, 6))
res["t_1000_calls_ms"] = round((time.time() - t) * 1000, 1)
t = time.time()
s = Rhino.Geometry.Sphere(Rhino.Geometry.Point3d.Origin, 10).ToBrep()
m = Rhino.Geometry.Mesh.CreateFromBrep(s, Rhino.Geometry.MeshingParameters.Default)
res["t_sphere_mesh_ms"] = round((time.time() - t) * 1000, 1)
try:
    t = time.time()
    clr_ok = Rhino.RhinoApp.GetPlugInObject("Grasshopper")
    import clr
    clr.AddReference("Grasshopper")
    from Grasshopper.Kernel import GH_DocumentIO
    from Grasshopper.Kernel.Special import GH_NumberSlider
    res["t_load_gh_plugin_s"] = round(time.time() - t, 2)
    io = GH_DocumentIO()
    io.Open(r"H:\Mi unidad\PARAMETRIC IA_New_shot\textures\03_organica_quadres\grasshopper\superficie_organica_quadres.gh")
    doc = io.Document; doc.Enabled = True
    S = {o.NickName: o for o in doc.Objects if isinstance(o, GH_NumberSlider)}
    t = time.time(); doc.NewSolution(True); res["gh_first_solve_s"] = round(time.time() - t, 2)
    ts = []
    for v in (0.3, 0.5, 0.4):
        S["DEPTH"].Slider.Value = System.Decimal(v); S["DEPTH"].ExpireSolution(False)
        t = time.time(); doc.NewSolution(False); ts.append(round(time.time() - t, 2))
    res["gh_depth_solve_s"] = ts
    doc.Enabled = False; doc.Dispose()
except Exception as e:
    res["gh_error"] = repr(e)[:300]
res["t_total_s"] = round(time.time() - T0, 2)
print(json.dumps(res))
json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sp8_rhinoinside.json"), "w"), indent=1)

