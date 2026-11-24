"""Kontrak API publik untuk Frontend: contracts/public-api.openapi.json dibuat dari response model.

Bila tes ini gagal setelah perubahan yang disengaja, perbarui berkasnya:
    UPDATE_CONTRACT=1 .venv/bin/python -m pytest tests/test_public_contract.py
"""

import copy
import json
import os
from pathlib import Path

CONTRACT = Path(__file__).resolve().parent.parent / "contracts" / "public-api.openapi.json"


def _refs(node, found):
    if isinstance(node, dict):
        if "$ref" in node:
            found.add(node["$ref"].rsplit("/", 1)[-1])
        for value in node.values():
            _refs(value, found)
    elif isinstance(node, list):
        for value in node:
            _refs(value, found)


def public_contract(app):
    spec = app.openapi()
    paths = copy.deepcopy({p: v for p, v in spec["paths"].items() if p.startswith("/api/public/")})
    for methods in paths.values():
        for op in methods.values():
            op["responses"].pop("422", None)  # bentuk galat sebenarnya ada di README, bukan bawaan FastAPI
    schemas = spec["components"]["schemas"]
    used, found = set(), set()
    _refs(paths, found)
    while found - used:
        pending = found - used
        used |= pending
        for name in pending:
            _refs(schemas[name], found)
    return {
        "openapi": spec["openapi"],
        "info": {"title": "Japri API publik (read-only)", "version": "1"},
        "paths": paths,
        "components": {"schemas": {n: schemas[n] for n in sorted(used)}},
    }


def test_kontrak_publik_sama_dengan_berkas_yang_dibagikan_ke_frontend(app):
    current = json.dumps(public_contract(app), indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if os.environ.get("UPDATE_CONTRACT"):
        CONTRACT.write_text(current)
    assert CONTRACT.read_text() == current


def test_kontrak_tidak_memuat_field_kontak(app):
    text = json.dumps(public_contract(app)["components"])
    for forbidden in ("phone", "telegram", "chat_id", "email", "created_by"):
        assert forbidden not in text
