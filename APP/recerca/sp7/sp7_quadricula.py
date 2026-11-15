# SP-7: quadricula de prova (escacs de 10 mm al pla del patro) pintada sobre la superficie A25,
# per comparar uv_arc i ARAP a la zona de 100 mm. Render simple amb OpenCV (projeccio en perspectiva,
# ordre de pintor, ombrejat lambertia). Entorn: C:\dev\venvs\textura  ->  python -I sp7_quadricula.py
import json, os
import numpy as np
import cv2

HERE = os.path.dirname(os.path.abspath(__file__))
SQ, N = 10.0, 4


def tris_of(NG, keep):
    out = []
    for i in range(NG - 1):
        for j in range(NG - 1):
            a, b, c, e = i * NG + j, (i + 1) * NG + j, (i + 1) * NG + j + 1, i * NG + j + 1
            for t in ((a, b, c), (a, c, e)):
                if all(x in keep for x in t):
                    out.append(t)
    return out


def subdivide(P, U):
    out = []
    for i in range(N):
        for j in range(N - i):
            tri = [(i, j), (i + 1, j), (i, j + 1)]
            out.append(tri)
            if i + j < N - 1:
                out.append([(i + 1, j), (i + 1, j + 1), (i, j + 1)])
    res = []
    for tri in out:
        w = np.array([[a / N, b / N, (N - a - b) / N] for a, b in tri])
        res.append((w @ P, w @ U))
    return res


def render(V, tris, pos, uv, cam, tgt, size=(900, 700), f=1500):
    fwd = tgt - cam; fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, [0, 0, 1.0]); right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    light = np.array([0.3, -0.5, 1.0]); light /= np.linalg.norm(light)
    polys = []
    for t in tris:
        P = V[list(t)]; U = uv[[pos[x] for x in t]]
        for p3, u2 in subdivide(P, U):
            cu, cv = u2.mean(0)
            k = (int(np.floor(cu / SQ)) + int(np.floor(cv / SQ))) % 2
            base = np.array([40, 120, 235.0]) if k == 0 else np.array([245, 245, 245.0])  # BGR
            n = np.cross(p3[1] - p3[0], p3[2] - p3[0]); n /= np.linalg.norm(n) + 1e-12
            if n[2] < 0: n = -n
            shade = 0.35 + 0.65 * max(0.0, float(n @ light))
            rel = p3 - cam
            z = rel @ fwd
            xy = np.stack([rel @ right, rel @ up], 1) / z[:, None] * f
            pix = np.round(xy * [1, -1] + [size[0] / 2, size[1] / 2]).astype(np.int32)
            polys.append((z.mean(), pix, tuple(int(c) for c in base * shade)))
    img = np.full((size[1], size[0], 3), 255, np.uint8)
    for _, pix, col in sorted(polys, key=lambda q: -q[0]):
        cv2.fillConvexPoly(img, pix, col, lineType=cv2.LINE_AA)
    return img


def main():
    m = json.load(open(os.path.join(HERE, "malla_A25.json")))
    q = json.load(open(os.path.join(HERE, "quadricula_A25_W100.json")))
    V = np.array(m["V"]); idx = q["idx"]; pos = {g: k for k, g in enumerate(idx)}
    tris = tris_of(m["NG"], pos)
    c = V[idx].mean(0)
    views = {"persp": (c + np.array([0, -170, 160.0]), c), "planta": (c + np.array([0, -0.01, 330.0]), c)}
    for vn, (cam, tgt) in views.items():
        row = []
        for name in ("uv_arc", "arap"):
            img = render(V, tris, pos, np.array(q[name]), cam, tgt)
            label = {"uv_arc": "uv_arc (SP-1): area max 16 %", "arap": "ARAP regional: area max 5 %"}[name]
            cv2.putText(img, label, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 2, cv2.LINE_AA)
            row.append(img)
        out = np.hstack(row)
        cv2.imwrite(os.path.join(HERE, "quadricula_A25_W100_%s.png" % vn), out)
        print(vn, out.shape)


if __name__ == "__main__":
    main()
