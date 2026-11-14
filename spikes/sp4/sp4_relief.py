# SP-4: via A (contornos). Se ejecuta DENTRO de Rhino: exec de este fichero tras fijar CFG.
# Pipeline por contorno: circulo en mm -> (u,v) por longitud de arco (SP-1) -> curva sobre la superficie ->
# parche local (Surface.Trim) -> Split con la curva -> cara interior -> Brep.CreateFromOffsetFace (solido).
import math, time, json, os
import Rhino
import Rhino.Geometry as rg
import scriptcontext as sc

src = open(r"H:\Mi unidad\PARAMETRIC IA_New_shot\spikes\sp1\sp1_mapping.py", encoding="utf-8").read().split("R = run()")[0]
exec(src)  # Setup, arc_table, inv_len, make_surfaces...

OUT4 = r"H:\Mi unidad\PARAMETRIC IA_New_shot\spikes\sp4"


def contour_uv(s, tu, cu, tv, cv, cx, cy, r, npts=24):
    pts = []
    for k in range(npts):
        a = 2 * math.pi * k / npts
        u = inv_len(tu, cu, cx + r * math.cos(a)); v = inv_len(tv, cv, cy + r * math.sin(a))
        if u is None or v is None:
            return None
        pts.append((u, v))
    return pts


def make_boss(s, uvs, depth, tol):
    """devuelve (Brep|None, motivo_fallo)"""
    us = [p[0] for p in uvs]; vs = [p[1] for p in uvs]
    mu = 0.35 * (max(us) - min(us)); mv = 0.35 * (max(vs) - min(vs))
    ui = rg.Interval(max(min(us) - mu, s.du.Min), min(max(us) + mu, s.du.Max))
    vi = rg.Interval(max(min(vs) - mv, s.dv.Min), min(max(vs) + mv, s.dv.Max))
    sub = s.S.Trim(ui, vi)
    if sub is None:
        return None, "trim"
    patch = sub.ToBrep()
    pl = [rg.Point3d(u, v, 0) for (u, v) in uvs]
    pl.append(pl[0])  # estilo periodico: el ultimo punto repite el primero
    c2 = rg.Curve.CreateInterpolatedCurve(pl, 3, rg.CurveKnotStyle.ChordPeriodic)
    if c2 is None:
        return None, "curve"
    crv = s.S.Pushup(c2, tol)
    if crv is None:
        return None, "pushup"
    if not crv.IsClosed:
        return None, "pushup_open"
    import System
    cl = System.Collections.Generic.List[rg.Curve]()
    cl.Add(crv)
    pieces = patch.Split(cl, tol)
    if not pieces or len(pieces) < 2:
        return None, "split"
    inner = min(pieces, key=lambda b: rg.AreaMassProperties.Compute(b).Area)
    solid = rg.Brep.CreateFromOffsetFace(inner.Faces[0], depth, tol, False, True)
    if solid is None:
        return None, "offset"
    return solid, None


def run_case(s, k, depth, tol, add_to_doc=False):
    W = 180.0
    tu, cu = arc_table(s, True); tv, cv = arc_table(s, False)
    pitch = W / k; r = 0.3 * pitch
    t0 = time.time()
    ok = 0; fails = {}; valid = 0; solids = 0; vol = 0.0; times = []
    for i in range(k):
        for j in range(k):
            cx = -W / 2 + pitch * (i + 0.5); cy = -W / 2 + pitch * (j + 0.5)
            t1 = time.time()
            uvs = contour_uv(s, tu, cu, tv, cv, cx, cy, r)
            if uvs is None:
                fails["fuera_dominio"] = fails.get("fuera_dominio", 0) + 1; continue
            try:
                b, why = make_boss(s, uvs, depth, tol)
            except Exception as e:
                b, why = None, "excepcion:%s" % str(e)[:40]
            times.append(time.time() - t1)
            if b is None:
                fails[why] = fails.get(why, 0) + 1; continue
            ok += 1
            if b.IsValid: valid += 1
            if b.IsSolid: solids += 1
            vp = rg.VolumeMassProperties.Compute(b)
            if vp: vol += abs(vp.Volume)
            if add_to_doc:
                sc.doc.Objects.AddBrep(b)
    total = time.time() - t0
    n = k * k
    exp_vol = n * math.pi * r * r * abs(depth)
    return {"contornos": n, "ok": ok, "fallos": fails, "validos": valid, "solidos": solids,
            "tiempo_total_s": round(total, 2), "tiempo_medio_ms": round(1000 * sum(times) / max(len(times), 1), 1),
            "volumen_mm3": round(vol, 1), "volumen_esperado_aprox_mm3": round(exp_vol, 1),
            "r_mm": round(r, 2), "profundidad_mm": depth, "tol": tol}

