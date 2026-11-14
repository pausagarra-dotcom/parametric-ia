# Texturas desde imagen sobre superficies Rhino — Brief para Claude Code

Nov 11, 2026 · @Pau

## 1. Objetivo

Replicar la textura de una imagen de referencia sobre una superficie de un modelo 3D de Rhino y poder controlar parámetros para ajustarla sobre el modelo. Nada más.

El flujo tiene cuatro etapas:

1. **Entrada:** una imagen plana de la textura o bien una imagen de un objeto con la textura aplicada. El modelo del objeto 3d del rhino con la selección de la superficie donde queremos aplicar la textura
2. **Referencia:** Claude interpreta la textura y se obtiene un patrón de referencia limpio y repetible. Tambien hacemos el mapa de profundidad.
3. **Mapeo:** el patrón se proyecta sobre la superficie elegida.
4. **Ajuste y relieve:** el usuario controla parámetros (escala, rotación, densidad, profundidad) hasta que la textura encaje sobre el modelo. Dentro de grashopper o donde se más fácil.

**Resultado esperado:** la textura de la imagen aplicada sobre la superficie, reconocible respecto al original y editable mediante parámetros que se puedan entender y cambiar.

**Decisión de diseño a confirmar:** Claude no genera imágenes ráster por sí mismo; analiza imágenes y escribe código o descripciones paramétricas. Por eso «generar la imagen de referencia» se plantea así: Claude interpreta la textura y un generador determinista produce el patrón. Si se prefiere un modelo generativo de imagen externo, ese módulo se puede sustituir sin tocar el resto.

## 2. Alcance

El MVP cubre una sola superficie y una imagen plana de entrada; el resto entra por fases. El primer caso de prueba es un cilindro y la dificultad aumenta a partir de ahí (doble curvatura, superficies orgánicas).

| Capacidad | MVP | Fase posterior | Fuera de alcance |
|---|---|---|---|
| Entrada | Imagen plana (PNG/JPG) | Objeto 3D con textura (se convierte a imagen) | Búsqueda web de imágenes |
| Superficie destino | Una cara de un brep de Rhino | Varias caras y continuidad en las costuras | Modelos solo de malla |
| Referencia | Modo fiel y modo reinterpretado | Biblioteca de patrones guardados | Generación ráster con IA externa |
| Control manual | Escala, rotación, desplazamiento, densidad, profundidad | Máscaras por zonas y profundidad variable | Pintado libre de zonas |

Queda fuera del proyecto el análisis de fabricabilidad, el export a CAD y cualquier producto comercial.

## 3. Flujo de usuario

Cada etapa termina en un punto de aprobación: el usuario ve el resultado intermedio y decide si continúa, repite o vuelve atrás, así un error de interpretación no se arrastra hasta el final.

| Etapa | El usuario | El sistema devuelve | Se aprueba |
|---|---|---|---|
| 1. Entrada | Indica la imagen y la superficie de Rhino | Previsualización de la imagen y de la cara elegida con su dirección U/V | Imagen y superficie correctas |
| 2. Referencia | Elige modo fiel o reinterpretado | Baldosa repetible, ficha de parámetros del patrón y vista de 3×3 repeticiones | Patrón reconocible y sin costuras |
| 3. Mapeo | Elige el método de mapeo | Patrón sobre la superficie y mapa de distorsión | Distorsión aceptable |
| 4. Ajuste y relieve | Mueve parámetros nombrados y fija profundidad y lado (relieve o grabado) | Vista previa ligera que se actualiza y geometría final al confirmar | Aspecto deseado |

La etapa 4 se puede repetir indefinidamente sin volver a llamar a Claude: solo la etapa 2 consume interpretación; el resto es cálculo determinista.

## 4. Arquitectura

Cuatro etapas encadenadas, cada una una librería independiente con entradas y salidas definidas; solo la interpretación de la imagen usa Claude.

*(Diagrama: arquitectura · 4 etapas sobre Rhino, una con Claude — no incluido en la exportación de texto.)*

Claude interviene únicamente en la etapa de referencia; el mapeo, el ajuste y el relieve son cálculo determinista dentro de Rhino, por lo que se pueden repetir sin volver a llamar a Claude. Claude se opera desde Claude Code: la herramienta no llama a la API de Claude, así que no necesita clave de API ni genera coste propio.

## 5. Requisitos por módulo

Cada módulo tiene entrada y salida definidas, para poder probarlo sin el resto y sustituirlo si falla.

### 5.1 Entrada

- Acepta PNG/JPG y la normaliza (resolución, escala de grises opcional) guardando sus metadatos.
- La superficie se identifica por su GUID en Rhino, usando una cara de un brep y su dominio U/V; las caras recortadas se tratan por su dominio envolvente.
- Fase posterior: de un objeto 3D con textura se extrae el mapa de textura (o una vista ortogonal) y se convierte en imagen plana.

### 5.2 Imagen de referencia: dos modos

| | Modo fiel | Modo reinterpretado |
|---|---|---|
| Idea | Replicar la textura de la imagen tal cual | Describir el patrón y regenerarlo |
| Quién hace qué | Procesado de imagen (OpenCV): separa patrón de color, detecta la periodicidad y recorta la celda mínima. Claude revisa el resultado con visión y ajusta parámetros | Claude (visión) describe el patrón en un JSON: tipo de retícula, motivo, proporciones, orientación. Un generador lo dibuja |
| Salida | Baldosa repetible y mapa de alturas; contornos si es vectorizable | Baldosa repetible, mapa de alturas y contornos, todo con parámetros nombrados |
| Fortaleza | Se parece al original | Totalmente editable y sin costuras por construcción |
| Riesgo | Costuras y ruido en imágenes reales | El resultado puede no parecerse lo bastante |

Ambos modos entregan una baldosa con sus periodos en X e Y. Ambos modos son prioritarios y se desarrollan en paralelo.

### 5.3 Mapeo sobre la superficie

- **Escala física:** el tamaño del patrón se define en mm, no en unidades UV, para que no dependa de cómo esté parametrizada la superficie.
- **Métodos:** (a) UV paramétrico de la superficie, (b) proyección planar o cilíndrica para caras casi planas o cilíndricas, (c) llevar geometría plana a la superficie con la operación Flow/Sporph de Rhino. La disponibilidad y estabilidad de (c) en RhinoCommon hay que verificarla en el primer spike.
- **Mapa de distorsión:** relación de áreas y ángulos por muestreo, con un umbral inicial propuesto del 15% (ajustable).
- Gestión de costuras, orientación de la normal y caras recortadas.

### 5.4 Ajuste y relieve

Todos los controles son parámetros nombrados, y cada uno se documenta con nombre, unidad, rango, valor por defecto y una frase de explicación, para que puedas entender y modificar el resultado.

- Escala (mm por periodo), rotación, desplazamiento en U y V, densidad o espaciado, espejado, deformación anisotrópica y semilla de aleatoriedad.
- Profundidad del relieve (mm), relieve o grabado y perfil (vertical, cónico, redondeado).
- Máscara: una curva cerrada que limita la zona de aplicación (MVP) y, más adelante, varias zonas con valores distintos.
- Primera interfaz: fichero de parámetros más comando de Rhino. Después, panel propio o componente de Grasshopper con sliders.
- Vista previa ligera (curvas o malla gruesa) mientras se ajusta y cálculo completo solo al confirmar.

Para dar volumen a la textura hay dos vías:

- **Vía A, por contornos (preferida):** los contornos cerrados se llevan a la superficie y se extruyen o desplazan en la normal. Mantiene superficies NURBS.
- **Vía B, por mapa de alturas:** desplazamiento de una malla. Sirve para texturas orgánicas.
- Riesgo de rendimiento: con cientos de contornos las operaciones pueden ser lentas o inestables; se prevén lotes y tolerancias configurables.

## 6. Riesgos y experimentos de validación

Los tres riesgos que pueden bloquear el proyecto son el mapeo sobre superficies orgánicas, la extracción de un patrón repetible sin costuras y la generación del relieve; se atacan primero con experimentos pequeños. Los umbrales son propuestas para que las confirmes.

| ID | Riesgo | Experimento | Criterio de éxito |
|---|---|---|---|
| SP-0 | Que el bucle Claude Code y Rhino no funcione con fluidez | Desde Claude Code, ejecutar un script que cree y modifique geometría en Rhino y lea un fichero .3dm | El ciclo editar, ejecutar y ver el resultado se hace sin pasos manuales |
| SP-1 | Distorsión del mapeo | Mapear una baldosa de prueba con los tres métodos, empezando por un cilindro y subiendo a una cara plana y a una superficie orgánica | Distorsión máxima menor del 15% en la superficie orgánica con al menos un método |
| SP-2 | Patrón no reconocible o con costuras | Modo fiel con 10 imágenes de texturas reales | Al menos el 75% reconocibles por diseñadores; cero costuras visibles en al menos 4 de 5 patrones |
| SP-3 | El modo reinterpretado no se parece a lo pedido | Claude describe 10 patrones, el generador los dibuja y un diseñador los valora | Al menos 3 de 5 pruebas con «es lo que esperaba o cerca» |
| SP-4 | Relieve que no se genera bien o es demasiado lento | Vía A con unos cientos de contornos sobre una superficie curva | Geometría generada sin errores y en menos de 3 min por generación |

**Planes de repliegue:** si SP-4 falla, la textura se aplica como curvas o imagen sobre la superficie, sin relieve real. Si SP-1 falla en superficies orgánicas, el MVP se restringe a caras planas y cilíndricas. Si SP-2 falla, se avanza con el modo reinterpretado mientras se corrige el fiel.

## 7. Plan de implementación

El trabajo avanza en cuatro fases y no se pasa a la siguiente sin cumplir los criterios de la puerta intermedia.

*(Diagrama: plan de implementación · 4 fases, 3 puertas — no incluido en la exportación de texto.)*

Las fases no llevan fechas: las duraciones se fijan al terminar el SP-0, cuando se sabe cuánto cuesta iterar con Rhino desde Claude Code. La fase 1 es la que decide el alcance real del MVP, porque cada spike fallido activa su plan de repliegue de la sección 6.

## 8. Criterios de aceptación, suposiciones y preguntas abiertas

El MVP se da por bueno cuando, a partir de una imagen y una cara de Rhino, la textura aparece replicada sobre la superficie y puedes ajustarla con parámetros sin ayuda.

**Criterios de aceptación del MVP**

- Con una imagen y una cara de Rhino, la textura aparece sobre la superficie en menos de 3 minutos por generación.
- La textura es reconocible respecto a la imagen de referencia.
- Cada parámetro tiene nombre, unidad, rango, valor por defecto y explicación, y al cambiarlo se actualiza la vista previa sin llamar a Claude.
- Cada módulo tiene pruebas automáticas y un conjunto de casos de referencia.

**Suposiciones que he hecho** (cámbialas si no son correctas)

1. Claude interpreta la imagen y un generador determinista crea el patrón; Claude no genera píxeles.
2. Rhino es el motor de geometría.
3. El MVP trabaja con una sola superficie y una sola imagen plana.
4. La profundidad del relieve se mantiene como parámetro, porque sin ella la textura no tiene volumen sobre el modelo; la comprobación de fabricación queda fuera.
5. Rhino 9 es la versión de trabajo. No he podido confirmar sus capacidades de scripting ni su conexión con Claude Code, así que se verifican en el SP-0.

**Decisiones confirmadas**

- La versión de Rhino es la 9.
- Claude se opera desde Claude Code; la herramienta no lo llama por sí misma.
- Los modos fiel y reinterpretado son ambos prioritarios.
- El primer caso de prueba es un cilindro y la dificultad aumenta después.
- El sistema operativo es Windows.

**Preguntas abiertas:** ninguna por ahora.

## 9. Instrucciones de arranque para Claude Code

Exporta este documento a Markdown, guárdalo como BRIEF.md en la raíz del repositorio y pega este prompt como primer mensaje; la primera sesión solo planifica.

Lee BRIEF.md completo antes de hacer nada.

Tu tarea ahora es SOLO planificar, no implementar:

1. Resume en 10 líneas cómo entiendes el proyecto y señala ambigüedades o contradicciones del brief.
2. Revisa las decisiones confirmadas de la sección 8 y hazme las preguntas que bloqueen el plan (máximo 5).
3. Propón la estructura del repositorio y las entradas y salidas de cada módulo de la sección 5.
4. Genera PLAN.md con fases, tareas y criterios de aceptación medibles, empezando por los spikes SP-0 a SP-4.
5. Para cada afirmación sobre la API de Rhino marcada «a verificar», indica cómo la vas a verificar.

Reglas:

- Distingue hechos verificados, suposiciones y opiniones. Si no sabes algo, dilo.
- No añadas funcionalidades fuera del alcance de la sección 2.
- Cada módulo es independiente, con pruebas automáticas y parámetros documentados (nombre, unidad, rango, valor por defecto, explicación).
- Pide confirmación antes de instalar dependencias o tocar archivos fuera del repositorio.
- Señala los puntos débiles de mis decisiones y propón alternativas si las hay.

Cuando el plan esté aprobado, el siguiente paso es ejecutar el SP-0 (bucle Claude Code y Rhino), porque de él depende cómo se trabaja el resto.
