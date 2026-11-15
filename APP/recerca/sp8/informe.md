# SP-8 · Velocidad de la conexión con Rhino (informe, parte 1)

Fecha: 2026-11-15. Leyenda: [H] medido en esta sesión · [S] suposición · [?] por verificar.
Scripts de medida: los he guardado fuera del proyecto, en el scratchpad de la sesión (`sp8_trivial.py`, `sp8_gh.py`).

## Qué se ha medido [H]
1. **Transporte: `RhinoCode.exe`**, la herramienta oficial de Rhino 9 para enviar scripts a un Rhino abierto (`C:\Program Files\Rhino 9\System\RhinoCode.exe`).
   - Un script vacío tarda **0,50–0,65 s** por llamada, sobre todo por arrancar el programa cada vez.
   - El script se ejecuta dentro de Rhino y la salida no vuelve por la consola: el resultado se tiene que devolver mediante un fichero o una conexión.
   - [S] Con una conexión persistente (Rhino escucha en una tubería, `rhinocode_remotepipe_<PID>`, o un servidor propio dentro de Rhino), el transporte bajaría a milisegundos.
2. **Cálculo: la textura 03** (`superficie_organica_quadres.gh`), abierta en memoria y resuelta sin abrir el lienzo (no se ha guardado ni modificado):

| Acción | Tiempo |
|---|---|
| Abrir el `.gh` | 0,23 s |
| Primera solución completa | 6,4 s |
| Mover `DEPTH` o `TILT` | **3,0–3,1 s** |
| Mover `CELL` | 2,5–3,0 s |
| Mover `STEP` a 1,5 (malla más fina) | 5,1 s |
| `STEP` en 2 o en 4 (el máximo), moviendo `DEPTH` | ~3,0 s en los dos casos |

   - **Por qué no baja con una malla más gruesa:** el componente más lento es **«Placa quadres»**, un segundo modelo colocado al lado (+260 mm) dentro del mismo `.gh`, que tarda unos 3,3 s. Después vienen MALLA (1,7 s) y REJILLA (1,1 s). [S] Sin la placa, la superficie sola tardaría unos 1,5–2,8 s.

## Conclusiones
1. **Lo que limita la velocidad es el cálculo de Rhino y Grasshopper, no la conexión.** Con el transporte actual son unos 0,5 s; con una conexión persistente sería casi nada.
2. **Con las definiciones actuales, cada cambio de slider tarda ~3 s.** Para una app que responda «al momento» hace falta:
   - (a) **definiciones pensadas para la app:** solo la superficie a texturizar, sin modelos de comparación al lado, y con la fórmula evaluada una sola vez por cada coordenada local (el truco de la 03);
   - (b) **una vista previa ligera mientras se mueve el slider** y el cálculo completo al soltarlo;
   - (c) [O, **decisión de Pau**] una vista previa instantánea calculada en el propio visor (desplazamiento en la tarjeta gráfica con la misma fórmula), mientras Rhino calcula la geometría buena al soltar el slider. Es más rápido, pero supone tener **dos implementaciones de la fórmula** que se tienen que mantener iguales. Choca con la decisión 4, que dice un solo motor.
3. **ARAP (SP-7):** con numpy puro tarda de segundos a minutos. [S] Con un solver de matrices dispersas (scipy) bajaría a menos de un segundo.

## Parte 2 (2026-11-15, con permiso de Pau: scipy 1.18.1 y rhinoinside 0.8.2 instalados en `C:\dev\venvs\textura`; sin ninguna conexión a la API de pago) [H]
1. **ARAP con scipy** (`sp8_arap_scipy.py`): la misma zona A25 de 100 mm del SP-7 (2702 vértices, 5099 triángulos).
   - **80 iteraciones en 1,13 s**, con el mismo resultado: distorsión de área máxima del 5,04 % y ningún triángulo girado. Antes, con numpy puro, tardaba minutos.
   - [S] Con 20 iteraciones probablemente basta (~0,3 s).
   - ⚠ El LSCM con solver exacto da un resultado degenerado: la formulación tiene un error de signo u orientación. ARAP lo corrige igualmente, pero hay que arreglar el LSCM antes de usarlo en la app.
2. **Rhino.Inside CPython** (`sp8_rhinoinside.py`): **no funciona con Rhino 9 en este equipo.**
   - `rhinoinside` 0.8.2 busca .NET 9 para Rhino 9, y aquí solo está instalado .NET 10.
   - He forzado .NET 10 y también he probado la variante .NET Framework (`net48`). En los dos casos el proceso se cierra con el código 5, sin ningún mensaje.
   - [?] Posibles causas: Rhino 9 todavía en fase WIP o beta, la licencia de evaluación, o que ya haya otro Rhino abierto.
   - Se puede volver a probar cuando haya un Rhino 9 definitivo con licencia.
3. **Alternativa sin Rhino.Inside** [O]: un **servidor pequeño que corra dentro de Rhino 9** (un script de Python que escucha en `localhost`).
   - El backend le pide «cambia DEPTH a 0,5» y recibe la malla.
   - Se obtiene lo mismo que con Rhino.Inside: Rhino siempre abierto, la definición cargada y un transporte de milisegundos, sin depender del paquete.
   - Es la opción que propongo para la fase 3. Todavía no se ha probado.

## Parte 3: servidor dentro de Rhino (2026-11-15) [H]
Archivos:
- `sp8_servidor_rhino.py`: se ejecuta dentro de Rhino 9. Es un servidor HTTP en `127.0.0.1:8765` con la textura 03 abierta en memoria. El cálculo se hace en el hilo principal de Rhino.
- `sp8_client.py`: lo mide desde el entorno de Python. Resultados en `sp8_servidor.json`.

| Medida | Resultado |
|---|---|
| `ping` (ida y vuelta, sin cálculo) | **5–10 ms** |
| Cambiar `DEPTH` (petición completa) | **3,1–3,3 s**, de los que **solo ~8 ms son de transporte** |

- **Error encontrado (y corregido en el servidor):**
  - Con el documento activo, *cambiar el valor del slider ya lanza una solución*, y después `NewSolution` hacía otra. Cada cambio costaba **~6 s**, cuando debería costar 3.
  - Solución: desactivar el documento mientras se cambia el valor y resolver una sola vez.
  - ⚠ Por eso los ~3 s de la parte 1 medían solo la segunda solución: el coste real con aquel código era ~6 s.
- **Conclusión:** el servidor dentro de Rhino **sirve como conexión de la app**. El transporte es despreciable, y lo único que queda es el cálculo de la definición. Sustituye a Rhino.Inside.

## Decisión sobre la vista previa (Pau, 2026-11-15)
**Sí a la vista previa instantánea en el visor**, la opción (c).
- No gasta tokens de Claude: se calcula en la tarjeta gráfica del navegador.
- El coste es solo de desarrollo: la fórmula de cada textura existirá en dos sitios (Rhino para la geometría buena y el visor para la vista previa).
- Para que no se desajusten, la fórmula se escribirá **una sola vez** en un formato común (las mismas líneas que ya están en `formula_patro.md`). [S] Se generarán automáticamente la versión para Rhino y la del visor, y una prueba automática comparará las dos alturas en puntos de control.

## Pendiente (instalación ya hecha)
- **Rhino.Inside CPython** (paquete `rhinoinside`): Rhino dentro del mismo proceso de Python que el backend, sin transporte.
- **scipy:** para medir ARAP con un solver de verdad.
- **Rhino.Compute en local:** [?] hay que descargarlo de McNeel. Es la vía para tener un servidor con más usuarios.

Siguiendo la regla del plan, no se instala nada sin el permiso de Pau. En el entorno `C:\dev\venvs\textura`, `pip` necesita `--trusted-host` por la inspección SSL del equipo (como en el SP-0).
