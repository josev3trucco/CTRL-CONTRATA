"""Definiciones del contrato de interfaz aplicadas en Python puro sobre filas
ya descargadas, sin llamar a la API.
"""

from __future__ import annotations

from datetime import datetime, timezone

ACTIVE_STATUS = "En ejecución"


def is_active(estado_contrato: str, fecha_de_fin_del_contrato: str) -> bool:
    """Un contrato está activo (contrato de interfaz §A7) si:

    1. `estado_contrato` es exactamente "En ejecución".
    2. `fecha_de_fin_del_contrato` es hoy o una fecha futura.

    Si `fecha_de_fin_del_contrato` está vacía, es `None`, o no se puede
    interpretar como fecha, devuelve `False` (no se puede confirmar que esté
    vigente) sin lanzar una excepción.
    """
    if estado_contrato != ACTIVE_STATUS:
        return False

    if not fecha_de_fin_del_contrato:
        return False

    try:
        end_date = datetime.fromisoformat(fecha_de_fin_del_contrato)
    except (ValueError, TypeError):
        return False

    if end_date.tzinfo is None:
        end_date = end_date.replace(tzinfo=timezone.utc)

    today_utc = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return end_date >= today_utc
