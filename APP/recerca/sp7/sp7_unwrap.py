# SP-7: desplegament d'una superficie organica amb minima distorsio.
# S'executa FORA de Rhino, a l'entorn C:\dev\venvs\textura (numpy + OpenCV):
#   python -I sp7_unwrap.py
# Entrada: malla_A10/25/40.json (generades a Rhino: vertexs 3D d'una graella UV 81x81
#          de les superficies organiques del SP-1, i les coordenades uv_arc del SP-1).
# Metodes comparats:
#   uv_arc - el millor del SP-1 (longitud d'arc al llarg de les isocorbes centrals)
#   lscm   - desplegament conforme (conserva angles), escalat per conservar l'area total
#   arap   - "as rigid as possible": reparteix l'error entre area i angle (iniciat amb LSCM)
# Distorsio per triangle (mateixa idea que el SP-1, pero independent de la rotacio):
#   area   = |s1*s2 - 1|        longitud = max(|s1-1|, |s2-1|)        angle = s1/s2 - 1
#   (s1 >= s2 son els valors singulars de la derivada patro(mm) -> superficie)
import json, os, sys
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
WINDOWS = (40, 60, 80, 100)


def load(A):
    d = json.load(open(os.path.join(HERE, "malla_A%d.json" % A)))
    NG = d["NG"]
    V = np.array(d["V"], float)
    tris = []
    for i in range(NG - 1):
        for j in range(NG - 1):
            a, b, c, e = i * NG + j, (i + 1) * NG + j, (i + 1) * NG + j + 1, i * NG + j + 1
            tris += [(a, b, c), (a, c, e)]
    return V, np.array(tris), np.array(d["uv_arc"], float), d["center"]


def local_frames(V, T):
    p0, p1, p2 = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
    e1 = p1 - p0
    n = np.cross(e1, p2 - p0)
    area = 0.5 * np.linalg.norm(n, axis=1)
    n /= np.linalg.norm(n, axis=1)[:, None]
    ex = e1 / np.linalg.norm(e1, axis=1)[:, None]
    ey = np.cross(n, ex)
    # coordenades locals 2D dels 3 vertexs
    X = np.stack([np.zeros(len(T)), np.einsum("ij,ij->i", e1, ex), np.einsum("ij,ij->i", p2 - p0, ex)], 1)
    Y = np.stack([np.zeros(len(T)), np.zeros(len(T)), np.einsum("ij,ij->i", p2 - p0, ey)], 1)
    # gradient d'una funcio lineal: grad f = G @ f_tri  (G: 2x3 per triangle)
    G = np.zeros((len(T), 2, 3))
    for k in range(3):
        k1, k2 = (k + 1) % 3, (k + 2) % 3
        G[:, 0, k] = (Y[:, k1] - Y[:, k2])
        G[:, 1, k] = (X[:, k2] - X[:, k1])
    G /= (2 * area)[:, None, None]
    return G, area


class Sparse:
    def __init__(self, r, c, v, shape):
        self.r, self.c, self.v, self.shape = np.asarray(r), np.asarray(c), np.asarray(v), shape
    def mv(self, x):
        return np.bincount(self.r, self.v * x[self.c], minlength=self.shape[0])
    def rmv(self, y):
        return np.bincount(self.c, self.v * y[self.r], minlength=self.shape[1])


def cgls(A, b, x0, iters=4000, tol=1e-10):
    x = x0.copy(); r = b - A.mv(x); s = A.rmv(r); p = s.copy(); g = s @ s
    g0 = g
    for _ in range(iters):
        q = A.mv(p); a = g / (q @ q); x += a * p; r -= a * q
        s = A.rmv(r); gn = s @ s
        if gn < tol * g0: break
        p = s + (gn / g) * p; g = gn
    return x


def lscm(V, T, G, area, pins, pin_uv):
    nV, nT = len(V), len(T)
    w = np.sqrt(area)
    rows, cols, vals = [], [], []
    # incognites: u (0..nV-1), v (nV..2nV-1); condicio conforme: grad v = R90 grad u
    #   Gx.v + Gy.u = 0   ;   Gy.v - Gx.u = 0
    for k in range(3):
        idx = T[:, k]
        rows += [np.arange(nT), np.arange(nT), nT + np.arange(nT), nT + np.arange(nT)]
        cols += [nV + idx, idx, nV + idx, idx]
        vals += [w * G[:, 0, k], w * G[:, 1, k], w * G[:, 1, k], -w * G[:, 0, k]]
    rows, cols, vals = np.concatenate(rows), np.concatenate(cols), np.concatenate(vals)
    # fixa dos vertexs: es treuen de les incognites i passen al terme independent
    fixed = np.concatenate([pins, nV + pins]); fval = np.concatenate([pin_uv[:, 0], pin_uv[:, 1]])
    free = np.ones(2 * nV, bool); free[fixed] = False
    newidx = -np.ones(2 * nV, int); newidx[free] = np.arange(free.sum())
    xfix = np.zeros(2 * nV); xfix[fixed] = fval
    b = -np.bincount(rows, vals * xfix[cols], minlength=2 * nT)
    m = free[cols]
    A = Sparse(rows[m], newidx[cols[m]], vals[m], (2 * nT, free.sum()))
    x = cgls(A, b, np.zeros(free.sum()))
    full = xfix.copy(); full[free] = x
    uv = np.stack([full[:nV], full[nV:]], 1)
    return uv


def rescale_area(V, T, uv):
    a3 = triangle_area3(V, T).sum(); a2 = np.abs(triangle_area2(uv, T)).sum()
    c = uv.mean(0)
    return c + (uv - c) * np.sqrt(a3 / a2)


def arap(V, T, G, area, uv0, iters=60):
    nV, nT = len(V), len(T)
    w = np.sqrt(area)
    rows, cols, vals = [], [], []
    for k in range(3):
        rows += [np.arange(nT), nT + np.arange(nT)]
        cols += [T[:, k], T[:, k]]
        vals += [w * G[:, 0, k], w * G[:, 1, k]]
    A = Sparse(np.concatenate(rows), np.concatenate(cols), np.concatenate(vals), (2 * nT, nV))
    uv = uv0.copy()
    for it in range(iters):
        J = np.stack([np.einsum("tij,tj->ti", G, uv[T, 0]), np.einsum("tij,tj->ti", G, uv[T, 1])], 1)  # files: grad u, grad v
        U, S, Vt = np.linalg.svd(J)
        D = np.ones((nT, 2)); D[:, 1] = np.sign(np.linalg.det(U @ Vt))
        R = U @ (D[:, :, None] * Vt)
        for c in range(2):
            b = np.concatenate([w * R[:, c, 0], w * R[:, c, 1]])
            uv[:, c] = cgls(A, b, uv[:, c], iters=600, tol=1e-12)
    return uv


def triangle_area3(V, T):
    return 0.5 * np.linalg.norm(np.cross(V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]]), axis=1)


def triangle_area2(uv, T):
    a = uv[T[:, 1]] - uv[T[:, 0]]; b = uv[T[:, 2]] - uv[T[:, 0]]
    return 0.5 * (a[:, 0] * b[:, 1] - a[:, 1] * b[:, 0])


def distortion(V, T, uv):
    E3 = np.stack([V[T[:, 1]] - V[T[:, 0]], V[T[:, 2]] - V[T[:, 0]]], 2)          # 3x2
    E2 = np.stack([uv[T[:, 1]] - uv[T[:, 0]], uv[T[:, 2]] - uv[T[:, 0]]], 2)       # 2x2
    K = E3 @ np.linalg.inv(E2)                                                       # d(3D)/d(patro)
    s = np.linalg.svd(K, compute_uv=False)
    s1, s2 = s[:, 0], s[:, 1]
    flipped = triangle_area2(uv, T) <= 0
    return {"area": np.abs(s1 * s2 - 1), "length": np.maximum(np.abs(s1 - 1), np.abs(s2 - 1)), "angle": s1 / s2 - 1, "flip": flipped}


def window_stats(uv, T, ci, d, W):
    c = (uv[T].mean(1) - uv[ci])
    m = (np.abs(c[:, 0]) <= W / 2) & (np.abs(c[:, 1]) <= W / 2)
    out = {"n": int(m.sum())}
    for k in ("area", "length", "angle"):
        v = d[k][m]
        out[k] = {"max": round(float(v.max()), 4), "p95": round(float(np.percentile(v, 95)), 4)}
    out["flip"] = int(d["flip"][m].sum())
    return out


def draw_map(uv, T, ci, vals, W, path, vmax=0.3, title=""):
    S = 4.0; size = 900
    c = uv - uv[ci]
    img = np.full((size, size, 3), 255, np.uint8)
    for t, v in zip(T, vals):
        p = np.round(c[t] * S + size / 2).astype(np.int32)
        p[:, 1] = size - p[:, 1]
        x = min(v / vmax, 1.0)
        col = cv2.applyColorMap(np.uint8([[int(255 * x)]]), cv2.COLORMAP_TURBO)[0, 0].tolist()
        cv2.fillConvexPoly(img, p, col)
    h = int(W / 2 * S)
    cv2.rectangle(img, (size // 2 - h, size // 2 - h), (size // 2 + h, size // 2 + h), (0, 0, 0), 2)
    cv2.putText(img, title, (12, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    cv2.putText(img, "0%", (12, size - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    for i in range(300):
        col = cv2.applyColorMap(np.uint8([[int(255 * i / 299)]]), cv2.COLORMAP_TURBO)[0, 0].tolist()
        cv2.line(img, (50 + i, size - 50), (50 + i, size - 30), col, 1)
    cv2.putText(img, ">= %d%%" % int(vmax * 100), (360, size - 34), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)
    cv2.imwrite(path, img)


def main():
    results = {}
    for A in (10, 25, 40):
        V, T, uv_arc, ci = load(A)
        G, area = local_frames(V, T)
        # pins: dos vertexs als extrems de la fila central, a la seva posicio uv_arc
        NG = int(round(np.sqrt(len(V))))
        pins = np.array([(NG // 2), (NG - 1) * NG + NG // 2])
        uv_l = rescale_area(V, T, lscm(V, T, G, area, pins, uv_arc[pins]))
        uv_a = arap(V, T, G, area, uv_l)
        res = {}
        for name, uv in (("uv_arc", uv_arc), ("lscm", uv_l), ("arap", uv_a)):
            d = distortion(V, T, uv)
            res[name] = {str(W): window_stats(uv, T, ci, d, W) for W in WINDOWS}
            draw_map(uv, T, ci, d["area"], 100, os.path.join(HERE, "mapa_area_A%d_%s.png" % (A, name)),
                     title="A%d  %s  distorsio d'area (quadrat = 100 mm)" % (A, name))
            np.save(os.path.join(HERE, "uv_A%d_%s.npy" % (A, name)), uv)
        results["A%d" % A] = res
        print("A%d" % A, json.dumps({k: {W: (v[W]["area"]["max"], v[W]["length"]["max"], v[W]["angle"]["max"], v[W]["flip"]) for W in ("60", "100")} for k, v in res.items()}))
    json.dump(results, open(os.path.join(HERE, "sp7_results.json"), "w"), indent=1)


def regional():
    """Desplega NOMES la zona a texturar (finestra W centrada), com faria l'app."""
    out = {}
    for A in (10, 25, 40):
        V, T, uv_arc, ci = load(A)
        out["A%d" % A] = {}
        for W in WINDOWS:
            c = uv_arc[T].mean(1) - uv_arc[ci]
            m = (np.abs(c[:, 0]) <= W / 2) & (np.abs(c[:, 1]) <= W / 2)
            Ts = T[m]
            used = np.unique(Ts); remap = -np.ones(len(V), int); remap[used] = np.arange(len(used))
            Vs, Ts2, uvs = V[used], remap[Ts], uv_arc[used]
            ci2 = remap[ci]
            G, area = local_frames(Vs, Ts2)
            # pins: els dos vertexs mes allunyats en x a la fila del centre
            row = np.where(np.abs(uvs[:, 1] - uvs[ci2, 1]) < 1e-6)[0]
            pins = np.array([row[np.argmin(uvs[row, 0])], row[np.argmax(uvs[row, 0])]])
            uv_l = rescale_area(Vs, Ts2, lscm(Vs, Ts2, G, area, pins, uvs[pins]))
            uv_a = arap(Vs, Ts2, G, area, uv_l, iters=80)
            e = {}
            for name, uv in (("uv_arc", uvs), ("lscm", uv_l), ("arap", uv_a)):
                d = distortion(Vs, Ts2, uv)
                e[name] = {k: {"max": round(float(d[k].max()), 4), "p95": round(float(np.percentile(d[k], 95)), 4)} for k in ("area", "length", "angle")}
                e[name]["flip"] = int(d["flip"].sum())
                if W == 100 and A == 25:
                    draw_map(uv, Ts2, ci2, d["area"], 100, os.path.join(HERE, "mapa_regional_A25_W100_%s.png" % name),
                             title="A25 regional 100 mm  %s  distorsio d'area" % name)
                    np.save(os.path.join(HERE, "uvreg_A25_W100_%s.npy" % name), uv)
                    np.save(os.path.join(HERE, "uvreg_A25_W100_idx.npy"), used)
            out["A%d" % A][str(W)] = e
            print("A%d W%d" % (A, W), {k: (v["area"]["max"], v["length"]["max"], v["angle"]["max"], v["flip"]) for k, v in e.items()})
    json.dump(out, open(os.path.join(HERE, "sp7_regional.json"), "w"), indent=1)


if __name__ == "__main__":
    if "regional" in sys.argv:
        regional()
    else:
        main()
