# Textures des d'imatge sobre superfícies Rhino

A partir d'una foto de referència es crea una textura paramètrica (Grasshopper + Python 3) que s'aplica sobre una superfície de Rhino 9.

## Carpetes

```
/
├─ README.md            aquest índex
├─ docs/                brief.md, PLAN.md i l'accés directe al brief de Google Docs
├─ textures/            una carpeta per textura, numerada per ordre de creació
│  ├─ 01_funda_rombos/
│  ├─ 02_placa_quadres/
│  ├─ 03_organica_quadres/
│  └─ 04_seient_colissos/
├─ recerca/             spikes de validació (SP-0 bucle Rhino, SP-1 mapeig, SP-4 relleu), amb informe.md
└─ historial/           una nota per commit, amb la data al nom (AAAA-MM-DD_NN_descripcio.md)
```

Cada textura té la mateixa estructura:

```
textures/NN_nom/
├─ README.md       què és, data, referència, sliders i com es reconstrueix
├─ referencia/     fotos de referència
├─ grasshopper/    el fitxer .gh lliurat
├─ scripts/        codi Python del component i, si n'hi ha, el script que genera el .gh
├─ rhino/          models .3dm de treball (si n'hi ha)
└─ captures/       captures de Rhino i comparacions amb la referència
```

## Regles
1. **Textura nova = carpeta nova.** Abans de començar, Claude pregunta el nom i crea `textures/NN_nom/` amb el número següent.
2. **No es modifica mai una textura lliurada** per fer-ne una altra, encara que s'assemblin. Una textura antiga només es toca si es demana explícitament.
3. **Cada commit té la seva nota** a `historial/`, amb la data del dia, i una etiqueta git amb el mateix codi (p. ex. `2026-11-14_01`). Per recuperar una versió anterior, demana-ho a Claude indicant l'etiqueta (p. ex. `2026-11-14_01`).

## Entorn
- Rhino 9.1 (Python 3.13 dins de Rhino), connectat a Claude Code amb les eines `mcp__rhino__*`.
- Processament d'imatge fora de Rhino, a l'entorn virtual `C:\dev\venvs\textura` (OpenCV, numpy, pytest), fora de Drive.
