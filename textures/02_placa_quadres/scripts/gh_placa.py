# GH Python 3: placa plana con cuadrados HUNDIDOS en damero (uno si, uno no) que se desvanecen al acercarse a la arista. Ref: cases/sp2/test_02.jpg
# ENTRADAS (nombre = variable) vienen de sliders; si falta una se usa el valor por defecto. Salida: plate (Mesh). Unidades mm.
import math, time, Rhino, Rhino.Geometry as rg
_t0 = time.time()
def _g(n, d):
    v = globals().get(n)
    return d if v is None else v
PL_W=max(_g('PL_W',120.0),10.0)    # ancho de la placa
PL_H=max(_g('PL_H',160.0),10.0)    # alto de la placa
PL_T=max(_g('PL_T',10.0),1.0)      # grosor
PL_R=_g('PL_R',24.0)               # radio de las esquinas (en planta)
EDGE_R=_g('EDGE_R',6.0)            # radio del canto superior (redondeo de la arista)
CELL=max(_g('CELL',8.0),1.0)       # paso de la reticula (lado del cuadrado + junta)
PATTERN=int(_g('PATTERN',0))       # 0 damero (como la referencia: un cuadrado hundido, el siguiente plano), 1 todos hundidos
GAP=max(_g('GAP',0.2),0.0)         # margen plano alrededor de cada cuadrado hundido
CORNER_R=max(_g('CORNER_R',1.2),0.0)    # radio de las esquinas del cuadrado hundido (en PROFILE 7 afecta a las 4 esquinas; las marcadas se notan mas)
WALL=_g('WALL',0.2)               # ancho (en planta) de la pared del hundido (PROFILE 7: ancho de la caida en los lados con arista marcada)
DEPTH=_g('DEPTH',0.4)          # profundidad del hundido (negativo = cuadrados en relieve)
PROFILE=int(_g('PROFILE',7))       # pared: 0 suave (S), 1 lineal, 2 cuarto de circulo, 3 cuenco parabolico, 4 borde redondeado + cuenco, 5 dos aristas + dos lados fundidos, 6 canal, 7 COMO LA REFERENCIA: fondo parabolico suave entre las dos esquinas marcadas, aristas marcadas (con radio RIM) arriba-derecha y abajo-izquierda que se funden hacia las otras dos
RIM=max(_g('RIM',0.4),0.05)        # PROFILE 4/5/7: radio (en planta) del redondeo de la arista marcada (menos = arista mas viva)
CRISP=int(_g('CRISP',0))           # PROFILE 5/7: esquinas marcadas: 0 arriba-derecha+abajo-izquierda (referencia), 1 arriba-izquierda+abajo-derecha (gira 90 grados cada paso)
SOFT=min(max(_g('SOFT',0.7),0.05),1.0)  # PROFILE 5: fraccion del cuadrado en la que el fondo sube hasta fundirse con los lados sin arista
AXIS=int(_g('AXIS',0))             # PROFILE 6: direccion del canal: 0 el canal corre en X (aristas a izquierda/derecha, radio arriba/abajo), 1 en Y
SIDE=max(_g('SIDE',0.3),0.02)     # PROFILE 6: ancho del redondeo de las dos aristas laterales (menos = arista mas marcada)
TILT=min(max(_g('TILT',0.8),0.0),1.0)   # PROFILE 7: inclinacion del fondo hacia la esquina marcada (0 = simetrico)
LIP=min(max(_g('LIP',0.3),0.0),1.0)     # PROFILE 7: fuerza de la arista marcada (labio que sigue el contorno redondeado, fuerte en las esquinas marcadas)
ANGLE=_g('ANGLE',0.0)              # giro de la reticula (grados)
FADE_GAP=max(_g('FADE_GAP',3.0),0.0)    # mm planos (sin textura) entre el final del redondeo del canto y el inicio del patron
FADE_LEN=max(_g('FADE_LEN',25.0),0.0)   # mm en los que la profundidad pasa de 0 a plena (hacia el interior)
FADE_MODE=int(_g('FADE_MODE',0))   # 0 suave tangente (smoothstep), 1 coseno, 2 lineal, 3 smoothstep^2 (mas tiempo plano junto al borde)
DETAIL=max(int(_g('DETAIL',2)),1)  # 1..6: resolucion de la malla (PROFILE 7: paso de nodos ~ 3.4/DETAIL mm). Mas = mas fino, mas caras y mas tiempo
STEP_MAX=max(_g('STEP_MAX',1.0),0.2)    # separacion maxima entre nodos en zonas planas (fondo, junta y canto)

PL_R=min(max(PL_R,0.0),min(PL_W,PL_H)/2.0)
EDGE_R=min(max(EDGE_R,0.0),PL_T*0.95,min(PL_W,PL_H)/2.0-0.01)
CX=PL_W/2.0; CY=PL_H/2.0
half=CELL/2.0
g2=min(GAP/2.0,half*0.9)
W=min(max(WALL,0.01),half-g2)
FL=half-g2-W                        # semilado del fondo plano
F0=EDGE_R+FADE_GAP                  # distancia al borde donde el patron vale 0
ca=math.cos(math.radians(ANGLE)); sa=math.sin(math.radians(ANGLE))

def rr(px,py,cx,cy,hx,hy,r):
    qx=abs(px-cx)-(hx-r); qy=abs(py-cy)-(hy-r)
    return math.hypot(max(qx,0),max(qy,0))+min(max(qx,qy),0)-r
def sdf(x,y):
    return rr(x,y,CX,CY,CX,CY,PL_R)
EDGE_SEG=max(int(_g('EDGE_SEG',12)),2)   # segmentos del redondeo del canto
D_GRID=min(EDGE_R+max(0.3,min(1.0,FADE_GAP*0.5)), min(PL_W,PL_H)/2.0-0.5)   # la reticula llega hasta aqui; desde aqui al borde: anillos del canto
def sdf_in(x,y):
    return sdf(x,y)+D_GRID
def grad(x,y):
    e=1e-4; gx=(sdf(x+e,y)-sdf(x-e,y))/(2*e); gy=(sdf(x,y+e)-sdf(x,y-e))/(2*e)
    n=math.hypot(gx,gy) or 1.0
    return gx/n, gy/n
def snap(x,y):
    for _ in range(8):
        d=sdf_in(x,y)
        if d<=0: break
        e=1e-3; gx=(sdf(x+e,y)-sdf(x-e,y))/(2*e); gy=(sdf(x,y+e)-sdf(x,y-e))/(2*e)
        n=gx*gx+gy*gy or 1.0
        x-=d*gx/n; y-=d*gy/n
    return x,y
def sm(t):
    t=min(max(t,0.0),1.0); return t*t*(3-2*t)
def env_at(d):      # 0 junto a la arista -> 1 en el interior
    if FADE_LEN<=1e-6: return 1.0 if d>=F0 else 0.0
    t=min(max((d-F0)/FADE_LEN,0.0),1.0)
    if FADE_MODE==1: return 0.5*(1-math.cos(math.pi*t))
    if FADE_MODE==2: return t
    if FADE_MODE==3: return sm(sm(t))
    return sm(t)
def wall(t):
    t=min(max(t,0.0),1.0)
    if PROFILE==1: return t
    if PROFILE==2: return math.sqrt(max(1.0-(1.0-t)**2,0.0))
    if PROFILE==3: return 1.0-(1.0-t)**2
    if PROFILE==4:   # el borde arranca tangente (redondeo de ancho RIM) y sigue en un cuenco parabolico hasta el centro
        e=t*W; rm=min(RIM,W*0.9)
        es=e*e/(2.0*rm) if e<rm else e-rm/2.0
        T=min(es/(W-rm/2.0),1.0)
        return 1.0-(1.0-T)**2
    return t*t*(3-2*t)
PH=half-g2                          # semilado del cuadrado hundido
# Las curvas de nivel del hundido son superelipses (cuadrado con esquinas redondeadas, sin aristas en las diagonales).
# El exponente sale de CORNER_R: la esquina del borde pasa por el mismo punto que un cuadrado redondeado de ese radio.
_rc=min(CORNER_R,PH*0.999)
if _rc<=0.01: NEXP=None
else: NEXP=min(max(-math.log(2.0)/math.log(1.0-(1.0-1.0/math.sqrt(2.0))*_rc/PH),2.0),40.0)
def _rrect_in(a,b,PHh,rc):              # distancia hacia dentro desde el borde de un cuadrado redondeado
    qx=abs(a)-(PHh-rc); qy=abs(b)-(PHh-rc)
    return -(math.hypot(max(qx,0.0),max(qy,0.0))+min(max(qx,qy),0.0)-rc)
_WC=max(WALL,0.05); _RC=min(max(CORNER_R,0.05),PH*0.95)
_RHO=min(RIM/_WC,0.9)
def pocket7(a,b):
    """Hundido 'como la referencia' (a,b: coordenadas en la celda; esquinas marcadas = arriba-derecha y abajo-izquierda).
    Fondo: (1-s^2)(1-t^2)*(1+TILT*p), con p=(s+t)/2: polinomio, a ras en todo el contorno del cuadrado. TILT lo inclina hacia la
    diagonal marcada (degradado oscuro->claro como la referencia). Sin valores absolutos, minimos, angulos ni divisiones: ninguna banda.
    Se suma el labio LIP*p^2 (fuerte solo en las esquinas marcadas) y una rampa corta WALL en el contorno redondeado (arista nitida)."""
    ec=_rrect_in(a,b,PH,_RC)
    if ec<=0.0: return 0.0
    s_=min(max(a/PH,-1.0),1.0); t_=min(max(b/PH,-1.0),1.0)
    p=(s_+t_)*0.5
    f=max((1.0-s_*s_)*(1.0-t_*t_),0.0)*(1.0+TILT*p)
    T=min(ec/_WC,1.0); M=1.0-(1.0-T)**2
    return (f+LIP*p*p)*M
def _bmax7():
    best=0.0; n=24
    for i in range(n+1):
        for j in range(n+1):
            best=max(best,pocket7(-PH+2*PH*i/n,-PH+2*PH*j/n))
    return best or 1.0
BMAX7=_bmax7() if PROFILE==7 else 1.0
def cell_depth(u,v):  # 0..1 en coordenadas de la reticula
    iu=round(u/CELL); iv=round(v/CELL)
    if PATTERN==0 and (int(iu)+int(iv))%2!=0: return 0.0     # damero: esta celda queda plana
    if PROFILE==7:
        a=u-CELL*iu; b=v-CELL*iv
        for _ in range(CRISP%4): a,b=-b,a                     # CRISP gira las esquinas marcadas
        return pocket7(a,b)/BMAX7
    if PROFILE==6:
        a=u-CELL*iu; b=v-CELL*iv
        if AXIS%2==1: a,b=b,a                                 # a: a lo largo del canal, b: a traves
        if abs(a)>=PH or abs(b)>=PH: return 0.0
        rm=min(RIM,PH*0.9); e=PH-abs(b)                       # extremos arriba/abajo: entra tangente con radio (ancho RIM) y sigue en curva parabolica
        es=e*e/(2.0*rm) if e<rm else e-rm/2.0
        T=min(es/(PH-rm/2.0),1.0); f=1.0-(1.0-T)**2
        sw=min(SIDE,PH); t=min((PH-abs(a))/sw,1.0); g=1.0-(1.0-t)**2   # aristas laterales: caida corta y marcada
        rc=min(CORNER_R,PH); ec=-rr(a,b,0.0,0.0,PH,PH,rc)    # esquinas redondeadas en planta
        if ec<=0: return 0.0
        mk=min(ec/sw,1.0); mk=1.0-(1.0-mk)**2
        return f*g*mk
    if PROFILE==5:
        a=u-CELL*iu; b=v-CELL*iv
        for _ in range(CRISP%4): a,b=-b,a                     # gira para que las aristas queden a la izquierda y arriba
        if abs(a)>=PH or abs(b)>=PH: return 0.0
        dl=a+PH; dt=PH-b                                      # distancia a la arista izquierda y a la de arriba
        rc=min(CORNER_R,PH)
        if dl<rc and dt<rc: ec=rc-math.hypot(rc-dl,rc-dt)     # esquina redondeada entre las dos aristas
        else: ec=min(dl,dt)
        if ec<=0: return 0.0
        t=min(ec/min(RIM,PH),1.0); rim=1.0-(1.0-t)**2         # caida marcada junto a las aristas
        hu=sm(min((PH-a)/(2.0*PH)/SOFT,1.0))                  # sube hasta 0, tangente, en el lado derecho (sin arista)
        hv=sm(min((PH+b)/(2.0*PH)/SOFT,1.0))                  # idem en el lado de abajo
        return rim*hu*hv
    a=abs(u-CELL*iu); b=abs(v-CELL*iv)
    if NEXP is None: q=max(a,b)
    else:
        mx=max(a,b)
        q=mx*((a/mx)**NEXP+(b/mx)**NEXP)**(1.0/NEXP) if mx>1e-12 else 0.0
    e=PH-q                              # distancia hacia dentro desde el borde del hundido
    if e<=0: return 0.0
    return wall(e/W)
def zt(x,y,u,v):
    d=max(-sdf(x,y),0.0)
    ed=EDGE_R-math.sqrt(max(EDGE_R**2-(EDGE_R-d)**2,0.0)) if d<EDGE_R else 0.0
    env=env_at(d)
    dep=DEPTH*env*cell_depth(u,v) if env>0 else 0.0
    return PL_T-ed-dep

# --- nodos 1D dentro de una celda: caen sobre las lineas de quiebre (junta / pared / fondo) y el centro
def _sub(a,b,n):
    return [a+(b-a)*k/float(n) for k in range(1,n+1)]
def make_loc(det,stp):
    pos=[0.0]
    if FL>1e-6 and PROFILE!=7: pos+=_sub(0.0,FL,max(1,int(math.ceil(FL/stp))))
    if PROFILE==7:         # reparto uniforme (la superficie es suave) + nodos sobre el borde del hundido y su redondeo
        # DETAIL = resolucion de la malla: 2 = paso de siempre (~1.7 mm); 4 ~ 0.9 mm; 6 ~ 0.6 mm (la solucion tarda mas)
        ust=max(0.3,min(stp,2.0)*1.15*2.0/float(det)); n=max(3,int(math.ceil(PH/ust)))
        key_=[0.0,PH,max(PH-_WC,0.0),max(PH-0.6,0.0)]
        uni=[PH*k/float(n) for k in range(1,n)]
        pos=key_+[q for q in uni if min(abs(q-kk) for kk in key_)>0.3*ust]
    elif PROFILE==6:         # nodos densos junto a las aristas laterales y en el radio de los extremos
        rm=min(RIM,PH*0.9); sw=min(SIDE,PH); n=max(2,int(math.ceil((PH-rm)/stp)))
        pos=[0.0]+_sub(0.0,PH-rm,n)+[PH, PH-min(sw,rm*0.9)]
    elif PROFILE==5:         # nodos densos junto a las aristas + reparto uniforme en el resto
        rm=min(RIM,PH); n=max(det+1,int(math.ceil((PH-rm)/1.1)))
        pos=[0.0]+_sub(0.0,PH-rm,n)+[PH-rm*k/2.0 for k in range(2)]
    elif PROFILE==4:         # 2 nodos dentro del redondeo del borde + DETAIL en el cuenco
        rm=min(RIM,W*0.9)
        pos+=[(half-g2)-rm*k/2.0 for k in range(2)]
        pos+=[(half-g2)-rm-(W-rm)*k/float(det) for k in range(det)]
    elif PROFILE in (2,3):   # nodos mas densos junto a la arista viva
        pos+=[(half-g2)-W*(1.0-math.cos(0.5*math.pi*k/float(det))) for k in range(det)]
    else:
        pos+=_sub(FL,half-g2,det)
    if g2>1e-6: pos+=[half] if PROFILE==7 else _sub(half-g2,half,max(1,int(math.ceil(g2/stp))))
    loc=sorted(set([round(p,6) for p in pos]+[round(-p,6) for p in pos]))
    return [p for p in loc if p<half-1e-7]        # [-half, half): la siguiente celda aporta su -half
# rango de la reticula que cubre la placa (en coordenadas u,v giradas)
cs=[(-CX,-CY),(CX,-CY),(CX,CY),(-CX,CY)]
us=[ x*ca+y*sa for x,y in cs]; vs=[-x*sa+y*ca for x,y in cs]
# limite de densidad: si la malla saldria enorme (celda muy pequena, DETAIL alto o placa grande) se simplifica para que GH no se bloquee
NODE_BUDGET=max(int(_g('NODE_BUDGET',250000)),5000)
def est(loc):
    k=len(loc)/CELL
    return (max(us)-min(us))*k*(max(vs)-min(vs))*k
det=DETAIL; stp=STEP_MAX; loc=make_loc(det,stp)
while est(loc)>NODE_BUDGET and (det>1 or stp<half):
    if det>1: det-=1
    else: stp=min(stp*1.5,half)
    loc=make_loc(det,stp)
warn=""
if det!=DETAIL or stp!=STEP_MAX:
    warn=" | AVISO: malla simplificada (DETAIL %d, paso %.2f mm) por limite de %d nodos" % (det,stp,NODE_BUDGET)
if est(loc)>NODE_BUDGET*1.5:
    warn+=" | AVISO: malla muy densa (~%d nodos), puede tardar: sube CELL" % est(loc)
def axis(lo,hi):
    k0=int(math.floor(lo/CELL))-1; k1=int(math.ceil(hi/CELL))+1
    out=[]
    for k in range(k0,k1+1):
        for p in loc:
            q=k*CELL+p
            if lo-STEP_MAX-CELL*0.5<=q<=hi+STEP_MAX+CELL*0.5: out.append(q)
    return out
U=axis(min(us),max(us)); V=axis(min(vs),max(vs))
nu=len(U); nv=len(V)
def xy(i,j):
    u=U[i]; v=V[j]
    return CX+u*ca-v*sa, CY+u*sa+v*ca
inside={}
def ins(i,j):
    k=(i,j)
    if k not in inside:
        x,y=xy(i,j); inside[k]=sdf_in(x,y)<=0
    return inside[k]
vid={}; pts=[]; key={}
def _snap_arc(u,v):
    # PROFILE 7: en las esquinas redondeadas del hundido, los nodos de la linea exterior (a ras) van al arco de radio rc y los de la linea
    # interior (desplazada WALL hacia dentro) al arco de radio rc-WALL: la malla sigue el radio y la arista mantiene su ancho.
    iu=int(round(u/CELL)); iv=int(round(v/CELL))
    if PATTERN==0 and (iu+iv)%2!=0: return u,v
    a=u-CELL*iu; b=v-CELL*iv
    if abs(a)>PH+1e-6 or abs(b)>PH+1e-6: return u,v
    cc=PH-_RC
    if abs(a)<=cc or abs(b)<=cc: return u,v
    dx=abs(a)-cc; dy=abs(b)-cc; dd=math.hypot(dx,dy)
    outer=abs(abs(a)-PH)<1e-6 or abs(abs(b)-PH)<1e-6
    inner=abs(abs(a)-(PH-_WC))<1e-6 or abs(abs(b)-(PH-_WC))<1e-6
    if outer: r=_RC
    elif inner and _RC-_WC>0.05: r=_RC-_WC
    else: return u,v
    if dd<=r+1e-9: return u,v
    k=r/dd
    a2=math.copysign(cc+dx*k,a); b2=math.copysign(cc+dy*k,b)
    return CELL*iu+a2, CELL*iv+b2
def vertex(i,j):
    k=(i,j)
    if k in vid: return vid[k]
    if PROFILE==7:
        U[i],V[j]  # indices validos
        _u,_v=_snap_arc(U[i],V[j])
        x,y=CX+_u*ca-_v*sa, CY+_u*sa+_v*ca
    else:
        x,y=xy(i,j)
    x,y=snap(x,y)
    kk=(round(x,4),round(y,4))
    if kk in key: vid[k]=key[kk]; return key[kk]
    n=len(pts); pts.append((x,y,(_u if PROFILE==7 else U[i]),(_v if PROFILE==7 else V[j]))); key[kk]=n; vid[k]=n; return n
tops=[]
def add(ids):
    u=[]
    for t in ids:
        if t not in u: u.append(t)
    if len(u)==3: tops.append(u)
# celdas planas del damero completamente dentro de la placa: un abanico (pocos triangulos) en vez de la reticula fina
_idxU={round(q,5):k for k,q in enumerate(U)}; _idxV={round(q,5):k for k,q in enumerate(V)}
_flatblocks={}
def _flat_block(ib,jb):
    k=(ib,jb)
    if k in _flatblocks: return _flatblocks[k]
    ok=False
    if PATTERN==0 and PROFILE==7 and (ib+jb)%2!=0:
        i0=_idxU.get(round(ib*CELL-half,5)); i1=_idxU.get(round(ib*CELL+half,5))
        j0=_idxV.get(round(jb*CELL-half,5)); j1=_idxV.get(round(jb*CELL+half,5))
        if None not in (i0,i1,j0,j1) and all(ins(a,b) for a,b in ((i0,j0),(i1,j0),(i1,j1),(i0,j1))):
            # tambien deben estar dentro los 4 vecinos laterales mas cercanos al borde (evita fan sobre nodos recortados)
            ok=(i0,i1,j0,j1)
    _flatblocks[k]=ok
    return ok
for j in range(nv-1):
    for i in range(nu-1):
        c4=((i,j),(i+1,j),(i+1,j+1),(i,j+1))
        if not any(ins(a,b) for a,b in c4): continue
        _ib=int(round(((U[i]+U[i+1])*0.5)/CELL)); _jb=int(round(((V[j]+V[j+1])*0.5)/CELL))
        if _flat_block(_ib,_jb) and abs(((U[i]+U[i+1])*0.5)-_ib*CELL)<half and abs(((V[j]+V[j+1])*0.5)-_jb*CELL)<half: continue
        A,B,C,D=[vertex(a,b) for a,b in c4]
        uc=(U[i]+U[i+1])*0.5; vc=(V[j]+V[j+1])*0.5
        a=uc-CELL*round(uc/CELL); b=vc-CELL*round(vc/CELL)
        if a*b>0: add([A,B,C]); add([A,C,D])     # cuadrante I/III: arista de la esquina del hundido va como "/"
        else: add([A,B,D]); add([B,C,D])          # cuadrante II/IV: "\"
for (_ib,_jb),_bl in list(_flatblocks.items()):
    if not _bl: continue
    i0,i1,j0,j1=_bl
    per=[(i,j0) for i in range(i0,i1)]+[(i1,j) for j in range(j0,j1)]+[(i,j1) for i in range(i1,i0,-1)]+[(i0,j) for j in range(j1,j0,-1)]
    ids=[vertex(a,b) for a,b in per]
    uc=_ib*CELL; vc=_jb*CELL
    xc,yc=CX+uc*ca-vc*sa, CY+uc*sa+vc*ca
    cid=len(pts); pts.append((xc,yc,uc,vc))
    for k in range(len(ids)):
        a_=ids[k]; b_=ids[(k+1)%len(ids)]
        if a_!=b_: tops.append([cid,a_,b_])
m=rg.Mesh()
for (x,y,u,v) in pts: m.Vertices.Add(x,y,zt(x,y,u,v))
for f in tops: m.Faces.AddFace(f[0],f[1],f[2])
# borde de la reticula (sobre el contorno interior, zona plana) -> anillos del canto hacia fuera -> pared vertical -> tapa inferior en abanico (planta convexa)
edges=set()
for f in tops:
    for k in range(3): edges.add((f[k],f[(k+1)%3]))
bnd=[(a,b) for (a,b) in edges if (b,a) not in edges]
rings=[]                                   # (distancia al borde exterior, z)
if D_GRID>EDGE_R+1e-6: rings.append((EDGE_R,PL_T))
if EDGE_R>1e-6:
    for k in range(1,EDGE_SEG+1):
        ps=0.5*math.pi*k/EDGE_SEG
        rings.append((EDGE_R-EDGE_R*math.sin(ps), PL_T-EDGE_R+EDGE_R*math.cos(ps)))
rings.append((0.0,0.0))
rv={}
def ring_v(a,k):                           # vertice del anillo k que sale del vertice de borde a
    kk=(a,k)
    if kk not in rv:
        x,y=pts[a][0],pts[a][1]; nx,ny=grad(x,y); dd,z=rings[k]
        s=D_GRID-dd
        rv[kk]=m.Vertices.Add(x+nx*s,y+ny*s,z)
    return rv[kk]
for (a,b) in bnd:
    pa,pb=a,b
    for k in range(len(rings)):
        qa,qb=ring_v(a,k),ring_v(b,k)
        m.Faces.AddFace(pa,qa,qb,pb)
        pa,pb=qa,qb
ctr=m.Vertices.Add(CX,CY,0.0)
for (a,b) in bnd:
    m.Faces.AddFace(ctr,ring_v(b,len(rings)-1),ring_v(a,len(rings)-1))
m.Vertices.CombineIdentical(True,True); m.Compact()
m.Normals.ComputeNormals()
m.FaceNormals.ComputeFaceNormals(); m.Unweld(math.radians(_g('SMOOTH_ANGLE',75.0)), True)   # separa solo aristas de mas de 60 grados (canto inferior); el borde de los hundidos queda soldado y se ve igual en toda la zona de desvanecimiento
# normales analiticas en la cara superior (zona de la reticula): sombreado suave aunque la malla sea gruesa
if PROFILE==7 and _g('SMOOTH_NORMALS',1):
    _h=0.03
    def _uv(x,y):
        dx=x-CX; dy=y-CY
        return dx*ca+dy*sa, -dx*sa+dy*ca
    _V=m.Vertices
    for _i in range(_V.Count):
        _p=_V[_i]
        if _p.Z<PL_T*0.6: continue
        if -sdf(_p.X,_p.Y)<D_GRID-1e-3: continue
        _d=-sdf(_p.X,_p.Y)
        if env_at(_d)<=0.0: continue
        _u,_v=_uv(_p.X,_p.Y)
        _iu=round(_u/CELL); _iv=round(_v/CELL)
        _du=abs(_u-CELL*_iu); _dv=abs(_v-CELL*_iv)
        if _du>PH+_h and _dv>PH+_h: continue                   # junta plana
        if PATTERN==0 and (_iu+_iv)%2!=0 and _du<PH-_h and _dv<PH-_h: continue    # celda plana (el borde si se evalua)
        _z0=_p.Z
        if abs(_z0-PL_T)<1e-9:                                # a ras (junta, celda plana, contorno del hundido): normal vertical
            m.Normals[_i]=rg.Vector3f(0.0,0.0,1.0); continue
        _a1,_b1=_uv(_p.X+_h,_p.Y); _a2,_b2=_uv(_p.X-_h,_p.Y); _a3,_b3=_uv(_p.X,_p.Y+_h); _a4,_b4=_uv(_p.X,_p.Y-_h)
        _zx=(zt(_p.X+_h,_p.Y,_a1,_b1)-zt(_p.X-_h,_p.Y,_a2,_b2))/(2*_h); _zy=(zt(_p.X,_p.Y+_h,_a3,_b3)-zt(_p.X,_p.Y-_h,_a4,_b4))/(2*_h)
        _n=math.sqrt(_zx*_zx+_zy*_zy+1.0)
        m.Normals[_i]=rg.Vector3f(-_zx/_n,-_zy/_n,1.0/_n)
vol=rg.VolumeMassProperties.Compute(m)
if vol and vol.Volume<0: m.Flip(True,True,True); vol=rg.VolumeMassProperties.Compute(m)
plate = m
info = "caras %d | cerrada %s | valida %s | vol %.0f mm3 | %.2f s" % (m.Faces.Count, m.IsClosed, m.IsValid, abs(vol.Volume) if vol else -1, time.time()-_t0) + warn
print(info)

# --- Actualizar EN VIVO un objeto de Rhino (opcional) ---
# TARGET: GUID (texto) de la malla de Rhino a reemplazar. Se conserva su posicion (esquina minima del bbox) y sus atributos.
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
            _new.Translate(_bb.Min.X, _bb.Min.Y, _bb.Min.Z)
            _doc.Objects.Replace(_gid, _new)
            _doc.Views.Redraw()
            print("Actualizado %s: %d caras" % (_t, _new.Faces.Count))
    except Exception as _e:
        print("TARGET error: %s" % _e)
