"""Prueba date_anomalies y missing_information contra 20 contratos reales,
y arma una respuesta completa con build_response para cada operación.
"""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from secop_agent.connector import fetch_active_contracts  # noqa: E402
from secop_agent.response import build_response  # noqa: E402
from secop_agent.rules import date_anomalies, missing_information  # noqa: E402


def main() -> None:
    fetch_result = fetch_active_contracts(limit=20)
    print(f"Filas recibidas: {len(fetch_result.rows)}")
    print(f"URL: {fetch_result.url}\n")

    anomalies_result = date_anomalies(fetch_result.rows)
    anomalies_response = build_response(
        request_id="explore-rules-date_anomalies",
        fetch_results=[fetch_result],
        result=anomalies_result,
    )
    print("=== date_anomalies ===")
    print(json.dumps(anomalies_response, indent=2, ensure_ascii=False))

    missing_result = missing_information(fetch_result.rows)
    missing_response = build_response(
        request_id="explore-rules-missing_information",
        fetch_results=[fetch_result],
        result=missing_result,
    )
    print("\n=== missing_information ===")
    print(json.dumps(missing_response, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
