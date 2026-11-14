# SP-1: distorsion del mapeo de una ventana de patron (mm) sobre una cara.
# Se ejecuta DENTRO de Rhino (run_python -> exec de este fichero).
# Metodos: uv (parametrico), planar (proyeccion), cyl (proyeccion cilindrica, solo cilindros), sporph (SporphSpaceMorph).
# Distorsion por muestreo: longitud en X, longitud en Y, angulo entre ejes, area. 0 = sin distorsion.
import math, json, os
import Rhino
import Rhino.Geometry as rg
import scriptcontext as sc

OUT = r"H:\Mi unidad\PARAMETRIC IA_New_shot\spikes\sp1"
TOL = 0.001
N = 21          # muestras por eje
H = 0.25        # mm, paso para diferencias finitas
THRESH = 0.15


def unit(v):
    v = rg.Vector3d(v); v.Unitize(); return v


def surf_length(S, a, b, along_u):
    d = S.Domain(0 if along_u else 1)
    pts = []
    for i in range(41):
        t = d.ParameterAt(i / 40.0)
        pts.append(S.PointAt(t, b) if along_u else S.PointAt(a, t))
    return sum(pts[i].DistanceTo(pts[i + 1]) for i in range(40))


class Setup(object):
    def __init__(self, name, brep, W, kind):
        self.name, self.brep, self.W, self.kind = name, brep, W, kind
        self.S = brep.Faces[0].UnderlyingSurface()
        du, dv = self.S.Domain(0), self.S.Domain(1)
        self.uc, self.vc = du.Mid, dv.Mid
        self.C = self.S.PointAt(self.uc, self.vc)
        self.Nn = unit(self.S.NormalAt(self.uc, self.vc))
        e = 1e-3 * du.Length
        Su = unit(self.S.PointAt(self.uc + e, self.vc) - self.S.PointAt(self.uc - e, self.vc))
        Y = unit(rg.Vector3d.CrossProduct(self.Nn, Su))
        self.plane = rg.Plane(self.C, Su, Y)
        self.Lu = surf_length(self.S, 0, self.vc, True)
        self.Lv = surf_length(self.S, self.uc, 0, False)
        self.du, self.dv = du, dv


def f_uv(s):
    def f(x, y):
        u = s.uc + x / s.Lu * s.du.Length
        v = s.vc + y / s.Lv * s.dv.Length
        if not (s.du.IncludesParameter(u) and s.dv.IncludesParameter(v)):
            return None
        return s.S.PointAt(u, v)
    return f


def arc_table(s, along_u, n=400):
    d = s.du if along_u else s.dv
    ts = [d.ParameterAt(i / float(n)) for i in range(n + 1)]
    pts = [s.S.PointAt(t, s.vc) if along_u else s.S.PointAt(s.uc, t) for t in ts]
    cum = [0.0]
    for i in range(n):
        cum.append(cum[-1] + pts[i].DistanceTo(pts[i + 1]))
    tc = s.uc if along_u else s.vc
    # longitud acumulada en el parametro central
    k = min(range(n + 1), key=lambda i: abs(ts[i] - tc))
    s0 = cum[k]
    return ts, [c - s0 for c in cum]


def inv_len(ts, cum, L):
    if L < cum[0] or L > cum[-1]:
        return None
    lo, hi = 0, len(cum) - 1
    while hi - lo > 1:
        m = (lo + hi) // 2
        if cum[m] <= L: lo = m
        else: hi = m
    w = (L - cum[lo]) / max(cum[hi] - cum[lo], 1e-12)
    return ts[lo] + w * (ts[hi] - ts[lo])


def f_uv_arc(s):
    tu, cu = arc_table(s, True); tv, cv = arc_table(s, False)
    def f(x, y):
        u = inv_len(tu, cu, x); v = inv_len(tv, cv, y)
        if u is None or v is None:
            return None
        return s.S.PointAt(u, v)
    return f


def f_uv_local(s):
    e = 1e-4
    su = (s.S.PointAt(s.uc + e, s.vc) - s.S.PointAt(s.uc - e, s.vc)).Length / (2 * e)
    sv = (s.S.PointAt(s.uc, s.vc + e) - s.S.PointAt(s.uc, s.vc - e)).Length / (2 * e)
    def f(x, y):
        u = s.uc + x / su; v = s.vc + y / sv
        if not (s.du.IncludesParameter(u) and s.dv.IncludesParameter(v)):
            return None
        return s.S.PointAt(u, v)
    return f


def f_planar(s):
    def f(x, y):
        start = s.plane.PointAt(x, y, 0) + s.Nn * 1000.0
        # proyecta hacia -N; coge el impacto mas cercano al punto de partida
        pts = rg.Intersect.Intersection.ProjectPointsToBreps([s.brep], [start], -s.Nn, TOL)
        if not pts or len(pts) == 0:
            return None
        return min(pts, key=lambda p: p.DistanceTo(start))
    return f


def f_cyl(s):
    ok, cyl = s.S.TryGetCylinder(TOL)
    if not ok:
        return None
    ax = unit(cyl.Axis); r = cyl.Radius
    # origen angular = direccion centro->eje; z = y del patron
    # eje infinito
    t = rg.Vector3d.Multiply(rg.Vector3d(s.C - cyl.Center), ax)
    p_axis = cyl.Center + ax * t
    radial0 = unit(s.C - p_axis)
    tang = unit(rg.Vector3d.CrossProduct(ax, radial0))
    def f(x, y):
        a = x / r
        rad = radial0 * math.cos(a) + tang * math.sin(a)
        return p_axis + ax * y + rad * r
    return f


def f_sporph(s):
    W = s.W
    tu, cu = arc_table(s, True); tv, cv = arc_table(s, False)
    u0, u1 = inv_len(tu, cu, -W / 2), inv_len(tu, cu, W / 2)
    v0, v1 = inv_len(tv, cv, -W / 2), inv_len(tv, cv, W / 2)
    tgt = s.S.Trim(rg.Interval(u0, u1), rg.Interval(v0, v1))
    src = rg.PlaneSurface(s.plane, rg.Interval(-W / 2, W / 2), rg.Interval(-W / 2, W / 2))
    morph = Rhino.Geometry.Morphs.SporphSpaceMorph(src, tgt)
    morph.Tolerance = TOL
    def f(x, y):
        p = s.plane.PointAt(x, y, 0)
        q = morph.MorphPoint(p)
        return q
    return f


def measure(f, W):
    xs = [(-W / 2 + W * i / (N - 1)) for i in range(N)]
    # evita el borde exacto para diferencias hacia adelante
    xs = [min(max(x, -W / 2 + H), W / 2 - H) for x in xs]
    area_d, len_d, ang_d, n_ok, n_all = [], [], [], 0, 0
    for x in xs:
        for y in xs:
            n_all += 1
            try:
                p0, px, py = f(x, y), f(x + H, y), f(x, y + H)
            except Exception:
                p0 = px = py = None
            if p0 is None or px is None or py is None:
                continue
            a = (px - p0) / H; b = (py - p0) / H
            la, lb = a.Length, b.Length
            if la < 1e-9 or lb < 1e-9:
                continue
            cos = rg.Vector3d.Multiply(a, b) / (la * lb)
            th = math.acos(max(-1, min(1, cos)))
            cross = rg.Vector3d.CrossProduct(a, b).Length
            n_ok += 1
            area_d.append(abs(cross - 1.0))
            len_d.append(max(abs(la - 1.0), abs(lb - 1.0)))
            ang_d.append(abs(th - math.pi / 2) / (math.pi / 2))
    def stats(v):
        if not v: return None
        v = sorted(v)
        return {"max": round(v[-1], 4), "p95": round(v[int(0.95 * (len(v) - 1))], 4)}
    return {"coverage": round(n_ok / float(n_all), 3), "area": stats(area_d), "length": stats(len_d), "angle": stats(ang_d)}


def make_surfaces(amps=(10, 25, 40)):
    res = []
    cyl = rg.Cylinder(rg.Circle(rg.Plane.WorldXY, 40.0), 100.0).ToBrep(False, False)
    res.append(Setup("cilindro_r40", cyl, 60.0, "cyl"))
    pl = rg.Brep.CreateFromCornerPoints(rg.Point3d(0, 0, 0), rg.Point3d(100, 0, 0), rg.Point3d(100, 100, 0), rg.Point3d(0, 100, 0), TOL)
    res.append(Setup("plano_100", pl, 60.0, "plane"))
    for A in amps:
        n = 7
        pts = []
        for i in range(n):
            for j in range(n):
                z = A * math.sin(i * 1.1 + 0.5) * math.cos(j * 0.9 + 0.3)
                pts.append(rg.Point3d(i * 200.0 / (n - 1), j * 200.0 / (n - 1), z))
        ns = rg.NurbsSurface.CreateFromPoints(pts, n, n, 3, 3)
        res.append(Setup("organica_A%d" % A, ns.ToBrep(), 100.0, "org"))
    return res


def run():
    results = {}
    for s in make_surfaces():
        entry = {"W_mm": s.W, "Lu": round(s.Lu, 2), "Lv": round(s.Lv, 2)}
        for name, mk in (("uv_dom", f_uv), ("uv_local", f_uv_local), ("uv_arc", f_uv_arc), ("planar", f_planar), ("cyl", f_cyl), ("sporph", f_sporph)):
            try:
                f = mk(s)
                entry[name] = measure(f, s.W) if f else "n/a"
            except Exception as e:
                entry[name] = "error: %s" % e
        results[s.name] = entry
    with open(os.path.join(OUT, "sp1_results.json"), "w") as fh:
        json.dump(results, fh, indent=1)
    return results

R = run()
for k, v in R.items():
    print(k, json.dumps(v))
