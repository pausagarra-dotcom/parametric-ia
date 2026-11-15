# GH Python 3: funda con rombos hundidos, en NURBS (solido valido para SolidWorks).
# Textura 05 (2026-11-15). Parte de la 01 (rombos que se desvanecen), pero cada rombo es UN parche Bezier liso.
# Las ENTRADAS (nombre = variable) vienen de sliders; si falta una, se usa el valor por defecto.
# Salida: funda (Brep, solido cerrado). Unidades mm.
import math, Rhino, Rhino.Geometry as rg

def _g(n, d):
    v = globals().get(n)
    return d if v is None else v

# --- funda (losa) ---
PH_W = _g('PH_W', 75.0)       # ancho
PH_H = _g('PH_H', 165.0)      # alto
PH_T = _g('PH_T', 8.5)        # grosor
PH_R = _g('PH_R', 12.0)       # radio de las esquinas
EDGE_R = _g('EDGE_R', 3.0)    # radio del canto superior (tambien en el hueco de camara)
CAM_X0 = _g('CAM_X0', 8.0); CAM_X1 = _g('CAM_X1', 72.0)
CAM_Y0 = _g('CAM_Y0', 117.0); CAM_Y1 = _g('CAM_Y1', 159.0)
CAM_R = _g('CAM_R', 6.0)      # radio de las esquinas del hueco de camara
# --- rombos ---
CELL_W = _g('CELL_W', 6.063)  # diagonal horizontal del rombo
CELL_H = _g('CELL_H', 9.11)   # diagonal vertical del rombo
DEPTH = _g('DEPTH', 0.5)      # profundidad maxima del hundido
SUAVIDAD = min(max(_g('SUAVIDAD', 1.0), 0.0), 1.0)   # 1 = fondo redondeado liso; 0 = se acerca a la piramide de la 01
GRADO = min(max(int(_g('GRADO', 6)), 2), 9)          # grado del parche Bezier (mas = puede ser mas puntiagudo)
GAP = max(_g('GAP', 0.5), 0.0)                       # ancho de la franja plana entre rombos (0 = rombos pegados, arista viva)
# --- zona texturada y desvanecimiento (igual que la 01) ---
TX_CX = PH_W / 2.0
TX_CY = _g('TX_CY', 58.0)
TX_A = _g('TX_A', 27.5)
TX_B = _g('TX_B', 55.0)
FADE_IN = min(max(_g('FADE_IN', 0.0), 0.0), 0.95)
FADE_N = max(_g('FADE_N', 2.018), 1.0)
FADE_MODE = int(_g('FADE_MODE', 0))
MIN_D = _g('MIN_D', 0.002)    # rombos con hundido maximo menor que esto no se modelan (quedan planos)
TOL = 0.001

def sm(t):
    t = min(max(t, 0.0), 1.0); return t * t * (3 - 2 * t)

def env_at(x, y):
    q = ((abs(x - TX_CX) / TX_A) ** FADE_N + (abs(y - TX_CY) / TX_B) ** FADE_N) ** (1.0 / FADE_N)
    t = min(max((q - FADE_IN) / max(1.0 - FADE_IN, 1e-6), 0.0), 1.0)
    if FADE_MODE == 1: return 0.5 * (1 + math.cos(math.pi * t))
    if FADE_MODE == 2: return 1.0 - t
    if FADE_MODE == 3: return 1.0 - sm(sm(t))
    return 1.0 - sm(t)

def rr(px, py, cx, cy, hx, hy, r):
    qx = abs(px - cx) - (hx - r); qy = abs(py - cy) - (hy - r)
    return math.hypot(max(qx, 0), max(qy, 0)) + min(max(qx, qy), 0) - r

def sdf(x, y):   # <0 dentro de la pieza
    return max(rr(x, y, PH_W / 2, PH_H / 2, PH_W / 2, PH_H / 2, PH_R),
               -rr(x, y, (CAM_X0 + CAM_X1) / 2, (CAM_Y0 + CAM_Y1) / 2, (CAM_X1 - CAM_X0) / 2, (CAM_Y1 - CAM_Y0) / 2, CAM_R))

# --- forma del rombo: red de control Bezier (n+1)x(n+1) en coordenadas (ws, wt) del rombo ---
# blanda: (1-s^2)(1-t^2) exacta en Bernstein: c_k = 4 k (n-k) / (n (n-1))
# piramide: 1 - max(|s|,|t|) en los puntos de Greville k/n (la Bezier la suaviza)
n = GRADO
soft1 = [4.0 * k * (n - k) / (n * (n - 1)) for k in range(n + 1)]
SHAPE = [[0.0] * (n + 1) for _ in range(n + 1)]
for a in range(n + 1):
    for b in range(n + 1):
        s = 2.0 * a / n - 1.0; t = 2.0 * b / n - 1.0
        soft = soft1[a] * soft1[b]
        pyr = 1.0 - max(abs(s), abs(t))
        SHAPE[a][b] = SUAVIDAD * soft + (1.0 - SUAVIDAD) * pyr

HW = CELL_W / 2.0; HH = CELL_H / 2.0
def lp(I, J):    # punto de la red de medio rombo (enteros -> coordenadas identicas en rombos vecinos)
    return (TX_CX + I * HW, TX_CY + J * HH)

# GAP: cada rombo se encoge hacia su centro (homotecia) para que sus lados queden a GAP/2 de la arista de la celda
INSET = 1.0 - (GAP / 2.0) * math.sqrt(HW * HW + HH * HH) / (HW * HH)
if INSET < 0.2: INSET = 0.2
def shrink(C, P): return (C[0] + INSET * (P[0] - C[0]), C[1] + INSET * (P[1] - C[1]))

def bilin(P0, P1, P2, P3, ws, wt):   # P0 abajo (ws0,wt0), P1 derecha (1,0), P2 arriba (1,1), P3 izquierda (0,1)
    a = (1 - ws) * (1 - wt); b = ws * (1 - wt); c = ws * wt; d = (1 - ws) * wt
    return (a * P0[0] + b * P1[0] + c * P2[0] + d * P3[0], a * P0[1] + b * P1[1] + c * P2[1] + d * P3[1])

def flat_ok(P0, P1, P2, P3):   # todo el rombo cae en la parte plana (fuera del canto R y del hueco)
    lim = -EDGE_R - 0.05
    for A, B in ((P0, P1), (P1, P2), (P2, P3), (P3, P0)):
        for k in range(9):
            w = k / 8.0
            if sdf(A[0] + w * (B[0] - A[0]), A[1] + w * (B[1] - A[1])) > lim: return False
    return True

# --- recorrer los rombos (centros con I+J par) ---
Imax = int(math.ceil((TX_A + HW) / HW)) + 1
Jmax = int(math.ceil((TX_B + HH) / HH)) + 1
cells = {}; lost_depth = 0.0
for I in range(-Imax, Imax + 1):
    for J in range(-Jmax, Jmax + 1):
        if (I + J) % 2: continue
        P0 = lp(I, J - 1); P1 = lp(I + 1, J); P2 = lp(I, J + 1); P3 = lp(I - 1, J)
        if GAP > 0:
            Cc = lp(I, J); P0, P1, P2, P3 = [shrink(Cc, P) for P in (P0, P1, P2, P3)]
        net = []; dmax = 0.0
        for a in range(n + 1):
            row = []
            for b in range(n + 1):
                x, y = bilin(P0, P1, P2, P3, a / float(n), b / float(n))
                d = DEPTH * env_at(x, y) * SHAPE[a][b] if SHAPE[a][b] != 0.0 else 0.0
                dmax = max(dmax, d)
                row.append((x, y, d))
            net.append(row)
        if dmax < MIN_D: continue
        if not flat_ok(P0, P1, P2, P3):
            lost_depth = max(lost_depth, dmax); continue
        cells[(I, J)] = (dmax, net, (P0, P1, P2, P3))

# rombos que solo se tocan por un vertice (contorno pellizcado): se quita el de menor hundido (solo sin GAP)
changed = GAP <= 0
while changed:
    changed = False
    for (I, J) in list(cells.keys()):
        for (a, b) in ((I + 1, J), (I - 1, J), (I, J + 1), (I, J - 1)):
            ring = [(a - 1, b), (a + 1, b), (a, b - 1), (a, b + 1)]
            k = [c in cells for c in ring]
            if k == [True, True, False, False] or k == [False, False, True, True]:
                p, q = (ring[0], ring[1]) if k[0] else (ring[2], ring[3])
                rm = p if cells[p][0] <= cells[q][0] else q
                lost_depth = max(lost_depth, cells[rm][0]); del cells[rm]; changed = True; break
        if changed: break

patches = []; kept = []
for (I, J), (dmax, net, corners) in sorted(cells.items()):
        ns = rg.NurbsSurface.Create(3, False, n + 1, n + 1, n + 1, n + 1)
        for a in range(n + 1):
            for b in range(n + 1):
                x, y, d = net[a][b]
                ns.Points.SetPoint(a, b, rg.Point3d(x, y, PH_T - d))
        for k in range(ns.KnotsU.Count): ns.KnotsU[k] = 0.0 if k < n else 1.0
        for k in range(ns.KnotsV.Count): ns.KnotsV[k] = 0.0 if k < n else 1.0
        patches.append(ns.ToBrep()); kept.append((I, J))

# --- agujeros de la cara superior ---
if GAP > 0:
    # cada rombo es un agujero propio; entre rombos queda la franja plana
    zig = []
    for (I, J) in kept:
        P = cells[(I, J)][2]
        zig.append(rg.PolylineCurve([rg.Point3d(p[0], p[1], PH_T) for p in (P[0], P[1], P[2], P[3], P[0])]))
else:
    # contorno de la zona de rombos (aristas que solo usa un rombo)
    cnt = {}
    for (I, J) in kept:
        vs = [(I, J - 1), (I + 1, J), (I, J + 1), (I - 1, J)]
        for k in range(4):
            e = tuple(sorted((vs[k], vs[(k + 1) % 4])))
            cnt[e] = cnt.get(e, 0) + 1
    bnd = [rg.LineCurve(rg.Point3d(lp(*e[0])[0], lp(*e[0])[1], PH_T), rg.Point3d(lp(*e[1])[0], lp(*e[1])[1], PH_T))
           for e, c in cnt.items() if c == 1]
    zig = list(rg.Curve.JoinCurves(bnd, TOL)) if bnd else []

# --- losa exacta: paredes verticales, canto superior R (cilindro en los tramos rectos, toro en las esquinas) ---
ZF = PH_T - EDGE_R            # cota donde empieza el canto
Z = rg.Vector3d.ZAxis
def rrect_parts(x0, y0, x1, y1, r):
    # tramos en sentido antihorario: ('L', A, B, normal_hacia_dentro_del_rectangulo) / ('A', centro, ang0, ang1)
    return [('L', (x0 + r, y0), (x1 - r, y0), (0, 1)), ('A', (x1 - r, y0 + r), 1.5 * math.pi, 2.0 * math.pi),
            ('L', (x1, y0 + r), (x1, y1 - r), (-1, 0)), ('A', (x1 - r, y1 - r), 0.0, 0.5 * math.pi),
            ('L', (x1 - r, y1), (x0 + r, y1), (0, -1)), ('A', (x0 + r, y1 - r), 0.5 * math.pi, math.pi),
            ('L', (x0, y1 - r), (x0, y0 + r), (1, 0)), ('A', (x0 + r, y0 + r), math.pi, 1.5 * math.pi)]

def rrect_curve(x0, y0, x1, y1, r, z):
    pc = rg.PolyCurve()
    for p in rrect_parts(x0, y0, x1, y1, r):
        if p[0] == 'L':
            pc.Append(rg.Line(rg.Point3d(p[1][0], p[1][1], z), rg.Point3d(p[2][0], p[2][1], z)))
        else:
            c, a0, a1 = p[1], p[2], p[3]
            pl = rg.Plane(rg.Point3d(c[0], c[1], z), Z)
            pc.Append(rg.Arc(rg.Circle(pl, r), rg.Interval(a0, a1)))
    return pc

def loop_faces(x0, y0, x1, y1, r, hole, z0=0.0, lift=0.0):
    # paredes (desde z0) y canto de un contorno; hole=True: el material esta FUERA del rectangulo
    # lift: sube el canto (solo en el cortador del hueco) para que corte la cara superior en angulo y no tangente
    sg = -1.0 if hole else 1.0
    out = []
    R = EDGE_R
    ZF = PH_T - EDGE_R + lift
    for p in rrect_parts(x0, y0, x1, y1, r):
        if p[0] == 'L':
            A = rg.Point3d(p[1][0], p[1][1], 0); B = rg.Point3d(p[2][0], p[2][1], 0)
            nv = rg.Vector3d(p[3][0] * sg, p[3][1] * sg, 0)
            out.append(rg.Surface.CreateExtrusion(rg.LineCurve(A + Z * z0, B + Z * z0), Z * (ZF - z0)).ToBrep())
            pts = [A + nv * (R - R * math.cos(f)) + Z * (ZF + R * math.sin(f)) for f in (0.0, math.pi / 4, math.pi / 2)]
            arc = rg.ArcCurve(rg.Arc(pts[0], pts[1], pts[2]))
            out.append(rg.Surface.CreateExtrusion(arc, B - A).ToBrep())
        else:
            c, a0, a1 = p[1], p[2], p[3]
            C = rg.Point3d(c[0], c[1], 0)
            wall = rg.ArcCurve(rg.Arc(rg.Circle(rg.Plane(C + Z * z0, Z), r), rg.Interval(a0, a1)))
            out.append(rg.Surface.CreateExtrusion(wall, Z * (ZF - z0)).ToBrep())
            u = rg.Vector3d(math.cos(a0), math.sin(a0), 0)
            # radio del perfil: hacia dentro (r - ...) en el contorno exterior, hacia fuera (r + ...) en el hueco
            pts = [C + u * (r - sg * (R - R * math.cos(f))) + Z * (ZF + R * math.sin(f)) for f in (0.0, math.pi / 4, math.pi / 2)]
            prof = rg.ArcCurve(rg.Arc(pts[0], pts[1], pts[2]))
            rs = rg.RevSurface.Create(prof, rg.Line(C, C + Z), 0.0, a1 - a0)
            out.append(rs.ToBrep())
    return out

R = EDGE_R
msg = []
def join1(parts, what):
    j = rg.Brep.JoinBreps(parts, TOL)
    if not j or len(j) != 1 or not j[0].IsSolid:
        msg.append("AVISO: %s no queda cerrado (%d piezas)" % (what, len(j) if j else 0)); return None
    b = j[0]
    if b.SolidOrientation == rg.BrepSolidOrientation.Inward: b.Flip()
    return b

# 1) losa con canto R y los rombos (sin hueco de camara)
pieces = loop_faces(0, 0, PH_W, PH_H, PH_R, False)
pieces += list(rg.Brep.CreatePlanarBreps([rrect_curve(0, 0, PH_W, PH_H, PH_R, 0.0)], TOL))
pieces += list(rg.Brep.CreatePlanarBreps([rrect_curve(R, R, PH_W - R, PH_H - R, PH_R - R, PH_T)] + zig, TOL))
slab = join1(pieces + patches, "la losa")
# 2) cortador del hueco: paredes, abocinado R y prolongacion por encima y por debajo
#    CAM_LIFT: el abocinado del hueco se sube 0,02 mm. Asi corta la cara superior con un angulo de unos 6 grados en vez de
#    quedar tangente (la booleana falla con contactos tangentes, p. ej. en la franja de 6 mm entre el hueco y el borde).
CAM_LIFT = 0.02
ZB = -1.0; ZT = PH_T + 1.0
cut = loop_faces(CAM_X0, CAM_Y0, CAM_X1, CAM_Y1, CAM_R, True, ZB, CAM_LIFT)
up = rrect_curve(CAM_X0 - R, CAM_Y0 - R, CAM_X1 + R, CAM_Y1 + R, CAM_R + R, PH_T + CAM_LIFT)
cut.append(rg.Surface.CreateExtrusion(up, Z * (ZT - PH_T - CAM_LIFT)).ToBrep())
cut += list(rg.Brep.CreatePlanarBreps([rrect_curve(CAM_X0, CAM_Y0, CAM_X1, CAM_Y1, CAM_R, ZB)], TOL))
cut += list(rg.Brep.CreatePlanarBreps([rrect_curve(CAM_X0 - R, CAM_Y0 - R, CAM_X1 + R, CAM_Y1 + R, CAM_R + R, ZT)], TOL))
cutter = join1(cut, "el cortador del hueco")
# 3) losa - cortador
funda = None
if slab is not None and cutter is not None:
    d = rg.Brep.CreateBooleanDifference(slab, cutter, TOL)
    if d and len(d) == 1:
        funda = d[0]; funda.MergeCoplanarFaces(TOL)
        if funda.SolidOrientation == rg.BrepSolidOrientation.Inward: funda.Flip()
    else:
        msg.append("AVISO: la diferencia booleana ha dado %d piezas" % (len(d) if d else 0))

if funda is not None:
    naked = sum(1 for e in funda.Edges if e.Valence == rg.EdgeAdjacency.Naked)
    msg.append("rombos: %d | caras: %d | valido: %s | solido: %s | aristas abiertas: %d"
               % (len(patches), funda.Faces.Count, funda.IsValid, funda.IsSolid, naked))
if lost_depth > 0: msg.append("rombos no modelados (tocan el canto o solo un vertice): hundido max %.4f mm" % lost_depth)
print("\n".join(msg))

# --- Actualizar EN VIVO un objeto de Rhino (opcional) ---
# TARGET: GUID (texto) del objeto de Rhino a reemplazar. Se conserva su posicion (esquina minima del bbox) y sus atributos.
_t = globals().get('TARGET')
if _t and funda is not None:
    import System
    _doc = Rhino.RhinoDoc.ActiveDoc
    try:
        _gid = System.Guid(str(_t).strip())
        _obj = _doc.Objects.FindId(_gid)
        if _obj is None:
            print("TARGET no encontrado: %s" % _t)
        else:
            _bb = _obj.Geometry.GetBoundingBox(True)
            _new = funda.DuplicateBrep()
            _new.Translate(_bb.Min.X, _bb.Min.Y, _bb.Min.Z)
            _doc.Objects.Replace(_gid, _new)
            _doc.Views.Redraw()
            print("Actualizado %s" % _t)
    except Exception as _e:
        print("TARGET error: %s" % _e)
