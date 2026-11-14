# SP-2 (fiel, 1 imagen): textura de rombos piramidales sobre placa plana, en Rhino (run_python -> exec).
# Parametros (medidos en test_01.JPG por autocorrelacion, ver sp2_fiel.py):
#   DIAG_W_PX=12.26, DIAG_H_PX=20.25 (diagonales del rombo en px de la foto)  [H]
#   MM_PER_PX=0.45  -> escala SUPUESTA (movil ~75 mm = ~165 px)               [S]
#   DEPTH_MM=0.5    -> altura de la piramide SUPUESTA (no medible en 2D)      [S]
import Rhino, Rhino.Geometry as rg, scriptcontext as sc, json
MM_PER_PX=0.45; DIAG_W_PX=12.26; DIAG_H_PX=20.25
CELL_W=DIAG_W_PX*MM_PER_PX; CELL_H=DIAG_H_PX*MM_PER_PX   # mm
DEPTH_MM=0.5; PLATE_W=60.0; PLATE_H=60.0; BASE_MM=2.0; STEP=0.3
def z(x,y):
    # rombos centrados en la red (i*W, j*H) y ((i+.5)*W,(j+.5)*H); piramide = 1 - distancia L1 normalizada
    best=0.0
    for ox,oy in ((0,0),(.5,.5)):
        u=(x/CELL_W-ox); v=(y/CELL_H-oy)
        u-=round(u); v-=round(v)
        h=1-2*(abs(u)+abs(v))        # 1 en el centro, 0 en el borde del rombo
        if h>best: best=h
    return DEPTH_MM*best
nx=int(PLATE_W/STEP); ny=int(PLATE_H/STEP)
m=rg.Mesh()
for j in range(ny+1):
    for i in range(nx+1):
        m.Vertices.Add(i*STEP,j*STEP,z(i*STEP,j*STEP))
for j in range(ny+1):
    for i in range(nx+1):
        m.Vertices.Add(i*STEP,j*STEP,-BASE_MM)
off=(nx+1)*(ny+1); idx=lambda i,j:j*(nx+1)+i
for j in range(ny):
    for i in range(nx):
        m.Faces.AddFace(idx(i,j),idx(i+1,j),idx(i+1,j+1),idx(i,j+1))                          # cara superior
        m.Faces.AddFace(off+idx(i,j+1),off+idx(i+1,j+1),off+idx(i+1,j),off+idx(i,j))          # fondo
for i in range(nx):
    m.Faces.AddFace(idx(i,0),off+idx(i,0),off+idx(i+1,0),idx(i+1,0))
    m.Faces.AddFace(idx(i+1,ny),off+idx(i+1,ny),off+idx(i,ny),idx(i,ny))
for j in range(ny):
    m.Faces.AddFace(idx(0,j+1),off+idx(0,j+1),off+idx(0,j),idx(0,j))
    m.Faces.AddFace(idx(nx,j),off+idx(nx,j),off+idx(nx,j+1),idx(nx,j+1))
m.Normals.ComputeNormals(); m.Compact()
m.UnifyNormals()
print("cerrada",m.IsClosed,"valida",m.IsValid,"caras",m.Faces.Count,"celda mm",round(CELL_W,2),round(CELL_H,2))
pass  # no se borra nada de la escena
sc.doc.Objects.AddMesh(m)
Rhino.RhinoApp.RunScript("_SelNone _Zoom _All _Extents",False)
sc.doc.Views.Redraw()
