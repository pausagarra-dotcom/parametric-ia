# 2026-11-15 · 01 · APP: SP-7, mapeig UV amb mínima distorsió

Etiqueta git: `2026-11-15_01` · Punt anterior: `2026-11-14_05`

## Què s'ha desat
- **`APP/recerca/sp7/`:** el SP-7.
  - `informe.md`: comparació de tres mètodes per desplegar les superfícies orgàniques del SP-1: uv_arc, LSCM i ARAP.
    - **Resultat:** ARAP aplicat només a la zona a texturar baixa la distorsió d'àrea a A25 / 100 mm del 16,2 % al **5,0 %**, i a A40 del 32 % al **12 %**.
    - Serà el mètode per defecte per a superfícies orgàniques.
  - `sp7_unwrap.py`: desplegament i mesura (numpy, entorn `C:\dev\venvs\textura`).
  - `sp7_quadricula.py`: quadrícula de prova de 10 mm sobre la superfície (OpenCV).
  - Dades: `malla_A*.json` (generades a Rhino), `sp7_results.json`, `sp7_regional.json`, `quadricula_A25_W100.json` i els desplegaments en `.npy`.
  - Imatges:
    - `quadricula_A25_W100_persp.png` i `_planta.png`: uv_arc i ARAP de costat;
    - `mapa_regional_*.png` i `mapa_area_*.png`: mapes de distorsió.
- **`APP/PLAN.md`:** inclou l'estat del SP-7.

## Què NO ha canviat
- Les textures 01–04 no s'han tocat.
- Queden fora d'aquest commit, sense desar, els canvis d'altres sessions:
  - `textures/01_funda_rombos/README.md` i `textures/01_funda_rombos/rhino/`
  - `textures/04_seient_colissos/grasshopper/seient_colissos.gh`
  - les notes `historial/2026-11-14_01` i `_02`

## Com tornar a aquest punt
Demana-ho a Claude indicant l'etiqueta `2026-11-15_01`.
