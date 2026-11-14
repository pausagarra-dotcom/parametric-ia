# Fórmula del patró (tauler de quadrats enfonsats)

Tot en mm. Es llegeix igual al llenç de Grasshopper (`gh/superficie_organica_quadres.gh`: un node «Evaluate» per línia, amb el text de la fórmula en un panell groc al costat) i al script de la placa (`gh/placa_quadres.gh`, `spikes/sp2/gh_placa.py`, funció `pocket7`).

> **Com va tan ràpid:** tots els quadres enfonsats són idèntics en coordenades locals. El script REJILLA només calcula, per a cada punt de la malla, la seva coordenada local `(a0, b0)` i si la cel·la és enfonsada (`par = 0`). La fórmula de sota s'avalua **una sola vegada per cada `(a0, b0)` diferent** (uns 60 punts), i el script MALLA reparteix el resultat per totes les cel·les. El desvaïment cap a la vora es calcula a part per x i per y (`env = min(envx, envy)`).

## Coordenades de la cel·la
```
x, y   = posició del punt (mm; a la superfície orgànica, longitud d'arc des de la cantonada)
iu     = round((x - OFF_X) / CELL)         iv = round((y - OFF_Y) / CELL)       cel·la del punt
a0     = (x - OFF_X) - CELL*iu             b0 = (y - OFF_Y) - CELL*iv           coordenades locals
(a, b) = (a0, b0) girat ROT * 90°          ROT tria les cantonades marcades
par    = |(iu + iv) mod 2|                 només s'enfonsen les cel·les amb par = 0 (tauler)
PH     = (CELL - GAP) / 2                  semicostat del quadrat enfonsat
s = a/PH     t = b/PH     p = (s + t)/2    (s, t, p limitats a [-1, 1])
```

## Forma
```
fons      f   = (1 - s²)(1 - t²)(1 + TILT·p)                 polinomi, al ras en tot el contorn
llavi     lip = LIP · p²                                      aresta marcada: forta a dalt-dreta i baix-esquerra
contorn   ec  = RC - sqrt(max(|a|-(PH-RC),0)² + max(|b|-(PH-RC),0)²) - min(max(|a|-(PH-RC),|b|-(PH-RC)),0)
                (distància interior al quadrat arrodonit de radi RC = CORNER_R)
rampa     M   = 1 - (1 - min(max(ec,0)/WALL, 1))²             aresta nítida d'ample WALL
raw       = (f + lip) · M      si par = 0 i ec > 0; si no, 0
BMAX      = max_p [ (1-p²)²(1+TILT·p) + LIP·p² ]              fa que la profunditat màxima sigui exactament DEPTH
```

## Vora de la superfície (només a la superfície orgànica)
```
d   = min(x, Lx-x, y, Ly-y)                                   distància a la vora (mm)
env = smoothstep((d - FADE_GAP) / FADE_LEN)                   el patró s'esvaeix cap a la vora
```

## Resultat
```
z = -DEPTH · raw / BMAX · env          desplaçament al llarg de la normal de la superfície (negatiu = enfonsat)
```

## Sliders
| Slider | Què fa | Per defecte |
|---|---|---|
| `CELL` | costat de la cel·la (pas del tauler) | 8 mm |
| `GAP` | marge pla al voltant de cada quadrat enfonsat | 0,2 mm |
| `CORNER_R` | radi de les cantonades del quadrat | 1,2 mm |
| `WALL` | ample de l'aresta (0,2 = tall net) | 0,2 mm |
| `DEPTH` | profunditat màxima (negatiu = relleu) | 0,4 mm |
| `TILT` | inclinació del fons cap a la cantonada marcada | 0,8 |
| `LIP` | força de l'aresta marcada | 0,3 |
| `ROT` | gira 90° quines cantonades són les marcades (0–3) | 0 |
| `OFF_X`, `OFF_Y` | desplaça el tauler | 0 |
| `FADE_GAP`, `FADE_LEN` | on i com s'esvaeix el patró cap a la vora (superfície orgànica) | 10 / 30 mm |
| `STEP` | densitat de la malla (menys = més fina i més lenta) | 2 mm |

## Temps de càlcul (superfície de 216×205 mm, 34.580 punts)
Reconstrucció completa ≈ 3 s (abans 18 s). Moure `DEPTH`, `TILT`, `LIP` o `ROT` ≈ 1,7 s; `WALL`, `CORNER_R`, `CELL`, `STEP`, `OFF_X/Y` o `FADE_*` ≈ 3 s.
