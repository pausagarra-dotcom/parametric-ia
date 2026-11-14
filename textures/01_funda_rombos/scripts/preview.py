import numpy as np, cv2
W,H=5.52,9.11; D=0.5; S=0.1
x=np.arange(0,40,S); y=np.arange(0,40,S); X,Y=np.meshgrid(x,y)
z=np.zeros_like(X)
for ox,oy in ((0,0),(.5,.5)):
    u=X/W-ox; v=Y/H-oy; u-=np.round(u); v-=np.round(v)
    z=np.maximum(z,D*np.clip(1-2*(abs(u)+abs(v)),0,None))
gy,gx=np.gradient(z,S)
sh=np.clip(0.62+0.38*(-gx*0.5+gy*0.8)/(D/(W/2)),0,1)
img=(np.dstack([sh*0.55,sh*0.75,sh*0.98])*255).astype(np.uint8)
cv2.imwrite("preview_flat.png",cv2.resize(img[::-1],None,fx=2,fy=2)); cv2.imwrite("preview_height.png",cv2.resize((z[::-1]/D*255).astype(np.uint8),None,fx=2,fy=2))
