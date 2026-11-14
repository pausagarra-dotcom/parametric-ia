# Construye en Grasshopper 1 el patron de tablero hundido sobre una SUPERFICIE ORGANICA, con la formula en nodos nativos 'Evaluate'
# (cada formula escrita en un panel de texto junto a su nodo) y sliders. Se ejecuta dentro de Rhino (run_python).
# Solo hay dos scripts auxiliares y ninguno contiene la formula: REJILLA (donde se evalua) y MALLA (ensamblar la malla).
import System, math, Grasshopper as gh, Rhino, Rhino.Geometry as rg
import Grasshopper.Kernel.Data as GD
from System.Drawing import PointF, RectangleF, Color
from Grasshopper.Kernel import GH_ParameterSide
from Grasshopper.Kernel.Special import GH_NumberSlider, GH_Panel, GH_Group
from Grasshopper.Kernel.Types import GH_Surface, GH_Number
from Grasshopper.GUI.Base import GH_SliderAccuracy
ROOT = r"H:\Mi unidad\PARAMETRIC IA_New_shot"
SP = ROOT + r"\textures\03_organica_quadres\scripts"
OUT = ROOT + r"\textures\03_organica_quadres\grasshopper\superficie_organica_quadres.gh"
SRC3DM = ROOT + r"\recerca\sp4\sp4_625_bosses.3dm"
G = lambda s: System.Guid(s)
GID = dict(EVAL=G("cc2b626f-6eff-4d08-9829-2877560693f4"), SURF=G("deaf8653-5528-4286-807c-3de8b8dad781"),
           PY=G("719467e6-7cf5-4848-99b0-c5dd57e5442c"), EVSRF=G("353b206e-bde5-4f02-a913-b3b8a977d4b9"),
           AMP=G("6ec39468-dae7-4ffa-a766-f2ab22a2c62e"), MOVE=G("e9eb1dcf-92f6-4d4d-84ae-96222d60f56b"),
           SERIES=G("e64c5fb1-845c-4ab1-8911-5f338516ba67"), BOUNDS=G("f44b92b0-3b5b-493a-86f4-fd7408c3daf3"),
           DEDOM=G("825ea536-aebb-41e9-af32-8baeb2ecb590"))
# --- superficie organica (objeto 646 del fichero de SP-4), con dominio [0,1]x[0,1]
f3 = Rhino.FileIO.File3dm.Read(SRC3DM)
srf = None
for i, o in enumerate(f3.Objects):
    if i == 646:
        srf = o.Geometry.Faces[0].ToNurbsSurface(); break
srf.SetDomain(0, rg.Interval(0, 1)); srf.SetDomain(1, rg.Interval(0, 1))
brep = srf.ToBrep()

canvas = gh.Instances.ActiveCanvas
_old = canvas.Document
doc = gh.Kernel.GH_Document()
gh.Instances.DocumentServer.AddDocument(doc)
canvas.Document = doc
doc.Enabled = True
if _old is not None and _old is not doc: gh.Instances.DocumentServer.RemoveDocument(_old)
def emit(guid, x, y, nick=None):
    c = gh.Instances.ComponentServer.EmitObject(guid)
    c.CreateAttributes(); c.Attributes.Pivot = PointF(x, y)
    if nick: c.NickName = nick
    doc.AddObject(c, False); return c
def panel(x, y, w, h, text, nick=None, color=None):
    p = GH_Panel(); p.CreateAttributes(); p.UserText = text
    if nick: p.NickName = nick
    doc.AddObject(p, False)
    p.Attributes.Pivot = PointF(x, y); p.Attributes.Bounds = RectangleF(x, y, w, h)
    if color is not None: p.Properties.Colour = color
    return p
def slider(name, lo, val, hi, dec, x, y):
    s = GH_NumberSlider(); s.CreateAttributes(); s.NickName = name
    s.Slider.Type = GH_SliderAccuracy.Integer if dec == 0 else GH_SliderAccuracy.Float
    s.Slider.DecimalPlaces = dec
    s.Slider.Minimum = System.Decimal(lo); s.Slider.Maximum = System.Decimal(hi)
    s.SetSliderValue(System.Decimal(val)); s.Attributes.Pivot = PointF(x, y)
    doc.AddObject(s, False); return s
def set_inputs(c, names):
    # nodo Evaluate: se conserva la primera entrada (la expresion) y se crean las variables con los nombres dados
    while c.Params.Input.Count > 1: c.Params.UnregisterInputParameter(c.Params.Input[c.Params.Input.Count - 1])
    for k, n in enumerate(names):
        p = c.CreateParameter(GH_ParameterSide.Input, k + 1); p.NickName = n; p.Name = n; c.Params.RegisterInputParam(p)
    c.Params.OnParametersChanged(); c.VariableParameterMaintenance()
def type_hint(param, name):
    th = param.TypeHints
    for h in th:
        if h.TypeName == name:
            th.Select(h.HintID); return
def out_of(src):
    return src.Params.Output[0] if hasattr(src, 'Params') and src.Params.Output.Count else src
SRCS = {}          # clave -> parametro de salida
groups = {}
def reg(key, obj, out=0):
    SRCS[key] = obj.Params.Output[out] if hasattr(obj, 'Params') else obj
    return obj

# ======================= 0. Texto con la formula completa =======================
FORMULA = (
"PATRON: TABLERO DE CUADRADOS HUNDIDOS CON ARISTA NITIDA   (todo en mm)\n"
"\n"
" TESELADO (script REJILLA, solo decide donde se evalua):  x,y = posicion sobre la superficie en mm (longitud de arco)\n"
"     iu = round((x-OFF_X)/CELL)   iv = round((y-OFF_Y)/CELL)    celda          par = |(iu+iv) mod 2|   solo se hunden las celdas con par = 0 (damero)\n"
"     a0 = (x-OFF_X)-CELL*iu       b0 = (y-OFF_Y)-CELL*iv        coordenadas locales en la celda (UA, UB: las distintas, unos cientos)\n"
" Todos los hundidos son iguales en coordenadas locales: la formula de abajo se evalua una vez por cada (a0,b0) distinto y se reparte por las celdas.\n"
"\n"
" (a,b) = (a0,b0) girado ROT*90 grados                          ROT elige las esquinas marcadas\n"
" PH = (CELL-GAP)/2            semilado del cuadrado hundido\n"
" s = a/PH     t = b/PH     p = (s+t)/2          (s,t,p limitados a [-1,1])\n"
"\n"
" FONDO     f   = (1-s^2) * (1-t^2) * (1 + TILT*p)         polinomio, a ras en todo el contorno\n"
" LABIO     lip = LIP * p^2                                 arista marcada: fuerte en las esquinas arriba-derecha/abajo-izquierda\n"
" CONTORNO  ec  = RC - sqrt(max(|a|-(PH-RC),0)^2 + max(|b|-(PH-RC),0)^2) - min(max(|a|-(PH-RC),|b|-(PH-RC)),0)    (RC = CORNER_R)\n"
" RAMPA     M   = 1 - (1 - min(max(ec,0)/WALL, 1))^2        arista nitida de ancho WALL\n"
" PROF.     raw = (f + lip) * M        si ec > 0, si no 0\n"
" NORMAL.   BMAX = max_p [ (1-p^2)^2 (1+TILT p) + LIP p^2 ]  -> la profundidad maxima es exactamente DEPTH\n"
" PERFIL    zu  = -DEPTH * raw / BMAX                        (un valor por cada (a0,b0) distinto)\n"
" BORDE     envx = smoothstep((min(x,Lx-x)-FADE_GAP)/FADE_LEN)   envy = igual con y        env = min(envx, envy)   (el patron se desvanece hacia el borde)\n"
"\n"
" RESULTADO z = zu * env     desplazamiento (mm) a lo largo de la normal de la superficie:  S = B + z*N     (lo ensambla el script MALLA)\n"
)
panel(0, -420, 1500, 400, FORMULA, "FORMULA", Color.FromArgb(255, 255, 250, 205))

# ======================= 1. Sliders =======================
SL = [('CELL', 3, 8, 30, 2), ('GAP', 0, 0.2, 3, 2), ('CORNER_R', 0, 1.2, 5, 2), ('WALL', 0.05, 0.2, 2, 2),
      ('DEPTH', -2, 0.4, 2, 2), ('TILT', 0, 0.8, 1, 2), ('LIP', 0, 0.3, 1, 2), ('ROT', 0, 0, 3, 0),
      ('OFF_X', 0, 0, 30, 2), ('OFF_Y', 0, 0, 30, 2), ('FADE_GAP', 0, 10, 60, 1), ('FADE_LEN', 1, 30, 80, 1), ('STEP', 0.8, 2.0, 4, 2)]
for k, (n, lo, v, hi, dec) in enumerate(SL):
    s = slider(n, lo, v, hi, dec, 0, 20 + 32 * k); SRCS[n] = s
panel(0, 0, 300, 20, "SLIDERS (mueve y mira la superficie)", "t_sl", Color.FromArgb(255, 220, 235, 255))

# ======================= 2. Superficie + rejilla =======================
sp = emit(GID['SURF'], 380, 40, "SRF")
sp.PersistentData.Append(GH_Surface(brep), GD.GH_Path(0))
SRCS['SRF'] = sp
rej = emit(GID['PY'], 640, 40, "REJILLA (donde se evalua)")
while rej.Params.Input.Count: rej.Params.UnregisterInputParameter(rej.Params.Input[0])
for p in list(rej.Params.Output):
    if p.NickName != 'out': rej.Params.UnregisterOutputParameter(p)
for k, n in enumerate(['SRF', 'CELL', 'GAP', 'WALL', 'CORNER_R', 'STEP', 'OFF_X', 'OFF_Y']):
    p = rej.CreateParameter(GH_ParameterSide.Input, k); p.NickName = n; p.Name = n; rej.Params.RegisterInputParam(p)
for n in ['UV', 'XM', 'YM', 'NX', 'NY', 'LU', 'LV', 'UA', 'UB', 'UIDX', 'XSL', 'YSL', 'info']:
    p = rej.CreateParameter(GH_ParameterSide.Output, rej.Params.Output.Count); p.NickName = n; p.Name = n; rej.Params.RegisterOutputParam(p)
rej.Params.OnParametersChanged(); rej.VariableParameterMaintenance()
type_hint(rej.Params.Input[0], 'Brep')
rej.SetSource(open(SP + r"\gh_org_rejilla.py", encoding="utf-8").read())
for n in ['SRF', 'CELL', 'GAP', 'WALL', 'CORNER_R', 'STEP', 'OFF_X', 'OFF_Y']:
    rej.Params.Input[['SRF', 'CELL', 'GAP', 'WALL', 'CORNER_R', 'STEP', 'OFF_X', 'OFF_Y'].index(n)].AddSource(SRCS[n])
for n in ['UV', 'XM', 'YM', 'NX', 'NY', 'LU', 'LV', 'UA', 'UB', 'UIDX', 'XSL', 'YSL']:
    SRCS[n] = [p for p in rej.Params.Output if p.NickName == n][0]

# ======================= 3. Nodos de la formula (Evaluate + panel con el texto) =======================
NODES = [
 # clave, titulo, formula, [(variable, origen)], columna
 ('PH',  "PH = semilado del hundido",           "(c-g)/2",                         [('c','CELL'),('g','GAP')], 0),
 ('A',   "a = a0 girado ROT*90",                 "if(r<0.5,a0,if(r<1.5,-b0,if(r<2.5,-a0,b0)))", [('r','ROT'),('a0','UA'),('b0','UB')], 1),
 ('B',   "b = b0 girado ROT*90",                 "if(r<0.5,b0,if(r<1.5,a0,if(r<2.5,-b0,-a0)))", [('r','ROT'),('a0','UA'),('b0','UB')], 1),
 ('EC',  "ec = distancia al contorno redondeado","rc-sqrt(max(abs(a)-(PH-rc),0)^2+max(abs(b)-(PH-rc),0)^2)-min(max(abs(a)-(PH-rc),abs(b)-(PH-rc)),0)", [('a','A'),('b','B'),('PH','PH'),('rc','CORNER_R')], 2),
 ('F',   "f = fondo (1-s2)(1-t2)(1+TILT p)",     "max((1-min(1,max(-1,a/PH))^2)*(1-min(1,max(-1,b/PH))^2),0)*(1+k*min(1,max(-1,(a+b)/(2*PH))))", [('a','A'),('b','B'),('PH','PH'),('k','TILT')], 2),
 ('LIPN',"lip = LIP p2 (arista marcada)",        "L*min(1,max(-1,(a+b)/(2*PH)))^2", [('a','A'),('b','B'),('PH','PH'),('L','LIP')], 2),
 ('M',   "M = rampa de la arista (WALL)",        "1-(1-min(max(ec,0)/w,1))^2",      [('ec','EC'),('w','WALL')], 3),
 ('RAW', "raw = (f + lip) M",                    "if(ec>0,(f+l)*m,0)",              [('ec','EC'),('f','F'),('l','LIPN'),('m','M')], 3),
 ('ENVX',"envx = desvanecimiento segun x",       "3*min(max((min(x,Lx-x)-F0)/FL,0),1)^2-2*min(max((min(x,Lx-x)-F0)/FL,0),1)^3", [('x','XSL'),('Lx','LU'),('F0','FADE_GAP'),('FL','FADE_LEN')], 4),
 ('ENVY',"envy = desvanecimiento segun y",       "3*min(max((min(y,Ly-y)-F0)/FL,0),1)^2-2*min(max((min(y,Ly-y)-F0)/FL,0),1)^3", [('y','YSL'),('Ly','LV'),('F0','FADE_GAP'),('FL','FADE_LEN')], 4),
]
COLX = 1000; COLW = 1050; ROWH = 190
row_in_col = {}
node_obj = {}
for key, title, formula, varlist, col in NODES:
    r = row_in_col.get(col, 0); row_in_col[col] = r + 1
    x = COLX + col * COLW; y = 40 + r * ROWH
    pn = panel(x, y, 560, 78, formula, "f_" + key, Color.FromArgb(255, 255, 250, 205))
    ev = emit(GID['EVAL'], x + 600, y, title)
    set_inputs(ev, [v for v, _ in varlist])
    ev.Params.Input[0].AddSource(pn)
    for k, (v, srcname) in enumerate(varlist):
        ev.Params.Input[k + 1].AddSource(SRCS[srcname])
    SRCS[key] = ev.Params.Output[0]; node_obj[key] = ev
    if key == 'PH': pass

# --- normalizacion: BMAX por muestreo (nodos nativos)
bx = COLX + 5 * COLW; by = 40 + 2 * ROWH + 60
def const_panel(x, y, text): return panel(x, y, 60, 20, text)
ser = emit(GID['SERIES'], bx, by + 0, "Series t")
for k, t in enumerate(["0", "0.01", "101"]):
    cp = const_panel(bx - 90, by + k * 24, t); ser.Params.Input[k].AddSource(cp)
pn = panel(bx, by + 120, 560, 60, "(1-t^2)^2*(1+k*t)+L*t^2", "f_BM", Color.FromArgb(255, 255, 250, 205))
evb = emit(GID['EVAL'], bx + 600, by + 120, "g(t) = fondo + labio sobre la diagonal marcada")
set_inputs(evb, ['t', 'k', 'L'])
evb.Params.Input[0].AddSource(pn); evb.Params.Input[1].AddSource(ser.Params.Output[0])
evb.Params.Input[2].AddSource(SRCS['TILT']); evb.Params.Input[3].AddSource(SRCS['LIP'])
bnd = emit(GID['BOUNDS'], bx + 1000, by + 120, "Bounds")
bnd.Params.Input[0].AddSource(evb.Params.Output[0])
ded = emit(GID['DEDOM'], bx + 1100, by + 120, "BMAX = maximo")
ded.Params.Input[0].AddSource(bnd.Params.Output[0])
SRCS['BM'] = ded.Params.Output[1]

# --- resultado: perfil zu (un valor por cada coordenada local distinta)
zx = COLX + 5 * COLW; zy = 40
pn = panel(zx, zy, 560, 60, "-DEPTH*raw/bm", "f_Z", Color.FromArgb(255, 255, 250, 205))
evz = emit(GID['EVAL'], zx + 600, zy, "zu = perfil de profundidad (mm)")
set_inputs(evz, ['DEPTH', 'raw', 'bm'])
evz.Params.Input[0].AddSource(pn)
for k, nme in enumerate(['DEPTH', 'RAW', 'BM']): evz.Params.Input[k + 1].AddSource(SRCS[nme])
SRCS['Z'] = evz.Params.Output[0]

# ======================= 4. Aplicar a la superficie =======================
ex = zx; ey = zy + 200
es = emit(GID['EVSRF'], ex, ey, "Evaluar superficie")
es.Params.Input[0].AddSource(SRCS['SRF']); es.Params.Input[1].AddSource(SRCS['UV'])
ml = emit(GID['PY'], ex + 500, ey, "MALLA (desplazar y ensamblar)")
while ml.Params.Input.Count: ml.Params.UnregisterInputParameter(ml.Params.Input[0])
for p in list(ml.Params.Output):
    if p.NickName != 'out': ml.Params.UnregisterOutputParameter(p)
MIN = ['P', 'NX', 'NY', 'XM', 'YM', 'ZU', 'UIDX', 'ENVX', 'ENVY']
for k, n in enumerate(MIN):
    p = ml.CreateParameter(GH_ParameterSide.Input, k); p.NickName = n; p.Name = n
    p.Access = gh.Kernel.GH_ParamAccess.item if n in ('NX', 'NY') else gh.Kernel.GH_ParamAccess.list
    ml.Params.RegisterInputParam(p)
for n in ['mesh', 'info']:
    p = ml.CreateParameter(GH_ParameterSide.Output, ml.Params.Output.Count); p.NickName = n; p.Name = n; ml.Params.RegisterOutputParam(p)
ml.Params.OnParametersChanged(); ml.VariableParameterMaintenance()
type_hint(ml.Params.Input[0], 'Point3d')
ml.SetSource(open(SP + r"\gh_org_malla.py", encoding="utf-8").read())
_src = {'P': es.Params.Output[0],
        'NX': SRCS['NX'], 'NY': SRCS['NY'], 'XM': SRCS['XM'], 'YM': SRCS['YM'], 'ZU': SRCS['Z'], 'UIDX': SRCS['UIDX'],
        'ENVX': SRCS['ENVX'], 'ENVY': SRCS['ENVY']}
for k, n in enumerate(MIN): ml.Params.Input[k].AddSource(_src[n])
from Grasshopper.Kernel.Parameters import Param_Mesh
mp = Param_Mesh(); mp.CreateAttributes(); mp.NickName = 'superficie texturada'; mp.Attributes.Pivot = PointF(ex + 900, ey)
doc.AddObject(mp, False)
mp.AddSource([p for p in ml.Params.Output if p.NickName == 'mesh'][0])
# los componentes de calculo no previsualizan: solo el parametro Mesh
for c in list(doc.Objects):
    if hasattr(c, 'Params') and hasattr(c, 'Hidden') and c.Name in ('Evaluate', 'Python 3 Script', 'Move', 'Evaluate Surface', 'Amplitude'): c.Hidden = True
sp.Hidden = False

doc.NewSolution(True)
canvas.Refresh()
gh.Kernel.GH_DocumentIO(doc).SaveQuiet(OUT)
doc.FilePath = OUT
print("guardado", OUT, "objetos", doc.ObjectCount)
errs = []
for c in doc.Objects:
    if hasattr(c, 'RuntimeMessages'):
        for lvl in (gh.Kernel.GH_RuntimeMessageLevel.Error, gh.Kernel.GH_RuntimeMessageLevel.Warning):
            for m in c.RuntimeMessages(lvl): errs.append((c.NickName, str(lvl), str(m)))
print("mensajes:", errs[:12])
print("malla:", [str(x) for x in ml.Params.Output[1].VolatileData.AllData(True)] if ml.Params.Output.Count > 1 else None)
