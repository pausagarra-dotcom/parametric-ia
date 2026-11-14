# SP-4 — Relieve vía A, por contornos (informe)

Fecha: 2026-11-11. Marcas: [H] medido en esta sesión · [S] suposición · [?] sin verificar.
Código: `sp4_relief.py` (dentro de Rhino con `run_python`; reutiliza `uv_arc` del SP-1). Datos: `sp4_results_a.json`, `sp4_results_b.json`. Geometría de la prueba grande: `sp4_625_bosses.3dm` (22,8 MB).

## Qué se probó [H]

Superficie orgánica A25 del SP-1 (NURBS 200×200 mm, relieve 25 mm), ventana de patrón de 180 mm con una rejilla k×k de círculos (radio = 0,3·paso), profundidad 1,5 mm.

Pipeline por contorno: círculo en mm → puntos (u,v) por longitud de arco → curva interpolada cerrada en el plano UV → `Surface.Pushup` (curva exacta sobre la superficie) → parche local (`Surface.Trim` alrededor del contorno) → `Brep.Split` con la curva → cara interior → `Brep.CreateFromOffsetFace` (sólido, un lado).

## Resultados [H]

| Caso | Contornos | Correctos | Válidos / sólidos | Tiempo total | Medio por contorno |
|---|---|---|---|---|---|
| Relieve, tol 0,01 | 9 | 9 | 9 / 9 | 2 s | 167 ms |
| Relieve, tol 0,01 | 100 | 100 | 100 / 100 | 14,5 s | 111 ms |
| Relieve, tol 0,01 | 289 | 289 | 289 / 289 | 36,9 s | 97 ms |
| Relieve, tol 0,01 | **625** | **625** | **625 / 625** | **70,4 s** | 87 ms |
| Grabado (profundidad −1,5), tol 0,01 | 100 | 100 | 100 / 100 | 14,3 s | 109 ms |
| Relieve, tol 0,001 | 100 | 100 | 100 / 100 | 21,8 s | 169 ms |

- Cero fallos en todos los casos. El coste crece de forma lineal (~0,1 s por contorno); tolerancia 0,001 cuesta ~50 % más que 0,01. Los tiempos son informativos (sin cronómetro, acordado).
- Dirección: con profundidad +1,5 el centroide del sólido queda a +0,70 mm de la superficie a lo largo de la normal; con −1,5 queda a −0,80 mm. Es decir, signo positivo = relieve (hacia la normal) y negativo = grabado.
- Volumen total medido 13 255 mm³ frente a ~13 741 mm³ de la estimación plana (−3,5 %): coherente con la distorsión de área del mapeo en esta superficie (SP-1), no se ha investigado más.

## Hechos de API aprendidos [H]

- `CreateInterpolatedCurve` con `ChordPeriodic` exige repetir el primer punto al final; sin eso la curva queda abierta.
- `Curve.PullToBrepFace` devolvió curvas **abiertas** aquí; `Surface.Pushup` de la curva UV es lo que funciona.
- `Brep.Split` debe recibir un `System.Collections.Generic.List[Curve]` tipado (una lista de Python con `NurbsCurve` falla en la conversión).
- Hacer el `Split` sobre un **parche local** y no sobre la cara completa mantiene el coste constante por contorno.
- `Brep.CreateFromOffsetFace(cara, d, tol, bothSides=False, createSolid=True)` da sólidos NURBS válidos y cerrados.

## Veredicto frente al criterio

Criterio: *geometría generada sin errores y en menos de 3 min.* El tiempo se acordó sin umbral. **Sin errores: cumplido** (625/625). Como referencia, 625 contornos tardaron 70 s en este equipo, por debajo de los 3 min que había en el brief. El plan de repliegue de SP-4 (curvas sin relieve real) **no se activa**.

## Límites del spike (importantes)

- [S] Solo círculos de 24 puntos: formas simples, convexas y sin agujeros. Los contornos de una imagen real (vectorizados, irregulares, con muchos puntos, con huecos o que se tocan) **no están probados** y son el mayor riesgo pendiente.
- Los relieves son sólidos sueltos, **no se unieron con una base** (la superficie sigue siendo una cara abierta, sin espesor). Las booleanas con cientos de sólidos no se midieron.
- No se probó la superficie A40, caras recortadas, costuras ni contornos que cruzan el borde del parche.
- No se probó la vía B (mapa de alturas / malla).
- La captura del viewport se tomó, pero la escena contiene geometría previa de otros spikes y no la usé como evidencia visual.
- El código es de spike, sin pruebas automáticas.
