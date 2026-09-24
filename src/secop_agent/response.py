"""Sobre de respuesta común a todas las operaciones del agente (contrato §A4)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from secop_agent.connector import DATASET_ID, FetchResult

CONTRACT_VERSION = "0.2.1"
AGENT_VERSION = "0.1.0"  # sin mecanismo de versionado todavía, fijo por ahora
RULES_VERSION = "0.1.0"
SOURCE_NAME = "SECOP II - Contratos Electrónicos"

DEFINITIONS = {
    "active": "estado_contrato = 'En ejecución' y fecha_de_fin_del_contrato >= fecha de consulta",
}


def build_response(
    request_id: str,
    fetch_results: list[FetchResult],
    result: Any,
    warnings: list | None = None,
    errors: list | None = None,
    max_items: int | None = None,
) -> dict:
    """Arma el sobre de respuesta común (contrato §A4) a partir de:

    - `request_id`: identificador de la solicitud, provisto por quien llama.
    - `fetch_results`: uno o más `FetchResult` de `connector.py`, usados para
      construir `provenance.queries`.
    - `result`: el contenido específico de la operación.
    - `warnings` / `errors`: listas opcionales; `status` es "error" si
      `errors` no está vacía.
    - `max_items`: si se pasa y `result` es una lista que llegó a ese
      tamaño, `truncated` es `True`.
    """
    warnings = warnings if warnings is not None else []
    errors = errors if errors is not None else []

    truncated = False
    if max_items is not None and isinstance(result, list):
        truncated = len(result) >= max_items

    queries = [
        {"url": fetch_result.url, "params": fetch_result.params, "fetched_at": fetch_result.fetched_at}
        for fetch_result in fetch_results
    ]

    return {
        "contract_version": CONTRACT_VERSION,
        "request_id": request_id,
        "status": "ok" if not errors else "error",
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "provenance": {
            "source": SOURCE_NAME,
            "dataset_id": DATASET_ID,
            "queries": queries,
            "agent_version": AGENT_VERSION,
            "rules_version": RULES_VERSION,
        },
        "definitions": dict(DEFINITIONS),
        "result": result,
        "truncated": truncated,
        "warnings": warnings,
        "errors": errors,
    }
