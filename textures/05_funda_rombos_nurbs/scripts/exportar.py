# Genera la geometria con los valores por defecto del script y la guarda en .3dm, .x_t y STEP.
# Se ejecuta dentro de Rhino (run_python). Escribe primero en una carpeta local y despues copia al proyecto
# (Google Drive va lento con archivos grandes). Comprueba que el STEP se vuelve a leer como solido.
#   VARIANTE = 'phone' o 'cyl'
import Rhino, Rhino.Geometry as rg, os, shutil, time, tempfile
VARIANTE = globals().get('VARIANTE', 'phone')
ROOT = r"H:\Mi unidad\PARAMETRIC IA_New_shot\textures\05_funda_rombos_nurbs"
SRC = {'phone': 'gh_phone_nurbs.py', 'cyl': 'gh_cylinder_nurbs.py'}[VARIANTE]
OUTVAR = {'phone': 'funda', 'cyl': 'cilindro'}[VARIANTE]
NAME = {'phone': 'funda_rombos_nurbs', 'cyl': 'cilindro_rombos_nurbs'}[VARIANTE]
g = {"__name__": "gh"}
exec(open(os.path.join(ROOT, "scripts", SRC), encoding="utf-8").read(), g)
geo = g[OUTVAR]
assert geo is not None and geo.IsValid and geo.IsSolid, "la geometria no es un solido valido"
tmp = os.path.join(tempfile.gettempdir(), "rombos_nurbs"); os.makedirs(tmp, exist_ok=True)
hd = Rhino.RhinoDoc.CreateHeadless(None)
hd.ModelUnitSystem = Rhino.UnitSystem.Millimeters
lay = Rhino.DocObjects.Layer(); lay.Name = NAME; li = hd.Layers.Add(lay)
at = Rhino.DocObjects.ObjectAttributes(); at.LayerIndex = li; at.Name = NAME
hd.Objects.AddBrep(geo, at)
info = {}
for ext in ("3dm", "x_t", "stp"):
    p = os.path.join(tmp, NAME + "." + ext); t0 = time.time()
    ok = hd.Write3dmFile(p, Rhino.FileIO.FileWriteOptions()) if ext == "3dm" else hd.Export(p)
    info[ext] = (ok, round(time.time() - t0, 2), round(os.path.getsize(p) / 1e6, 2))
hd.Dispose()
# relectura del STEP
hd = Rhino.RhinoDoc.CreateHeadless(None); hd.Import(os.path.join(tmp, NAME + ".stp"))
bs = [o.Geometry for o in hd.Objects if isinstance(o.Geometry, rg.Brep)]
re = [(b.Faces.Count, b.IsValid, b.IsSolid) for b in bs]
hd.Dispose()
shutil.copy(os.path.join(tmp, NAME + ".3dm"), os.path.join(ROOT, "rhino", NAME + ".3dm"))
for ext in ("x_t", "stp"):
    shutil.copy(os.path.join(tmp, NAME + "." + ext), os.path.join(ROOT, "salida", NAME + "." + ext))
print("archivos (ok, s, MB):", info)
print("STEP releido (caras, valido, solido):", re)
