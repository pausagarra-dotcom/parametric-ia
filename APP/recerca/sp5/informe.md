# SP-5 · Entrada des de SolidWorks (informe)

Data: 2026-11-14. Llegenda: [H] mesurat en aquesta sessió · [S] suposició · [?] a verificar.
Fitxers: `APP/Proves/test 01.STEP` (29 KB) i `APP/Proves/test 01.x_t` (7 KB, capçalera: *Parasolid 31.1 · SOLIDWORKS 2020*).
Mètode: importació en un document de Rhino 9 sense interfície (`RhinoDoc.CreateHeadless` + `Import`) i en una segona instància de Rhino. El document de treball de Pau no s'ha tocat.

## Resultats

### STEP → Rhino 9 [H]
- Importació correcta. Unitats: **mil·límetres**; tolerància del document: 0,001 mm.
- Un sòlid tancat i vàlid (`IsSolid`, `IsValid`). Nom de l'objecte: `Eliminar cara1`, el nom de l'operació de SolidWorks.
- Caixa contenidora: cilindre de r = 25 mm i 117 mm de llargada, al llarg de l'eix Y.
- **5 cares, i es conserven les particions:**

| Cara | Tipus | Àrea (mm²) | Color | Interpretació |
|---|---|---|---|---|
| 0 | cilindre r 25 | 7 932,34 | — | lateral (≈ 50,5 mm) |
| 1 | cilindre r 25 | 7 932,34 | — | lateral (≈ 50,5 mm) |
| **2** | cilindre r 25 | **2 513,64** | **blau (2, 61, 210)** | **franja partida de 16 mm: zona a texturar** |
| 3 | pla | 1 963,50 | — | tapa |
| 4 | pla | 1 963,50 | — | tapa |

- Comprovació: 2 × 7 932,34 + 2 513,64 = 18 378,3 mm², que coincideix amb l'àrea lateral 2π·25·117 = 18 378,9 mm².
- **El color de cara arriba a Rhino** (`BrepFace.PerFaceColor`). Per tant, l'app pot trobar automàticament la cara a texturar pel color (decisió B1).
- Les cares són de revolució o planes, i Rhino reconeix el cilindre exacte (r = 25,00). Això permet triar automàticament el mètode de mapeig cilíndric, que en el SP-1 va donar 0 % de distorsió.

### Parasolid (`.x_t`) → Rhino 9 [H]
- **Rhino 9 no importa Parasolid.**
  - La importació falla en un document sense interfície.
  - En una instància normal, l'ordre `_-Import` es queda bloquejada.
  - La llista de connectors instal·lats té **«Parasolid Export»**, però cap «Parasolid Import».
- En canvi, hi ha **«Solidworks Import»**: [S] Rhino pot llegir directament fitxers natius de SolidWorks (`.SLDPRT`). Falta provar si conserva els colors i les particions.

## Conclusions
1. **El STEP és suficient com a format d'entrada:** conserva les particions, el color de cara i les unitats. Respon a la preocupació de la pregunta B1 (mantenir particions).
2. **El Parasolid no serveix com a entrada amb Rhino 9.** Alternativa: el `.SLDPRT` natiu, si es vol estalviar l'exportació (cal provar-ho).
3. **Troballa per a la sortida:** Rhino 9 **exporta** Parasolid. Parasolid és el nucli geomètric de SolidWorks, així que [S] un `.x_t` pot obrir-se a SolidWorks 2020 amb menys problemes que un STEP. Al SP-6 es provaran tots dos (STEP i `.x_t`) com a sortida.
4. **Detecció de la cara a texturar:** pel color de cara, amb la possibilitat de triar-la amb un clic si no n'hi ha cap de pintada.

## Pendent
- [?] Provar un `.SLDPRT` (colors, particions, unitats).
- [?] Provar una superfície orgànica (NURBS lliure) exportada de SolidWorks, no només un cilindre.
