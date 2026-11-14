# Construeix al llenç de Grasshopper 1 obert: component Python 3 (gh_seient.py) + sliders + sortida Mesh + panell TARGET.
# S'executa dins de Rhino (run_python). Desa a textures/04_seient_colissos/grasshopper/seient_colissos.gh.
import System, Grasshopper as gh
from Grasshopper.Kernel import GH_ParameterSide
from Grasshopper.Kernel.Special import GH_NumberSlider, GH_Panel, GH_Group
from Grasshopper.GUI.Base import GH_SliderAccuracy
from Grasshopper.Kernel.Parameters import Param_Mesh
ROOT = r"H:\Mi unidad\PARAMETRIC IA_New_shot"
SRC = ROOT + r"\textures\04_seient_colissos\scripts\gh_seient.py"
OUT = ROOT + r"\textures\04_seient_colissos\grasshopper\seient_colissos.gh"
# nom, mínim, valor, màxim, decimals (0 = enter)
SLIDERS = [
    # contorn
    ('L', 150, 273.5, 350, 1), ('W', 60, 136, 200, 1), ('NOSE_W', 10, 33.4, 80, 1), ('NOSE_TAPER', 0, 0.069, 0.3, 3),
    ('WIDE_START', 20, 98, 250, 1), ('WIDE_POS', 100, 226.5, 340, 1), ('WIDE_P', 0.2, 1.78, 4, 2),
    ('REAR_DROP', 0, 25.4, 80, 1), ('REAR_R', 0.5, 10.5, 40, 1), ('NOSE_R', 0.5, 5.1, 30, 1),
    # finestra
    ('SLOT_START', 20, 75, 200, 1), ('SLOT_W1', 2, 16.4, 60, 1), ('SLOT_W2', 2, 24, 80, 1),
    ('SLOT_SPLIT', 100, 238, 340, 1), ('FLARE', 0, 0.0815, 0.5, 4), ('TIP_R', 0, 2.5, 10, 2),
    # volum
    ('THICK', 0.5, 2.5, 10, 2), ('DIP', -10, 3, 15, 1), ('KICK', -10, 4, 20, 1), ('NOSE_DROP', -10, 2, 15, 1),
    ('CROWN_NOSE', 0, 5, 30, 1), ('CROWN_REAR', 0, 14, 40, 1), ('CROWN_P', 1, 2.4, 6, 2),
    # ovals
    ('CW', 1, 4.9, 20, 2), ('CL', 2, 17.6, 50, 2), ('OVAL_W', 0.5, 3.6, 20, 2), ('OVAL_L', 0.5, 17.5, 50, 2),
    ('OVAL_Q', 1, 2.2, 6, 2), ('HEIGHT', -3, 0.8, 3, 2), ('FOLLOW_START', 0, 0.65, 0.99, 2), ('FOLLOW_OUT', 0, 1, 2, 2),
    ('COL_SHIFT', -10, 0, 10, 2), ('ROW_SHIFT', -30, 0, 30, 2), ('FOLLOW_MODE', 0, 0, 1, 0),
    # esvaïment i malla
    ('FADE_EDGE_GAP', 0, 0.5, 10, 2), ('FADE_EDGE', 0.1, 4, 30, 2), ('FADE_SLOT_GAP', 0, 0.8, 10, 2),
    ('FADE_SLOT', 0.1, 3, 30, 2), ('FADE_NOSE_START', 0, 5, 150, 1), ('FADE_NOSE', 0.1, 85, 200, 1),
    ('DETAIL', 0.15, 0.7, 3, 2),
]
GROUPS = [("Contorn", 0, 10), ("Finestra", 10, 16), ("Volum", 16, 23), ("Ovals", 23, 34), ("Esvaïment i malla", 34, 41)]
canvas = gh.Instances.ActiveCanvas
doc = gh.Kernel.GH_Document()
gh.Instances.DocumentServer.AddDocument(doc)
canvas.Document = doc
doc.Enabled = True

comp = gh.Instances.ComponentServer.EmitObject(System.Guid("719467e6-7cf5-4848-99b0-c5dd57e5442c"))  # Python 3 Script
comp.CreateAttributes()
comp.Attributes.Pivot = System.Drawing.PointF(760, 600)
comp.NickName = "Seient colissos"
comp.Hidden = True   # només es previsualitza el paràmetre Mesh 'seient' (evita la malla doble al visor)
doc.AddObject(comp, False)
for p in list(comp.Params.Input): comp.Params.UnregisterInputParameter(p)
for p in list(comp.Params.Output):
    if p.NickName != 'out': comp.Params.UnregisterOutputParameter(p)
names = [s[0] for s in SLIDERS] + ['TARGET']
for i, n in enumerate(names):
    p = comp.CreateParameter(GH_ParameterSide.Input, i)
    p.NickName = n; p.Name = n; p.Description = n
    comp.Params.RegisterInputParam(p)
po = comp.CreateParameter(GH_ParameterSide.Output, comp.Params.Output.Count)
po.NickName = 'seient'; po.Name = 'seient'; po.Description = 'Malla de la peça superior del seient'
comp.Params.RegisterOutputParam(po)
comp.Params.OnParametersChanged(); comp.VariableParameterMaintenance()
comp.SetSource(open(SRC, encoding='utf-8').read())

sliders = []
y = 100
for gname, a, b in GROUPS:
    ids = System.Collections.Generic.List[System.Guid]()
    for k in range(a, b):
        n, lo, val, hi, dec = SLIDERS[k]
        s = GH_NumberSlider()
        s.CreateAttributes()
        s.NickName = n
        s.Slider.Type = GH_SliderAccuracy.Integer if dec == 0 else GH_SliderAccuracy.Float
        s.Slider.DecimalPlaces = dec
        s.Slider.Minimum = System.Decimal(lo); s.Slider.Maximum = System.Decimal(hi)
        s.SetSliderValue(System.Decimal(val))
        s.Attributes.Pivot = System.Drawing.PointF(250, y)
        doc.AddObject(s, False)
        comp.Params.Input[k].AddSource(s)
        ids.Add(s.InstanceGuid)
        y += 26
    grp = GH_Group(); grp.CreateAttributes(); grp.NickName = gname
    grp.Colour = System.Drawing.Color.FromArgb(60, 170, 200, 230)
    doc.AddObject(grp, False)
    for gid in ids: grp.AddObject(gid)
    y += 30
pan = GH_Panel(); pan.CreateAttributes()
pan.NickName = 'TARGET (GUID de l\'objecte)'; pan.UserText = ''
pan.Attributes.Pivot = System.Drawing.PointF(250, y + 10)
doc.AddObject(pan, False)
comp.Params.Input[len(SLIDERS)].AddSource(pan)
mp = Param_Mesh(); mp.CreateAttributes(); mp.NickName = 'seient'
mp.Attributes.Pivot = System.Drawing.PointF(1060, 620)
doc.AddObject(mp, False)
mp.AddSource(comp.Params.Output[[q.NickName for q in comp.Params.Output].index('seient')])

doc.NewSolution(True)
canvas.Refresh()
io = gh.Kernel.GH_DocumentIO(doc)
io.SaveQuiet(OUT)
doc.FilePath = OUT
print("desat", OUT, "objectes", doc.ObjectCount)
print("missatges:", [str(m) for m in comp.RuntimeMessages(gh.Kernel.GH_RuntimeMessageLevel.Error)], [str(m) for m in comp.RuntimeMessages(gh.Kernel.GH_RuntimeMessageLevel.Warning)])
print("sortida seient:", mp.VolatileDataCount)
