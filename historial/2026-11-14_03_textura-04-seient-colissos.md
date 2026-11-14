# 2026-11-14 · 03 · Textura 04: seient colissos

Etiqueta git: `2026-11-14_03` · Punt anterior: `2026-11-14_02`

## Què s'ha desat
- **Textura nova `textures/04_seient_colissos/`:**
  - La peça blanca superior d'un seient de bicicleta: una closca prima amb una finestra central que s'obre en Y pel darrere.
  - Té ovals en relleu a portell que s'esvaeixen abans de les vores i cap al morro.
  - Tot es genera amb sliders, també el contorn, que està ajustat a la foto de planta.
  - `grasshopper/seient_colissos.gh`: un component Python 3 amb 41 sliders en 5 grups, la sortida `seient` (Mesh) i el panell TARGET. El codi va a dins del `.gh`.
  - `scripts/gh_seient.py` és el codi del component, i `scripts/build_gh_seient.py` el generador del `.gh`.
  - `rhino/seient_colissos.3dm` té dues malles:
    - la versió actual, amb columnes verticals a la zona central i inclinades a la vora de la part ampla;
    - al costat, la versió anterior, amb les columnes seguint el contorn (`FOLLOW_MODE` 1).
  - A `referencia/` hi ha les fotos de referència i les correccions marcades. A `captures/` hi ha les comparacions amb les fotos i la malla ombrejada amb 4 llums.
- **Canvis fets durant la sessió:**
  - El nom inicial era `04_seient`.
  - Ovals estrets: 3,6 mm en lloc de 6.
  - L'esvaïment del morro comença a la línia marcada, a uns 90 mm de la punta.
  - Zona central amb columnes verticals.
- **`README.md` de l'arrel:**
  - S'hi afegeix `04_seient_colissos` a l'índex.
  - Inclou també dos petits canvis de redacció que ja hi havia sense desar.

## Què NO ha canviat
- Les textures 01, 02 i 03 no s'han tocat.
- Queden fora d'aquest commit, sense desar, els canvis que ja hi havia i que són d'altres sessions:
  - `APP/`
  - `textures/01_funda_rombos/README.md` i `textures/01_funda_rombos/rhino/`
  - les notes `historial/2026-11-14_01` i `_02`

## Suposicions pendents de confirmar
- La mida (273,5 × 136 mm), l'alçada del relleu (0,8 mm), el gruix (2,5 mm) i el perfil lateral són estimacions fetes a partir de les fotos. Totes es poden canviar amb sliders.

## Com tornar a aquest punt
Demana-ho a Claude indicant l'etiqueta `2026-11-14_03`. Es pot recuperar un sol fitxer o tot el projecte.
