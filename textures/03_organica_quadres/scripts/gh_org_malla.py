# GH Python 3 -- MALLA: reparte el resultado de la formula sobre los nodos, desplaza la superficie y ensambla la malla con normales suaves.
# La formula (nodos 'Evaluate' del lienzo) se evalua una vez por coordenada local distinta; aqui solo se "pega" en cada celda hundida:
#     z(nodo) = ZU[UIDX(nodo)] * min(ENVX[i], ENVY[j])         (0 si el nodo esta en una celda plana)
# Punto desplazado S = B + z N, con N = normal de la superficie (producto vectorial de las tangentes de la propia rejilla de puntos base P).
# Normal del punto desplazado:  n = N - (dz/dx) Tx - (dz/dy) Ty   (Tx,Ty tangentes unitarias; dz/dx por diferencias finitas no uniformes sobre
# la rejilla), asi el sombreado es suave aunque la malla sea gruesa y la arista nitida se mantiene.
# Entradas: P (puntos base de 'Evaluar superficie'), NX, NY, XM, YM, ZU, UIDX, ENVX, ENVY      Salida: mesh
import math, Rhino, Rhino.Geometry as rg
from System.Collections.Generic import List
nx = int(NX); ny = int(NY)
P0 = list(P)
xm = [float(v) for v in XM]; ym = [float(v) for v in YM]
zu = [float(v) for v in ZU]; uidx = [int(v) for v in UIDX]; ex = [float(v) for v in ENVX]; ey = [float(v) for v in ENVY]
n = nx * ny
px = [p.X for p in P0]; py = [p.Y for p in P0]; pz = [p.Z for p in P0]
z = [0.0] * n
for j in range(ny):
    eyj = ey[j]
    for i in range(nx):
        k = j * nx + i; u = uidx[k]
        if u >= 0:
            e = ex[i] if ex[i] < eyj else eyj
            z[k] = zu[u] * e
def d1(f0, f1, f2, h1, h2):
    # derivada en el nodo central con pasos h1 (atras) y h2 (adelante), no uniformes.
    # Diferencia centrada donde el campo es suave; junto a una pared (un vecino a menos de 0.6 mm) se toma el menor de los dos
    # lados (minmod), para que la pared nitida no se "corra" hacia el fondo; a ras (f1 = 0) la normal es la de la superficie.
    db = (f1 - f0) / h1; df = (f2 - f1) / h2
    if min(h1, h2) >= 0.6:      # nodo lejos de cualquier pared: diferencia centrada (campo suave)
        return -h2 / (h1 * (h1 + h2)) * f0 + (h2 - h1) / (h1 * h2) * f1 + h1 / (h2 * (h1 + h2)) * f2
    if db * df <= 0: return 0.0     # nodo pegado a una pared: el menor de los dos lados
    return math.copysign(min(abs(db), abs(df)), db)
vl = List[rg.Point3d](); normals = []
sq = math.sqrt
for j in range(ny):
    ja = max(j - 1, 0); jb = min(j + 1, ny - 1)
    for i in range(nx):
        k = j * nx + i
        ia = max(i - 1, 0); ib = min(i + 1, nx - 1)
        ka = j * nx + ia; kb = j * nx + ib
        tx0 = px[kb] - px[ka]; tx1 = py[kb] - py[ka]; tx2 = pz[kb] - pz[ka]
        ka2 = ja * nx + i; kb2 = jb * nx + i
        ty0 = px[kb2] - px[ka2]; ty1 = py[kb2] - py[ka2]; ty2 = pz[kb2] - pz[ka2]
        lx = sq(tx0 * tx0 + tx1 * tx1 + tx2 * tx2) or 1.0; ly = sq(ty0 * ty0 + ty1 * ty1 + ty2 * ty2) or 1.0
        tx0 /= lx; tx1 /= lx; tx2 /= lx; ty0 /= ly; ty1 /= ly; ty2 /= ly
        n0 = tx1 * ty2 - tx2 * ty1; n1 = tx2 * ty0 - tx0 * ty2; n2 = tx0 * ty1 - tx1 * ty0     # Tx x Ty = normal de la superficie
        ln = sq(n0 * n0 + n1 * n1 + n2 * n2) or 1.0
        n0 /= ln; n1 /= ln; n2 /= ln
        zk = z[k]
        if zk == 0.0:                       # a ras: el punto y la normal de la superficie tal cual
            vl.Add(P0[k]); normals.append(rg.Vector3f(n0, n1, n2)); continue
        vl.Add(rg.Point3d(px[k] + n0 * zk, py[k] + n1 * zk, pz[k] + n2 * zk))
        hx1 = max(abs(xm[k] - xm[ka]), 1e-6); hx2 = max(abs(xm[kb] - xm[k]), 1e-6)
        if i == 0: zx = (z[kb] - zk) / hx2
        elif i == nx - 1: zx = (zk - z[ka]) / hx1
        else: zx = d1(z[ka], zk, z[kb], hx1, hx2)
        hy1 = max(abs(ym[k] - ym[ka2]), 1e-6); hy2 = max(abs(ym[kb2] - ym[k]), 1e-6)
        if j == 0: zy = (z[kb2] - zk) / hy2
        elif j == ny - 1: zy = (zk - z[ka2]) / hy1
        else: zy = d1(z[ka2], zk, z[kb2], hy1, hy2)
        a = n0 - zx * tx0 - zy * ty0; b = n1 - zx * tx1 - zy * ty1; c = n2 - zx * tx2 - zy * ty2
        L = sq(a * a + b * b + c * c)
        normals.append(rg.Vector3f(a / L, b / L, c / L))
m = rg.Mesh()
m.Vertices.AddVertices(vl)
# la topologia solo depende de NX, NY: se guarda entre ejecuciones
try:
    import scriptcontext as _sc
    _st = _sc.sticky
except Exception:
    _st = {}
_key = ('org_malla_caras', nx, ny)
fl = _st.get(_key)
if fl is None:
    fl = List[rg.MeshFace]()
    for j in range(ny - 1):
        for i in range(nx - 1):
            A = j * nx + i; B = A + 1; C = A + nx + 1; D = A + nx
            # diagonal siempre en la direccion "\" (arriba-izquierda -> abajo-derecha): es la direccion en la que el fondo casi no varia
            # (la diagonal marcada es la de arriba-derecha a abajo-izquierda); asi las aristas de la malla no cruzan el degradado
            fl.Add(rg.MeshFace(A, B, D)); fl.Add(rg.MeshFace(B, C, D))
    _st[_key] = fl
m.Faces.AddFaces(fl)
m.Normals.Clear()
for v in normals: m.Normals.Add(v)
m.Compact()
mesh = m
info = "malla: %d vertices, %d caras" % (m.Vertices.Count, m.Faces.Count)
print(info)
