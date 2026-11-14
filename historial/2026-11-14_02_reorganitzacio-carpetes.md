# 2026-11-14 · 02 · Reorganització de carpetes

Etiqueta git: `2026-11-14_02` · Punt anterior: `2026-11-14_01`

## Què ha canviat
- **Estructura nova:**
  - `textures/` té una carpeta per textura: `01_funda_rombos`, `02_placa_quadres` i `03_organica_quadres`.
  - Cada carpeta té les subcarpetes `referencia/`, `grasshopper/`, `scripts/`, `rhino/` i `captures/`, i un `README.md`.
  - `recerca/` conté els spikes SP-0, SP-1 i SP-4.
  - `docs/` conté el brief i el pla.
  - `historial/` conté aquestes notes.
- **Desaparegudes:** les carpetes antigues `gh/`, `spikes/` i `cases/`.
- **Esborrades:** 32 captures de Rhino que havien sortit en blanc. Totes eren imatges buides; si cal, es poden recuperar del punt `2026-11-14_01`.
- **Copiada:** la foto `test_02` (i el detall) també a la textura 03, perquè les textures 02 i 03 en parteixen totes dues.
- **Rutes actualitzades:** només les línies de ruta de `build_gh_placa.py`, `build_gh_organica.py`, `sp1_mapping.py` i `sp4_relief.py`, i les referències de `formula_patro.md`.
- **Nou:** `README.md` a l'arrel, amb l'índex i les regles, i un README per textura.

## Què NO ha canviat
- Els tres `.gh` lliurats, els `.3dm` i les fotos són **byte a byte idèntics** (comprovat amb SHA-256). Els `.gh` no s'han tornat a generar.
- El codi dels components de les textures (`gh_phone.py`, `gh_cylinder.py`, `gh_placa.py`, `gh_org_*.py`) no s'ha tocat.

## Com tornar a aquest punt
```
git checkout 2026-11-14_02
```
