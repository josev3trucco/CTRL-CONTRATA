"""Definiciones del contrato de interfaz aplicadas en Python puro sobre filas
ya descargadas, sin llamar a la API.
"""

from __future__ import annotations

from datetime import datetime, timezone

ACTIVE_STATUS = "En ejecución"


def parse_date(value: str | None) -> datetime | None:
    """Interpreta una fecha del dataset real (ISO 8601, formato
    `"2026-09-20T00:00:00.000"` u otro que entienda `datetime.fromisoformat`).

    Devuelve `None` si `value` está vacío, es `None`, o no se puede
    interpretar como fecha, sin lanzar una excepción. Compartida por
    `is_active` y por las reglas de `rules.py` para no duplicar el parseo.
    """
    if not value:
        return None

    try:
        parsed = datetime.fromisoformat(value)
    except (ValueError, TypeError):
        return None

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    return parsed


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

    end_date = parse_date(fecha_de_fin_del_contrato)
    if end_date is None:
        return False

    today_utc = datetime.now(timezone.utc).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return end_date >= today_utc
