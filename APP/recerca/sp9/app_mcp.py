# SP-9: servidor MCP minim (stdio, sense dependencies) amb les accions de l'app.
# En aquesta prova les accions nomes escriuen l'estat a estat.json; a l'app cridaran el servidor de dins de Rhino.
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "estat.json")
DEFAULT = {"textura": "02_placa_quadres", "params": {"CELL": 8.0, "DEPTH": 0.4, "TILT": 0.8, "LIP": 0.3}, "historial": []}

TOOLS = [
    {"name": "llegir_estat", "description": "Torna la textura activa i els valors actuals dels seus sliders.",
     "inputSchema": {"type": "object", "properties": {}, "additionalProperties": False}},
    {"name": "canviar_parametre", "description": "Canvia el valor d'un slider de la textura activa (mm o sense unitat).",
     "inputSchema": {"type": "object", "properties": {"nom": {"type": "string"}, "valor": {"type": "number"},
                                                      "motiu": {"type": "string"}},
                     "required": ["nom", "valor"], "additionalProperties": False}},
]


def load():
    if os.path.exists(STATE):
        return json.load(open(STATE, encoding="utf-8"))
    return json.loads(json.dumps(DEFAULT))


def save(s):
    json.dump(s, open(STATE, "w", encoding="utf-8"), indent=1, ensure_ascii=False)


def call(name, args):
    s = load()
    if name == "llegir_estat":
        return json.dumps({"textura": s["textura"], "params": s["params"]})
    if name == "canviar_parametre":
        n = args["nom"].upper()
        if n not in s["params"]:
            return "Error: el slider %s no existeix. Sliders: %s" % (n, ", ".join(s["params"]))
        old = s["params"][n]; s["params"][n] = float(args["valor"])
        s["historial"].append({"nom": n, "abans": old, "despres": float(args["valor"]), "motiu": args.get("motiu", "")})
        save(s)
        return "%s: %s -> %s" % (n, old, args["valor"])
    return "Error: eina desconeguda"


def send(o):
    sys.stdout.write(json.dumps(o) + "\n"); sys.stdout.flush()


for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    m = json.loads(line); mid = m.get("id"); meth = m.get("method")
    if meth == "initialize":
        send({"jsonrpc": "2.0", "id": mid, "result": {
            "protocolVersion": m["params"].get("protocolVersion", "2025-06-18"),
            "capabilities": {"tools": {}}, "serverInfo": {"name": "app-textures", "version": "0.1"}}})
    elif meth == "tools/list":
        send({"jsonrpc": "2.0", "id": mid, "result": {"tools": TOOLS}})
    elif meth == "tools/call":
        txt = call(m["params"]["name"], m["params"].get("arguments", {}) or {})
        send({"jsonrpc": "2.0", "id": mid, "result": {"content": [{"type": "text", "text": txt}], "isError": txt.startswith("Error")}})
    elif meth == "ping":
        send({"jsonrpc": "2.0", "id": mid, "result": {}})
    elif mid is not None:
        send({"jsonrpc": "2.0", "id": mid, "error": {"code": -32601, "message": "method not found"}})
