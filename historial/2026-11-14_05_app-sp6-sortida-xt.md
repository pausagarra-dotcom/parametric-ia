# 2026-11-14 · 05 · APP: SP-6, sortida cap a SolidWorks

Etiqueta git: `2026-11-14_05` · Punt anterior: `2026-11-14_04`

## Què s'ha desat
- **`APP/recerca/sp6/informe.md`:** el SP-6.
  - La fórmula de la textura 02 aplicada a la zona blava del `test 01`, com a solució nova; la textura lliurada no s'ha tocat.
  - Sòlid NURBS tancat i vàlid.
  - **Decisió: la sortida és Parasolid (`.x_t`).** SolidWorks 2020 l'obre, mentre que el STEP no l'acaba d'importar.
  - El mètode provat, una sola superfície que passa per punts, **no serveix**:
    - quadrats tallats en forma de falca al contorn;
    - ondulacions dins dels quadrats;
    - massa pes (25 MB).
  - Següent pas: quadrats NURBS nets amb el tauler ajustat a la zona.
- **Captures:** `sp6_solid_Arctic.png` i `sp6_detall_Arctic.png`.
- **`APP/PLAN.md`:** inclou la decisió de sortida en `.x_t` i l'estat del SP-5 i el SP-6.
- **`APP/recerca/sp5/informe.md`:** correcció. La cara blava és una zona retallada a la part de dalt del cilindre, no una franja al voltant.
- **`.gitignore`:** els fitxers de geometria del SP-6 (`.stp`, `.x_t`, `.3dm`, uns 100 MB) queden fora de git. Continuen a Drive, a `APP/recerca/sp6/`.

## Què NO ha canviat
- Les textures 01–04 no s'han tocat.
- Queden fora d'aquest commit, sense desar, els canvis d'altres sessions:
  - `textures/01_funda_rombos/README.md` i `textures/01_funda_rombos/rhino/`
  - les notes `historial/2026-11-14_01` i `_02`

## Com tornar a aquest punt
Demana-ho a Claude indicant l'etiqueta `2026-11-14_05`.
