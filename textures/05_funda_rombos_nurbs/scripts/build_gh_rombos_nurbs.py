# Construye en el lienzo de Grasshopper 1 abierto los dos componentes Python 3 de la textura 05
# (funda y cilindro en NURBS) con sus sliders, la salida Brep y el panel TARGET. El codigo va DENTRO del .gh.
# Se ejecuta dentro de Rhino (run_python). Guarda textures/05_funda_rombos_nurbs/grasshopper/funda_rombos_nurbs.gh
import System, Grasshopper as gh
from Grasshopper.Kernel import GH_ParameterSide
from Grasshopper.Kernel.Special import GH_NumberSlider, GH_Panel, GH_Group
from Grasshopper.GUI.Base import GH_SliderAccuracy
from Grasshopper.Kernel.Parameters import Param_Brep
ROOT = r"H:\Mi unidad\PARAMETRIC IA_New_shot\textures\05_funda_rombos_nurbs"
OUT = ROOT + r"\grasshopper\funda_rombos_nurbs.gh"
# nombre, minimo, valor, maximo, decimales (0 = entero)
PHONE = [
    ('PH_W', 40, 75, 120, 1), ('PH_H', 100, 165, 220, 1), ('PH_T', 4, 8.5, 15, 2), ('PH_R', 1, 12, 30, 1),
    ('EDGE_R', 0.5, 3, 6, 2), ('CAM_X0', 0, 8, 70, 1), ('CAM_X1', 10, 72, 75, 1), ('CAM_Y0', 80, 117, 200, 1),
    ('CAM_Y1', 90, 159, 220, 1), ('CAM_R', 0.5, 6, 20, 1),
    ('CELL_W', 2, 6.063, 15, 3), ('CELL_H', 3, 9.11, 25, 2), ('DEPTH', 0, 0.5, 2, 2), ('SUAVIDAD', 0, 1, 1, 2),
    ('GRADO', 2, 6, 9, 0), ('GAP', 0, 0.5, 2, 2),
    ('TX_A', 5, 27.5, 37, 1), ('TX_B', 10, 55, 80, 1), ('TX_CY', 10, 58, 110, 1), ('FADE_IN', 0, 0, 0.95, 2),
    ('FADE_N', 2, 2.018, 8, 3), ('FADE_MODE', 0, 0, 3, 0), ('MIN_D', 0, 0.002, 0.05, 3),
]
PHONE_GROUPS = [("Funda", 0, 10), ("Rombos", 10, 16), ("Zona y desvanecimiento", 16, 23)]
CYL = [
    ('CYL_R', 10, 40, 80, 1), ('CYL_H', 30, 100, 200, 1),
    ('CELL_W', 2, 5.52, 15, 2), ('CELL_H', 3, 9.11, 25, 2), ('DEPTH', 0, 0.5, 2, 2), ('SUAVIDAD', 0, 1, 1, 2),
    ('GRADO', 2, 6, 9, 0), ('GAP', 0, 0.5, 2, 2),
    ('ZONES', 1, 2, 6, 0), ('PHASE', 0, 0, 360, 0), ('ZONE_HALF', 10, 90, 180, 0), ('TX_B', 10, 45, 100, 0),
    ('TX_CZ', 0, 50, 200, 0), ('FADE_IN', 0, 0.3, 0.95, 2), ('FADE_N', 2, 4, 8, 1), ('FADE_MODE', 0, 0, 3, 0),
    ('MIN_D', 0, 0.002, 0.05, 3),
]
CYL_GROUPS = [("Cilindro", 0, 2), ("Rombos", 2, 8), ("Zonas y desvanecimiento", 8, 17)]

canvas = gh.Instances.ActiveCanvas
doc = gh.Kernel.GH_Document()
gh.Instances.DocumentServer.AddDocument(doc)
canvas.Document = doc
doc.Enabled = True

def build(nick, src, sliders, groups, outname, outdesc, x0, y0, color):
    comp = gh.Instances.ComponentServer.EmitObject(System.Guid("719467e6-7cf5-4848-99b0-c5dd57e5442c"))  # Python 3 Script
    comp.CreateAttributes()
    comp.NickName = nick
    comp.Hidden = True
    doc.AddObject(comp, False)
    for p in list(comp.Params.Input): comp.Params.UnregisterInputParameter(p)
    for p in list(comp.Params.Output):
        if p.NickName != 'out': comp.Params.UnregisterOutputParameter(p)
    names = [s[0] for s in sliders] + ['TARGET']
    for i, nm in enumerate(names):
        p = comp.CreateParameter(GH_ParameterSide.Input, i)
        p.NickName = nm; p.Name = nm; p.Description = nm
        comp.Params.RegisterInputParam(p)
    po = comp.CreateParameter(GH_ParameterSide.Output, comp.Params.Output.Count)
    po.NickName = outname; po.Name = outname; po.Description = outdesc
    comp.Params.RegisterOutputParam(po)
    comp.Params.OnParametersChanged(); comp.VariableParameterMaintenance()
    comp.SetSource(open(src, encoding='utf-8').read())
    y = y0
    for gname, a, b in groups:
        ids = System.Collections.Generic.List[System.Guid]()
        for k in range(a, b):
            nm, lo, val, hi, dec = sliders[k]
            s = GH_NumberSlider(); s.CreateAttributes(); s.NickName = nm
            s.Slider.Type = GH_SliderAccuracy.Integer if dec == 0 else GH_SliderAccuracy.Float
            s.Slider.DecimalPlaces = dec
            s.Slider.Minimum = System.Decimal(lo); s.Slider.Maximum = System.Decimal(hi)
            s.SetSliderValue(System.Decimal(val))
            s.Attributes.Pivot = System.Drawing.PointF(x0, y)
            doc.AddObject(s, False)
            comp.Params.Input[k].AddSource(s)
            ids.Add(s.InstanceGuid); y += 26
        grp = GH_Group(); grp.CreateAttributes(); grp.NickName = gname; grp.Colour = color
        doc.AddObject(grp, False)
        for gid in ids: grp.AddObject(gid)
        y += 30
    pan = GH_Panel(); pan.CreateAttributes()
    pan.NickName = 'TARGET %s (GUID)' % outname; pan.UserText = ''
    pan.Attributes.Pivot = System.Drawing.PointF(x0, y + 10)
    doc.AddObject(pan, False)
    comp.Params.Input[len(sliders)].AddSource(pan)
    comp.Attributes.Pivot = System.Drawing.PointF(x0 + 520, (y0 + y) / 2.0)
    bp = Param_Brep(); bp.CreateAttributes(); bp.NickName = outname
    bp.Attributes.Pivot = System.Drawing.PointF(x0 + 820, (y0 + y) / 2.0 + 20)
    doc.AddObject(bp, False)
    bp.AddSource(comp.Params.Output[[q.NickName for q in comp.Params.Output].index(outname)])
    return comp, bp, y

c1, b1, yend = build("Funda rombos NURBS", ROOT + r"\scripts\gh_phone_nurbs.py", PHONE, PHONE_GROUPS,
                     'funda', 'Funda con rombos (solido NURBS cerrado)', 250, 100, System.Drawing.Color.FromArgb(60, 170, 200, 230))
c2, b2, _ = build("Cilindro rombos NURBS", ROOT + r"\scripts\gh_cylinder_nurbs.py", CYL, CYL_GROUPS,
                  'cilindro', 'Cilindro con rombos (solido NURBS cerrado)', 250, yend + 120, System.Drawing.Color.FromArgb(60, 230, 200, 170))
doc.NewSolution(True)
canvas.Refresh()
io = gh.Kernel.GH_DocumentIO(doc)
io.SaveQuiet(OUT)
doc.FilePath = OUT
print("guardado", OUT, "objetos", doc.ObjectCount)
for c, b in ((c1, b1), (c2, b2)):
    print(c.NickName, "errores:", [str(m) for m in c.RuntimeMessages(gh.Kernel.GH_RuntimeMessageLevel.Error)],
          "avisos:", [str(m) for m in c.RuntimeMessages(gh.Kernel.GH_RuntimeMessageLevel.Warning)], "salida:", b.VolatileDataCount)
