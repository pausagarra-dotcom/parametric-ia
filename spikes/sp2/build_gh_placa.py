# Construye en el lienzo de Grasshopper 1 abierto: componente Python 3 (gh_placa.py) + sliders + salida Mesh + panel TARGET.
# Se ejecuta dentro de Rhino (run_python). Guarda en gh/placa_quadres.gh.
import System, Grasshopper as gh
from Grasshopper.Kernel import GH_ParameterSide
from Grasshopper.Kernel.Special import GH_NumberSlider, GH_Panel
from Grasshopper.GUI.Base import GH_SliderAccuracy
from Grasshopper.Kernel.Parameters import Param_Mesh
ROOT = r"H:\Mi unidad\PARAMETRIC IA_New_shot"
SRC = ROOT + r"\spikes\sp2\gh_placa.py"
OUT = ROOT + r"\gh\placa_quadres.gh"
# nombre, min, valor, max, decimales (0 = entero)
SLIDERS = [
    ('PL_W', 20, 120, 400, 1), ('PL_H', 20, 160, 400, 1), ('PL_T', 2, 10, 30, 2),
    ('PL_R', 0, 24, 100, 1), ('EDGE_R', 0, 6, 15, 2),
    ('CELL', 2, 8, 30, 2), ('PATTERN', 0, 0, 1, 0), ('GAP', 0, 0.2, 5, 2), ('CORNER_R', 0, 1.2, 10, 2),
    ('WALL', 0.05, 0.2, 15, 2), ('DEPTH', -3, 0.4, 3, 2),
    ('PROFILE', 0, 7, 7, 0), ('RIM', 0.05, 0.4, 3, 2), ('CRISP', 0, 0, 3, 0),
    ('LIP', 0, 0.3, 1, 2), ('TILT', 0, 0.8, 1, 2),
    ('SOFT', 0.05, 0.7, 1, 2), ('AXIS', 0, 0, 1, 0), ('SIDE', 0.02, 0.3, 3, 2), ('ANGLE', -90, 0, 90, 1),
    ('FADE_GAP', 0, 3, 30, 2), ('FADE_LEN', 0, 25, 80, 1), ('FADE_MODE', 0, 0, 3, 0), ('DETAIL', 1, 2, 6, 0),
]
canvas = gh.Instances.ActiveCanvas
doc = gh.Kernel.GH_Document()
gh.Instances.DocumentServer.AddDocument(doc)
canvas.Document = doc

comp = gh.Instances.ComponentServer.EmitObject(System.Guid("719467e6-7cf5-4848-99b0-c5dd57e5442c"))  # Python 3 Script
comp.CreateAttributes()
comp.Attributes.Pivot = System.Drawing.PointF(700, 300)
comp.NickName = "Placa quadres"
comp.Hidden = True   # solo previsualiza el parametro Mesh 'placa' (evita la malla doble en el visor)
doc.AddObject(comp, False)
# entradas/salidas: fuera las de serie, dejamos 'out' y anadimos 'plate'
for p in list(comp.Params.Input): comp.Params.UnregisterInputParameter(p)
for p in list(comp.Params.Output):
    if p.NickName != 'out': comp.Params.UnregisterOutputParameter(p)
names = [s[0] for s in SLIDERS] + ['TARGET']
for i, n in enumerate(names):
    p = comp.CreateParameter(GH_ParameterSide.Input, i)
    p.NickName = n; p.Name = n; p.Description = n
    comp.Params.RegisterInputParam(p)
po = comp.CreateParameter(GH_ParameterSide.Output, comp.Params.Output.Count)
po.NickName = 'plate'; po.Name = 'plate'; po.Description = 'Malla de la placa'
comp.Params.RegisterOutputParam(po)
comp.Params.OnParametersChanged(); comp.VariableParameterMaintenance()
comp.SetSource(open(SRC, encoding='utf-8').read())

for k, (n, lo, val, hi, dec) in enumerate(SLIDERS):
    s = GH_NumberSlider()
    s.CreateAttributes()
    s.NickName = n
    s.Slider.Type = GH_SliderAccuracy.Integer if dec == 0 else GH_SliderAccuracy.Float
    s.Slider.DecimalPlaces = dec
    s.Slider.Minimum = System.Decimal(lo); s.Slider.Maximum = System.Decimal(hi)
    s.SetSliderValue(System.Decimal(val))
    s.Attributes.Pivot = System.Drawing.PointF(250, 160 + 30 * k)
    doc.AddObject(s, False)
    comp.Params.Input[k].AddSource(s)
pan = GH_Panel(); pan.CreateAttributes()
pan.NickName = 'TARGET (GUID del objeto)'; pan.UserText = ''
pan.Attributes.Pivot = System.Drawing.PointF(250, 160 + 30 * len(SLIDERS) + 10)
doc.AddObject(pan, False)
comp.Params.Input[len(SLIDERS)].AddSource(pan)
mp = Param_Mesh(); mp.CreateAttributes(); mp.NickName = 'placa'
mp.Attributes.Pivot = System.Drawing.PointF(1000, 320)
doc.AddObject(mp, False)
mp.AddSource(comp.Params.Output[[q.NickName for q in comp.Params.Output].index('plate')])

doc.NewSolution(True)
canvas.Refresh()
io = gh.Kernel.GH_DocumentIO(doc)
io.SaveQuiet(OUT)
doc.FilePath = OUT
print("guardado", OUT, "objetos", doc.ObjectCount)
print("mensajes:", [str(m) for m in comp.RuntimeMessages(gh.Kernel.GH_RuntimeMessageLevel.Error)], [str(m) for m in comp.RuntimeMessages(gh.Kernel.GH_RuntimeMessageLevel.Warning)])
print("salida placa:", mp.VolatileDataCount)
