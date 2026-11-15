# SP-9 · Chat local: condiciones de uso (informe, parte 1)

Fecha: 2026-11-15. Leyenda: [H] comprobado en la documentación oficial · [S] suposición · [?] por verificar.

## Qué dice la documentación oficial de Anthropic [H]
1. **Agent SDK** (code.claude.com/docs/en/agent-sdk/overview):
   > «Unless previously approved, Anthropic does not allow third party developers to offer claude.ai login or rate limits for their products, including agents built on the Claude Agent SDK.»
   - Es decir: un producto propio **no puede ofrecer a otras personas** el inicio de sesión de claude.ai (suscripción Pro/Max). Hay que usar una clave de API.
   - El uso del SDK se rige por los *Commercial Terms of Service*.
2. **Modo no interactivo `claude -p`** (code.claude.com/docs/en/headless):
   - Es la forma documentada de usar Claude Code desde un programa: respuestas en JSON o en streaming, continuar conversaciones con `--resume`, permisos por herramienta y servidores MCP con `--mcp-config`.
   - El modo `--bare`, el recomendado para scripts, **no usa la sesión de la suscripción, solo la clave de API**. La documentación anuncia que **pasará a ser el modo por defecto de `-p`**.

## Qué significa para la app
- **Beta, con un solo usuario (Pau) en su propio ordenador:** [S] llamar a `claude -p` con su propia sesión es usar Claude Code personalmente, no ofrecer un inicio de sesión a terceros. Técnicamente funciona hoy, pero:
  - [S] la tendencia es que el uso desde scripts vaya con clave de API (`--bare` por defecto);
  - [?] no hay ninguna frase que autorice explícitamente este caso. Si se quiere certeza, hay que preguntar a Anthropic.
- **Con más usuarios:** **es obligatorio usar una clave de API** (Claude Console, pago por uso). Está claro en la documentación.

## Recomendación [O]
1. **Diseñar el chat para que funcione con clave de API desde el principio.** El motor sería el Agent SDK o `claude -p --bare` con `ANTHROPIC_API_KEY`. Así no habrá que rehacer nada cuando haya más usuarios.
2. Mientras dure la beta personal, **se puede probar con la sesión local de Pau** (`claude -p` sin `--bare`), dejando claro que es provisional.
3. El coste de la API para un solo usuario es bajo. [S] Una conversación para retocar una textura debería costar céntimos; se medirá con `total_cost_usd`, que `claude -p` devuelve en cada respuesta.

## Parte 2: ciclo completo con Claude Code local (2026-11-15) [H]
Se ha usado la sesión local de Pau (`claude -p` sin `--bare`, versión 2.1.197). **Sin clave de API ni pago por uso.**

Archivos:
- `app_mcp.py`: servidor MCP mínimo, sin dependencias, con las acciones `llegir_estat` y `canviar_parametre`. En esta prueba escribe en `estat.json`; en la app llamará al servidor de dentro de Rhino (SP-8).
- `mcp_config.json`: configuración para cargar ese servidor.
- `prova_xat.ps1`: el mensaje de prueba.
- `prova_xat_resposta.json`: la respuesta de Claude.

**Mensaje:** una captura del SP-6 + «los cuadrados se ven demasiado profundos, hazlos un 25 % menos hondos».

**Resultado:**
- Claude lee el estado, llama a `canviar_parametre` (DEPTH de 0,4 a 0,3, con el motivo) y responde: *«He reduït el DEPTH de 0.4 a 0.3 mm (25% menys fondo)…»*.
- `estat.json` guarda el cambio y su historial. ✔

| Medida | Valor |
|---|---|
| Tiempo total (incluido el arranque de Claude Code) | 25,9 s |
| Tiempo de la conversación | 11,3 s, 4 turnos |
| Coste **estimado** que da Claude Code | 0,42 USD |

- ⚠ Con la sesión local este coste no se cobra: cuenta dentro del límite de la suscripción. **Con clave de API sí se cobraría.**
- El coste es alto porque `claude -p` sin `--bare` carga todo el contexto de Claude Code: unos 64 000 tokens de instrucciones y herramientas.
- [S] Con el chat de la app hecho con la API, una instrucción de sistema corta, solo las acciones de la app y la caché de instrucciones, se espera que cueste una fracción de esto. Se medirá antes de activar nada de pago.
- [S] Los ~15 s de arranque desaparecen si la app mantiene una sesión abierta (Agent SDK o `--resume`) en lugar de arrancar Claude Code en cada mensaje.

## Conclusión del SP-9
**El ciclo funciona:** mensaje con captura → Claude → acción de la app → cambio de slider registrado.
- Para la beta personal se puede usar Claude Code local.
- Para más usuarios hará falta clave de API, y antes hay que reducir el contexto para que el coste por mensaje sea bajo.
