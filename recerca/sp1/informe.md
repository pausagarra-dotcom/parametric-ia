# SP-1 — Distorsión del mapeo (informe)

Fecha: 2026-11-11. Marcas: [H] medido en esta sesión · [S] suposición · [?] sin verificar.
Código: `sp1_mapping.py` (se ejecuta dentro de Rhino con `run_python`). Datos: `sp1_results.json`, `sp1_window_sweep.json`.

## Método de medida [H]

Ventana de patrón de W×W mm, rejilla de 21×21 puntos; en cada punto se mapean (x,y), (x+h,y), (x,y+h) con h = 0,25 mm y se calcula: escala en X, escala en Y, ángulo entre ejes y área. Distorsión = desviación respecto a 0: **área** |A−1|, **longitud** máx(|sx−1|,|sy−1|), **ángulo** |θ−90°|/90°. Se informa el máximo. Umbral del brief: 15 %.

Métodos probados: `uv_dom` (UV normalizado por el dominio), `uv_local` (UV con la velocidad en el centro), `uv_arc` (UV con tabla de longitud de arco a lo largo de las isocurvas centrales), `planar` (proyección ortogonal a la normal en el centro), `cyl` (proyección cilíndrica, solo si la cara es un cilindro) y `sporph` (`SporphSpaceMorph` plano → subsuperficie).

Superficies: cilindro r = 40 (ventana 60 mm), plano 100×100 (60 mm), y una superficie NURBS de 200×200 mm con malla de control 7×7 y relieve z = A·sin·cos, con A = 10, 25, 40 mm (ventana 100 mm).

## Resultados (distorsión máxima de área / longitud / ángulo) [H]

| Superficie | uv_dom | uv_local | **uv_arc** | planar | cyl | sporph |
|---|---|---|---|---|---|---|
| Cilindro r40 | 0,1 % | 0 % | **0 %** | 50 % | **0 %** | 0 % |
| Plano | 0 % | 0 % | **0 %** | 0 % | n/a | 0 % |
| Orgánica A10 | 56 % | 215 % | **3,1 %** | 6,0 % | n/a | 72 % |
| Orgánica A25 | 57 % | 178 % | **16,2 %** | 51 % | n/a | 65 % |
| Orgánica A40 | 61 % | 136 % | **32,2 %** | 425 % | n/a | 56 % |

Barrido de ventana con `uv_arc` (área máx.): A25 → 40 mm 6,5 % · 60 mm 10,9 % · 80 mm 14,5 % · 100 mm 16,2 %; A40 → 40 mm 12,8 % · 60 mm 21,4 % · 80 mm 28,4 % · 100 mm 32,2 %. Cobertura 100 % en todos los casos.

## Hallazgos

1. [H] **El UV "ingenuo" falla en NURBS reales aunque la superficie sea casi plana.** La parametrización de una NURBS no es proporcional a la longitud de arco (aquí la velocidad en el centro era ~0,66 de la media). Normalizar por el dominio da 56 % de error en una superficie casi plana. En el cilindro funciona solo porque su parametrización es por arco. Consecuencia: la "escala física en mm" exige remuestrear por longitud de arco; no basta con pasar de mm a UV con un factor.
2. [H] **El método UV con tabla de longitud de arco (`uv_arc`) es el mejor general**: exacto en cilindro y plano, 3 % en orgánica suave, 16 % en orgánica media.
3. [H] **Proyección planar** solo sirve en superficies casi planas (6 % en A10); empeora muy rápido con la pendiente (425 % en A40 por pliegues).
4. [H] **Proyección cilíndrica** exacta en cilindros (0 %), tal como se esperaba.
5. [H] **Sporph** funciona (`SporphSpaceMorph(Surface, Surface)` se construye y mapea puntos) pero equivale a un UV lineal en la subsuperficie, así que no corrige la parametrización: peor que `uv_arc`. No aporta ventaja sobre `uv_arc` en este montaje.
6. [H] El error de ángulo (≈4 % en A25, ≈10 % en A40) no se corrige con el remuestreo: viene de la curvatura. En superficies de doble curvatura ninguna aplicación puede conservar a la vez distancias y ángulos; solo se reparte el error.

## Veredicto frente al criterio

Criterio: *distorsión máxima < 15 % en la superficie orgánica con al menos un método.*

- **Cumplido** en la orgánica suave (A10: 3,1 % con `uv_arc`) y en la orgánica media con ventana de ≤ 80 mm (A25: 14,5 %).
- **No cumplido** en A25 con ventana de 100 mm (16,2 %) ni en A40 salvo ventanas ≤ 40 mm (12,8 %).
- El criterio depende de qué se entienda por "orgánica". [?] El brief no lo define; mi superficie sinusoidal es una elección mía y no representa necesariamente tus modelos.

**Conclusión provisional:** SP-1 pasa para superficies suavemente curvadas; para curvatura mayor, la distorsión crece con el tamaño de la ventana y hay que aceptar un límite (ventana pequeña o repetir por zonas) o un mapeo por optimización (LSCM/ARAP, fuera de lo probado). El plan de repliegue (MVP solo planas y cilíndricas) **no** se activa por ahora, pero el MVP debería declarar el rango admisible: curvatura/pendiente máxima y tamaño de ventana.

## Límites de este spike

- [S] Una sola familia de superficies orgánicas (senoidal) y un solo patrón de ventana cuadrada centrada.
- No se probaron costuras, caras recortadas ni la orientación de la normal.
- No se hizo comprobación visual del patrón mapeado ni se guardaron los `.3dm` de los casos en `cases/` todavía.
- El código es de spike, sin pruebas automáticas; pasará a M3 con pruebas en la fase 2.
- Los métodos probados mapean puntos; la aplicación a curvas/contornos (vía A) y a la malla (vía B) se mide en SP-4.
