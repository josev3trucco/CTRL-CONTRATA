"""Prueba fetch_contracts_selected: trae pocas filas con $select y muestra qué llegó.

documento_proveedor se pide a la API (hace falta para supplier_key, ver
src/secop_agent/identity.py) pero es un dato sensible de paso: nunca se imprime
ni se guarda tal cual. Aquí solo se confirma que llegó, sin mostrar su valor.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from secop_agent.connector import fetch_contracts_selected  # noqa: E402

SENSITIVE_COLUMNS = {"documento_proveedor"}


def redact(row: dict) -> dict:
    return {
        key: ("<redactado>" if key in SENSITIVE_COLUMNS else value)
        for key, value in row.items()
    }


def main() -> None:
    result = fetch_contracts_selected(limit=5)

    columns = sorted({key for row in result.rows for key in row})
    print(f"Filas recibidas: {len(result.rows)}")
    print(f"Columnas pedidas ({len(columns)}): {columns}")
    print(f"URL: {result.url}")

    if result.rows:
        print("\nPrimera fila (documento_proveedor redactado):")
        print(json.dumps(redact(result.rows[0]), indent=2, ensure_ascii=False))

    out_dir = ROOT / "data" / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_file = out_dir / f"secop2_contratos_selected_{stamp}.json"
    payload = {
        "source_url": result.url,
        "params": result.params,
        "fetched_at": result.fetched_at,
        "rows": [redact(row) for row in result.rows],
    }
    out_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nGuardado en: {out_file.relative_to(ROOT)} (documento_proveedor redactado)")


if __name__ == "__main__":
    main()
