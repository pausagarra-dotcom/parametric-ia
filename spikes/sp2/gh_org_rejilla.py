# GH Python 3 -- REJILLA: puntos de muestreo (u,v) sobre la superficie, repartidos en mm por longitud de arco.
# NO contiene la formula del patron (esa esta en los nodos 'Evaluate' del lienzo). Solo decide DONDE se evalua el patron:
#   * lineas de nodos alineadas con los bordes de las celdas y del hundido (arista nitida) + nodos de las esquinas redondeadas sobre su arco.
# Entradas: SRF, CELL, GAP, WALL, CORNER_R, STEP, OFF_X, OFF_Y
# Salidas : UV (puntos {u,v}), XM, YM (coordenadas en mm sobre la superficie), NX, NY (nodos por fila/columna), LU, LV (largo en mm),
#           UA, UB (coordenadas locales (a,b) DISTINTAS que aparecen en las celdas hundidas), UIDX (por nodo: indice en UA/UB, o -1 si el nodo cae en una celda plana),
#           XSL, YSL (lineas de la reticula en x e y), info
# Todos los hundidos son iguales en coordenadas locales: la formula solo hay que evaluarla en UA,UB (unos cientos de puntos), no en cada nodo.
import math, bisect, Rhino, Rhino.Geometry as rg
def _g(n, d):
    v = globals().get(n)
    return d if v is None else v
CELL = max(float(_g('CELL', 8.0)), 1.0); GAP = max(float(_g('GAP', 0.2)), 0.0)
WALL = float(_g('WALL', 0.2)); RC0 = float(_g('CORNER_R', 1.2)); STEP = max(float(_g('STEP', 2.0)), 0.4)
OFF_X = float(_g('OFF_X', 0.0)); OFF_Y = float(_g('OFF_Y', 0.0))
s = SRF
if isinstance(s, rg.Brep): s = s.Faces[0].UnderlyingSurface()
d0 = s.Domain(0); d1 = s.Domain(1)
def table(direction, const_t, M=700):
    c = s.IsoCurve(direction, const_t); dom = c.Domain
    ts = [dom.T0 + (dom.T1 - dom.T0) * k / M for k in range(M + 1)]
    pts = [c.PointAt(t) for t in ts]
    cum = [0.0]
    for k in range(1, M + 1): cum.append(cum[-1] + pts[k].DistanceTo(pts[k - 1]))
    return ts, cum
TU, CU = table(0, d1.Mid)      # a lo largo de u, v en el centro
TV, CV = table(1, d0.Mid)      # a lo largo de v, u en el centro
LU = CU[-1]; LV = CV[-1]
def inv(ts, cum, x):
    if x <= 0: return ts[0]
    if x >= cum[-1]: return ts[-1]
    i = bisect.bisect_right(cum, x) - 1
    f = (x - cum[i]) / (cum[i + 1] - cum[i]) if cum[i + 1] > cum[i] else 0.0
    return ts[i] + (ts[i + 1] - ts[i]) * f
half = CELL / 2.0; PH = half - GAP / 2.0
WL = min(max(WALL, 0.05), PH); RC = min(max(RC0, 0.05), PH * 0.95)
n = max(2, int(math.ceil(PH / STEP)))
keys = [0.0, PH, max(PH - WL, 0.0)]
uni = [PH * k / float(n) for k in range(1, n) if min(abs(PH * k / float(n) - kk) for kk in keys) > 0.3 * STEP]
pos = set(round(p, 6) for p in keys + uni + ([half] if GAP < 0.01 else []))     # con junta, las lineas +-PH de celdas contiguas ya la delimitan
loc = sorted(set([round(p, 6) for p in pos] + [round(-p, 6) for p in pos]))
loc = [p for p in loc if p < half - 1e-7]
def axis(L, off):
    xs = {0.0, round(L, 6)}
    for k in range(int(math.floor((0 - off) / CELL)) - 1, int(math.ceil((L - off) / CELL)) + 2):
        for p in loc:
            x = off + k * CELL + p
            if 1e-6 < x < L - 1e-6: xs.add(round(x, 6))
    out = []
    for x in sorted(xs):
        if not out or x - out[-1] > 1e-4: out.append(x)
    return out
XS = axis(LU, OFF_X); YS = axis(LV, OFF_Y)
NX = len(XS); NY = len(YS)
cc = PH - RC
def snap(x, y):
    # nodos de las esquinas redondeadas: linea exterior -> arco de radio RC, linea interior (WALL dentro) -> arco de radio RC-WALL
    if x <= 1e-6 or y <= 1e-6 or x >= LU - 1e-6 or y >= LV - 1e-6: return x, y
    iu = int(round((x - OFF_X) / CELL)); iv = int(round((y - OFF_Y) / CELL))
    if (iu + iv) % 2 != 0: return x, y
    a = (x - OFF_X) - CELL * iu; b = (y - OFF_Y) - CELL * iv
    if abs(a) > PH + 1e-6 or abs(b) > PH + 1e-6: return x, y
    if abs(a) <= cc or abs(b) <= cc: return x, y
    dx = abs(a) - cc; dy = abs(b) - cc; dd = math.hypot(dx, dy)
    outer = abs(abs(a) - PH) < 1e-6 or abs(abs(b) - PH) < 1e-6
    inner = abs(abs(a) - (PH - WL)) < 1e-6 or abs(abs(b) - (PH - WL)) < 1e-6
    if outer: r = RC
    elif inner and RC - WL > 0.05: r = RC - WL
    else: return x, y
    if dd <= r + 1e-9: return x, y
    k = r / dd
    return OFF_X + CELL * iu + math.copysign(cc + dx * k, a), OFF_Y + CELL * iv + math.copysign(cc + dy * k, b)
UV = []; XM = []; YM = []; UIDX = []; UA = []; UB = []
_uniq = {}
for y in YS:
    for x in XS:
        xx, yy = snap(x, y)
        XM.append(xx); YM.append(yy)
        UV.append(rg.Point3d(inv(TU, CU, xx), inv(TV, CV, yy), 0.0))
        iu = int(round((xx - OFF_X) / CELL)); iv = int(round((yy - OFF_Y) / CELL))
        if (iu + iv) % 2 != 0:                      # damero: celda plana
            UIDX.append(-1); continue
        a = (xx - OFF_X) - CELL * iu; b = (yy - OFF_Y) - CELL * iv
        key = (round(a, 5), round(b, 5))
        if key not in _uniq:
            _uniq[key] = len(UA); UA.append(key[0]); UB.append(key[1])
        UIDX.append(_uniq[key])
XSL = list(XS); YSL = list(YS)
info = "rejilla %d x %d = %d nodos | %d coordenadas locales distintas | superficie %.1f x %.1f mm (arco por el centro)" % (NX, NY, NX * NY, len(UA), LU, LV)
print(info)
