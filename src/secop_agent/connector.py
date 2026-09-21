"""Conector de SECOP II (datos abiertos de datos.gov.co, API Socrata/SODA).

Un conector hace una sola cosa: pedir datos a una fuente y devolverlos junto
con su procedencia (de dónde y cuándo salieron). No interpreta nada.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone

import requests

DATASET_ID = "jbjy-vk9h"  # SECOP II - Contratos Electrónicos
BASE_URL = f"https://www.datos.gov.co/resource/{DATASET_ID}.json"


@dataclass
class FetchResult:
    """Filas descargadas más su procedencia."""

    rows: list[dict]
    url: str
    params: dict
    fetched_at: str  # ISO 8601, UTC


def fetch_contracts(
    limit: int = 10,
    where: str | None = None,
    order: str | None = None,
    offset: int = 0,
    timeout: int = 30,
) -> FetchResult:
    """Consulta contratos con SoQL. `where` y `order` usan la sintaxis de SoQL.

    Ejemplo (verifica antes los nombres de columnas con scripts/explore.py):
        fetch_contracts(limit=20, where="valor_del_contrato > 1000000000")
    """
    params: dict = {"$limit": limit, "$offset": offset}
    if where:
        params["$where"] = where
    if order:
        params["$order"] = order

    headers = {}
    token = os.environ.get("SOCRATA_APP_TOKEN")
    if token:
        headers["X-App-Token"] = token

    resp = requests.get(BASE_URL, params=params, headers=headers, timeout=timeout)
    resp.raise_for_status()

    return FetchResult(
        rows=resp.json(),
        url=resp.url,
        params=params,
        fetched_at=datetime.now(timezone.utc).isoformat(),
    )
