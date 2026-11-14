# 01 · Funda de rombes

Data: 2026-11-11 · Referència: `referencia/test_01.JPG` (funda de mòbil taronja amb rombes enfonsats)

Rombes enfonsats que s'esvaeixen cap a la vora de la zona texturada. Hi ha dues variants al mateix `.gh`:
- **Funda de mòbil** (`scripts/gh_phone.py`, sortida `phone`).
- **Cilindre** amb rombes als costats (`scripts/gh_cylinder.py`, sortida `cyl`).

## Fitxers
| Fitxer | Què és |
|---|---|
| `grasshopper/funda_rombos.gh` | La definició lliurada: components Python 3 amb sliders del mateix nom que les variables. |
| `scripts/gh_phone.py`, `scripts/gh_cylinder.py` | Codi dels dos components (és el mateix que hi ha dins del `.gh`). |
| `scripts/sp2_fiel.py` | Mesura de la mida del rombe a la foto (autocorrelació). |
| `scripts/sp2_flat.py`, `sp2_phone.py`, `preview*.py` | Prototips previs (patró pla i funda) i vistes prèvies en imatge. |
| `captures/` | Proves de malla soldada/no soldada (A/B/C) i captures finals. |

## Sliders principals
`CELL_W` 5,52 mm i `CELL_H` 9,11 mm (diagonals del rombe, mesurades a la foto), `DEPTH` 0,5 mm, zona texturada (`TX_*`), desvaïment (`FADE_IN`, `FADE_N`, `FADE_MODE`) i densitat de malla (`DETAIL`).

## Reconstrucció
No hi ha cap script generador guardat: el `.gh` es va muntar des de Rhino amb el codi de `scripts/`.
