# 02 · Placa de quadrats

Data: 2026-11-13 / 14 · Referència: `referencia/test_02.jpg` i el detall `test_02_detail.JPG`

Quadrats enfonsats en **tauler d'escacs** (un sí, un no) sobre una placa plana amb les cantonades i el cantell arrodonits. Els quadrats s'esvaeixen abans d'arribar al cantell. El perfil per defecte (`PROFILE` 7) reprodueix la referència: fons parabòlic suau, arestes marcades a dalt-dreta i baix-esquerra que es fonen cap a les altres dues.

## Fitxers
| Fitxer | Què és |
|---|---|
| `grasshopper/placa_quadres.gh` | La definició lliurada: un component Python 3 amb sliders, sortida `plate` (Mesh) i panell TARGET. |
| `scripts/gh_placa.py` | Codi del component (és el que hi ha dins del `.gh`). |
| `scripts/build_gh_placa.py` | Genera el `.gh` des de Rhino (`run_python`). |
| `rhino/placa_quadres.3dm`, `placa_quadres_02.3dm` | Models de treball. |
| `captures/` | Versions successives (v1–v3, tauler, suau, dues arestes, canal) i comparacions amb la referència. |

## Sliders principals
`CELL` 8 mm, `GAP` 0,2 mm, `CORNER_R` 1,2 mm, `WALL` 0,2 mm, **`DEPTH` 0,4 mm**, `TILT` 0,8, `LIP` 0,3, `PATTERN` (0 tauler, 1 tots), `PROFILE`, `FADE_GAP`, `FADE_LEN`. La fórmula està explicada a `../03_organica_quadres/formula_patro.md`.

## Reconstrucció
Executar `scripts/build_gh_placa.py` dins de Rhino. **Sobreescriu** `grasshopper/placa_quadres.gh`: només s'ha de fer si es vol canviar aquesta textura.
