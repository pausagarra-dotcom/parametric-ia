# GH Python 3: peça superior blanca del seient (closca prima amb finestra central oberta en Y pel darrere)
# amb OVALS EN RELLEU a portell, en columnes que segueixen el contorn i que s'esvaeixen abans de les vores.
# Ref: textures/04_seient_colissos/referencia/seient_planta.jpg i seient_explosionat.jpg
# ENTRADES (nom = variable) venen de sliders; si en falta una es fa servir el valor per defecte. Sortida: seient (Mesh). Unitats mm.
# Eixos: X al llarg (darrere a X=0, morro a X=L), Y de costat, Z amunt. d = distància des de la punta del morro.
import math, time, Rhino, Rhino.Geometry as rg
_t0 = time.time()
def _g(n, d):
    v = globals().get(n)
    return d if v is None else float(v)

# --- Contorn en planta (ajustat a la foto, error rms 0,4 mm) ---
L          = max(_g('L', 273.5), 100.0)      # llargada total
W          = max(_g('W', 136.0), 40.0)       # amplada màxima
NOSE_W     = max(_g('NOSE_W', 33.4), 5.0)    # amplada del morro
NOSE_TAPER = _g('NOSE_TAPER', 0.069)         # quant s'eixampla el morro per cada mm de llargada
WIDE_START = _g('WIDE_START', 98.0)          # d on comença a obrir-se cap a la part ampla
WIDE_POS   = _g('WIDE_POS', 226.5)           # d de l'amplada màxima
WIDE_P     = max(_g('WIDE_P', 1.78), 0.2)    # forma de l'obertura (>1 obre més tard)
REAR_DROP  = _g('REAR_DROP', 25.4)           # quant s'estreny de WIDE_POS fins al darrere
REAR_R     = max(_g('REAR_R', 10.5), 0.5)    # arrodoniment del final del darrere
NOSE_R     = max(_g('NOSE_R', 5.1), 0.5)     # arrodoniment de la punta del morro
# --- Finestra central ---
SLOT_START = _g('SLOT_START', 75.0)          # d on comença la finestra (extrem rodó)
SLOT_W1    = max(_g('SLOT_W1', 16.4), 2.0)   # amplada de la finestra al davant
SLOT_W2    = max(_g('SLOT_W2', 24.0), 2.0)   # amplada de la finestra on comença la Y
SLOT_SPLIT = _g('SLOT_SPLIT', 238.0)         # d on la finestra s'obre en Y
FLARE      = _g('FLARE', 0.0815)             # obertura de la Y: s += FLARE*(d-SLOT_SPLIT)^1.7
TIP_R      = max(_g('TIP_R', 2.5), 0.0)      # arrodoniment de les puntes de les ales (darrere)
# --- Volum ---
THICK      = max(_g('THICK', 2.5), 0.3)      # gruix de la closca (cantell arrodonit de radi THICK/2)
DIP        = _g('DIP', 3.0)                  # enfonsament del centre del seient (perfil lateral)
KICK       = _g('KICK', 4.0)                 # pujada del darrere
NOSE_DROP  = _g('NOSE_DROP', 2.0)            # caiguda de la punta del morro
CROWN_NOSE = _g('CROWN_NOSE', 5.0)           # caiguda lateral (bombat) al morro
CROWN_REAR = _g('CROWN_REAR', 14.0)          # caiguda lateral (bombat) a la part ampla
CROWN_P    = max(_g('CROWN_P', 2.4), 1.0)    # forma del bombat (més alt = més pla al centre)
# --- Ovals en relleu ---
CW         = max(_g('CW', 4.9), 1.0)         # separació entre columnes
CL         = max(_g('CL', 17.6), 2.0)        # pas al llarg d'una columna (les columnes veïnes van desplaçades CL/2)
OVAL_W     = max(_g('OVAL_W', 3.6), 0.5)     # amplada de l'oval (estret, com a la foto de detall)
OVAL_L     = max(_g('OVAL_L', 17.5), 0.5)    # llargada de l'oval
OVAL_Q     = max(_g('OVAL_Q', 2.2), 1.0)     # forma de les puntes (2 = el·lipse, >2 més rom, <2 més punxegut)
HEIGHT     = _g('HEIGHT', 0.8)               # alçada del relleu (negatiu = enfonsat); 0,7-1,4 mm mesurat a la silueta de la foto
FOLLOW_START = min(max(_g('FOLLOW_START', 0.65), 0.0), 0.99)  # zona central de columnes verticals: fins a |y| = FOLLOW_START * W/2
FOLLOW_OUT = _g('FOLLOW_OUT', 1.0)           # fora d'aquesta zona les columnes s'inclinen seguint la vora (0 = rectes, 1 = paral·leles a la vora)
FOLLOW_MODE = int(round(_g('FOLLOW_MODE', 0)))  # 0 = zona central vertical (actual); 1 = versió anterior (columnes que segueixen el contorn comprimint-se, F = 0,8·(|y|/w)²)
COL_SHIFT  = _g('COL_SHIFT', 0.0)            # desplaça les columnes de costat
ROW_SHIFT  = _g('ROW_SHIFT', 0.0)            # desplaça els ovals al llarg
# --- Esvaïment ---
FADE_EDGE_GAP   = _g('FADE_EDGE_GAP', 0.5)   # franja llisa a la vora exterior
FADE_EDGE       = max(_g('FADE_EDGE', 4.0), 0.01)   # longitud de l'esvaïment a la vora exterior
FADE_SLOT_GAP   = _g('FADE_SLOT_GAP', 0.8)   # franja llisa a la vora de la finestra
FADE_SLOT       = max(_g('FADE_SLOT', 3.0), 0.01)
FADE_NOSE_START = _g('FADE_NOSE_START', 5.0)   # d on els ovals ja han desaparegut del tot (prop de la punta del morro)
FADE_NOSE       = max(_g('FADE_NOSE', 85.0), 0.01)  # longitud de l'esvaïment: ovals sencers a d = FADE_NOSE_START+FADE_NOSE (90 mm, just davant la finestra)
DETAIL     = min(max(_g('DETAIL', 0.7), 0.15), 5.0)  # mida de la malla (mm); més petit = més fi (0,7 ≈ 3 s, 0,5 ≈ 9 s)
WALL_N     = 8                                # segments del cantell arrodonit

def sstep(t):
    t = 0.0 if t < 0 else (1.0 if t > 1 else t); return t*t*(3-2*t)
def sstep2(t):                                # C2: evita bandes a la llum
    t = 0.0 if t < 0 else (1.0 if t > 1 else t); return t*t*t*(t*(t*6-15)+10)
def trans(d):
    return sstep((d-WIDE_START)/max(WIDE_POS-WIDE_START, 1e-6))**WIDE_P
def halfw_body(d):                             # mitja amplada sense els arrodoniments dels extrems (per al bombat i les columnes)
    n = NOSE_W/2 + NOSE_TAPER*d
    wb = n + (W/2 - n)*trans(d)
    r = min(max((d-WIDE_POS)/max(L-WIDE_POS, 1e-6), 0.0), 1.0)
    return max(wb - REAR_DROP*r*r, 1e-3)
def halfw(d):                                  # mitja amplada del contorn
    wb = halfw_body(d)
    cap = 1.0
    if d > L-REAR_R: cap = math.sqrt(max(1-((d-(L-REAR_R))/REAR_R)**2, 0.0))
    if d < NOSE_R:   cap = math.sqrt(max(1-((NOSE_R-d)/NOSE_R)**2, 0.0))
    return max(wb, 0.0)*cap
_SR = SLOT_W1/2; _SC = SLOT_START + _SR       # centre de l'extrem rodó de la finestra
def slothw(d):                                 # mitja amplada de la finestra (-1 = no n'hi ha)
    if d < SLOT_START: return -1.0
    if d < _SC: return math.sqrt(max(_SR*_SR-(_SC-d)**2, 0.0))
    lin = _SR + (SLOT_W2/2-_SR)*min(max((d-_SC)/max(SLOT_SPLIT-_SC, 1e-6), 0.0), 1.0)
    return lin + FLARE*max(d-SLOT_SPLIT, 0.0)**1.7
_ROW = {}
def row(d):                                    # valors que només depenen de d (la malla té moltes files amb la mateixa d)
    k = round(d, 6); r = _ROW.get(k)
    if r is None:
        w = max(halfw(d), 1e-3); dd = 0.5
        wp = (halfw(min(d+dd, L))-halfw(max(d-dd, 0.0)))/(2*dd)
        sw = slothw(d)
        sp = 0.0
        if d >= _SC:
            sp = (slothw(d+dd)-slothw(max(d-dd, _SC)))/(2*dd); sp = max(min(sp, 50.0), -50.0)
        zl = -DIP*math.sin(math.pi*d/L)**2 + KICK*min(max((d-(L-40))/40, 0.0), 1.0)**2 - NOSE_DROP*max((15-d)/15, 0.0)**2
        cr = CROWN_NOSE + (CROWN_REAR-CROWN_NOSE)*trans(d)
        nose = sstep2((d-FADE_NOSE_START)/FADE_NOSE)
        r = (w, 1.0/math.sqrt(1+wp*wp), sw, 1.0/math.sqrt(1+sp*sp), zl, cr, nose, halfw_body(d))
        _ROW[k] = r
    return r
def base(d, y):                                # superfície de dalt sense textura
    wb, zl, cr = row(d)[7], row(d)[4], row(d)[5]
    return zl - cr*min(abs(y)/wb, 1.2)**CROWN_P
def texture(d, y):                             # alçada dels ovals (0..HEIGHT) amb l'esvaïment
    w, cw_, sw, cs_, _, _, nose, wb = row(d)
    if nose <= 0.0: return 0.0
    ay = abs(y)
    de = (w-ay)*cw_                            # distància aproximada a la vora exterior
    if d < _SC:
        ds = math.hypot(ay, d-_SC) - _SR        # extrem rodó de la finestra
        if sw > 0: ds = min(ds, ay-sw)
    else:
        ds = (ay-sw)*cs_
    env = nose*sstep2((de-FADE_EDGE_GAP)/FADE_EDGE)*sstep2((ds-FADE_SLOT_GAP)/FADE_SLOT)
    if env <= 0.0: return 0.0
    # columnes verticals al centre; a la vora de la part ampla es desplacen amb l'amplada (s'inclinen paral·leles a la vora, sense comprimir-se)
    if FOLLOW_MODE == 1:                       # versió anterior (per comparar)
        u = y*(W/2/wb)**(0.8*min(ay/wb, 1.0)**2) - COL_SHIFT
    else:
        t = sstep((ay/(W/2) - FOLLOW_START)/(1.0 - FOLLOW_START))
        u = (ay + FOLLOW_OUT*t*(W/2 - wb))*(1 if y >= 0 else -1) - COL_SHIFT
    v = d - ROW_SHIFT
    A = OVAL_W/2; B = OVAL_L/2
    i0 = int(round(u/CW)); h = 0.0
    for i in (i0-1, i0, i0+1):                 # suma de les tres columnes veïnes, cadascuna amb el seu oval més proper
        ph = CL/2 if (i % 2) else 0.0
        j = round((v-ph)/CL); dv = v-(j*CL+ph); du = u-i*CW
        r2 = (du/A)**2 + (abs(dv)/B)**OVAL_Q
        if r2 < 1.0: h += (1.0-r2)**3          # perfil C2 a la vora de l'oval
    return HEIGHT*h*env

warn = ""
tol = 0.001
# --- 1. Contorn tancat de la peça (vora exterior + finestra), puntes arrodonides ---
def solve_tip():                               # d on la finestra arriba a la vora exterior
    a, b = max(SLOT_SPLIT, _SC), L
    if slothw(b) < halfw(b): return None
    for _ in range(60):
        m = (a+b)/2
        if slothw(m) < halfw(m): a = m
        else: b = m
    return (a+b)/2
dtip = solve_tip()
if dtip is None:
    dtip = L; warn += " | la finestra no arriba al darrere"
def ds_list(a, b, step):
    n = max(int(abs(b-a)/step), 2); return [a+(b-a)*k/n for k in range(n+1)]
# punts de la vora exterior: de la punta dreta (darrere) al morro i fins a la punta esquerra
dd_out = ds_list(dtip, 12.0, 2.0) + ds_list(12.0, 0.0, 0.25)[1:]
right = [rg.Point3d(L-d, halfw(d), 0) for d in dd_out]
left = [rg.Point3d(p.X, -p.Y, 0) for p in reversed(right[:-1])]
outer = rg.Curve.CreateInterpolatedCurve(right+left, 3)
# finestra: de la punta esquerra, rodejant l'extrem del davant, fins a la punta dreta
dd_sl = ds_list(dtip, _SC+0.5, 2.0)
sl_left = [rg.Point3d(L-d, -slothw(d), 0) for d in dd_sl]
cap = []
for k in range(1, 24):                         # semicercle de l'extrem del davant (centre d=_SC, y=0)
    phi = -math.pi/2 + math.pi*k/24
    cap.append(rg.Point3d(L-(_SC-_SR*math.cos(phi)), _SR*math.sin(phi), 0))
sl_right = [rg.Point3d(p.X, -p.Y, 0) for p in reversed(sl_left)]
slot = rg.Curve.CreateInterpolatedCurve(sl_left+cap+sl_right, 3)
joined = rg.Curve.JoinCurves([outer, slot], 0.01)
bound = joined[0] if joined else None
if bound is not None and not bound.IsClosed:
    bound = None; warn += " | contorn obert"
if bound is not None and TIP_R > 0:
    f = rg.Curve.CreateFilletCornersCurve(bound, TIP_R, tol, math.radians(5))
    if f is not None: bound = f
    else: warn += " | no s'han pogut arrodonir les puntes"
# el cantell arrodonit sobresurt THICK/2: es desplaça el contorn cap a dins
if bound is not None:
    best = None
    for sgn in (1, -1):
        offs = bound.Offset(rg.Plane.WorldXY, sgn*THICK/2, tol, rg.CurveOffsetCornerStyle.Sharp)
        if offs and len(offs) == 1 and offs[0].IsClosed:
            amp = rg.AreaMassProperties.Compute(offs[0])
            if amp and (best is None or amp.Area < best[0]): best = (amp.Area, offs[0])
    if best: bound = best[1]
    else: warn += " | no s'ha pogut desplaçar el contorn"

seient = None
if bound is not None:
    # --- 2. Malla plana uniforme dins del contorn ---
    brep = rg.Brep.CreatePlanarBreps(bound, tol)[0]
    mp = rg.MeshingParameters()
    mp.MaximumEdgeLength = DETAIL; mp.MinimumEdgeLength = 1e-4
    mp.GridAspectRatio = 1.0; mp.SimplePlanes = False; mp.RefineGrid = True; mp.JaggedSeams = False
    pm = rg.Mesh()
    for q in rg.Mesh.CreateFromBrep(brep, mp): pm.Append(q)
    pm.Vertices.CombineIdentical(True, True); pm.Compact()
    pm.FaceNormals.ComputeFaceNormals()
    if pm.FaceNormals[0].Z < 0: pm.Flip(True, True, True)
    N = pm.Vertices.Count
    fa = list(pm.Vertices.ToFloatArray())      # x0,y0,z0,x1,... (una sola crida a Rhino: molt més ràpid)
    PX = fa[0::3]; PY = fa[1::3]
    # --- 3. Vora: llaç ordenat de vèrtexs ---
    key = {}
    for i in range(N): key[(round(PX[i], 3), round(PY[i], 3))] = i
    nk = pm.GetNakedEdges()
    loop = max(nk, key=lambda pl: pl.Count) if nk else None
    if nk and len(nk) > 1: warn += " | %d vores obertes" % len(nk)
    lp = [(p.X, p.Y) for p in loop]
    bidx = [key.get((round(x, 3), round(y, 3)), -1) for x, y in lp[:-1]]
    if -1 in bidx: warn += " | vora sense correspondència"
    area2 = sum(lp[k][0]*lp[k+1][1]-lp[k+1][0]*lp[k][1] for k in range(len(lp)-1))
    if area2 < 0: bidx.reverse()               # sentit antihorari: la normal cap enfora és (ty,-tx)
    # --- 4. Vèrtexs de dalt (amb ovals) i de sota (gruix al llarg de la normal) ---
    TX = [0.0]*N; TY = [0.0]*N; TZ = [0.0]*N; BX = [0.0]*N; BY = [0.0]*N; BZ = [0.0]*N
    e = 0.05; sq = math.sqrt
    for i in range(N):
        X = PX[i]; Y = PY[i]; d = L-X
        z = base(d, Y)
        gx = (base(d-e, Y)-base(d+e, Y))/(2*e)  # dz/dX (X = L-d)
        gy = (base(d, Y+e)-base(d, Y-e))/(2*e)
        k = 1.0/sq(gx*gx+gy*gy+1.0); nx = -gx*k; ny = -gy*k; nz = k
        t = texture(d, Y)
        TX[i] = X+nx*t; TY[i] = Y+ny*t; TZ[i] = z+nz*t
        BX[i] = X-nx*THICK; BY[i] = Y-ny*THICK; BZ[i] = z-nz*THICK
    m = pm.DuplicateMesh()                     # cara de dalt: mateixa topologia, vèrtexs moguts
    for i in range(N): m.Vertices.SetVertex(i, TX[i], TY[i], TZ[i])
    bm = pm.DuplicateMesh()                    # cara de sota
    for i in range(N): bm.Vertices.SetVertex(i, BX[i], BY[i], BZ[i])
    bm.Flip(True, True, True)
    m.Append(bm)                               # vèrtexs de sota: N+i
    # --- 5. Cantell arrodonit (mitja canya de radi THICK/2) ---
    nb = len(bidx)
    rings = [list(bidx)]
    nxt = 2*N
    wall_pts = []
    for k in range(1, WALL_N):
        th = math.pi*k/WALL_N; ct = math.cos(th); st = math.sin(th); ring = []
        for a in range(nb):
            i = bidx[a]; ip = bidx[(a-1) % nb]; inx = bidx[(a+1) % nb]
            tx = PX[inx]-PX[ip]; ty = PY[inx]-PY[ip]; ln = math.hypot(tx, ty) or 1.0
            mx, my, mz = ty/ln, -tx/ln, 0.0
            cx = (TX[i]+BX[i])/2; cy = (TY[i]+BY[i])/2; cz = (TZ[i]+BZ[i])/2
            ex = TX[i]-cx; ey = TY[i]-cy; ez = TZ[i]-cz; r = sq(ex*ex+ey*ey+ez*ez) or 1e-9
            ex /= r; ey /= r; ez /= r
            dp = mx*ex+my*ey+mz*ez; mx -= ex*dp; my -= ey*dp; mz -= ez*dp
            ml = sq(mx*mx+my*my+mz*mz) or 1.0; mx /= ml; my /= ml; mz /= ml
            wall_pts.append((cx+r*(ct*ex+st*mx), cy+r*(ct*ey+st*my), cz+r*(ct*ez+st*mz)))
            ring.append(nxt); nxt += 1
        rings.append(ring)
    rings.append([N+i for i in bidx])
    for p in wall_pts: m.Vertices.Add(p[0], p[1], p[2])
    wf = []
    for k in range(WALL_N):
        r0 = rings[k]; r1 = rings[k+1]
        for a in range(nb):
            b = (a+1) % nb
            wf.append(rg.MeshFace(r0[a], r1[a], r1[b], r0[b]))   # normal cap enfora
    m.Faces.AddFaces(wf)
    m.Normals.ComputeNormals(); m.Compact()
    vol = rg.VolumeMassProperties.Compute(m) if m.IsClosed else None
    if vol and vol.Volume < 0:
        m.Flip(True, True, True); vol = rg.VolumeMassProperties.Compute(m)
    seient = m
    bb = m.GetBoundingBox(True)
    info = "caras %d | cerrada %s | valida %s | vol %.0f mm3 | %.0fx%.0fx%.0f mm | %.2f s" % (
        m.Faces.Count, m.IsClosed, m.IsValid, abs(vol.Volume) if vol else -1, bb.Max.X-bb.Min.X, bb.Max.Y-bb.Min.Y, bb.Max.Z-bb.Min.Z, time.time()-_t0) + warn
else:
    info = "ERROR: no s'ha pogut fer el contorn" + warn
print(info)

# --- Actualitzar EN VIU un objecte de Rhino (opcional) ---
# TARGET: GUID (text) de la malla de Rhino a reemplaçar. Es conserva la seva posició (cantonada mínima del bbox) i els atributs.
_t = globals().get('TARGET')
if _t and seient is not None:
    import System
    _doc = Rhino.RhinoDoc.ActiveDoc
    try:
        _gid = System.Guid(str(_t).strip())
        _obj = _doc.Objects.FindId(_gid)
        if _obj is None:
            print("TARGET no trobat: %s" % _t)
        else:
            _bb = _obj.Geometry.GetBoundingBox(True); _mb = seient.GetBoundingBox(True)
            _new = seient.DuplicateMesh()
            _new.Translate(_bb.Min.X-_mb.Min.X, _bb.Min.Y-_mb.Min.Y, _bb.Min.Z-_mb.Min.Z)
            _doc.Objects.Replace(_gid, _new)
            _doc.Views.Redraw()
            print("Actualitzat %s: %d cares" % (_t, _new.Faces.Count))
    except Exception as _e:
        print("TARGET error: %s" % _e)
