# SP-8: mateix desplegament ARAP del SP-7 (zona A25 de 100 mm), pero amb matrius disperses de scipy
# i la factoritzacio feta una sola vegada. Mesura el temps i comprova que dona la mateixa distorsio.
# Entorn: C:\dev\venvs\textura  ->  python -I sp8_arap_scipy.py
import os, sys, time, json
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla

SP7 = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "sp7")
sys.path.insert(0, SP7)
import sp7_unwrap as U  # noqa: E402


def rows_matrix(T, G, area, nV):
    nT = len(T); w = np.sqrt(area)
    r, c, v = [], [], []
    for k in range(3):
        r += [np.arange(nT), nT + np.arange(nT)]
        c += [T[:, k], T[:, k]]
        v += [w * G[:, 0, k], w * G[:, 1, k]]
    return sp.csr_matrix((np.concatenate(v), (np.concatenate(r), np.concatenate(c))), shape=(2 * nT, nV)), w


def lscm_sp(T, G, area, nV, pins, pin_uv):
    nT = len(T); w = np.sqrt(area)
    r, c, v = [], [], []
    for k in range(3):
        idx = T[:, k]
        r += [np.arange(nT), np.arange(nT), nT + np.arange(nT), nT + np.arange(nT)]
        c += [nV + idx, idx, nV + idx, idx]
        v += [w * G[:, 0, k], w * G[:, 1, k], w * G[:, 1, k], -w * G[:, 0, k]]
    A = sp.csc_matrix((np.concatenate(v), (np.concatenate(r), np.concatenate(c))), shape=(2 * nT, 2 * nV))
    fixed = np.concatenate([pins, nV + pins]); fval = np.concatenate([pin_uv[:, 0], pin_uv[:, 1]])
    free = np.setdiff1d(np.arange(2 * nV), fixed)
    b = -A[:, fixed] @ fval
    Af = A[:, free]
    x = spla.spsolve((Af.T @ Af).tocsc(), Af.T @ b)
    full = np.zeros(2 * nV); full[fixed] = fval; full[free] = x
    return np.stack([full[:nV], full[nV:]], 1)


def arap_sp(T, G, area, uv0, iters):
    nV = len(uv0)
    A, w = rows_matrix(T, G, area, nV)
    M = (A.T @ A).tolil(); M[0, :] = 0; M[0, 0] = 1  # fixa el vertex 0 (translacio)
    lu = spla.splu(M.tocsc())
    At = A.T.tocsr()
    uv = uv0.copy()
    for _ in range(iters):
        J = np.stack([np.einsum("tij,tj->ti", G, uv[T, 0]), np.einsum("tij,tj->ti", G, uv[T, 1])], 1)
        Uu, S, Vt = np.linalg.svd(J)
        D = np.ones((len(T), 2)); D[:, 1] = np.sign(np.linalg.det(Uu @ Vt))
        R = Uu @ (D[:, :, None] * Vt)
        for c in range(2):
            rhs = At @ np.concatenate([w * R[:, c, 0], w * R[:, c, 1]])
            rhs[0] = uv[0, c]
            uv[:, c] = lu.solve(rhs)
    return uv


def main():
    V, T, uv_arc, ci = U.load(25)
    W = 100
    c = uv_arc[T].mean(1) - uv_arc[ci]
    m = (np.abs(c[:, 0]) <= W / 2) & (np.abs(c[:, 1]) <= W / 2)
    Ts = T[m]; used = np.unique(Ts); remap = -np.ones(len(V), int); remap[used] = np.arange(len(used))
    Vs, Ts2, uvs = V[used], remap[Ts], uv_arc[used]; ci2 = remap[ci]
    t0 = time.time()
    G, area = U.local_frames(Vs, Ts2)
    row = np.where(np.abs(uvs[:, 1] - uvs[ci2, 1]) < 1e-6)[0]
    pins = np.array([row[np.argmin(uvs[row, 0])], row[np.argmax(uvs[row, 0])]])
    uv_l = U.rescale_area(Vs, Ts2, lscm_sp(Ts2, G, area, len(Vs), pins, uvs[pins]))
    t1 = time.time()
    uv_a = arap_sp(Ts2, G, area, uv_l, 80)
    t2 = time.time()
    dl, da = U.distortion(Vs, Ts2, uv_l), U.distortion(Vs, Ts2, uv_a)
    res = {"vertexs": len(Vs), "triangles": len(Ts2), "t_lscm_s": round(t1 - t0, 3), "t_arap80_s": round(t2 - t1, 3),
           "lscm_area_max": round(float(dl["area"].max()), 4), "arap_area_max": round(float(da["area"].max()), 4),
           "arap_flip": int(da["flip"].sum())}
    # malla mes fina: subdivideix 2x (aprox. 1,25 mm) per veure com escala
    print(json.dumps(res))
    json.dump(res, open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sp8_arap_scipy.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
