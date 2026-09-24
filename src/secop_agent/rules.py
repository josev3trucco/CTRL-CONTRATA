"""Reglas de análisis sobre contratos ya descargados (contrato §A5).

Todas las funciones de este módulo operan en Python puro sobre filas que ya
trae `SELECTED_COLUMNS`; ninguna vuelve a llamar a la API.
"""

from __future__ import annotations

from datetime import datetime, timezone

from secop_agent.connector import SELECTED_COLUMNS
from secop_agent.definitions import ACTIVE_STATUS, parse_date

# Valores de relleno conocidos en el dataset real (case-sensitive, tal como
# aparecen). Cadena vacía y None se tratan aparte como "empty".
PLACEHOLDER_VALUES = {"No definido", "Sin Descripcion", "No Definido"}

# id_contrato es el identificador mismo, documento_proveedor es sensible (no
# se reporta su valor) y urlproceso es un objeto anidado: ninguno aplica al
# chequeo de missing_information.
_MISSING_INFO_FIELDS = [
    field
    for field in SELECTED_COLUMNS
    if field not in {"id_contrato", "documento_proveedor", "urlproceso"}
]


def date_anomalies(rows: list[dict]) -> list[dict]:
    """Detecta inconsistencias de fechas (contrato §5.5) en `rows`.

    Tipos implementados: ENDED_BUT_IN_EXECUTION, END_BEFORE_START,
    SIGNED_AFTER_START, MISSING_DATE. Un mismo contrato puede tener varias
    anomalías a la vez.
    """
    today_utc = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    results = []
    for row in rows:
        signed_raw = row.get("fecha_de_firma")
        start_raw = row.get("fecha_de_inicio_del_contrato")
        end_raw = row.get("fecha_de_fin_del_contrato")
        status = row.get("estado_contrato")

        signed = parse_date(signed_raw)
        start = parse_date(start_raw)
        end = parse_date(end_raw)

        anomalies = []

        if status == ACTIVE_STATUS and end is not None and end < today_utc:
            anomalies.append("ENDED_BUT_IN_EXECUTION")

        if end is not None and start is not None and end < start:
            anomalies.append("END_BEFORE_START")

        if signed is not None and start is not None and signed > start:
            anomalies.append("SIGNED_AFTER_START")

        if signed is None or start is None or end is None:
            anomalies.append("MISSING_DATE")

        # TODO: requiere duracion_del_contrato, fuera de SELECTED_COLUMNS (DURATION_MISMATCH)

        if anomalies:
            results.append(
                {
                    "contract_id": row.get("id_contrato"),
                    "entity_name": row.get("nombre_entidad"),
                    "anomalies": anomalies,
                    "dates": {
                        "signed_at": signed_raw,
                        "start_date": start_raw,
                        "end_date": end_raw,
                    },
                    "status": status,
                }
            )

    return results


def missing_information(rows: list[dict]) -> list[dict]:
    """Detecta campos vacíos o con valores de relleno (contrato §5.4),
    solo sobre las columnas de `SELECTED_COLUMNS` (excepto `id_contrato`,
    `documento_proveedor` y `urlproceso`).
    """
    results = []
    for row in rows:
        missing = []
        for field in _MISSING_INFO_FIELDS:
            value = row.get(field)
            if value is None or value == "":
                missing.append({"field": field, "issue": "empty", "value_seen": value})
            elif value in PLACEHOLDER_VALUES:
                missing.append({"field": field, "issue": "placeholder", "value_seen": value})

        if missing:
            results.append(
                {
                    "contract_id": row.get("id_contrato"),
                    "missing": missing,
                    # TODO: sugerencias desde otras instancias del proveedor, requiere supplier_key
                    "suggestions": [],
                }
            )

    return results
