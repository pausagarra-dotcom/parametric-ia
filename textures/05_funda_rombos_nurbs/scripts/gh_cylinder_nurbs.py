# GH Python 3: cilindro con rombos hundidos en los costados, en NURBS (solido valido para SolidWorks).
# Textura 05 (2026-11-15). Variante cilindro de la 01: cada rombo es UN parche Bezier liso.
# Entradas = variables (sliders). Salida: cilindro (Brep, solido cerrado). mm / grados.
import math, Rhino, Rhino.Geometry as rg

def _g(n, d):
    v = globals().get(n)
    return d if v is None else v

CYL_R = _g('CYL_R', 40.0); CYL_H = _g('CYL_H', 100.0)
CELL_W = _g('CELL_W', 5.52); CELL_H = _g('CELL_H', 9.11)   # CELL_W se ajusta para que quepa un numero entero alrededor
DEPTH = _g('DEPTH', 0.5)
SUAVIDAD = min(max(_g('SUAVIDAD', 1.0), 0.0), 1.0)        # 1 = fondo redondeado liso; 0 = se acerca a la piramide de la 01
GRADO = min(max(int(_g('GRADO', 6)), 2), 9)
GAP = max(_g('GAP', 0.5), 0.0)                             # ancho de la franja lisa entre rombos (0 = rombos pegados)
ZONES = max(int(_g('ZONES', 2)), 1)
PHASE = _g('PHASE', 0.0)
ZONE_HALF = max(_g('ZONE_HALF', 90.0), 1.0)
TX_B = max(_g('TX_B', 45.0), 1.0); TX_CZ = _g('TX_CZ', CYL_H / 2.0)
FADE_IN = min(max(_g('FADE_IN', 0.3), 0.0), 0.95)
FADE_N = max(_g('FADE_N', 4.0), 1.0)
FADE_MODE = int(_g('FADE_MODE', 0))
MIN_D = _g('MIN_D', 0.002)
TOL = 0.001
MARGIN = 0.5                   # distancia minima de un rombo a las tapas

def sm(t):
    t = min(max(t, 0.0), 1.0); return t * t * (3 - 2 * t)

def angdist(th):
    best = 360.0
    for k in range(ZONES):
        d = abs(((th - (PHASE + k * 360.0 / ZONES) + 180.0) % 360.0) - 180.0); best = min(best, d)
    return best

def env_at(sig, z):
    a = angdist(math.degrees(sig / CYL_R))
    q = ((a / ZONE_HALF) ** FADE_N + (abs(z - TX_CZ) / TX_B) ** FADE_N) ** (1.0 / FADE_N)
    t = min(max((q - FADE_IN) / max(1.0 - FADE_IN, 1e-6), 0.0), 1.0)
    if FADE_MODE == 1: return 0.5 * (1 + math.cos(math.pi * t))
    if FADE_MODE == 2: return 1.0 - t
    if FADE_MODE == 3: return 1.0 - sm(sm(t))
    return 1.0 - sm(t)

n = GRADO
soft1 = [4.0 * k * (n - k) / (n * (n - 1)) for k in range(n + 1)]
SHAPE = [[SUAVIDAD * soft1[a] * soft1[b] + (1.0 - SUAVIDAD) * (1.0 - max(abs(2.0 * a / n - 1), abs(2.0 * b / n - 1)))
          for b in range(n + 1)] for a in range(n + 1)]

# Bernstein en t_k = k/n y su inversa (para interpolar el parche ya enrollado sobre el cilindro)
def bern(k, t): return math.comb(n, k) * t ** k * (1 - t) ** (n - k)
Bm = [[bern(k, i / float(n)) for k in range(n + 1)] for i in range(n + 1)]
def inv(M):
    m = len(M); A = [row[:] + [1.0 if i == j else 0.0 for j in range(m)] for i, row in enumerate(M)]
    for c in range(m):
        p = max(range(c, m), key=lambda r: abs(A[r][c])); A[c], A[p] = A[p], A[c]
        pv = A[c][c]; A[c] = [v / pv for v in A[c]]
        for r in range(m):
            if r != c and A[r][c] != 0.0:
                f = A[r][c]; A[r] = [a - f * b for a, b in zip(A[r], A[c])]
    return [row[m:] for row in A]
Bi = inv(Bm)
Bi[0] = [1.0] + [0.0] * n; Bi[n] = [0.0] * n + [1.0]      # exactos: el borde solo depende de las muestras del borde

nx = max(int(round(2 * math.pi * CYL_R / CELL_W)), 1)
W = 2 * math.pi * CYL_R / nx
HW = W / 2.0; HH = CELL_H / 2.0
def lp(I, J): return (I * HW, TX_CZ + J * HH)
INSET = 1.0 - (GAP / 2.0) * math.sqrt(HW * HW + HH * HH) / (HW * HH)   # homotecia del rombo hacia su centro
if INSET < 0.2: INSET = 0.2
def shrink(C, P): return (C[0] + INSET * (P[0] - C[0]), C[1] + INSET * (P[1] - C[1]))
def bilin(P0, P1, P2, P3, ws, wt):
    a = (1 - ws) * (1 - wt); b = ws * (1 - wt); c = ws * wt; d = (1 - ws) * wt
    return (a * P0[0] + b * P1[0] + c * P2[0] + d * P3[0], a * P0[1] + b * P1[1] + c * P2[1] + d * P3[1])
def wrap(sig, z, d):
    th = sig / CYL_R; r = CYL_R - d
    return (r * math.cos(th), r * math.sin(th), z)

def flat_eval(net, ws, wt):   # Bezier plana (sig, z, d) en (ws, wt)
    bu = [bern(k, ws) for k in range(n + 1)]; bv = [bern(k, wt) for k in range(n + 1)]
    s = [0.0, 0.0, 0.0]
    for a in range(n + 1):
        for b in range(n + 1):
            w = bu[a] * bv[b]
            if w == 0.0: continue
            for c in range(3): s[c] += w * net[a][b][c]
    return s

Jmax = int(math.ceil((CYL_H / 2.0 + abs(TX_CZ - CYL_H / 2.0)) / HH)) + 2
NI = 2 * nx
cells = {}; lost = 0.0
for I in range(0, NI):
    for J in range(-Jmax, Jmax + 1):
        if (I + J) % 2: continue
        P0 = lp(I, J - 1); P1 = lp(I + 1, J); P2 = lp(I, J + 1); P3 = lp(I - 1, J)
        if GAP > 0:
            Cc = lp(I, J); P0, P1, P2, P3 = [shrink(Cc, P) for P in (P0, P1, P2, P3)]
        net = []; dmax = 0.0
        for a in range(n + 1):
            row = []
            for b in range(n + 1):
                s_, z_ = bilin(P0, P1, P2, P3, a / float(n), b / float(n))
                d = DEPTH * env_at(s_, z_) * SHAPE[a][b] if SHAPE[a][b] != 0.0 else 0.0
                dmax = max(dmax, d); row.append((s_, z_, d))
            net.append(row)
        if dmax < MIN_D: continue
        if P0[1] < MARGIN or P2[1] > CYL_H - MARGIN:
            lost = max(lost, dmax); continue
        cells[(I, J)] = (dmax, net, (P0, P1, P2, P3))

# rombos que solo se tocan por un vertice (contorno pellizcado): se quita el de menor hundido
def prune(cells, wrapI):
    changed = True
    while changed:
        changed = False
        for (I, J) in list(cells.keys()):
            for (a, b) in ((I + 1, J), (I - 1, J), (I, J + 1), (I, J - 1)):     # vertices del rombo
                ring = [((a - 1) % wrapI if wrapI else a - 1, b), ((a + 1) % wrapI if wrapI else a + 1, b),
                        (a % wrapI if wrapI else a, b - 1), (a % wrapI if wrapI else a, b + 1)]
                k = [c in cells for c in ring]
                if (k == [True, True, False, False]) or (k == [False, False, True, True]):
                    p, q = (ring[0], ring[1]) if k[0] else (ring[2], ring[3])
                    rm = p if cells[p][0] <= cells[q][0] else q
                    globals()['lost'] = max(globals()['lost'], cells[rm][0])
                    del cells[rm]; changed = True; break
            if changed: break
if GAP <= 0: prune(cells, NI)

patches = []; kept = []
for (I, J), (dmax, net, (P0, P1, P2, P3)) in sorted(cells.items()):
        # muestras enrolladas en t_k = k/n (bordes con d = 0 exacto) e interpolacion tensorial
        Sm = []
        for a in range(n + 1):
            row = []
            for b in range(n + 1):
                if a in (0, n) or b in (0, n):
                    s_, z_ = bilin(P0, P1, P2, P3, a / float(n), b / float(n)); d = 0.0
                else:
                    s_, z_, d = flat_eval(net, a / float(n), b / float(n))
                row.append(wrap(s_, z_, d))
            Sm.append(row)
        T = [[[sum(Bi[a][i] * Sm[i][b][c] for i in range(n + 1)) for c in range(3)] for b in range(n + 1)] for a in range(n + 1)]
        C = [[[sum(Bi[b][j] * T[a][j][c] for j in range(n + 1)) for c in range(3)] for b in range(n + 1)] for a in range(n + 1)]
        ns = rg.NurbsSurface.Create(3, False, n + 1, n + 1, n + 1, n + 1)
        for a in range(n + 1):
            for b in range(n + 1):
                ns.Points.SetPoint(a, b, rg.Point3d(*C[a][b]))
        for k in range(ns.KnotsU.Count): ns.KnotsU[k] = 0.0 if k < n else 1.0
        for k in range(ns.KnotsV.Count): ns.KnotsV[k] = 0.0 if k < n else 1.0
        patches.append(ns.ToBrep()); kept.append((I, J))

msg = []
cilindro = None
skin = rg.Brep.JoinBreps(patches, TOL) if patches else []
if not patches:
    cilindro = rg.Brep.CreateFromCylinder(rg.Cylinder(rg.Circle(CYL_R), CYL_H), True, True)
else:
    # contornos de la zona de rombos = aristas libres de la piel
    loops = []; cell_loops = []
    if GAP > 0:   # cada rombo es su propio contorno (mismo orden que kept)
        for b in patches:
            cell_loops.append(rg.Curve.JoinCurves([e.DuplicateCurve() for e in b.Edges], TOL)[0])
        loops = list(cell_loops)
    else:
        for b in skin:
            crv = [e.DuplicateCurve() for e in b.Edges if e.Valence == rg.EdgeAdjacency.Naked]
            loops += list(rg.Curve.JoinCurves(crv, TOL))
    # costado del cilindro con la costura en un angulo sin rombos (si lo hay)
    used = set(I % NI for (I, J) in kept)
    free = [I for I in range(NI) if I not in used and (I + 1) % NI not in used]     # costura entre I e I+1: no toca ningun rombo
    seam = ((free[0] + 0.5) * HW / CYL_R) if free else 0.0
    pl = rg.Plane(rg.Point3d.Origin, rg.Vector3d(math.cos(seam), math.sin(seam), 0), rg.Vector3d(-math.sin(seam), math.cos(seam), 0))
    cylb = rg.Brep.CreateFromCylinder(rg.Cylinder(rg.Circle(pl, CYL_R), CYL_H), True, True)
    side = [f for f in cylb.Faces if not f.IsPlanar(TOL)][0]
    caps = [f.DuplicateFace(False) for f in cylb.Faces if f.IsPlanar(TOL)]
    # Recortar el costado con todos los contornos a la vez cuesta O(n^2). Con GAP, antes se parte el costado en franjas
    # helicoidales que siguen el centro de las franjas lisas (lineas I-J = impar de la red, no tocan ningun rombo)
    # y cada franja se recorta solo con sus rombos.
    groups = [(side.DuplicateFace(False), loops)]
    if GAP > 0 and len(kept) > 80:
        K = max(2, min(NI // 2, len(kept) // 60))
        Ls = sorted(set(1 + 2 * int(round(k * NI / (2.0 * K))) for k in range(K)))
        hel = []
        for L in Ls:
            pts = []
            for i in range(81):
                z = CYL_H * i / 80.0
                sg = HW * (L + (z - TX_CZ) / HH)
                pts.append(rg.Point3d(CYL_R * math.cos(sg / CYL_R), CYL_R * math.sin(sg / CYL_R), z))
            hel.append(rg.Curve.CreateInterpolatedCurve(pts, 3))
        # los rombos que cruzan la costura se recortan en este primer paso (el costado aun es una sola cara)
        ssig = seam * CYL_R; P2 = 2 * math.pi * CYL_R
        def crosses_seam(I):
            d = ((I * HW - ssig + P2 / 2) % P2) - P2 / 2
            return abs(d) < INSET * HW + TOL
        seam_ids = set(i for i, (I, J) in enumerate(kept) if crosses_seam(I))
        strips = side.Split(hel + [cell_loops[i] for i in seam_ids], TOL)
        def strip_of(c):   # c = I - J (continuo) -> indice de franja
            c = c % NI
            for k in range(len(Ls)):
                a = Ls[k]; b = Ls[(k + 1) % len(Ls)] + (NI if k + 1 == len(Ls) else 0)
                if a < c < b or a < c + NI < b: return k
            return 0
        if strips is not None and strips.Faces.Count >= len(Ls):   # la costura puede partir alguna franja en dos
            pieces = []
            strip_caps = [f.DuplicateFace(False) for f in strips.Faces if f.IsPlanar(TOL)]   # tapas con las aristas ya partidas
            for f in strips.Faces:
                if f.IsPlanar(TOL): continue
                bbf = f.DuplicateFace(False).GetBoundingBox(True)
                if not (bbf.Min.Z < TOL or bbf.Max.Z > CYL_H - TOL): continue   # interior de un rombo de la costura: fuera
                # un punto interior de la franja -> su indice
                dom_u, dom_v = f.Domain(0), f.Domain(1); idx = None
                for iu in range(1, 60):
                    for iv in range(1, 60):
                        u = dom_u.ParameterAt(iu / 60.0); v = dom_v.ParameterAt(iv / 60.0)
                        if f.IsPointOnFace(u, v) == rg.PointFaceRelation.Interior:
                            p = f.PointAt(u, v); sg = math.atan2(p.Y, p.X) * CYL_R
                            idx = strip_of(sg / HW - (p.Z - TX_CZ) / HH); break
                    if idx is not None: break
                pieces.append((idx, f.DuplicateFace(False)))
            if all(k is not None for k, _ in pieces):
                bylp = [[] for _ in pieces]
                ok_all = True
                for i_c, ((I, J), lp_) in enumerate(zip(kept, cell_loops)):
                    if i_c in seam_ids: continue
                    k = strip_of(I - J)
                    cand = [i for i, (kk, _) in enumerate(pieces) if kk == k]
                    if len(cand) > 1:   # franja partida por la costura: el centro del rombo dice en que trozo esta
                        s_, z_ = lp(I, J); c3 = rg.Point3d(*wrap(s_, z_, 0.0))
                        hit = []
                        for i in cand:
                            fc = pieces[i][1].Faces[0]
                            okc, u, v = fc.ClosestPoint(c3)
                            if okc and fc.IsPointOnFace(u, v) != rg.PointFaceRelation.Exterior and fc.PointAt(u, v).DistanceTo(c3) < 0.01:
                                hit.append(i)
                        cand = hit[:1]
                    if not cand: ok_all = False; break
                    bylp[cand[0]].append(lp_)
                if ok_all:
                    groups = [(pieces[i][1], bylp[i]) for i in range(len(pieces))]
                    caps = strip_caps
    parts = list(caps); sp = True
    for fb0, lps in groups:
        r = fb0.Faces[0].Split(lps, TOL) if lps else fb0
        if r is None:
            sp = None; msg.append("AVISO: no se ha podido recortar el costado"); break
        for f in r.Faces:
            bb = f.DuplicateFace(False).GetBoundingBox(True)
            if bb.Min.Z < TOL or bb.Max.Z > CYL_H - TOL:      # costado exterior; fuera los trozos dentro de los rombos
                parts.append(f.DuplicateFace(False))
    if sp is not None:
        j = rg.Brep.JoinBreps(parts + list(skin), TOL)
        if j and len(j) == 1 and j[0].IsSolid:
            cilindro = j[0]
            if cilindro.SolidOrientation == rg.BrepSolidOrientation.Inward: cilindro.Flip()
        else:
            msg.append("AVISO: la union ha dado %d piezas" % (len(j) if j else 0))
    if not free and GAP <= 0: msg.append("aviso: no hay columna libre para la costura del cilindro")

if cilindro is not None:
    naked = sum(1 for e in cilindro.Edges if e.Valence == rg.EdgeAdjacency.Naked)
    msg.append("rombos: %d (alrededor %d, ancho real %.3f mm) | caras: %d | valido: %s | solido: %s | aristas abiertas: %d"
               % (len(patches), nx, W, cilindro.Faces.Count, cilindro.IsValid, cilindro.IsSolid, naked))
if lost > 0: msg.append("rombos no modelados (tocan las tapas o solo un vertice): hundido max %.4f mm" % lost)
print("\n".join(msg))

# --- Actualizar EN VIVO un objeto de Rhino (opcional) ---
# TARGET: GUID (texto) del objeto a reemplazar. Se conserva su posicion (centro XY del bbox y cota minima Z) y sus atributos.
_t = globals().get('TARGET')
if _t and cilindro is not None:
    import System
    _doc = Rhino.RhinoDoc.ActiveDoc
    try:
        _gid = System.Guid(str(_t).strip())
        _obj = _doc.Objects.FindId(_gid)
        if _obj is None:
            print("TARGET no encontrado: %s" % _t)
        else:
            _bb = _obj.Geometry.GetBoundingBox(True)
            _new = cilindro.DuplicateBrep()
            _new.Translate((_bb.Min.X + _bb.Max.X) / 2.0, (_bb.Min.Y + _bb.Max.Y) / 2.0, _bb.Min.Z)
            _doc.Objects.Replace(_gid, _new)
            _doc.Views.Redraw()
            print("Actualizado %s" % _t)
    except Exception as _e:
        print("TARGET error: %s" % _e)
