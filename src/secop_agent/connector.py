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

# Columnas que el contrato de interfaz (§A8) permite exponer. `documento_proveedor`
# se incluye porque hace falta para calcular supplier_key (§A6.1), pero es un dato
# sensible de paso: nunca debe salir tal cual en ninguna respuesta ni archivo guardado.
SELECTED_COLUMNS = [
    "id_contrato",
    "proceso_de_compra",
    "nombre_entidad",
    "nit_entidad",
    "modalidad_de_contratacion",
    "tipo_de_contrato",
    "valor_del_contrato",
    "valor_pagado",
    "fecha_de_firma",
    "fecha_de_inicio_del_contrato",
    "fecha_de_fin_del_contrato",
    "estado_contrato",
    "proveedor_adjudicado",
    "tipodocproveedor",
    "documento_proveedor",
    "urlproceso",
    "ultima_actualizacion",
]


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
    select: list[str] | None = None,
    timeout: int = 30,
) -> FetchResult:
    """Consulta contratos con SoQL. `where` y `order` usan la sintaxis de SoQL.

    `select` pide `$select` a la API de Socrata para que el servidor devuelva
    solo esas columnas (en vez de las 82 del dataset completo).

    Ejemplo (verifica antes los nombres de columnas con scripts/explore.py):
        fetch_contracts(limit=20, where="valor_del_contrato > 1000000000")
    """
    params: dict = {"$limit": limit, "$offset": offset}
    if where:
        params["$where"] = where
    if order:
        params["$order"] = order
    if select:
        params["$select"] = ",".join(select)

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


def _escape_soql_string(value: str) -> str:
    """Escapa comillas simples para usar `value` dentro de un literal SoQL ('...')."""
    return value.replace("'", "''")


def fetch_active_contracts(
    limit: int = 10,
    entity_name: str | None = None,
    order: str | None = None,
    offset: int = 0,
    timeout: int = 30,
) -> FetchResult:
    """Contratos activos (contrato de interfaz §A7): `estado_contrato` es
    exactamente "En ejecución" y `fecha_de_fin_del_contrato` es hoy o futura.

    "Hoy" se calcula en el momento de la llamada, nunca una fecha fija.
    `entity_name`, si se pasa, agrega `nombre_entidad = '...'` al mismo
    `$where` con AND.
    """
    today_utc = datetime.now(timezone.utc).strftime("%Y-%m-%dT00:00:00.000")
    clauses = [
        f"estado_contrato = '{_escape_soql_string('En ejecución')}'",
        f"fecha_de_fin_del_contrato >= '{today_utc}'",
    ]
    if entity_name:
        clauses.append(f"nombre_entidad = '{_escape_soql_string(entity_name)}'")

    return fetch_contracts(
        limit=limit,
        where=" AND ".join(clauses),
        order=order,
        offset=offset,
        select=SELECTED_COLUMNS,
        timeout=timeout,
    )


def fetch_contracts_selected(
    limit: int = 10,
    where: str | None = None,
    order: str | None = None,
    offset: int = 0,
    timeout: int = 30,
) -> FetchResult:
    """Como `fetch_contracts`, pero solo pide las columnas de `SELECTED_COLUMNS`
    (contrato de interfaz §A8), usando `$select` para que el filtrado ocurra
    en el servidor.
    """
    return fetch_contracts(
        limit=limit,
        where=where,
        order=order,
        offset=offset,
        select=SELECTED_COLUMNS,
        timeout=timeout,
    )
