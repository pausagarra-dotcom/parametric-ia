# SP-2 fiel: periodicidad de una textura por autocorrelacion (OpenCV/numpy). Uso: python -I sp2_fiel.py imagen x0 y0 x1 y1
import sys, json, cv2, numpy as np
p=sys.argv[1]; x0,y0,x1,y1=map(int,sys.argv[2:6])
g=cv2.imread(p,0).astype(np.float32)[y0:y1,x0:x1]
g=cv2.resize(g,None,fx=4,fy=4,interpolation=cv2.INTER_CUBIC)
g=g-cv2.GaussianBlur(g,(0,0),40)          # quita iluminacion lenta
w=np.outer(np.hanning(g.shape[0]),np.hanning(g.shape[1])); g=g*w
F=np.fft.fft2(g,s=(2*g.shape[0],2*g.shape[1])); ac=np.fft.fftshift(np.fft.ifft2(np.abs(F)**2).real)
ac/=ac.max(); cy,cx=np.array(ac.shape)//2
pk=[]
m=cv2.dilate(ac,np.ones((15,15)))
ys,xs=np.where((ac==m)&(ac>0.15))
for y,x in zip(ys,xs):
    dy,dx=(y-cy)/4.,(x-cx)/4.   # en px de la imagen original
    if (dx,dy)!=(0,0): pk.append((round(float(np.hypot(dx,dy)),2),round(float(dx),2),round(float(dy),2),round(float(ac[y,x]),2)))
pk.sort(); print(json.dumps(pk[:16]))
