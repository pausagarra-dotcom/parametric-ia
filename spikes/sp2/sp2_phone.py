# SP-2 (fiel, 1 imagen): funda de movil con rombos HUNDIDOS que se desvanecen hasta quedar tangentes. Rhino: run_python -> exec.
# Parametros (mm). [H]=medido en test_01.JPG, [S]=supuesto
import math, Rhino, Rhino.Geometry as rg, scriptcontext as sc
PH_W=75.0; PH_H=165.0; PH_T=8.5; PH_R=12.0; EDGE_R=3.0     # cuerpo [S] (escala: 0,44 mm/px con movil ~75 mm de ancho)
CELL_W=5.52; CELL_H=9.11                                   # diagonales del rombo [H en px, mm por escala S]
DEPTH=0.5                                                  # profundidad del hundido en el centro del rombo [S]
TX_CX=PH_W/2; TX_CY=58.0; TX_A=27.5; TX_B=55.0             # zona texturada (semiejes) [H aprox. de la foto]
FADE_IN=0.50                                               # q<FADE_IN: profundidad plena; q 0.5->1: baja a 0 tangente [H cualitativo]
CAM_X0=8.0; CAM_X1=72.0; CAM_Y0=117.0; CAM_Y1=159.0; CAM_R=6.0   # ventana de camara (agujero pasante) [H aprox.]
STEP=0.35; OX=500.0; OY=-800.0                              # malla y posicion en la escena
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
    q=((abs(x-TX_CX)/TX_A)**4+(abs(y-TX_CY)/TX_B)**4)**0.25
    env=1.0-sm((q-FADE_IN)/(1.0-FADE_IN))
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
nx=int(PH_W/STEP)+2; ny=int(PH_H/STEP)+2
vid={}; pts=[]; key={}
def vertex(i,j):
    k=(i,j)
    if k in vid: return vid[k]
    x,y=snap(i*STEP,j*STEP)
    kk=(round(x,4),round(y,4))
    if kk in key: vid[k]=key[kk]; return key[kk]
    n=len(pts); pts.append((x,y)); key[kk]=n; vid[k]=n; return n
tops=[]
for j in range(ny):
    for i in range(nx):
        cs=[(i,j),(i+1,j),(i+1,j+1),(i,j+1)]
        if all(sdf(a*STEP,b*STEP)>0 for a,b in cs): continue
        # evita quads totalmente fuera cuyo snap colapsa: se descartan si todos fuera
        ids=[vertex(a,b) for a,b in cs]
        u=[]; 
        for t in ids:
            if t not in u: u.append(t)
        if len(u)>=3: tops.append(u)
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
vol=rg.VolumeMassProperties.Compute(m)
if vol and vol.Volume<0: m.Flip(True,True,True)
m.Translate(OX,OY,0)
print("cerrada",m.IsClosed,"valida",m.IsValid,"caras",m.Faces.Count,"vol_mm3",round(abs(vol.Volume),0) if vol else None)
sc.doc.Objects.AddMesh(m); sc.doc.Views.Redraw()
