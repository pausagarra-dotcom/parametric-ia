# GH Python 3: cilindro con rombos hundidos en los costados, que se desvanecen hacia el centro. Entradas = variables; salida: cyl (Mesh). mm / grados.
import math, Rhino, Rhino.Geometry as rg
def _g(n, d):
    v = globals().get(n)
    return d if v is None else v
CYL_R=_g('CYL_R',40.0); CYL_H=_g('CYL_H',100.0)       # radio y altura del cilindro
CELL_W=_g('CELL_W',5.52); CELL_H=_g('CELL_H',9.11)    # rombo (CELL_W se ajusta un poco para que quepa un numero entero alrededor)
DEPTH=_g('DEPTH',0.5)                                 # profundidad del hundido
ZONES=max(int(_g('ZONES',2)),1)                       # numero de costados con textura (2 = izquierda y derecha)
PHASE=_g('PHASE',0.0)                                 # angulo (grados) del centro del primer costado
ZONE_HALF=max(_g('ZONE_HALF',90.0),1.0)               # semiancho angular (grados) hasta donde llega el desvanecimiento. 90 con 2 costados = nada en el centro
TX_B=max(_g('TX_B',45.0),1.0); TX_CZ=_g('TX_CZ',CYL_H/2.0)   # semialto de la zona y altura de su centro
FADE_IN=min(max(_g('FADE_IN',0.3),0.0),0.95)          # donde empieza a bajar la profundidad (0 = desde el centro del costado)
FADE_N=max(_g('FADE_N',4.0),1.0)                      # 2 = zona elipse, 8 = casi rectangular
FADE_MODE=int(_g('FADE_MODE',0))                      # 0 suave tangente, 1 coseno, 2 lineal (arista), 3 mantiene mas y cae al final
DETAIL=max(int(_g('DETAIL',2)),1)                     # subdivisiones por medio rombo (mas = mas caras)
def sm(t):
    t=min(max(t,0.0),1.0); return t*t*(3-2*t)
nx=max(int(round(2*math.pi*CYL_R/CELL_W)),1); W=2*math.pi*CYL_R/nx      # rombos enteros alrededor (sin costura)
def angdist(th):  # distancia angular (grados) al centro de costado mas cercano
    best=360.0
    for k in range(ZONES):
        d=abs(((th-(PHASE+k*360.0/ZONES)+180.0)%360.0)-180.0); best=min(best,d)
    return best
def depth_at(s,z,th):
    a=angdist(th)
    q=((a/ZONE_HALF)**FADE_N+(abs(z-TX_CZ)/TX_B)**FADE_N)**(1.0/FADE_N)
    t=min(max((q-FADE_IN)/max(1.0-FADE_IN,1e-6),0.0),1.0)
    if FADE_MODE==1: env=0.5*(1+math.cos(math.pi*t))
    elif FADE_MODE==2: env=1.0-t
    elif FADE_MODE==3: env=1.0-sm(sm(t))
    else: env=1.0-sm(t)
    if env<=0: return 0.0
    best=0.0
    for ox,oy in ((0,0),(.5,.5)):
        u=s/W-ox; v=(z-TX_CZ)/CELL_H-oy
        u-=round(u); v-=round(v)
        best=max(best,1-2*(abs(u)+abs(v)))
    return DEPTH*env*max(best,0.0)
def backslash(cu,cv):   # True si la arista del rombo en esta celda (centro cu,cv en unidades de rombo) va como "\"
    bd=None
    for ox,oy in ((0,0),(.5,.5)):
        du=cu-ox-round(cu-ox); dv=cv-oy-round(cv-oy)
        L=abs(du)+abs(dv)
        if bd is None or L<bd[0]-1e-9: bd=(L,du*dv>0)
    return bd[1]
M=nx*2*DETAIL                                  # columnas alrededor
DZ=CELL_H/(2.0*DETAIL)
zs=[0.0]
k=int(math.ceil((0.0-TX_CZ)/DZ))
while TX_CZ+k*DZ<CYL_H-1e-6:
    z=TX_CZ+k*DZ
    if z>1e-6: zs.append(z)
    k+=1
zs.append(CYL_H)
R=len(zs)
m=rg.Mesh()
for kk in range(R):
    z=zs[kk]
    for i in range(M):
        th=2*math.pi*i/M; s=CYL_R*th
        r=CYL_R-depth_at(s,z,math.degrees(th))
        m.Vertices.Add(r*math.cos(th),r*math.sin(th),z)
vi=lambda i,kk: kk*M+(i%M)
for kk in range(R-1):
    for i in range(M):
        A,B,C,D=vi(i,kk),vi(i+1,kk),vi(i+1,kk+1),vi(i,kk+1)
        cu=(i+.5)/(2.0*DETAIL); cv=((zs[kk]+zs[kk+1])/2.0-TX_CZ)/CELL_H
        if backslash(cu,cv): m.Faces.AddFace(A,B,D); m.Faces.AddFace(B,C,D)
        else: m.Faces.AddFace(A,B,C); m.Faces.AddFace(A,C,D)
b=m.Vertices.Add(0,0,0); t=m.Vertices.Add(0,0,CYL_H)
for i in range(M):
    m.Faces.AddFace(b,vi(i+1,0),vi(i,0))
    m.Faces.AddFace(t,vi(i,R-1),vi(i+1,R-1))
m.Normals.ComputeNormals(); m.Compact()
m.FaceNormals.ComputeFaceNormals(); m.Unweld(0.5236, True)   # separa solo aristas con mas de 30 grados (rim y tapas); pirámides suaves, sin lineas en Sombreado
vol=rg.VolumeMassProperties.Compute(m)
if vol and vol.Volume<0: m.Flip(True,True,True)
cyl = m

# --- Actualizar EN VIVO un objeto de Rhino (opcional) ---
# TARGET: GUID (texto) de la malla de Rhino a reemplazar. Se conserva su posicion (centro XY del bbox y cota minima Z) y sus atributos.
_t = globals().get('TARGET')
if _t:
    import System
    _doc = Rhino.RhinoDoc.ActiveDoc
    try:
        _gid = System.Guid(str(_t).strip())
        _obj = _doc.Objects.FindId(_gid)
        if _obj is None:
            print("TARGET no encontrado: %s" % _t)
        else:
            _bb = _obj.Geometry.GetBoundingBox(True)
            _new = m.DuplicateMesh()
            _new.Translate((_bb.Min.X+_bb.Max.X)/2.0, (_bb.Min.Y+_bb.Max.Y)/2.0, _bb.Min.Z)
            _doc.Objects.Replace(_gid, _new)
            _doc.Views.Redraw()
            print("Actualizado %s: %d caras" % (_t, _new.Faces.Count))
    except Exception as _e:
        print("TARGET error: %s" % _e)
