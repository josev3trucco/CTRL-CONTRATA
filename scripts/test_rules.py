"""Pruebas simples de date_anomalies y missing_information (sin pytest).

Corre: python scripts/test_rules.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from secop_agent.rules import date_anomalies, missing_information  # noqa: E402


def _base_row(contract_id: str, **overrides) -> dict:
    row = {
        "id_contrato": contract_id,
        "proceso_de_compra": "CO1.BDOS.0000000",
        "nombre_entidad": "ENTIDAD DE PRUEBA",
        "nit_entidad": "900000000",
        "modalidad_de_contratacion": "Contratación directa",
        "tipo_de_contrato": "Prestación de servicios",
        "valor_del_contrato": "1000000",
        "valor_pagado": "0",
        "fecha_de_firma": "2026-01-01T00:00:00.000",
        "fecha_de_inicio_del_contrato": "2026-01-05T00:00:00.000",
        "fecha_de_fin_del_contrato": "2026-06-01T00:00:00.000",
        "estado_contrato": "Cerrado",
        "proveedor_adjudicado": "Proveedor de Prueba SAS",
        "tipodocproveedor": "NIT",
        "documento_proveedor": "900123456",
        "urlproceso": {"url": "https://example.com"},
        "ultima_actualizacion": "2026-06-02T00:00:00.000",
    }
    row.update(overrides)
    return row


def test_ended_but_in_execution() -> None:
    row = _base_row(
        "TEST-1",
        estado_contrato="En ejecución",
        fecha_de_firma="2019-01-01T00:00:00.000",
        fecha_de_inicio_del_contrato="2019-06-01T00:00:00.000",
        fecha_de_fin_del_contrato="2020-01-01T00:00:00.000",
    )
    result = date_anomalies([row])
    assert len(result) == 1, f"esperaba 1 contrato con anomalías, obtuve {result!r}"
    assert result[0]["anomalies"] == ["ENDED_BUT_IN_EXECUTION"], result[0]["anomalies"]
    print("OK: En ejecución con fecha de fin pasada -> ENDED_BUT_IN_EXECUTION")


def test_end_before_start() -> None:
    row = _base_row(
        "TEST-2",
        fecha_de_firma="2026-01-01T00:00:00.000",
        fecha_de_inicio_del_contrato="2026-06-01T00:00:00.000",
        fecha_de_fin_del_contrato="2026-01-15T00:00:00.000",
    )
    result = date_anomalies([row])
    assert len(result) == 1
    assert result[0]["anomalies"] == ["END_BEFORE_START"], result[0]["anomalies"]
    print("OK: fecha de fin anterior a fecha de inicio -> END_BEFORE_START")


def test_signed_after_start() -> None:
    row = _base_row(
        "TEST-3",
        fecha_de_firma="2026-07-01T00:00:00.000",
        fecha_de_inicio_del_contrato="2026-06-01T00:00:00.000",
        fecha_de_fin_del_contrato="2027-01-01T00:00:00.000",
    )
    result = date_anomalies([row])
    assert len(result) == 1
    assert result[0]["anomalies"] == ["SIGNED_AFTER_START"], result[0]["anomalies"]
    print("OK: fecha de firma posterior a fecha de inicio -> SIGNED_AFTER_START")


def test_missing_date() -> None:
    row = _base_row("TEST-4", fecha_de_firma=None)
    result = date_anomalies([row])
    assert len(result) == 1
    assert result[0]["anomalies"] == ["MISSING_DATE"], result[0]["anomalies"]
    print("OK: fecha de firma faltante -> MISSING_DATE")


def test_varias_anomalias_a_la_vez() -> None:
    row = _base_row(
        "TEST-4B",
        fecha_de_firma="",
        fecha_de_inicio_del_contrato="2026-06-01T00:00:00.000",
        fecha_de_fin_del_contrato="2026-01-15T00:00:00.000",
    )
    result = date_anomalies([row])
    assert len(result) == 1
    assert set(result[0]["anomalies"]) == {"END_BEFORE_START", "MISSING_DATE"}, result[0]["anomalies"]
    print("OK: firma vacía + fin antes de inicio -> MISSING_DATE y END_BEFORE_START")


def test_sin_anomalias_no_aparece() -> None:
    row = _base_row("TEST-5")
    result = date_anomalies([row])
    assert result == [], f"esperaba lista vacía, obtuve {result!r}"
    print("OK: contrato sin anomalías -> no aparece en la salida")


def test_missing_information_empty() -> None:
    row = _base_row("TEST-6", modalidad_de_contratacion="")
    result = missing_information([row])
    assert len(result) == 1
    entry = next(m for m in result[0]["missing"] if m["field"] == "modalidad_de_contratacion")
    assert entry["issue"] == "empty", entry
    assert result[0]["suggestions"] == []
    print("OK: campo vacío -> issue 'empty'")


def test_missing_information_placeholder() -> None:
    row = _base_row("TEST-7", tipo_de_contrato="No definido")
    result = missing_information([row])
    assert len(result) == 1
    entry = next(m for m in result[0]["missing"] if m["field"] == "tipo_de_contrato")
    assert entry["issue"] == "placeholder", entry
    print("OK: valor de relleno conocido -> issue 'placeholder'")


def test_missing_information_sin_problemas_no_aparece() -> None:
    row = _base_row("TEST-8")
    result = missing_information([row])
    assert result == [], f"esperaba lista vacía, obtuve {result!r}"
    print("OK: contrato sin campos faltantes -> no aparece en la salida")


def main() -> None:
    test_ended_but_in_execution()
    test_end_before_start()
    test_signed_after_start()
    test_missing_date()
    test_varias_anomalias_a_la_vez()
    test_sin_anomalias_no_aparece()
    test_missing_information_empty()
    test_missing_information_placeholder()
    test_missing_information_sin_problemas_no_aparece()
    print("\nTodas las pruebas pasaron.")


if __name__ == "__main__":
    main()
