# PLAN · App de textures

Estat: **esborrany per aprovar** (2026-11-14). Res implementat.
Fonts: [README.md](README.md) (idea i decisions) i [PREGUNTES.md](PREGUNTES.md) (respostes de Pau).
Llegenda: **[H]** fet verificat · **[S]** suposició · **[O]** opinió · **[?]** a verificar.

## 1. Què construïm (resum)

1. Una app **local**, al navegador del PC de Pau, en **català** però preparada per a més idiomes. Fase beta amb un sol usuari i sense clients.
2. **Rhino 9** fa tots els càlculs en segon pla; ningú obre Rhino ni Grasshopper.
3. **Mode A (aplicar):** STEP o Parasolid → triar la superfície → triar una textura del catàleg → crear el mapeig UV amb Claude → ajustar → exportar STEP.
4. **Mode B (crear):** foto o tros modelat (STEP o `.x_t`, que es pot escalar) → el mateix procés que les textures 01–03 → textura nova a `textures/NN_nom/`.
5. **Xat amb Claude Code local** (compte de Pau). Accepta text, captures i fitxers de SolidWorks.
6. **Catàleg que creix:**
   - textures (congelades) + solucions d'aplicació per tipus de geometria;
   - estats: *pendent d'aprovació* → *aprovada* → *validada físicament* (impressió 3D);
   - els projectes es guarden a part.
7. **Presentació:** materials i mapes d'anàlisi (curvatura, zebra). Per defecte: fons blanc, material blanc mat, ombres suaus, estil minimalista.
8. **Fabricació:** indicar el procés (p. ex. injecció amb línia de partició, direcció de desmotllament i angle). L'app avisa i ajuda a modificar la textura perquè es pugui fabricar. **Mai bloqueja.**
9. **Sortida en Parasolid (`.x_t`)**, decidit després del SP-6, per etapes: primer la superfície texturada → després el sòlid texturat → més endavant totes les peces en un sol STEP.

## 2. Arquitectura proposada [O]

```
Navegador (localhost)
  visor 3D · sliders · catàleg · xat · captures i fitxers
        │  HTTP + WebSocket
Backend local (Python)
  ├─ és l'únic que parla amb Rhino: Rhino 9 sense interfície, la mateixa sessió sempre activa
  ├─ executa les definicions de Grasshopper de les textures
  ├─ base de dades: fitxers JSON + índex de cerca (catàleg a Drive; projectes a part)
  └─ servidor MCP amb les accions de l'app
        │
Claude Code local (compte de Pau)
  llegeix captures i fitxers, escriu codi i crida les accions de l'app
```

**Per què és la més ràpida (resposta a G1):**
- La interfície no és el coll d'ampolla; Rhino sí.
- Ara una textura tarda entre 1,7 i 3 s a recalcular-se ([H] textura 03).
- Per anar ràpid cal:
  - (a) mantenir Rhino sempre obert i amb la definició carregada, no arrencar-lo a cada petició;
  - (b) una previsualització lleugera mentre es mou el slider, i el càlcul complet en deixar-lo anar;
  - (c) enviar al navegador només la malla que ha canviat.
- Hi ha tres maneres de connectar el backend amb Rhino. El SP-8 les mesura i es tria la més ràpida:
  - Rhino.Inside dins del mateix procés de Python [?];
  - Rhino 9 obert, connectat pel mateix pont que fem servir ara [H funciona];
  - Rhino.Compute en local [?].

**Per què el backend té el seu propi MCP:**
- Claude no toca Rhino directament, sinó que crida les accions de l'app (`canviar_parametre`, `aplicar`, `desar_variant`, `cercar_solucions`…).
- Això assegura que tot queda registrat a la base de dades.
- Quan arribin més usuaris, només cal canviar Claude Code per l'API, sense tocar les accions.

## 3. Fase 0 · Fonaments

| Tasca | Criteri d'acceptació |
|---|---|
| Còpia del repositori a **GitHub privat** (G5): et guiaré pas a pas (compte, `gh auth login`, `git remote add`, `git push`) | `git push` funciona; les etiquetes `2026-11-14_NN` hi són |
| Licencia de **Rhino 9** (G3: ara és d'avaluació) | Rhino 9 llicenciat abans que caduqui l'avaluació [?] |
| Estructura de carpetes de l'app dins d'`APP/` i el **format comú del catàleg** (esquema JSON: textura, solució, projecte, estats, etiquetes E1) | Esquema escrit i validat amb un test; les textures 01–03 descrites amb aquest esquema **sense tocar els seus fitxers** |

## 4. Fase 1 · Spikes (decideixen què és possible)

Ordre: **SP-5 i SP-6 primer**, perquè la sortida a SolidWorks és el risc més gran. Després SP-7, SP-8 i SP-9.

| Spike | Què es prova | Criteri |
|---|---|---|
| **SP-5 · Entrada des de SolidWorks** | Un model vostre exportat de SolidWorks 2020 en **STEP i en Parasolid** (`.x_t`). Es comprova que es conserven les **particions** de cara i els **colors**, i que les unitats són mm | Rhino llegeix les cares partides i els colors dels dos formats [S STEP / ? x_t] |
| **SP-6 · Sortida cap a SolidWorks** | Una textura (la 02, com a solució nova, sense tocar la lliurada) sobre una superfície, sortint com a **superfície NURBS** → STEP → s'obre a **SolidWorks 2020**. Dos camins: (a) relleu NURBS exacte (els fons polinòmics es poden representar en NURBS [S]); (b) ajustar una NURBS a la malla | El fitxer s'obre a SW2020 sense errors; desviació respecte a la malla ≤ 0,01 mm; es mesuren el pes i el temps i aviso si són massa grans (D4) |
| **SP-7 · Mapeig UV amb mínima distorsió** | Comparar `uv_arc` (SP-1) amb un desplegament que minimitza la distorsió (LSCM/ARAP [?]) i amb corbes guia, sobre superfícies orgàniques. Visualitzar-ho amb una quadrícula de prova sobre la superfície | Menys distorsió que `uv_arc` a la superfície A25 del SP-1 (16,2 % a 100 mm), mostrat amb el mapa de distorsió |
| **SP-8 · Velocitat** | Les tres connexions amb Rhino (vegeu §2) amb la textura 03 | Temps des que es mou un slider fins que es veu el resultat al navegador; es tria la connexió més ràpida |
| **SP-9 · Xat local** | El backend parla amb Claude Code sense obrir el terminal, amb les accions MCP de l'app. S'hi envien una captura i un STEP | Claude rep la imatge i el fitxer i crida una acció que canvia un slider. **Abans, comprovar les condicions d'ús** d'aquest mode amb el compte personal [?] |

**Estat (2026-11-14):** SP-5 fet ([informe](recerca/sp5/informe.md)). El STEP conserva les particions, el color de cara i els mm. Rhino 9 **no importa** `.x_t`, però sí que l'**exporta**: al SP-6 es prova també com a format de sortida.
SP-6, primera part, feta ([informe](recerca/sp6/informe.md)). Amb el camí (b), una superfície per punts, el sòlid queda tancat i vàlid, però el fitxer pesa massa: 25 MB en STEP i 18,5 MB en `.x_t` per a una zona de 33 × 86 mm, amb una desviació màxima de 0,015 mm. **Decisió (Pau, 2026-11-14): la sortida és Parasolid (`.x_t`)**: SW2020 l'obre, mentre que el STEP no l'acaba d'importar. El format queda resolt. El que falta és la **qualitat de la geometria**: la superfície del camí (b) no és estètica (falques al contorn, ondulacions). El camí (a), NURBS net per quadrat amb el tauler ajustat a la zona, passa a la fase 2 com a manera estàndard de generar la sortida.

SP-7 fet ([informe](recerca/sp7/informe.md)): **ARAP aplicat només a la zona a texturar** baixa la distorsió d'àrea a A25 / 100 mm del 16,2 % (uv_arc) al **5,0 %**, i a A40 del 32 % al 12 %. Serà el mètode per defecte per a superfícies orgàniques; per a plans i cilindres es fa servir el desplegament exacte.

SP-8, parte 1 ([informe](recerca/sp8/informe.md)): enviar un script a Rhino con RhinoCode tarda ~0,5 s, pero **lo que limita es el cálculo**: cada cambio de slider de la textura 03 tarda ~3 s. Hacen falta definiciones pensadas para la app y una vista previa ligera. Parte 2: **ARAP con scipy tarda 1,1 s**. **Rhino.Inside no funciona** con Rhino 9 en este equipo, así que se propone un servidor pequeño dentro de Rhino. **Decisión: vista previa instantánea en el visor** (la fórmula se escribe una vez y una prueba comprueba que las dos versiones coinciden).
SP-8, parte 3: **servidor dentro de Rhino**: el transporte tarda ~8 ms (ping de 5–10 ms) y cada cambio de slider 3,1 s. Se ha corregido un doble cálculo que lo hacía tardar 6 s. Sustituye a Rhino.Inside.
SP-9, parte 2: **el ciclo del chat funciona** con Claude Code local y acciones MCP de la app (captura → Claude → `canviar_parametre`). Tarda 26 s (15 s de arranque) y tiene un coste estimado de 0,42 USD por mensaje (no se cobra con la suscripción). Con la API, antes hay que reducir el contexto.
**Fase 0: catálogo hecho** ([APP/cataleg](cataleg/README.md)): esquema, fichas de las texturas 01–04, soluciones S001–S004 y comprobación automática.
SP-9, parte 1 ([informe](recerca/sp9/informe.md)): Anthropic no permite ofrecer el login de claude.ai a otras personas en productos propios; con más usuarios hará falta **clave de API**. Recomendación: diseñar el chat con clave de API desde el principio y probar con la sesión local durante la beta.

Porta 1: un informe per spike a `APP/recerca/spN/informe.md` i la decisió de què entra a l'MVP.

## 5. Fase 2 · Catàleg i eines dins de Rhino (encara sense app)

Tot el que farà l'app, primer com a eines que funcionen dins de Rhino amb Claude Code com a xat:

1. **Importar i analitzar:** STEP o `.x_t` → llistar les cares (tipus, mida, corbatura, color o partició) → triar la superfície.
2. **Mapeig UV assistit (C1, punt clau):**
   - mètodes: `uv_arc`, planar, cilíndric, corba guia i desplegament;
   - quadrícula de prova i mapa de distorsió;
   - Claude proposa el millor mètode per a cada geometria.
   - Si la distorsió és alta, **s'informa i es busca la solució entre tots dos**, sense bloquejar res (C3).
3. **Controls de la textura:**
   - esvaïment opcional i controlable (C2), també a partir d'**imatges de suport** (màscara en grisos);
   - **relleu amb signe** (C4): una zona cap enfora amb transició suau cap endins, definida per una màscara o per corbes.
4. **Forats (B4):** de moment es treballa la superfície sense buidats; els forats es fan després a SolidWorks.
5. **Exportar la superfície texturada en STEP** (el que hagi resultat del SP-6).
6. **Presentació:** materials (plàstics, metall, fusta, tela) i mapes de curvatura i zebra, capturats amb l'estil per defecte (H2).
7. **Eines del mode B:** les d'anàlisi de la referència (retall, CLAHE, perfils de llum), d'ombrejat del camp d'alçades i de comparació, passades a mòduls reutilitzables.
8. **Registrar cada aplicació** com a solució al catàleg, en estat *pendent d'aprovació*.

Criteris de la fase:
- Una textura del catàleg aplicada de cap a cap sobre una superfície d'un STEP vostre, amb el STEP de sortida obert a SW2020.
- Una textura nova creada amb les eines del mode B.
- Tot registrat al catàleg.

## 6. Fase 3 · L'app local

| Peça | Criteri d'acceptació |
|---|---|
| Backend + connexió amb Rhino (la guanyadora del SP-8) | Rhino s'engega una sola vegada; els canvis de slider actualitzen la previsualització sense recarregar la definició |
| Visor 3D al navegador | Materials, curvatura, zebra; estil per defecte: blanc mat, fons blanc, ombres suaus |
| Panell de sliders generat des de l'esquema de la textura | Cada slider amb nom, unitat, rang i explicació (com al PLAN principal) |
| Xat (SP-9) amb captures i fitxers | Una petició del xat canvia la textura i queda registrada |
| Catàleg | Cerca per etiquetes (E1); estats *pendent* / *aprovada* / *validada físicament* amb la casella d'impressió 3D (F1); l'aprovació la fa només Pau (E2) |
| Projectes a part (A3, E3) | Els projectes no es barregen amb el catàleg compartit |
| Idiomes (G2) | Tots els textos en un fitxer `ca.json`; afegir un idioma = afegir un fitxer. Fer-ho des del principi costa poc [O] |

## 7. Fase 4 · Fabricació i sòlid

1. **Perfil de fabricació per projecte (D1):** per a injecció, línia de partició, pla o direcció de desmotllament i angle de desmotllament.
2. **Comprovació sobre la textura:**
   - anàlisi d'angle de desmotllament i de contrasortides;
   - radi i profunditat mínims;
   - mapa de colors de les zones que no compleixen.
3. **Ajuda per corregir (D2):** l'app proposa i aplica canvis a la textura (inclinar parets, suavitzar, reduir la profunditat en zones concretes) perquè es pugui fabricar. Mai bloqueja.
4. **Sortida en sòlid:** la peça sencera amb la textura incorporada (booleanes, no provades [H]).
5. **Després, sortida amb diverses peces:** totes les parts en un sol STEP.

## 8. Fase 5 · Més endavant (fora d'aquest pla)

- Més usuaris: servidor, API d'Anthropic amb clau, comptes.
- Renders d'alta qualitat amb direcció d'art.
- Textures que travessen diverses cares (costures).

## 9. Riscos

| Risc | Com el tractem |
|---|---|
| Sortida NURBS per a SolidWorks (la 02 i la 03 són malles) | SP-6, el primer de tots |
| Distorsió en superfícies orgàniques (vols el mínim possible) | SP-7; sempre informar, mai bloquejar |
| SolidWorks 2020 és una versió antiga: pot tenir problemes amb STEP grans o complexos [S] | Provar sempre amb SW2020 al SP-6 |
| La llicència d'avaluació de Rhino pot caducar a mig projecte [S] | Comprar Rhino 9 a la fase 0 |
| Condicions d'ús de Claude Code com a motor del xat de l'app [?] | Verificar-ho abans del SP-9; si no es pot, fer servir l'API amb clau |
| Repositori a Google Drive: el `.git` es pot corrompre amb la sincronització | Còpia a GitHub privat a la fase 0 |
| Operacions booleanes amb centenars de relleus (sòlid) | Fase 4; es mesuren abans de prometre-les |

## 10. Preguntes noves (respostes de Pau, 2026-11-14)

1. **Zones cap enfora / cap endins (C4):** es defineixen **amb una imatge** (màscara). → Fase 2, punt 3.
2. **Imatges de suport per a l'esvaïment (C2):** **totes les possibilitats**: esbossos, màscares en blanc i negre, captures anotades… L'app ha d'acceptar-les totes; Claude les interpreta i, quan calgui, les converteix en una màscara.
3. **Validació física (F1):** **SLA i FDM**. A la casella de validació s'indica la tecnologia. [S] La profunditat i el detall mínims que es veuen són diferents per a cada tecnologia (FDM molt més gruixut).
4. **Model de prova:** `APP/Proves/test 01.STEP` (29 KB) i `APP/Proves/test 01.x_t` (7 KB). [?] Falta confirmar que la superfície a texturar està pintada d'un color.
5. **GitHub:** Pau ja té compte.

## 11. Primer pas proposat

Fase 0 (GitHub + esquema del catàleg) i, en paral·lel, **SP-5 + SP-6** amb el model de prova de la pregunta 4.
