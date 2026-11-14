# PLAN.md — Texturas desde imagen sobre superficies Rhino

Estado: **borrador para aprobación**. Nada implementado, nada instalado, ningún fichero fuera de esta carpeta.
Leyenda: **[H]** hecho verificado · **[S]** suposición · **[O]** opinión · **[?]** no lo sé / a verificar.

## 0. Hechos que ya tengo (y los que no)

- [H] En esta sesión existen herramientas `mcp__rhino__*` (run_python, run_csharp, open_doc, get_viewport_image, g1_*/g2_* para Grasshopper 1 y 2…). El puente Claude Code ↔ Rhino existe como herramienta.
- [H] Primera llamada a `get_context`: se auto-lanzó un "slot" Rhino 9 (`aardvark`) y devolvió `rhino_closed` (el slot se cerró durante la llamada). Quiere decir: Rhino 9 arranca desde el puente, pero **no está demostrado que el bucle funcione con fluidez**. No reintenté para no empezar el SP-0 antes de la aprobación.
- [H] La carpeta no es un repositorio git y vive en Google Drive (`H:\Mi unidad`).
- [?] Capacidades de scripting de Rhino 9 (versión de Python, paquetes de terceros), estabilidad de Flow/Sporph, rendimiento del relieve: sin verificar (ver §5).

## 1. Comprensión del proyecto (10 líneas)

1. Dada una imagen plana y una cara de brep de Rhino, se aplica esa textura sobre la cara, en mm físicos, con relieve o grabado opcional.
2. Cuatro etapas con punto de aprobación: Entrada → Referencia → Mapeo → Ajuste y relieve.
3. Solo la etapa 2 usa interpretación de Claude (vía Claude Code, sin API); el resto es cálculo determinista.
4. Etapa 2 con dos modos en paralelo: *fiel* (OpenCV: periodicidad y celda mínima) y *reinterpretado* (Claude describe un JSON, un generador dibuja).
5. Ambos modos entregan baldosa repetible + periodos X/Y + mapa de alturas (+ contornos).
6. Mapeo con tres métodos (UV, proyección planar/cilíndrica, Flow/Sporph) y mapa de distorsión con umbral 15 %.
7. Relieve por contornos (vía A, NURBS) o por mapa de alturas (vía B, malla).
8. Parámetros nombrados y documentados (nombre, unidad, rango, defecto, explicación); vista previa ligera, cálculo completo al confirmar.
9. Cinco spikes (SP-0…SP-4) validan los riesgos antes del MVP; cada fallo activa un plan de repliegue.
10. MVP: una cara, una imagen plana, primer caso un cilindro; Windows y Rhino 9.

## 2. Ambigüedades y contradicciones del brief

| # | Dónde | Problema | Propuesta |
|---|---|---|---|
| A1 | §1 etapa 1 vs §2 | La etapa 1 admite "imagen de un objeto con la textura aplicada", pero §2 lo sitúa en fase posterior. | MVP = solo imagen plana (como §2). |
| A2 | §8 criterios vs §4 | "<3 min por generación": ¿incluye el paso interpretativo de Claude (interactivo, no medible)? | **Decidido (usuario, 2026-11-11): de momento no hay cronómetro.** El límite de 3 min queda en suspenso; se registran tiempos como dato informativo, sin criterio de éxito/fallo. Reactivable más adelante. |
| A3 | §5.2 | El modo fiel incluye "Claude revisa y ajusta parámetros": ese bucle no es determinista ni testeable automáticamente. | Separar: núcleo OpenCV determinista (testeable con casos de referencia) y revisión de Claude como paso manual documentado. |
| A4 | §5.1 | "La superficie se identifica por su GUID": en Rhino el GUID identifica el objeto (brep), no la cara. **[S]** hace falta GUID + índice de cara (ComponentIndex). | Identificador = (GUID del brep, índice de cara). A verificar en SP-0/1. |
| A5 | §5.3 | "Flow/Sporph": son dos comandos distintos de Rhino (FlowAlongSrf y Sporph). **[S]** | Tratarlo como un método (c) con dos candidatos; verificar cuál existe en RhinoCommon. |
| A6 | §6 SP-2 / SP-3 | Inconsistencia de tamaños: SP-2 usa 10 imágenes pero el criterio habla de "4 de 5"; SP-3 describe 10 patrones y valora "3 de 5". | Fijar denominadores: se miden las 10, y el criterio de costura se evalúa sobre los patrones periódicos medibles (≥4 de cada 5). Propuesta en SP-2/SP-3 de la fase 1. |
| A7 | §6 SP-2 | "Reconocible por diseñadores" no es automático; no se dice cuántos diseñadores ni quién aporta las 10 imágenes. | Q3. Mientras tanto, métricas objetivas auxiliares (SSIM/correlación de periodicidad, costura medida). |
| A8 | §1 etapa 4 | "Grasshopper o donde sea más fácil" vs §5.4 "fichero de parámetros + comando de Rhino primero". | Primera interfaz: fichero de parámetros (JSON) + comando; Grasshopper es fase posterior (como dice §5.4). |
| A9 | §2 vs §5.3 | "Modelos solo de malla" fuera de alcance, pero la vista previa y la vía B usan mallas. | Aclarado: la malla es salida interna, la entrada sigue siendo brep. |
| A10 | §5.2 | Sin cuantificar "sin costuras" ni "mapa de profundidad" (¿8/16 bits, mm por nivel?). | Definir en SP-2: métrica de costura (diferencia de borde opuesto en la baldosa) y escala de alturas en mm. |
| A11 | §7 / §4 | Los diagramas no se exportaron a texto, así que no veo los nombres exactos de las 4 fases ni las 3 puertas. | Defino yo las fases (§6); confírmame o corrígelas. |

## 3. Preguntas que bloquean el plan (máx. 5)

Respondidas por el usuario antes de empezar el SP-0. Mi recomendación va primero.

- **Q1 — Dónde corre el procesado de imagen (OpenCV/numpy).** Recomiendo un **Python externo con venv** (pytest, OpenCV y numpy ahí) que intercambia ficheros (PNG/JSON) con Rhino, en lugar de instalar OpenCV dentro del Python de Rhino. Ventaja: pruebas automáticas rápidas sin Rhino, módulos desacoplados. Requiere instalar dependencias → **necesito tu confirmación**.
- **Q2 — Dónde vive el venv y el repo.** La carpeta está en Google Drive: un venv con miles de ficheros se sincronizaría y ralentizaría Drive. Recomiendo `git init` en esta carpeta y el venv **fuera** de Drive (p. ej. `C:\dev\venvs\textura`) — eso toca fuera del repositorio, así que también necesito tu OK. Alternativa: venv dentro y excluirlo de la sincronización.
- **Q3 — Evaluación humana.** ¿Quién aporta las 10 imágenes de SP-2/SP-3 y quiénes son los "diseñadores" (cuántos)? Propongo: tú aportas ≥10 imágenes, 3 evaluadores mínimo, mayoría simple. Si no hay evaluadores, el criterio se rebaja a métricas objetivas más tu juicio.
- **Q4 — Cronómetro de "<3 min". RESUELTA: sin cronómetro por ahora** (ver A2). Los tiempos se anotan pero no deciden.
- **Q5 — Uso del puente Rhino en SP-0.** ¿Autorizas que use las herramientas `mcp__rhino__*` (lanzan Rhino 9 y ejecutan Python/C# con permisos de tu usuario) y que solo guarde ficheros `.3dm` dentro del repositorio? Alternativa si no es fiable: `rhinocode`/RhinoCompute por línea de comandos (a verificar).

## 4. Estructura del repositorio propuesta

```
/
├─ brief.md  PLAN.md  README.md  pyproject.toml
├─ src/textura/
│  ├─ common/            # esquema de parámetros, unidades, E/S de ficheros, contratos (dataclasses/JSON Schema)
│  ├─ m1_entrada/        # image_input.py (núcleo puro) · rhino_surface.py (adaptador Rhino)
│  ├─ m2_referencia/
│  │  ├─ fiel/           # periodicidad, celda mínima, separación patrón/color, mapa de alturas, contornos
│  │  └─ reinterpretado/ # pattern_spec.schema.json, generador determinista
│  ├─ m3_mapeo/          # escala física, uv, planar/cilíndrico, flow/sporph, mapa de distorsión
│  ├─ m4_ajuste/         # parámetros, máscara, relieve vía A (contornos), vía B (alturas), vista previa
│  └─ rhino_cmds/        # comando de Rhino + lectura del fichero de parámetros
├─ tests/                # un subdirectorio por módulo; núcleo con pytest sin Rhino
├─ tests_rhino/          # pruebas que requieren Rhino, lanzadas desde Claude Code vía puente
├─ cases/                # casos de referencia: imágenes, .3dm (cilindro, plano, orgánica), resultados esperados
├─ spikes/sp0 … sp4/     # código y informe breve (informe.md) por spike
└─ docs/params/          # tabla de parámetros por módulo (generada desde el esquema, para que no se desincronice)
```

Principio: **cada módulo = núcleo puro (testeable sin Rhino) + adaptador fino hacia Rhino**. Contratos entre módulos = ficheros (PNG + JSON con esquema), así cada módulo se prueba y sustituye aislado.

### Entradas y salidas por módulo

| Módulo | Entrada | Salida |
|---|---|---|
| **M1 Entrada** | Ruta PNG/JPG; en Rhino: GUID del brep + índice de cara | `image_norm.png` + `image_meta.json` (resolución, modo gris, hash); `surface_info.json` (dominio U/V, trimmed sí/no, tamaño mm aprox., dirección U/V, orientación normal); previsualizaciones |
| **M2a Fiel** | `image_norm.png`, parámetros de extracción | `tile.png` (repetible), `tile.json` (periodos X/Y en px, métrica de costura), `heightmap.png`, `contours.json` (si vectorizable), `preview_3x3.png` |
| **M2b Reinterpretado** | `pattern_spec.json` (escrito por Claude: retícula, motivo, proporciones, orientación) | Mismas salidas que M2a + ficha de parámetros del patrón |
| **M3 Mapeo** | `tile.json` + `contours.json`/`heightmap.png`, `surface_info.json`, método (uv/planar/cilíndrico/flow), parámetros de escala en mm | Geometría 2D mapeada sobre la cara (curvas o malla), `distortion_map` (área y ángulo por muestreo) + veredicto frente al umbral (15 % por defecto) |
| **M4 Ajuste y relieve** | Salida de M3, `params.json` (escala, rotación, desplazamiento U/V, densidad, espejado, anisotropía, semilla, profundidad, lado, perfil), máscara (curva cerrada) | Vista previa ligera (curvas/malla gruesa) y geometría final (NURBS vía A o malla vía B) al confirmar; `run_report.json` (tiempos, errores) |

Cada parámetro se documentará en `docs/params/<modulo>.md` con: nombre, unidad, rango, valor por defecto, explicación, generado desde un único esquema.

## 5. Afirmaciones sobre Rhino «a verificar» y cómo las verificaré

| # | Afirmación | Estado | Cómo la verifico |
|---|---|---|---|
| V1 | El bucle Claude Code ↔ Rhino 9 funciona sin pasos manuales | [?] (hay herramientas, primer intento `rhino_closed`) | SP-0: `run_python` imprime versión de Rhino y de Python; crear/modificar geometría; `save_doc`/`open_doc` de un `.3dm`; `get_viewport_image`. Repetir 10 ciclos y contar fallos. |
| V2 | Python de Rhino 9 soporta CPython 3 y paquetes de terceros | [?] | `import sys; sys.version`; probar un import de un paquete pequeño. Decisión Q1 evita depender de ello. |
| V3 | Se puede leer un `.3dm` desde script | [S] (RhinoCommon `File3dm.Read`) | SP-0: leer `cases/*.3dm` y listar objetos/breps. |
| V4 | Identificar la cara = GUID del brep + índice | [S] | SP-0/1: seleccionar una cara y comprobar que `ComponentIndex` es estable al guardar/reabrir. |
| V5 | Caras recortadas: dominio envolvente vía `BrepFace.Domain(0/1)` | [S] | SP-1: cara recortada de prueba; comparar dominio con el bounding UV de las curvas de recorte. |
| V6 | Flow/Sporph disponible y estable desde RhinoCommon | [?] (espacio `Rhino.Geometry.Morphs`, a confirmar) | SP-1: listar tipos del espacio de nombres por reflexión en `run_csharp`; aplicar a una baldosa en cilindro, plano y orgánica; si falta, `run_command` con FlowAlongSrf/Sporph. Registrar éxito/fallo y tiempo. |
| V7 | Llevar curvas a la superficie (pull) y calcular normales | [S] (`Curve.PullToBrepFace`, `Surface.NormalAt`) | SP-1/SP-4: probar sobre cilindro y orgánica; medir desviación. |
| V8 | Extruir/desplazar contornos en la normal manteniendo NURBS | [S] | SP-4: vía A con 100, 300, 600 contornos; registrar errores, tolerancias y tiempo (informativo, sin umbral). |
| V9 | Distorsión (área/ángulo) por muestreo | [S] (`Surface.Evaluate`, derivadas) | SP-1: comparar con un caso analítico (cilindro: distorsión conocida ≈ 0). |
| V10 | Grasshopper 1/2 utilizables desde el puente | [?] (existen `g1_*`/`g2_*`) | Solo fase posterior; probe mínimo tras SP-0, sin comprometer el MVP. |

## 6. Fases y criterios de aceptación

(Los nombres de fase son míos, A11.)

### Fase 1 — Spikes (decide el alcance real)

Orden: **SP-0 primero y solo**; después SP-1…SP-4 pueden avanzar en paralelo (no comparten ficheros).

| Spike | Tareas | Criterio medible |
|---|---|---|
| **SP-0** Bucle Claude Code ↔ Rhino | Confirmar Q1–Q5; script que cree un cilindro y una cara plana, los modifique, guarde y relea un `.3dm`; captura de viewport | **10/10** ciclos editar→ejecutar→ver sin intervención manual; tiempo por ciclo registrado; versión de Rhino/Python anotada; fallos documentados. Salida: duración de fases y modo de trabajo (puente vs línea de comandos). |
| **SP-1** Mapeo | Baldosa de prueba con métodos a, b, c sobre cilindro → plano → orgánica; mapa de distorsión | Distorsión máxima **<15 %** en la superficie orgánica con ≥1 método; cilindro con método b/UV <1 % (control analítico). Repliegue: MVP solo planas y cilíndricas. |
| **SP-2** Modo fiel | 10 imágenes reales (Q3); extracción de baldosa y periodos | ≥ **75 %** reconocibles por evaluadores; costura nula en ≥ **4/5** patrones periódicos (sobre los que se puede medir) + métrica de costura objetiva reportada. Repliegue: priorizar reinterpretado. |
| **SP-3** Modo reinterpretado | Claude describe 10 patrones, generador los dibuja | ≥ **3/5** evaluados como "lo esperado o cerca" (sobre las 5 valoradas); 10/10 sin costuras por construcción (verificable con prueba automática). |
| **SP-4** Relieve | Vía A con unos cientos de contornos en superficie curva | Geometría sin errores (0 fallos de operación); tiempo registrado, sin umbral (Q4). Repliegue: curvas/imagen sin relieve real. |

Puerta 1: informe por spike en `spikes/spN/informe.md` + decisión explícita de alcance MVP (qué repliegues se activan).

### Fase 2 — Módulos MVP (en paralelo, tras puerta 1)

| Módulo | Criterio de aceptación |
|---|---|
| M1 | Pruebas automáticas ≥ 90 % de las rutas del núcleo; PNG/JPG, errores claros ante formato inválido; GUID+cara resueltos en cilindro, plano, orgánica |
| M2a / M2b | Cada modo con ≥ 5 casos de referencia en `cases/`; periodos X/Y con error ≤ 1 % en patrones sintéticos conocidos; tile 3×3 sin costura; salida conforme al esquema JSON |
| M3 | Escala física exacta: patrón de N mm → medida sobre la superficie dentro de ±1 %; mapa de distorsión reproduce los casos analíticos |
| M4 | Cada parámetro con nombre/unidad/rango/defecto/explicación (comprobado por test que lo exige); vista previa actualizada sin llamar a Claude |

Puerta 2: cada módulo pasa sus pruebas aislado.

### Fase 3 — Integración y MVP

Cadena completa: imagen + cara → textura en superficie. Aceptación del MVP (del brief §8): textura reconocible (el límite de <3 min por generación queda en suspenso, Q4), parámetros con ficha completa y vista previa sin Claude, cada módulo con pruebas automáticas y casos de referencia.
Puerta 3: demostración con el cilindro y al menos un caso más difícil (según resultado de SP-1).

### Fase 4 — Posterior (fuera del MVP; solo si se aprueba)

Objeto 3D con textura como entrada, varias caras y costuras, máscaras por zonas, panel/Grasshopper, biblioteca de patrones.

## 7. Puntos débiles de tus decisiones, alternativas y cómo abaratarlas [O]

Principio añadido: en este proyecto "coste" no es dinero (Claude Code no se paga por token aquí) sino tres cosas que sí cuestan caro: (a) interpretación interactiva de Claude/sesión Rhino que no se puede cachear ni repetir en CI, (b) trabajo de desarrollo duplicado, (c) ciclos de iteración lentos por un puente Rhino inestable o por Google Drive. Cada punto de abajo pasa de "alternativa" a **decisión concreta** orientada a minimizar esas tres cosas; donde choca con algo ya "confirmado" en brief.md §8 lo marco explícitamente, porque eso sí necesita tu OK.

1. **Dos modos de referencia en paralelo duplican el trabajo de la etapa 2.** Decisión: no se desarrollan a la vez. Orden: **modo fiel primero** (OpenCV puro, determinista, se testea con pytest sin Rhino y sin Claude — es el camino barato) hasta pasar el criterio de SP-2; **reinterpretado pasa a 2b**, reutilizando el 100 % del contrato de salida (`tile.json`, `heightmap.png`, `contours.json`) ya validado por el fiel. Ahorra implementar y depurar dos módulos a la vez. **Choca con brief.md §8 ("ambos modos prioritarios y en paralelo")** → propuesta de ahorro pendiente de tu confirmación; si la apruebas, lo reflejo también en brief.md.
2. **Vía A (contornos/NURBS) solo funciona si la imagen es vectorizable; orgánicas/fotográficas caen en vía B (malla).** Decisión: clasificar automáticamente con una heurística barata (nº de colores dominantes + ratio bordes nítidos vs. degradados), **sin gastar una llamada a Claude en decidirlo**. Umbral de adopción: si en los 10 casos de SP-2 menos del 50 % resuelve por vía A, vía A pasa a fase posterior y el MVP se queda solo con vía B (evita mantener dos caminos de relieve en paralelo).
3. **"Reconocible" es subjetivo y los umbrales (75 %, 3 de 5) con pocos evaluadores son poco fiables.** Decisión: el criterio de paso pasa a ser una **métrica objetiva y automática** (SSIM y/o correlación de periodicidad), sin coste de coordinar personas y repetible en cada ejecución. La evaluación humana (Q3) queda como dato informativo opcional sobre una muestra pequeña (3 imágenes), no bloqueante.
4. **Dependencia fuerte del puente Rhino de terceros: ya falló la primera llamada.** Decisión: en SP-0 se prueba primero la vía más barata de automatizar — **script de Rhino por línea de comandos o tarea programada, sin sesión interactiva** — y solo si falla se recurre al puente `mcp__rhino__*`. Así las pruebas de regresión no dependen de mantener una sesión abierta y se repiten gratis.
5. **Claude interpretando por sesión interactiva no es reproducible**: dos sesiones pueden describir el mismo patrón distinto. Decisión: **cachear por hash de imagen** — si ya existe un `pattern_spec.json` aprobado para ese hash, no se vuelve a invocar a Claude, se reutiliza directamente como caso de referencia. Ahorra interpretaciones repetidas además de fijar el resultado.
6. **Proyecto en Google Drive**: riesgo de sincronización con venv y ficheros temporales (Q2). Decisión: además de sacar el venv (Q2), toda carpeta que cambia en cada ejecución (`tests_rhino/output`, `spikes/*/output`, `cases/*/generated`) se excluye de Drive (`.gitignore` + "disponible solo en este dispositivo", o directamente fuera de `H:\Mi unidad`). Evita gastar ancho de banda de sync y bloqueos de fichero a mitad de escritura que rompen el bucle con Rhino.
7. **Umbral de distorsión del 15 % único** mezcla área y ángulo. Decisión: separarlo desde el principio en dos parámetros independientes del esquema, `distortion_area_max` y `distortion_angle_max` (ambos 15 % por defecto, ajustables). El coste de hacerlo ahora es marginal frente a rehacer el esquema de `distortion_map` más adelante.
8. **(Nuevo) Coste del propio bucle de spikes.** SP-1…SP-4 no comparten ficheros, pero sí pueden compartir el mismo arranque de Rhino 9 — y el primer arranque ya fue inestable (`rhino_closed`). Decisión: agruparlos en la menor cantidad de sesiones/arranques de Rhino posible en vez de relanzar el slot por spike, y registrar en el informe de SP-0 cuánto cuesta (tiempo, fallos) cada arranque para decidir si conviene mantener una sesión larga o reiniciar por spike.

## 8. Reglas de trabajo que seguiré

- No instalo dependencias ni toco fuera del repositorio sin tu confirmación (Q1, Q2, Q5).
- Cada afirmación se marca [H]/[S]/[O]/[?]; si no sé algo, lo digo.
- Nada fuera del alcance de §2 del brief.
- Siguiente paso tras aprobar: **SP-0**.
