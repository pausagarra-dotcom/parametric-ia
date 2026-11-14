# 03 · Quadrats sobre superfície orgànica

Data: 2026-11-14 · Referència: `referencia/test_02.jpg` i `test_02_detail.JPG` (la mateixa que la 02)

El mateix patró de quadrats enfonsats en tauler d'escacs que la textura 02, aplicat sobre una superfície NURBS orgànica de 200×200 mm. El patró s'esvaeix cap a la vora. Aquí la fórmula **es veu al llenç**: cada línia és un node `Evaluate` natiu amb el text de la fórmula en un panell groc.

## Fitxers
| Fitxer | Què és |
|---|---|
| `grasshopper/superficie_organica_quadres.gh` | La definició lliurada. La superfície ja hi va inclosa. |
| `formula_patro.md` | La fórmula completa, els sliders i els temps de càlcul. |
| `scripts/build_gh_organica.py` | Genera el `.gh` des de Rhino (`run_python`). |
| `scripts/gh_org_rejilla.py` | Component REJILLA: on s'avalua la fórmula (punts per longitud d'arc). |
| `scripts/gh_org_malla.py` | Component MALLA: munta la malla final. |
| `rhino/organica_quadres.3dm` | Model de treball. |
| `captures/` | Resultat final, prova amb 4 llums, detall i comparació dels dos models. |

## Sliders principals
Els mateixos que la 02 (`CELL`, `GAP`, `CORNER_R`, `WALL`, **`DEPTH` 0,4 mm**, `TILT`, `LIP`, `ROT`, `OFF_X/Y`) més `FADE_GAP` 10 mm, `FADE_LEN` 30 mm i `STEP` 2 mm (densitat de malla).

## Reconstrucció
Executar `scripts/build_gh_organica.py` dins de Rhino. Llegeix la superfície de l'objecte 646 de `recerca/sp4/sp4_625_bosses.3dm`. **Sobreescriu** el `.gh`: només s'ha de fer si es vol canviar aquesta textura.
