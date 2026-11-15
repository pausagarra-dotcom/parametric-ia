# 2026-11-15 · 02 · APP: SP-8, SP-9 i catàleg (fase 0)

Etiqueta git: `2026-11-15_02` · Punt anterior: `2026-11-15_01`

## Què s'ha desat
- **`APP/recerca/sp8/`**, velocitat:
  - Enviar un script amb RhinoCode tarda ~0,5 s.
  - **ARAP amb scipy: 1,1 s.**
  - **Rhino.Inside no funciona** amb Rhino 9 en aquest equip.
  - **Servidor dins de Rhino:** 8 ms de transport, i cada canvi de slider de la textura 03 tarda 3,1 s. S'ha trobat i corregit un doble càlcul que el feia trigar 6 s.
  - Scripts: `sp8_servidor_rhino.py`, `sp8_client.py`, `sp8_arap_scipy.py`, `sp8_rhinoinside.py` i els resultats en JSON.
- **`APP/recerca/sp9/`**, xat:
  - **Condicions d'ús:** amb més usuaris cal clau d'API, perquè Anthropic no permet oferir l'inici de sessió de claude.ai en productes propis.
  - **Cicle complet provat amb Claude Code local** (sense API de pagament): captura → Claude → acció MCP de l'app `canviar_parametre`.
  - Fitxers: `app_mcp.py`, `mcp_config.json`, `prova_xat.ps1`, la resposta i `estat.json`.
- **`APP/cataleg/`**, fase 0:
  - `esquema.json`, amb els tres tipus de fitxa: textura, solució i projecte;
  - fitxes de les textures 01–04, totes en estat «pendent» fins que s'aprovin en sòlid;
  - solucions S001–S004;
  - `test_cataleg.py`: comprovació automàtica sense dependències.
- **`APP/README.md`:** canvi de la decisió 4. Hi haurà **previsualització instantània al visor** (GPU) amb la mateixa fórmula, i Rhino continua sent el motor de la geometria final.
- **`APP/PLAN.md`:** inclou l'estat dels SP-8, SP-9 i la fase 0.
- **Entorn de Python** (`C:\dev\venvs\textura`, fora del repositori): s'hi han afegit scipy 1.18.1 i rhinoinside 0.8.2, amb el permís de Pau.

## Què NO ha canviat
- Les textures 01–04 no s'han tocat.
- Queden fora d'aquest commit els canvis d'altres sessions:
  - la textura `05_funda_rombos_nurbs` i la seva fitxa del catàleg (sessió de la fase 2);
  - `APP/PROMPT_intro_app_D3.md`;
  - el `README.md` de l'arrel;
  - `textures/01_funda_rombos/README.md` i `rhino/`;
  - `textures/04_seient_colissos/grasshopper/seient_colissos.gh`;
  - les notes `historial/2026-11-14_01` i `_02`.
- Mentre la fitxa 05 no estigui en un commit, `test_cataleg.py` falla en un repositori net, perquè detecta la carpeta 05 sense fitxa.

## Com tornar a aquest punt
Demana-ho a Claude indicant l'etiqueta `2026-11-15_02`.
