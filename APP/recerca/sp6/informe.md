# SP-6 · Sortida cap a SolidWorks (informe)

Data: 2026-11-14. Llegenda: [H] mesurat en aquesta sessió · [S] suposició · [?] a verificar.
Entrada: `APP/Proves/test 01.STEP`. Textura: la fórmula de la 02 (quadrats enfonsats en tauler d'escacs), feta com a **solució nova**: els fitxers de `textures/02_placa_quadres/` no s'han tocat.
Camí provat: **(b)**, és a dir, una sola superfície NURBS que passa per una graella de punts del camp d'alçades.

## Correcció del SP-5
La cara blava (cara 2) **no és una franja al voltant del cilindre**, com es deia al SP-5. És una **zona retallada a la part de dalt** del cilindre, d'uns 32,8 × 85,6 mm desplegada (y entre 16 i 101 mm, x entre −15 i 15 mm). Les cares 0 i 1 són les dues meitats del cilindre, retallades al voltant d'aquesta zona. Les conclusions del SP-5 (particions, color i mm) continuen sent vàlides.

## Mètode
1. Es despleguen la zona i el seu contorn sobre el pla: coordenada d'arc `R·θ` i `y`. En un cilindre, el desplegament no té cap distorsió (SP-1).
2. Es calcula el camp d'alçades de la textura 02 amb els valors per defecte: CELL 8, GAP 0,2, CORNER_R 1,2, WALL 0,2, DEPTH 0,4, TILT 0,8 i LIP 0,3. El tauler va centrat a la zona.
3. **Esvaïment cap al contorn** (FADE_GAP 1 mm, FADE_LEN 3 mm): al contorn l'alçada és 0, de manera que la superfície texturada es pot cosir amb la resta del cilindre.
4. Una graella no uniforme, densa a les arestes dels quadrats (pas de 0,04 mm) i més ampla al fons (0,4 mm). Són **328 × 834 = 273 552 punts**, i per aquests punts passa una superfície NURBS cúbica.
5. La superfície es retalla amb el contorn original de la cara blava (`Brep.Split`) i es cus amb les altres quatre cares (`JoinBreps`, tolerància 0,01 mm).

## Resultats [H]
| Mesura | Valor |
|---|---|
| Sòlid final | **tancat i vàlid**, 5 cares (la textura substitueix la cara blava) |
| Àrea de la cara texturada | 2 518,13 mm² (original 2 513,64; +0,18 % pels quadrats) |
| Desviació respecte a la fórmula (20 000 punts a l'atzar) | mediana ≈ 0 · p99 0,0019 mm · p99,9 0,011 mm · **màx. 0,015 mm** |
| Temps | 63 s per calcular els punts (Python pur) · 0,6 s per ajustar la superfície · uns 230 s en total amb el retall i la unió |
| `sp6_solid.stp` | **24,8 MB** |
| `sp6_solid.x_t` (Parasolid) | **18,5 MB** |
| `sp6_solid.3dm` | 6,6 MB |
| `sp6_superficie.stp` / `.x_t` / `.3dm` | 24,9 / 18,5 / 6,6 MB (només la cara texturada) |

Captures: `sp6_solid_Arctic.png` (vista general) i `sp6_detall_Arctic.png` (detall).

## Valoració
1. **La sortida NURBS cap a SolidWorks és possible** [H a Rhino]: el sòlid queda tancat, vàlid i amb la textura incorporada. Es completen les dues primeres etapes de sortida (D3: superfície i sòlid).
2. **⚠ Pes massa gran (D4):**
   - 25 MB per a una zona de 33 × 86 mm. Una peça real amb una zona texturada deu vegades més gran donaria centenars de MB, i [S] SolidWorks 2020 tindria problemes per treballar-hi.
   - El camí (b), una sola superfície per punts, **no escala**: la graella ha de ser densa a tota la fila i a tota la columna per culpa d'unes arestes que només ocupen una franja estreta.
3. **⚠ Precisió al límit:** la desviació màxima és de 0,015 mm (la tolerància era 0,01). L'error es concentra a les cantonades marcades, on hi ha l'aresta més viva. Les captures hi mostren petites lluentors.
4. **Proposta per al següent pas: camí (a), NURBS exacte per quadrat.**
   - Cada quadrat és idèntic en coordenades locals: es construeix **una sola vegada** (fons polinòmic exacte + paret de rampa + cantonades arrodonides) i es col·loca per a cada cel·la.
   - [S] Ha de pesar molt menys (ordre de pocs MB) i ser exacte, sense error d'ajust.
   - Les cel·les afectades per l'esvaïment del contorn necessiten un tractament a part.
5. **Velocitat:** el càlcul dels punts en Python pur (63 s) es pot accelerar molt amb el truc de la textura 03 (avaluar la fórmula una vegada per cada coordenada local diferent) o fent servir numpy. Amb el camí (a) gairebé no caldrà.

## Prova a SolidWorks 2020 (Pau, 2026-11-14) [H]
- **El `.x_t` s'obre** a SolidWorks 2020. **El STEP no**: SolidWorks no l'acaba d'importar. → **La sortida per defecte serà Parasolid (`.x_t`).**
- **Resultat estètic: no és acceptable.** Hi ha tres causes:
  1. **Quadrats tallats al contorn:** amb un esvaïment curt (3 mm) sobre quadrats de 8 mm, les cel·les del contorn queden com a falques deformades.
  2. **Taques i ondulacions dins dels quadrats:** passar una sola superfície per una graella amb salts de densitat (0,04 → 0,4 mm) fa que la corba s'ondulgi. Es veu com a taques a l'ombrejat de SolidWorks. És un defecte del camí (b).
  3. **Tauler no adaptat a la zona:** 33 mm d'ample són 4,1 cel·les, i per això sobren mitges columnes als costats.

## Pendent
- [?] **Obrir `sp6_solid.x_t` i `sp6_solid.stp` a SolidWorks 2020.** El connector de SolidWorks no ha pogut connectar (SolidWorks no estava obert). Pau els pot obrir a mà; cal comprovar que s'obren, que el sòlid és vàlid (Eines → Comprovar) i com respon SolidWorks amb aquests pesos.
- Provar el camí (a) i comparar-ne el pes, la precisió i el temps.
