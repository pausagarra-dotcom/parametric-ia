# Preguntes abans del pla

Data: 2026-11-14. Responeu a sota de cada pregunta (`Resposta:`), aquí o al xat.
Cada pregunta porta **la meva proposta**: si no hi responeu, el pla farà servir aquest valor.
★ = pregunta que decideix l'arquitectura. Responeu-les primer.

---

## A. Usuaris i ús

**A1 ★ Qui farà servir l'app quan arribi la fase 3?** Tu, l'equip de disseny, clients…?
Per què: determina si cal tenir comptes i permisos, i com de simple ha de ser la interfície.
Proposta: tu i l'equip de disseny; clients no.
Resposta:de moment l'únic que farà servir l'apliació seré jo mateix

**A2. Quantes textures i projectes preveieu a l'any?**
Per què: dimensiona la base de dades i el cercador.
Proposta: unes 20 textures i uns 50 projectes l'any.
Resposta:l'ideal és fer-ne tant com poguem, evidentment si treballem 20 textures bàsiques ammb diferents maneres d'aplicacions ja será un èxit.

**A3 ★ Els models de clients són confidencials?**
Per què: amb l'opció API, els fitxers passarien per Anthropic, i ara ja passen per Google Drive. Si hi ha acords de confidencialitat, potser cal guardar els projectes en un altre lloc.
Proposta: es tracten com a confidencials; els projectes de client es guarden fora de la carpeta compartida del catàleg.
Resposta:correcte, de moment no hi ha cap client. estem a una fase beta. Quan tinguem l'aplicació avançada ja canviarem les necessitats.

## B. Entrada (STEP)

**B1 ★ Com s'indica on va la textura?**
Per què: un STEP de SolidWorks porta moltes cares, i triar-ne una malament és un error típic.
Proposta: la cara es pinta d'un color concret a SolidWorks (p. ex. vermell). [S] Rhino el llegeix del STEP. L'app també permetrà triar-la amb un clic.
Resposta:per poder mantenir particions, potser hauria també d'asumir arxius amb format parasolid (.xt )

**B2. Les unitats són sempre mil·límetres?**
Proposta: sí, i l'app avisarà si el STEP ve en una altra unitat.
Resposta:si, està pensada per disseny industrial, per tant la unitat de mesura més comú són els mm.

**B3. Quina mida tenen les peces i la zona texturada?** Per exemple: «carcassa de 150 mm, zona de 80×60 mm».
Per què: el SP-1 va mesurar que, en superfícies molt corbades, la distorsió passa del 15 % a partir de 80 mm. Amb la mida real sabrem si és un problema.
Resposta: la distorsió amb textures orgàniques hauria de ser el menys possible.

**B4. Les superfícies acostumen a estar retallades** (forats, contorns irregulars)?
Per què: les cares retallades encara no s'han provat.
Proposta: sí, és el cas habitual, i ho provem al primer spike.
Resposta: cada projecte és un món, pot ser que a dins de la superficié tingui forats. tot i així, per facilitar la creació de les textures podem deixar les operacions de buidat per després , quan tornem al solid les podrem fer fácilment.

## C. Aplicació de la textura

**C1. Com es decideix la direcció del patró?** Direcció U/V de la cara, una corba guia dibuixada a SolidWorks, un eix…
Proposta: per defecte, la direcció U de la cara, amb un slider de rotació (`ROT`, com ara) i la possibilitat d'afegir una corba guia.
Resposta: Aquest és un punt molt important. Clade ens ha de permetre i facilitar la creaciíó del uv maps o ajudar-nos per trobar la millor solució per l'aplicació de la textura per aconseguir el resultat què volem.

**C2. L'esvaïment cap a la vora es fa sempre** (com a les textures 01–03), o ha de ser opcional?
Proposta: opcional, activat per defecte, amb `FADE_GAP` i `FADE_LEN` com ara.
Resposta: ha de ser opcional,. i hem de poder controlar-ho. Per saber com s'han d'aplicar ens podem ajudar d'imatges de suport per explicar bé com han de ser els fades.

**C3. Què fem quan la distorsió supera el límit?** Només avisar, no deixar exportar, o partir la superfície en zones?
Proposta: avisar i mostrar el mapa de distorsió. El límit seria el 15 %, ajustable.
Resposta: Mai bloquejar, simplement informar i intentar treballar conjuntament per solucionar-ho de la millor manera.

**C4. El relleu va cap enfora, cap endins, o pot anar de totes dues maneres?**
Proposta: totes dues, amb un selector. Per defecte, cap endins (gravat), com la 02 i la 03.
Resposta: pot anar de les dues maneres. Estaria molt bé poder dissentar un mateix amb les dues opcions, una part / zona cap enfora i tenir una transició suau cap a dins.

## D. Fabricació i sortida

**D1 ★ Com es fabriquen les peces?** Injecció amb motlle, mecanitzat, impressió 3D, texturat làser del motlle…
Per què: cada procés té límits diferents (angle de desmoldeig, radi mínim d'eina, profunditat), i l'app els podria comprovar abans d'exportar.
Resposta: Seria un gran què poder marcar el sistema de fabricaciíó de la peça i que ens ajudi a entendre quins limitants té. Exenple: el en cas d'una peça d'injecció de plàstoc podriem marcar la linia de partage de la peça, i també el pla sobre el qual s'aplicarà l'angle de desmoldeig, i quin angle volem. d'aquesta manera poderem modificar la geometria perqè sigui fabricable.

**D2. Hi ha límits de fabricació que l'app hauria de comprovar?** Angle de desmoldeig mínim, radi mínim, profunditat mínima i màxima, gruix de paret…
Proposta: definir-los per projecte; l'app avisa si la textura els incompleix.
Resposta:Correcte, l'aplicació també ens hauria de poder ajudar-ho, exemple, modificar la textura per poder fabricar la geometria.

**D3 ★ Què ha de contenir el STEP de sortida?** La peça sencera amb la textura incorporada (un sol sòlid), o només la superfície texturada per substituir-la a SolidWorks? Ha de mantenir totes les peces en un mateix step.
Per què: la peça sencera implica operacions booleanes amb centenars de relleus, que encara no estan provades.
Proposta: la peça sencera en un sol sòlid; com a alternativa, la superfície sola.
Resposta:podem començar per la superficie amb la textura, després el solid amb la textura i més endavant mantenir les diferents parts de la geometria.

**D4. Quina tolerància i quin pes màxim de STEP accepteu?**
Proposta: tolerància de 0,01 mm (la del SP-4). El pes, a mesurar al spike.
Resposta: l'objectiu és que la gemetria quedi perfecte quan es vulgui fabricar, el pes anirà en funció d'aquesta necessitat. Avisa si consideeres que aques pes es massa gran per treballar.

**D5. Quina versió de SolidWorks feu servir?**
Per què: per provar que el STEP s'obre bé amb la vostra versió.
Resposta: Solidworks 2020

## E. Base de dades

**E1. Amb quines etiquetes voldríeu buscar textures?** Tipus de producte, material, acabat, sensació tàctil, estil, client…
Proposta: tipus de geometria, tipus de producte, material, acabat, estil i projecte.
Resposta:Em smbla bé les categories que proposes.

**E2. Qui decideix que una solució és prou bona per entrar a la base de dades?**
Per què: si hi entra tot, la base de dades s'omple de solucions dolentes.
Proposta: només tu, amb un botó «aprovar».
Resposta: només jo de moment. Les textures que no s'han valida queden etiquetades com pendents d'aprovació.

**E3. Els projectes de client van a la mateixa base de dades que les textures?**
Proposta: no. El catàleg (textures i solucions) és compartit; els projectes es guarden a part (vegeu A3).
Resposta: Correcte, els projectes es guarden a part.

## F. Creació de textures (mode B)

**F1. Quan es dona per acabada una textura?**
Proposta: quan tu la valides a ull contra la referència, com fins ara. L'app guarda la comparació de captures com a prova.
Resposta: l'aprovació final s'ha de fer un cop s'hagi passat al solid i es vegi bé la superfie. Hi hauria d'haver una casella per indicar que també s'ha validat físicament amb una impressió 3d.

**F2. Quines referències de `Altres Patterns/` són prioritàries?**
Per què: poden servir com a primers casos de prova del mode B dins de l'app.
Resposta:De moment és una carpteta amb referències. Jo anirñe dient quina textura treballem per ampliar la base de dades.

**F3. Si la referència és un tros modelat a SolidWorks, en quin format l'exportaríeu?**
Proposta: STEP d'una cel·la o d'un tros del patró, amb les mides reals.
Resposta: Tambñe pot ser un parasolid, format .xt. Les mides no tenen perquè ser reals, poder creixeer i decreixer el patró.

## G. App i entorn

**G1 ★ Aplicació web (al navegador) o d'escriptori?**
Proposta: web local (al teu PC, al navegador). Quan hi hagi més usuaris, la mateixa web passa a un servidor.
Resposta: currecte, de moment l'apliació es en local o al navegador. Amb això m'has d'ajudar per indicar quina opció és la més òprima per tenir l'aplicació més rápida de totes.

**G2. En quin idioma ha d'estar la interfície?** Català, castellà o anglès.
Proposta: català, preparada per afegir-ne d'altres.
Resposta: de moment català. A futur potser haurem de poder indicar quin idioma volem que estigui. Si no costa gens tenir-ho des de l'inici ho podem fer ja. 

**G3. Quin tipus de llicència de Rhino teniu i quantes?** Cloud Zoo o per màquina.
Resposta: de moment estem fent servir la d'avaluació, comprarem la versió 9 de Rhino.

**G4. Mantenim per a l'app la regla de cada commit amb nota a `historial/` i etiqueta?**
Proposta: sí, la mateixa regla.
Resposta:si

**G5. Cal una còpia del repositori fora de Drive?** Per exemple, a GitHub privat.
Per què: ara Drive és l'única còpia. Si es corromp el `.git` per la sincronització, es perd l'historial.
Proposta: sí, un repositori privat.
Resposta:si. m'hauràs d'indicar com fer-ho

## H. Presentació

**H1. Quins materials voleu a la biblioteca?** Els que feu servir habitualment: PC, ABS, TPU, alumini anoditzat…
Resposta:si, la majoria de mateials comuns. Metall , fusta, tela,

**H2. Cal exportar imatges o renders per presentar als clients?**
Proposta: sí, captures en alta resolució amb el material i el fons triats.
Resposta:si, podrem fer renders de gran qualitat més endavant, a futur haurem de fer la direcció d'art dels renders. Començem amb un fons blanc amb un material blanc mate, sombres suaus amb un estil minimalista
