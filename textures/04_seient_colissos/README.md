# 04 · Seient colissos (peça superior)

Data: 2026-11-14 · Referència: `referencia/seient_planta.jpg` (vista de dalt), `seient_explosionat.jpg` (vista explosionada), `seient_explosionat_anotat.png`, `seient_detall_ovals.png` (forma dels ovals), `seient_planta_direccio_ovals.png` i `zona_vertical_marcada.png` (direcció dels ovals) i `correccio_fade_morro.webp` (on comença l'esvaïment del morro)

Només la **peça blanca superior** del seient de la vista explosionada. És una closca prima amb el cantell arrodonit i una finestra central que comença rodona al morro i s'obre en Y pel darrere. Té **ovals en relleu** a portell, allargats en el sentit del seient. A la zona central (la marcada en blau a `referencia/zona_vertical_marcada.png`) les columnes van verticals; a la vora de la part ampla s'inclinen paral·leles al contorn sense comprimir-se. Els ovals s'esvaeixen abans de la vora exterior, de la finestra i de la punta del morro.

## Fitxers
| Fitxer | Què és |
|---|---|
| `grasshopper/seient_colissos.gh` | La definició lliurada: un component Python 3 amb sliders (en 5 grups), sortida `seient` (Mesh) i panell TARGET. El codi va a dins del `.gh`. |
| `scripts/gh_seient.py` | Codi del component (és el que hi ha dins del `.gh`). |
| `scripts/build_gh_seient.py` | Genera el `.gh` des de Rhino (`run_python`). |
| `rhino/seient_colissos.3dm` | Dues malles tancades (`DETAIL` 0,5, 340k cares cadascuna): la versió actual (capa `seient_colissos`) i, al costat (desplaçada 170 mm en Y), la versió anterior amb les columnes seguint el contorn sense zona vertical (capa `seient_colissos_anterior`, `FOLLOW_MODE` 1). |
| `captures/` | Prototip comparat amb la foto (planta i detall), la malla real ombrejada amb 4 llums i la vista obliqua al costat de la foto explosionada. |

## Mesures preses de la foto
- **Contorn:** mesurat fila per fila a la vista de dalt (vora dreta, simètrica respecte de l'eix de la finestra) i ajustat amb la fórmula dels sliders (error rms 0,4 mm). La foto no porta mides: **l'escala (0,30 mm/píxel → 273,5 × 136 mm) és una suposició.** Es canvia amb `L` i `W`.
- **Ovals:** columnes cada 4,9 mm (`CW`) i pas de 17,6 mm (`CL`), amb les columnes veïnes desplaçades mig pas. Els ovals fan 3,6 × 17,5 mm (`OVAL_W`, `OVAL_L`). La primera versió els tenia de 6 mm d'ample; el 2026-11-14 es van fer més estrets i elegants, mantenint la forma, seguint la foto de detall `referencia/seient_detall_ovals.png`.
- **Esvaïment del morro:** els ovals són sencers fins a d = 90 mm (just davant de la finestra, on es va marcar a `correccio_fade_morro.webp`) i s'esvaeixen fins a d = 5 mm (`FADE_NOSE_START` 5 + `FADE_NOSE` 85).
- **Alçada del relleu `HEIGHT` 0,8 mm:** a la silueta de l'ala a la foto explosionada els ovals sobresurten entre 0,7 i 1,4 mm. És una estimació.
- **Perfil lateral i bombat** (`DIP`, `KICK`, `NOSE_DROP`, `CROWN_*`) i **gruix** `THICK` 2,5 mm: estimats a ull a la foto explosionada.

## Sliders
- **Contorn:** `L`, `W`, `NOSE_W`, `NOSE_TAPER`, `WIDE_START`, `WIDE_POS`, `WIDE_P`, `REAR_DROP`, `REAR_R`, `NOSE_R`.
- **Finestra:** `SLOT_START`, `SLOT_W1`, `SLOT_W2`, `SLOT_SPLIT`, `FLARE` (obertura de la Y), `TIP_R` (arrodoniment de les puntes de les ales).
- **Volum:** `THICK`, `DIP`, `KICK`, `NOSE_DROP`, `CROWN_NOSE`, `CROWN_REAR`, `CROWN_P`.
- **Ovals:** `CW`, `CL`, `OVAL_W`, `OVAL_L`, `OVAL_Q` (forma de les puntes), `HEIGHT` (negatiu = enfonsat), `FOLLOW_START` (0,65: fins a quina fracció de W/2 les columnes són verticals), `FOLLOW_OUT` (1: quant s'inclinen les de fora, 1 = paral·leles a la vora), `COL_SHIFT`, `ROW_SHIFT`, `FOLLOW_MODE` (0 = zona central vertical, actual; 1 = versió anterior, per comparar).
- **Esvaïment i malla:** `FADE_EDGE_GAP`, `FADE_EDGE`, `FADE_SLOT_GAP`, `FADE_SLOT`, `FADE_NOSE_START`, `FADE_NOSE`, `DETAIL` (0,7 mm ≈ 3 s; 0,5 mm ≈ 9 s, per al model final).

Eixos: X al llarg (darrere a X=0, morro a X=L), Y de costat, Z amunt.

## Reconstrucció
Executar `scripts/build_gh_seient.py` dins de Rhino amb Grasshopper obert. **Sobreescriu** `grasshopper/seient_colissos.gh`: només s'ha de fer si es vol canviar aquesta textura.
