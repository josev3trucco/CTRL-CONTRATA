"""Primer contacto con SECOP II: trae pocas filas, muestra columnas y guarda la respuesta."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from secop_agent.connector import fetch_contracts  # noqa: E402


def main() -> None:
    result = fetch_contracts(limit=5)

    columns = sorted({key for row in result.rows for key in row})
    print(f"Filas recibidas: {len(result.rows)}")
    print(f"Columnas ({len(columns)}):")
    for name in columns:
        print(f"  - {name}")

    if result.rows:
        print("\nPrimera fila:")
        print(json.dumps(result.rows[0], indent=2, ensure_ascii=False))

    out_dir = ROOT / "data" / "raw"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out_file = out_dir / f"secop2_contratos_{stamp}.json"
    payload = {
        "source_url": result.url,
        "params": result.params,
        "fetched_at": result.fetched_at,
        "rows": result.rows,
    }
    out_file.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nGuardado en: {out_file.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
