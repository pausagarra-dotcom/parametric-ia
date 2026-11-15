# Prova del catàleg: cada fitxa compleix l'esquema, el nom del fitxer coincideix amb l'id,
# i totes les rutes que cita existeixen. Sense dependencies (validador propi del subconjunt
# d'esquema JSON que fem servir). Entorn: C:\dev\venvs\textura -> python -m pytest -q APP/cataleg
import json, os, re, glob
import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
SCHEMA = json.load(open(os.path.join(HERE, "esquema.json"), encoding="utf-8"))
TYPES = {"string": str, "number": (int, float), "integer": int, "boolean": bool, "object": dict, "array": list, "null": type(None)}


def resolve(ref):
    node = SCHEMA
    for part in ref.lstrip("#/").split("/"):
        node = node[part]
    return node


def validate(v, s, path="$"):
    errs = []
    if "$ref" in s:
        return validate(v, resolve(s["$ref"]), path)
    if "const" in s and v != s["const"]:
        errs.append("%s: ha de ser %r" % (path, s["const"]))
    if "enum" in s and v not in s["enum"]:
        errs.append("%s: %r no és a %r" % (path, v, s["enum"]))
    if "type" in s:
        ts = s["type"] if isinstance(s["type"], list) else [s["type"]]
        ok = any(isinstance(v, TYPES[t]) and not (t in ("number", "integer") and isinstance(v, bool)) for t in ts)
        if not ok:
            return errs + ["%s: tipus %s, esperat %s" % (path, type(v).__name__, ts)]
    if isinstance(v, str) and "pattern" in s and not re.search(s["pattern"], v):
        errs.append("%s: %r no compleix %s" % (path, v, s["pattern"]))
    if isinstance(v, dict):
        props = s.get("properties", {})
        for r in s.get("required", []):
            if r not in v:
                errs.append("%s: falta «%s»" % (path, r))
        for k, x in v.items():
            if k in props:
                errs += validate(x, props[k], path + "." + k)
            elif s.get("additionalProperties") is False:
                errs.append("%s: camp no previst «%s»" % (path, k))
    if isinstance(v, list) and "items" in s:
        for i, x in enumerate(v):
            errs += validate(x, s["items"], "%s[%d]" % (path, i))
    return errs


FILES = sorted(glob.glob(os.path.join(HERE, "textures", "*.json")) + glob.glob(os.path.join(HERE, "solucions", "*.json")))


def paths_in(d):
    keys = ("carpeta", "definicio", "formula", "referencies", "codi", "captures", "font")
    for k in keys:
        v = d.get(k)
        for p in (v if isinstance(v, list) else [v]):
            if isinstance(p, str):
                yield p


@pytest.mark.parametrize("f", FILES, ids=[os.path.basename(f) for f in FILES])
def test_fitxa(f):
    d = json.load(open(f, encoding="utf-8"))
    errs = validate(d, SCHEMA["$defs"][d.get("tipus", "?")])
    assert not errs, "\n".join(errs)
    assert os.path.splitext(os.path.basename(f))[0] == d["id"], "el nom del fitxer ha de ser l'id"
    falten = [p for p in paths_in(d) if not os.path.exists(os.path.join(ROOT, p))]
    assert not falten, "rutes que no existeixen: %s" % falten


def test_textures_de_les_solucions_existeixen():
    ids = {json.load(open(f, encoding="utf-8"))["id"] for f in glob.glob(os.path.join(HERE, "textures", "*.json"))}
    for f in glob.glob(os.path.join(HERE, "solucions", "*.json")):
        d = json.load(open(f, encoding="utf-8"))
        assert set(d["textures"]) <= ids, "%s cita textures que no són al catàleg" % d["id"]


def test_cada_textura_lliurada_te_fitxa():
    carpetes = {os.path.basename(p) for p in glob.glob(os.path.join(ROOT, "textures", "[0-9][0-9]_*")) if os.path.isdir(p)}
    fitxes = {os.path.splitext(os.path.basename(f))[0] for f in glob.glob(os.path.join(HERE, "textures", "*.json"))}
    assert carpetes <= fitxes, "textures sense fitxa: %s" % sorted(carpetes - fitxes)
