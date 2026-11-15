# 05 · Funda de rombes en NURBS

Data: 2026-11-15 · Referència: `referencia/test_01.JPG` (la mateixa foto que la 01)

Versió **NURBS** de la textura 01 (rombes enfonsats que s'esvaeixen), feta perquè la peça s'obri a **SolidWorks** com a sòlid vàlid i lleuger. La 01 no s'ha tocat.

Per què: la 01 surt com a **malla**. Convertir-la a NURBS (`_MeshToNURB`) dona milers de cares planes, facetes visibles, cares no vàlides i fitxers pesats. Aquí la geometria es construeix directament en NURBS a partir dels mateixos paràmetres.

Hi ha dues variants al mateix `.gh`:
- **Funda de mòbil** (`scripts/gh_phone_nurbs.py`, sortida `funda`).
- **Cilindre** amb rombes als costats (`scripts/gh_cylinder_nurbs.py`, sortida `cilindro`).

## Mètode
1. **Un pegat Bezier per rombe** (grau `GRADO`, per defecte 6 → xarxa de control de 7 × 7). El quadrat de paràmetres es correspon amb el rombe de forma afí, de manera que el pegat no té cap ajust ni cap error d'ajust.
2. **Les arestes del rombe són a profunditat 0**, a la cara de la peça. Amb `GAP` 0, els rombes veïns comparteixen exactament la mateixa aresta perquè els vèrtexs surten d'índexs enters de la xarxa.
3. **Forma del fons** (slider `SUAVIDAD`):
   - **1:** fons arrodonit i llis, `(1−s²)(1−t²)` exacte en Bernstein, com a la foto.
   - **0:** s'acosta a la piràmide de la 01, amb una aresta suavitzada pel pegat.
   - Entre totes dues, una barreja de les dues formes.
4. **Franja entre rombes** (slider `GAP`, per defecte 0,5 mm; afegit el 2026-11-15 a petició de Pau, com a la foto de referència):
   - Cada rombe s'encongeix cap al seu centre (homotècia), de manera que els seus costats queden a `GAP/2` de l'aresta de la cel·la.
   - Entre rombe i rombe queda una franja plana (llisa al cilindre).
   - La cara superior (o el costat del cilindre) porta un forat per rombe.
   - Al cilindre, el costat es parteix abans en franges helicoidals que segueixen el centre de les franges llises, i cada franja es retalla només amb els seus rombes. Si es retalla tot alhora, el temps creix amb el quadrat del nombre de rombes: 14 s → 5 s.
   - `GAP` = 0 torna als rombes enganxats, amb aresta viva.
5. **Esvaïment:** la mateixa fórmula que la 01 (`TX_*`, `FADE_*`), aplicada a cada punt de control. Els rombes amb un enfonsament màxim inferior a `MIN_D` no es modelen i queden plans.
6. **Funda:**
   - Llosa exacta: parets verticals i cantell R (cilindres als trams rectes i tors a les cantonades).
   - Menys un tallador del forat de càmera amb el seu propi cantell, en diferència booleana. Així es crea bé el nervi de 3 mm entre el forat i la vora dreta (8,098 mm, igual que a la malla de la 01).
   - El tallador puja **0,02 mm** (`CAM_LIFT`) perquè talli la cara superior en angle i no tangent. Si quedés tangent, la booleana fallaria a la franja de 6 mm de dalt.
7. **Cilindre:**
   - Cada pegat s'enrotlla sobre el cilindre i s'interpola en grau 6. Les arestes cauen exactament sobre el R (desviació mesurada 0).
   - El costat del cilindre es retalla amb els contorns de la zona. Amb `GAP` 0, la costura es posa en una columna sense rombes. Amb `GAP`, els rombes que creuen la costura es retallen en el primer pas.
8. **Neteja:**
   - Es treuen els rombes que toquen el cantell o les tapes.
   - Amb `GAP` 0, quan dos rombes només es toquen per un vèrtex (contorn pessigat), es treu el de menys enfonsament.
   - El script indica quin és l'enfonsament més gran que s'ha perdut.

## Resultats (valors per defecte, `GAP` 0,5 mm) [mesurat]
| | Funda | Cilindre |
|---|---|---|
| Rombes | 171 | 814 (46 al voltant, amplada real 5,464 mm) |
| Cares | 205 | 833 |
| Vàlid / sòlid / arestes obertes | sí / sí / 0 | sí / sí / 0 |
| Enfonsament més gran perdut | 0,0020 mm | 0,0030 mm |
| Temps de càlcul | ~1 s | ~5 s (2,5 s amb `GAP` 0) |
| `.x_t` / `.stp` / `.3dm` | 1,62 / 1,34 / 1,25 MB | 7,61 / 7,03 / 5,62 MB |
| STEP rellegit a Rhino | sòlid vàlid, 205 cares | sòlid vàlid, 833 cares |

Amb `GAP` 0 (rombes enganxats): funda de 209 cares i 1,17 MB en `.x_t`; cilindre de 807 cares i 4,92 MB.

Comparació: el SP-6 (camí b) donava 25 MB per a una zona de 33 × 86 mm. La malla convertida de la 01 donava un sòlid no vàlid de 9 445 cares.

Proves amb sliders extrems:
- Valors provats: `SUAVIDAD` 0 i 0,5, `GRADO` 9, `DEPTH` 1, rombes de 4 × 6 mm, zona gran, 3 zones al cilindre, R25 i `GAP` 0 / 0,2 / 0,3 / 1.
- Tots donen un sòlid vàlid.
- Si la zona arriba al cantell, el missatge avisa de quant enfonsament es perd (p. ex. 0,30 mm amb `TX_A` 35 i `TX_B` 75).

## Fitxers
| Fitxer | Què és |
|---|---|
| `grasshopper/funda_rombos_nurbs.gh` | Dos components Python 3 (funda i cilindre), cadascun amb sliders del mateix nom, una sortida Brep i un panell TARGET. **El codi va dins del `.gh`.** |
| `scripts/gh_phone_nurbs.py`, `scripts/gh_cylinder_nurbs.py` | El codi dels dos components (font de la qual el builder copia el codi). |
| `scripts/build_gh_rombos_nurbs.py` | Torna a construir el `.gh` des de Rhino (`run_python`, amb el Grasshopper obert). |
| `scripts/exportar.py` | Genera la geometria amb els valors per defecte i la desa en `.3dm`, `.x_t` i STEP (primer a una carpeta local i després la copia aquí). Comprova que el STEP es torna a llegir com a sòlid. |
| `rhino/*.3dm` | La funda i el cilindre, cadascun en el seu fitxer. |
| `salida/*.x_t`, `salida/*.stp` | Els fitxers per obrir a SolidWorks. |
| `captures/` | Captures de Rhino (vista general i detall; les línies negres són les arestes entre cares) i `funda_sombreado_4luces.png`: els pegats finals ombrejats sense arestes, des de 4 direccions de llum. |

## Ús
- **Grasshopper:** obre el `.gh`. Per actualitzar un objecte de Rhino en viu, enganxa el seu GUID al panell TARGET.
- **SolidWorks:** `salida/funda_rombos_nurbs.x_t` (o el `.stp`) → Obrir → Opcions → "Intentar formar sòlid(s)".

## Notes per a injecció
- **Funda** (desemmotllament en Z): els rombes són poc profunds (0,5 mm) i tenen parets suaus. No hi ha contrasortides.
- **Cilindre:** els rombes dels costats són **contrasortides** si el motlle s'obre en l'eix del cilindre. Caldran correderes, o una línia de partició que passi pel mig de cada zona.

## Pendent
- [?] Obrir els `.x_t` i els `.stp` a **SolidWorks 2020** i comprovar-los (Eines → Avaluar → Comprovar). Des d'aquí no s'ha pogut connectar amb SolidWorks.
