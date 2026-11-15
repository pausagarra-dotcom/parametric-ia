# 2026-11-15 · 03 · Textura 05: funda de rombes en NURBS

Etiqueta git: `2026-11-15_03` · Punt anterior: `2026-11-15_02`

## Què s'ha desat
- **Textura nova `textures/05_funda_rombos_nurbs/`:** la 01 refeta directament en NURBS perquè s'obri a SolidWorks com a sòlid vàlid i lleuger.
  - **Per què:** la malla de la 01 convertida amb `_MeshToNURB` donava 9 445 cares facetades i un sòlid no vàlid.
  - **Mètode:** un pegat Bezier per rombe.
  - **Sliders nous:**
    - `SUAVIDAD`: de fons arrodonit (1) a piràmide (0);
    - `GAP`: franja plana entre rombes, 0,5 mm per defecte;
    - `GRADO`: grau del pegat.
  - **Funda:** llosa exacta amb cantell R3 i forat de càmera fet en diferència booleana.
  - **Cilindre:** pegats enrotllats i interpolats.
  - `grasshopper/funda_rombos_nurbs.gh`: dos components Python 3 (funda i cilindre) amb sliders, sortida Brep i panell TARGET. El codi va dins del `.gh`.
  - `scripts/`:
    - `gh_phone_nurbs.py` i `gh_cylinder_nurbs.py`: el codi dels components;
    - `build_gh_rombos_nurbs.py`: torna a construir el `.gh`;
    - `exportar.py`: genera els fitxers `.3dm`, `.x_t` i STEP.
  - `salida/`: `funda_rombos_nurbs.x_t` / `.stp` (1,62 / 1,34 MB) i `cilindro_rombos_nurbs.x_t` / `.stp` (7,61 / 7,03 MB).
  - `rhino/`: un `.3dm` per a cada variant.
  - `captures/`: vistes de Rhino i ombrejat sense arestes des de 4 llums.
  - `referencia/test_01.JPG`: còpia de la foto de la 01.
- **`APP/cataleg/textures/05_funda_rombos_nurbs.json`:** la fitxa del catàleg (així ho demana el README del catàleg). La comprovació del catàleg passa: 11 de 11.
- **`README.md`:** la 05 afegida a l'índex de carpetes.

## Què NO ha canviat
- Les textures 01–04 no s'han tocat.
- Queden fora d'aquest commit, sense desar, els canvis d'altres sessions:
  - `textures/01_funda_rombos/README.md` i `textures/01_funda_rombos/rhino/`
  - `textures/04_seient_colissos/grasshopper/seient_colissos.gh`
  - les notes `historial/2026-11-14_01` i `_02`
  - `APP/PROMPT_intro_app_D3.md`

## Pendent
- Comprovar a SolidWorks 2020 els `.x_t` i els `.stp` (Eines → Avaluar → Comprovar).

## Com tornar a aquest punt
Demana-ho a Claude indicant l'etiqueta `2026-11-15_03`.
