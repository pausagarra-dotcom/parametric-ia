# SP-7 · Mapeig UV amb mínima distorsió (informe)

Data: 2026-11-15. Llegenda: [H] mesurat en aquesta sessió · [S] suposició · [?] a verificar.
Codi:
- `sp7_unwrap.py` (desplegament i mesura; numpy, fora de Rhino);
- `sp7_quadricula.py` (quadrícula de prova);
- les mallas de partida (`malla_A*.json`) es generen a Rhino.

Resultats: `sp7_results.json` (desplegament de tota la superfície) i `sp7_regional.json` (només la zona).

## Què s'ha provat
- **Superfícies:** les mateixes superfícies orgàniques del SP-1, reconstruïdes amb el seu codi. Són NURBS de 200 × 200 mm amb relleu d'amplitud A = 10, 25 i 40 mm, mostrejades en una malla de 81 × 81 punts (uns 2,5 mm entre punts).
- **Mètodes:**
  - **uv_arc:** el millor del SP-1 (longitud d'arc al llarg de les isocorbes centrals). Serveix de referència.
  - **LSCM:** desplegament conforme, que conserva els angles. S'escala perquè l'àrea total es conservi.
  - **ARAP** («tan rígid com sigui possible»): reparteix l'error entre àrea i angle. Comença des del resultat de LSCM i fa 60–80 iteracions.
- **Distorsió per triangle:**
  - àrea |s1·s2 − 1|, que és la mateixa mesura que al SP-1;
  - longitud màx(|s1 − 1|, |s2 − 1|);
  - angle s1/s2 − 1.
  
  Aquí s1 i s2 són els estiraments principals entre el pla del patró (mm) i la superfície. Es mesuren dins de finestres quadrades de 40, 60, 80 i 100 mm centrades a la superfície.
- **Validació:** uv_arc dona **16,15 %** d'àrea a A25 amb una finestra de 100 mm. El SP-1 va mesurar 16,2 % amb un altre mètode de mesura. ✔

## Resultat 1: si es desplega tota la superfície de 200 mm de cop [H]
LSCM i ARAP reparteixen l'error per tota la superfície, i això fa que **el centre quedi comprimit de manera uniforme**: ARAP dona un 7 % a A25 fins i tot amb una finestra de 40 mm. Desplegar més superfície de la necessària no ajuda.

## Resultat 2: si es desplega només la zona a texturar (com farà l'app) [H]
Distorsió d'àrea màxima:

| Superfície | Finestra | uv_arc | **ARAP** | LSCM |
|---|---|---|---|---|
| A10 | 100 mm | 3,1 % | **1,0 %** | 2,2 % |
| A25 | 40 mm | 6,2 % | **0,9 %** | (fallada del solver) |
| A25 | 60 mm | 11,1 % | **2,1 %** | 3,4 % |
| A25 | 80 mm | 14,4 % | **4,1 %** | (fallada del solver) |
| A25 | 100 mm | **16,2 %** | **5,0 %** | (fallada del solver) |
| A40 | 60 mm | 21,0 % | **5,0 %** | 7,4 % |
| A40 | 100 mm | **32,1 %** | **12,2 %** | 25,1 % |

- La longitud i l'angle es comporten igual. A A25 / 100 mm, ARAP dona 5,1 % de longitud i 5,4 % d'angle, mentre que uv_arc dona 12,9 % i 11,0 %.
- Cap mètode ha produït triangles girats.
- **LSCM no és fiable amb aquest solver.** En diversos casos no convergeix (surten distorsions del 99 %). Només serveix com a punt de partida, i ARAP el corregeix igualment.

Imatges:
- `quadricula_A25_W100_persp.png` i `_planta.png`: quadrícula de 10 mm sobre la superfície, comparant uv_arc i ARAP. Amb uv_arc els quadrats canvien de mida d'un costat a l'altre; amb ARAP són gairebé iguals.
- `mapa_regional_A25_W100_*.png`: mapa de distorsió d'àrea de cada mètode.
- `mapa_area_A*_*.png`: el mateix per al desplegament de tota la superfície.

## Veredicte
Criteri del pla: *menys distorsió que uv_arc a A25 amb 100 mm (16,2 %).* **Complert: ARAP regional dona 5,0 %, tres vegades menys.**
- A la superfície més corbada (A40), ARAP baixa la distorsió de 32 % a 12 %, **per sota del límit del 15 %**. Al SP-1 això només s'aconseguia amb finestres de 40 mm o menys.

## Què vol dir per a l'app
1. **Mètode per defecte per a superfícies orgàniques: ARAP aplicat només a la zona a texturar.**
   - Per a plans i cilindres no cal: el desplegament exacte ja dona un 0 % (SP-1 i SP-6).
   - L'app ha de reconèixer el tipus de cara (el SP-5 ja ho fa) i triar el mètode.
2. **Mapa de distorsió i quadrícula de prova:** són les dues eines visuals que l'app ha de mostrar abans d'aplicar una textura. Quan la distorsió és alta, **s'informa i no es bloqueja** (C3).
3. **Corba guia (orientació del patró):**
   - [S] No canvia la distorsió. Només fixa la rotació del patró sobre el pla desplegat, perquè l'ARAP deixa la rotació lliure.
   - Que el patró *segueixi* una corba que gira és una ampliació per més endavant (camp de direccions). No s'ha provat.
4. **Velocitat:** aquí s'ha fet amb numpy pur i un solver iteratiu fet a mà, i triga de segons a uns pocs minuts per cas. [S] Amb un solver de matrius disperses (scipy o libigl) baixarà a menys d'un segon. Es veurà al SP-8.

## Límits
- [S] Una sola família de superfícies (la senoidal del SP-1), sense retalls.
- Finestres quadrades. Una zona real té un contorn qualsevol; el mètode és el mateix, però no s'ha provat.
- Les distorsions són per triangle d'una malla de 2,5 mm. Els pics molt locals de la superfície real poden ser una mica més alts.
- La quadrícula de prova s'ha dibuixat amb OpenCV, perquè Rhino no pintava bé els colors d'una malla tan densa.
