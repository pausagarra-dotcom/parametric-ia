# Catàleg (fase 0)

El format comú de la base de dades de l'app. Cada fitxa és un fitxer JSON que compleix [`esquema.json`](esquema.json).

| Carpeta | Què hi ha | Es comparteix |
|---|---|---|
| `textures/` | Una fitxa per textura lliurada (`NN_nom.json`). Descriu la textura i apunta a la seva carpeta `textures/NN_nom/`, que **no es modifica mai**. | sí |
| `solucions/` | Com s'aplica una textura a cada tipus de geometria (`SNNN_nom.json`): mètode de mapeig, sortida, codi reutilitzable, problemes trobats i com es van resoldre, resultats. **És el que creix.** | sí |
| *projectes* | Els projectes de client **no van aquí** (A3, E3). L'esquema ja els defineix (`projecte`); la ubicació es decidirà a la fase 3. | no |

**Estats** (E2, F1):
- `pendent` → `aprovada` (validada en digital per Pau, passada a sòlid) → `descartada`;
- a més, la casella `validacio_fisica`, que indica si s'ha imprès en 3D i amb quina tecnologia (SLA o FDM).

Totes les textures 01–04 consten com a `pendent` fins que Pau les aprovi en sòlid.

**Etiquetes per cercar** (E1): tipus de geometria, tipus de producte, material, acabat, estil i projecte.

## Comprovació automàtica
```bash
C:\dev\venvs\textura\Scripts\python.exe -m pytest -q -p no:cacheprovider APP/cataleg
```
Comprova tres coses:
- que cada fitxa compleix l'esquema i que el nom del fitxer coincideix amb l'id;
- que totes les rutes que cita existeixen i que les textures que citen les solucions són al catàleg;
- que **cada carpeta `textures/NN_*` té la seva fitxa**.

## Contingut actual (2026-11-15)
- **Textures:** 01_funda_rombos, 02_placa_quadres, 03_organica_quadres, 04_seient_colissos.
- **Solucions:**
  - S001: cilindre amb zona retallada, sortida `.x_t` (SP-5/6);
  - S002: orgànica amb ARAP regional (SP-7/8);
  - S003: placa amb cantell arrodonit (textura 02);
  - S004: orgànica amb graella per longitud d'arc (textura 03).
- La textura `05_funda_rombos_nurbs` (feta en una altra sessió, la que treballa la fase 2) té la seva fitxa `textures/05_funda_rombos_nurbs.json`, creada per aquella sessió. Entra al repositori amb el commit d'aquella textura, no amb aquest.
