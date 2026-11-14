import re, math, numpy as np, cv2
src=open('sp2_phone.py',encoding='utf-8').read().split('nx=int')[0]
src=src.replace('import math, Rhino, Rhino.Geometry as rg, scriptcontext as sc','import math')
exec(src)
S=0.25; xs=np.arange(0,PH_W,S); ys=np.arange(0,PH_H,S)
Z=np.array([[zt(x,y) if sdf(x,y)<=0 else np.nan for x in xs] for y in ys])
valid=~np.isnan(Z); Zf=np.where(valid,Z,PH_T)
gy,gx=np.gradient(Zf,S)
sh=np.clip(0.75+0.9*(-gx*0.6+gy*0.8),0.2,1.0)
img=np.dstack([sh*0.30,sh*0.70,sh*0.98]); img[~valid]=0.93
img=(img*255).astype(np.uint8)[::-1]
cv2.imwrite('preview_phone.png',cv2.resize(img,None,fx=3,fy=3,interpolation=cv2.INTER_NEAREST))
# perfil a lo largo de Y por el centro del texturado
col=[zt(TX_CX,y) for y in np.arange(0,PH_H,0.1)]
print("min z cresta/valle sobre texturado, profundidad max:",round(PH_T-min(zt(x,TX_CY) for x in np.arange(30,45,0.05)),3))
for y in (58,70,85,100,110,113,116): print(y,round(PH_T-min(zt(x,y) for x in np.arange(30,45,0.05)),3))
