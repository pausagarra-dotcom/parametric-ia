# SP-0 — Bucle Claude Code ↔ Rhino (informe)

Fecha: 2026-11-11. Marcas: [H] verificado en esta sesión · [S] suposición · [?] sin verificar.

## Resultados

- [H] Rhino **9.1.26314.9001**, Python de Rhino **3.13.13** (CPython), win32. Vía puente `mcp__rhino__run_python`.
- [H] Primera llamada a `get_context` falló con `rhino_closed` (Rhino se auto-lanzó y se cerró); la segunda funcionó. Hay que tolerar un reintento tras un arranque en frío.
- [H] Crear (cilindro r=25, h=100: 3 caras), modificar (traslación) y añadir geometría: OK.
- [H] Guardar `.3dm` en el repo con `RhinoApp.RunScript('-_SaveAs "ruta" _Enter')` y releerlo con `File3dm.Read`: OK. `RhinoDoc.Write3dm` **no existe**; no usar.
- [H] Ciclo crear → modificar → guardar → releer con comprobación del nº de objetos: **10/10 correctos, ~0,18 s por ciclo** (0,4 s el primero). Sin pasos manuales.
- [H] `get_viewport_image` devuelve la captura del viewport (480×270 JPEG) + cámara y bounding box.
- [H] Dominio UV del cilindro: cara lateral U ∈ [0, 2πr = 157,08], V ∈ [0, 100]. Es decir, parametrizada por longitud de arco (útil para SP-1). Tapas: [-25,25]².
- [H] En RhinoCommon (Rhino 9.1) existe el espacio `Rhino.Geometry.Morphs` con `SporphSpaceMorph`, `FlowSpaceMorph`, `SplopSpaceMorph`, `BendSpaceMorph`, `TwistSpaceMorph`, `TaperSpaceMorph`, `StretchSpaceMorph`, `MaelstromSpaceMorph`, `MeshCageMorph`, `MeshMorphMesh`. **Presencia verificada; estabilidad y resultado de Flow/Sporph sobre superficies, no** (SP-1).
- [H] Rhino deja ficheros auxiliares junto al `.3dm` (`.rhl`, `.3dmbak`): añadidos a `.gitignore`. Rhino bloquea el fichero activo (no borrar/renombrar el `.3dm` abierto).
- [H] Grasshopper 1 y 2 aparecen en `get_context` (lienzos cerrados). Su uso real: sin probar (V10).

## Pendiente / problemas

- [H] **`pip install` falla por SSL** (`CERTIFICATE_VERIFY_FAILED`, certificado intermedio no confiable, típico de proxy/antivirus con inspección HTTPS). El venv `C:\dev\venvs\textura` está creado, **sin OpenCV/numpy/pytest**. No he desactivado la verificación SSL ni usado `--trusted-host` sin permiso del usuario (ver pregunta en la sesión).
- [?] Alternativa a `run_python`/puente (rhinocode, RhinoCompute): no hizo falta; el puente funciona.
- [H] Q4 resuelta por el usuario: sin cronómetro por ahora; los tiempos son solo informativos.
- [S] Q3: el único evaluador por ahora es el usuario; las imágenes de SP-2/SP-3 aún sin aportar.

## Actualización: dependencias instaladas

- [H] Con permiso del usuario, `pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org` (solo en el venv `C:\dev\venvs\textura`): OpenCV 5.0.0, numpy 2.5.4, pytest 9.2.0. La verificación SSL sigue activa en el resto del sistema; solo se omitió para esa instalación.

## Veredicto

Criterio SP-0 (**ciclo editar → ejecutar → ver sin pasos manuales**): **cumplido** con el puente. Modo de trabajo para el resto: scripts Python enviados con `run_python`, geometría de prueba guardada en `cases/` y `spikes/`, comprobación visual con `get_viewport_image`; el procesado de imagen queda en Python externo (venv) comunicando por ficheros, tal como se aprobó.
