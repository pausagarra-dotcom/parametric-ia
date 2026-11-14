# GH Python 3: funda con rombos hundidos. Las ENTRADAS (nombre = variable) vienen de sliders; si falta una, se usa el valor por defecto.
# Salida: phone (Mesh).  Unidades mm.
import math, Rhino, Rhino.Geometry as rg
def _g(n, d):
    v = globals().get(n)
    return d if v is None else v
PH_W=_g('PH_W',75.0)        # ancho del movil
PH_H=_g('PH_H',165.0)       # alto del movil
PH_T=_g('PH_T',8.5)         # grosor
PH_R=_g('PH_R',12.0)        # radio de esquinas
EDGE_R=_g('EDGE_R',3.0)     # radio del canto
CELL_W=_g('CELL_W',5.52)    # ancho del rombo (diagonal horizontal)
CELL_H=_g('CELL_H',9.11)    # alto del rombo (diagonal vertical)
DEPTH=_g('DEPTH',0.5)       # profundidad del hundido
TX_CX=PH_W/2
TX_CY=_g('TX_CY',58.0)      # centro Y de la zona texturada
TX_A=_g('TX_A',27.5)        # semiancho de la zona texturada
TX_B=_g('TX_B',55.0)        # semialto de la zona texturada
FADE_IN=_g('FADE_IN',0.50)  # 0..0.95: donde empieza a desvanecerse (0 = desde el centro, 0.95 = casi en el borde)
FADE_N=_g('FADE_N',4.0)     # 2 = zona elipse, 8 = casi rectangular
FADE_MODE=int(_g('FADE_MODE',0))  # 0 suave tangente (smoothstep), 1 coseno (tangente al final), 2 lineal (arista), 3 abrupto-suave (smoothstep^2, mas tiempo plano)
CAM_X0=_g('CAM_X0',8.0); CAM_X1=_g('CAM_X1',72.0); CAM_Y0=_g('CAM_Y0',117.0); CAM_Y1=_g('CAM_Y1',159.0); CAM_R=6.0
DETAIL=max(int(_g('DETAIL',2)),1)  # 1..4: subdivisiones de la malla por cada medio rombo. 2 = pirámides exactas con pocas caras; mas = bordes/fade mas finos
def rr(px,py,cx,cy,hx,hy,r):
    qx=abs(px-cx)-(hx-r); qy=abs(py-cy)-(hy-r)
    return math.hypot(max(qx,0),max(qy,0))+min(max(qx,qy),0)-r
def sdf(x,y):
    return max(rr(x,y,PH_W/2,PH_H/2,PH_W/2,PH_H/2,PH_R), -rr(x,y,(CAM_X0+CAM_X1)/2,(CAM_Y0+CAM_Y1)/2,(CAM_X1-CAM_X0)/2,(CAM_Y1-CAM_Y0)/2,CAM_R))
def snap(x,y):
    for _ in range(6):
        d=sdf(x,y)
        if d<=0: break
        e=1e-3; gx=(sdf(x+e,y)-sdf(x-e,y))/(2*e); gy=(sdf(x,y+e)-sdf(x,y-e))/(2*e)
        n=gx*gx+gy*gy or 1.0
        x-=d*gx/n; y-=d*gy/n
    return x,y
def sm(t):
    t=min(max(t,0.0),1.0); return t*t*(3-2*t)
def depth_at(x,y):
    q=((abs(x-TX_CX)/TX_A)**FADE_N+(abs(y-TX_CY)/TX_B)**FADE_N)**(1.0/FADE_N)
    t=min(max((q-FADE_IN)/max(1.0-FADE_IN,1e-6),0.0),1.0)
    if FADE_MODE==1: env=0.5*(1+math.cos(math.pi*t))
    elif FADE_MODE==2: env=1.0-t
    elif FADE_MODE==3: env=1.0-sm(sm(t))
    else: env=1.0-sm(t)
    if env<=0: return 0.0
    best=0.0
    for ox,oy in ((0,0),(.5,.5)):
        u=(x-TX_CX)/CELL_W-ox; v=(y-TX_CY)/CELL_H-oy
        u-=round(u); v-=round(v)
        best=max(best,1-2*(abs(u)+abs(v)))
    return DEPTH*env*max(best,0.0)
def zt(x,y):
    d=max(-sdf(x,y),0.0)
    ed=EDGE_R-math.sqrt(max(EDGE_R**2-(EDGE_R-d)**2,0.0)) if d<EDGE_R else 0.0
    return PH_T-ed-depth_at(x,y)
def backslash(cu,cv):   # True si la arista del rombo en esta celda (centro cu,cv en unidades de rombo) va como "\\"
    bd=None
    for ox,oy in ((0,0),(.5,.5)):
        du=cu-ox-round(cu-ox); dv=cv-oy-round(cv-oy)
        L=abs(du)+abs(dv)
        if bd is None or L<bd[0]-1e-9: bd=(L,du*dv>0)
    return bd[1]
DX=CELL_W/(2.0*DETAIL); DY=CELL_H/(2.0*DETAIL)   # la malla sigue la red de rombos: las aristas de las piramides caen sobre nodos
i0=-int(math.ceil(TX_CX/DX))-1; i1=int(math.ceil((PH_W-TX_CX)/DX))+1
j0=-int(math.ceil(TX_CY/DY))-1; j1=int(math.ceil((PH_H-TX_CY)/DY))+1
vid={}; pts=[]; key={}
def vertex(i,j):
    k=(i,j)
    if k in vid: return vid[k]
    x,y=snap(TX_CX+i*DX,TX_CY+j*DY)
    kk=(round(x,4),round(y,4))
    if kk in key: vid[k]=key[kk]; return key[kk]
    n=len(pts); pts.append((x,y)); key[kk]=n; vid[k]=n; return n
tops=[]
def add(ids):
    u=[]
    for t in ids:
        if t not in u: u.append(t)
    if len(u)>=3: tops.append(u)
for j in range(j0,j1):
    for i in range(i0,i1):
        cs=[(i,j),(i+1,j),(i+1,j+1),(i,j+1)]
        if all(sdf(TX_CX+a*DX,TX_CY+b*DY)>0 for a,b in cs): continue
        A,B,C,D=[vertex(a,b) for a,b in cs]
        # diagonal paralela a la arista del rombo en este cuadrante
        if backslash((i+.5)*DX/CELL_W,(j+.5)*DY/CELL_H): add([A,B,D]); add([B,C,D])   # arista "\\" -> diagonal BD
        else: add([A,B,C]); add([A,C,D])
N=len(pts)
m=rg.Mesh()
for (x,y) in pts: m.Vertices.Add(x,y,zt(x,y))
for (x,y) in pts: m.Vertices.Add(x,y,0.0)
for f in tops:
    if len(f)==4: m.Faces.AddFace(f[0],f[1],f[2],f[3]); m.Faces.AddFace(N+f[3],N+f[2],N+f[1],N+f[0])
    else: m.Faces.AddFace(f[0],f[1],f[2]); m.Faces.AddFace(N+f[2],N+f[1],N+f[0])
edges=set()
for f in tops:
    for k in range(len(f)): edges.add((f[k],f[(k+1)%len(f)]))
for (a,b) in edges:
    if (b,a) not in edges: m.Faces.AddFace(a,N+a,N+b,b)
m.Vertices.CombineIdentical(True,True); m.Compact()
m.Normals.ComputeNormals()
m.FaceNormals.ComputeFaceNormals(); m.Unweld(0.5236, True)   # separa solo aristas con mas de 30 grados (rim y tapas); pirámides suaves, sin lineas en Sombreado
vol=rg.VolumeMassProperties.Compute(m)
if vol and vol.Volume<0: m.Flip(True,True,True)
phone = m

# --- Actualizar EN VIVO un objeto de Rhino (opcional) ---
# TARGET: GUID (texto) del objeto malla de Rhino a reemplazar. Se conserva su posicion actual (esquina minima del bbox) y sus atributos.
_t = globals().get('TARGET')
if _t:
    import System, scriptcontext
    _doc = Rhino.RhinoDoc.ActiveDoc
    try:
        _gid = System.Guid(str(_t).strip())
        _obj = _doc.Objects.FindId(_gid)
        if _obj is None:
            print("TARGET no encontrado: %s" % _t)
        else:
            _bb = _obj.Geometry.GetBoundingBox(True)
            _new = m.DuplicateMesh()
            _new.Translate(_bb.Min.X, _bb.Min.Y, _bb.Min.Z)
            _doc.Objects.Replace(_gid, _new)
            _doc.Views.Redraw()
            print("Actualizado %s: %d caras" % (_t, _new.Faces.Count))
    except Exception as _e:
        print("TARGET error: %s" % _e)
