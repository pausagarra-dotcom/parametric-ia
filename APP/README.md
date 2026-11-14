# APP · Aplicació de textures sobre models STEP

Subprojecte d'**IA_New_shot**. Tota la documentació de l'aplicació viu en aquesta carpeta.
Estat: **idea definida, res implementat** (2026-11-14).
Pla: [PLAN.md](PLAN.md) · Respostes de Pau a les preguntes prèvies: [PREGUNTES.md](PREGUNTES.md) (on hi hagi contradicció, manen les respostes i el pla).
Llegenda: **[H]** fet verificat · **[S]** suposició · **[O]** opinió · **[?]** a verificar.

## Què ha de fer
L'app té **dos modes**, tots dos dins de l'app:

**A · Aplicar una textura del catàleg.** Carregar un model **STEP** (fet a SolidWorks), triar-ne les cares, aplicar-hi una textura ja feta, ajustar-la (sliders i xat) i exportar el model real per fabricar. Cada aplicació nova es guarda perquè un problema ja resolt no s'hagi de tornar a programar.

**B · Crear una textura nova** a partir d'una referència, amb el mateix procés que es va seguir per a les textures 01–03. La referència pot ser una **foto** o un **tros de geometria modelat a SolidWorks** (p. ex. una cel·la del patró), que és més precís que una foto perquè les mides ja hi són.
1. Pujar la referència i posar nom a la textura. L'app crea `textures/NN_nom/` amb el número següent.
2. Analitzar la referència: retallar, ampliar i realçar el contrast; identificar el patró (p. ex. tauler d'escacs o totes les cel·les); mesurar perfils de llum per deduir-ne la forma.
3. Fer un prototip del camp d'alçades i ombrejar-lo amb la llum de la referència per comparar-los.
4. Passar-lo a una definició de Grasshopper amb sliders anomenats.
5. Fer captures a Rhino, comparar-les amb la referència i corregir amb el xat fins que la textura s'hi assembli.
6. Lliurar: README, captures, scripts i `.gh` a la carpeta de la textura. A partir d'aquí la textura queda congelada i passa al catàleg.

En aquest mode el xat és imprescindible: Claude escriu i executa codi, i l'usuari valida a ull contra la referència.

## Què ha d'admetre el xat
- **Text**: les peticions de canvi.
- **Captures** (imatges): per assenyalar què cal canviar, com es feia fins ara (p. ex. les línies blaves de les bandes de llum).
- **Fitxers de SolidWorks**: un STEP (o la peça de SolidWorks [?]) per entendre un canvi o per **replicar un tros de geometria modelat**: l'app en mesura el perfil i les mides i en fa una textura paramètrica (mode B) o el repeteix directament sobre la superfície.

## Presentació del model
Per veure bé les superfícies, el visor ha de poder mostrar el model:
- **Amb diferents materials**: plàstic mat, plàstic brillant, metall, goma… amb il·luminació d'entorn.
- **Amb mapes d'anàlisi, com SolidWorks**: mapa de curvatura en colors, zebra (franges de reflex) i mapa d'entorn.

[O] A més de presentar, el mapa de curvatura i la zebra serveixen per **controlar la qualitat**: mostren els salts de curvatura que fins ara es veien com a bandes de llum (les línies blaves de la textura 02).

Com es fa:
- **Fases 1–2** (dins de Rhino): fer servir les eines natives de Rhino. [S] `_CurvatureAnalysis`, `_Zebra`, `_EMap` i els materials de render, capturats per script.
- **Fase 3** (a l'app): Rhino calcula la curvatura sobre la NURBS real i l'envia al visor com a colors. El visor només pinta els materials i la zebra. No és un segon motor de càlcul: la geometria continua sortint de Rhino (decisió 4).

## Decisions preses
1. **Les textures lliurades no es modifiquen mai.** El que creix és el coneixement de *com s'aplica una textura a cada tipus de geometria* (cilindre, placa amb cantell arrodonit, NURBS orgànica…).
2. **Entrada: només STEP**, de moment. L'equip modela a SolidWorks.
3. **Tota la feina es fa a l'aplicació.** Rhino (i les definicions de Grasshopper) treballa en segon pla com a motor de càlcul. L'usuari no obre Rhino ni Grasshopper.
4. **Un sol motor (Rhino)** per a la previsualització i per al model final. No hi haurà un visor web separat amb un càlcul propi.
5. **El resultat final ha de ser geometria real per fabricar**, no només una previsualització.
6. **Xat integrat a l'aplicació.** De moment només hi ha un usuari (Pau). Més endavant n'hi haurà més.
7. **L'app també serveix per crear textures noves** (mode B), no només per aplicar les existents. Textura nova = carpeta nova; mai es modifica una de lliurada.
8. **Presentació amb materials i mapes d'anàlisi** (curvatura, zebra), com SolidWorks.

## Base de dades (tres nivells)
| Nivell | Què guarda |
|---|---|
| Textures (no es toquen) | fórmula, sliders, referència → `../textures/NN_nom/` |
| Solucions d'aplicació (és el que creix) | tipus de geometria, mètode de mapeig, codi reutilitzable, problemes i solucions, resultats (distorsió, temps, captures) |
| Projectes | STEP, cares, textura, variant de sliders, solució aplicada, fitxer de sortida |

L'esquema concret encara no està escrit (pendent de l'OK).

## Fases
1. Base de dades al repositori + script que analitzi les cares d'un STEP + **procés de creació escrit com a passos repetibles** (eines d'anàlisi de la referència i de comparació reutilitzables, no només fetes a mida per a cada textura).
2. Eina dins de Rhino: STEP → anàlisi → recomanació → aplicar → exportar.
3. Aplicació amb Rhino en segon pla (Rhino.Compute [?]) + visor 3D + xat integrat, amb els dos modes (aplicar i crear).

## Abast i decisions sobre els riscos (2026-11-14)
- **Una sola superfície, sense costures.** De moment les textures s'apliquen sobre una superfície (orgànica o no). Les textures que travessen diverses cares (cara + arrodoniments) queden per més endavant.
- **Importar STEP de SolidWorks**: Pau confirma que Rhino ho fa sense problemes.
- **Sortida: un STEP** que s'obri a SolidWorks.
- **Xat**: començar amb **Claude Code local** amb el compte de Pau i passar a l'**API amb clau pròpia** quan hi hagi més usuaris. Les accions del xat (`canviar_parametre`, `desar_variant`, `aplicar`, `cercar_solucions`) seran les mateixes amb tots dos motors.
- **Opció local en un altre ordinador**: cal Claude Code amb la sessió iniciada, Rhino 9 amb llicència, el connector de Rhino i l'entorn de Python. La base de dades se sincronitza per Drive. No s'ha de treballar a dos ordinadors alhora.

## Riscos i preguntes obertes
- **[H] Risc principal: les textures 02 i 03 surten com a malla**, i un STEP per obrir a SolidWorks necessita un **sòlid NURBS**. Cal un spike que resolgui el pas malla → sòlid NURBS. Camins a provar:
  - (a) Generar els relleus directament com a NURBS. El SP-4 ja ho va fer amb 625 contorns sense cap error. [S] Els fons polinòmics de la 02 i la 03 es poden representar exactament com a superfícies NURBS.
  - (b) Ajustar una sola superfície NURBS per la malla desplaçada.
  
  [?] En tots dos casos falta saber el pes del STEP i si SolidWorks l'obre amb fluïdesa.
- [?] Llicència i desplegament de Rhino.Compute en un servidor.
- [?] Llicència de Rhino: Cloud Zoo (un ordinador alhora) o per màquina.
- [?] Condicions d'ús de l'opció local del xat.
- [?] Llegir fitxers natius de SolidWorks (`.SLDPRT`) des de Rhino, o fer-ho amb el connector de SolidWorks de Claude Code. Mentrestant, la via segura és exportar a STEP.

## Carpetes
- `Altres Patterns/` — imatges de referència per a textures futures.
