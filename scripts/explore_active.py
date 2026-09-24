"""Prueba fetch_active_contracts contra la API real (contrato §A7).

No redacta nada: no toca documento_proveedor, solo confirma que las filas
que llegan cumplen la regla de "contrato activo".
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from secop_agent.connector import fetch_active_contracts  # noqa: E402
from secop_agent.definitions import is_active  # noqa: E402

PREVIEW_COLUMNS = ["id_contrato", "nombre_entidad", "estado_contrato", "fecha_de_fin_del_contrato"]


def main() -> None:
    result = fetch_active_contracts(limit=5)

    print(f"Filas recibidas: {len(result.rows)}")
    print(f"URL: {result.url}\n")

    for row in result.rows:
        preview = {col: row.get(col) for col in PREVIEW_COLUMNS}
        confirmed = is_active(row.get("estado_contrato", ""), row.get("fecha_de_fin_del_contrato", ""))
        print(preview)
        print(f"  -> is_active() confirma activo: {confirmed}\n")


if __name__ == "__main__":
    main()
