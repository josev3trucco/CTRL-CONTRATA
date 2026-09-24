"""Pruebas simples de build_response (sin pytest, sin llamar a la API).

Corre: python scripts/test_response.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from secop_agent.connector import DATASET_ID, FetchResult  # noqa: E402
from secop_agent.response import CONTRACT_VERSION, build_response  # noqa: E402

FAKE_FETCH_RESULT = FetchResult(
    rows=[{"id_contrato": "TEST-1"}],
    url="https://www.datos.gov.co/resource/jbjy-vk9h.json?%24limit=1",
    params={"$limit": 1, "$offset": 0},
    fetched_at="2026-09-20T18:00:00+00:00",
)


def test_forma_esperada_ok() -> None:
    response = build_response(
        request_id="test-001",
        fetch_results=[FAKE_FETCH_RESULT],
        result=[{"contract_id": "TEST-1"}],
    )

    assert response["contract_version"] == CONTRACT_VERSION
    assert response["request_id"] == "test-001"
    assert response["status"] == "ok"
    assert response["provenance"]["dataset_id"] == DATASET_ID
    assert response["provenance"]["queries"] == [
        {
            "url": FAKE_FETCH_RESULT.url,
            "params": FAKE_FETCH_RESULT.params,
            "fetched_at": FAKE_FETCH_RESULT.fetched_at,
        }
    ]
    assert response["definitions"]["active"]
    assert response["result"] == [{"contract_id": "TEST-1"}]
    assert response["truncated"] is False
    assert response["warnings"] == []
    assert response["errors"] == []
    print("OK: sobre de respuesta con forma esperada y status 'ok'")


def test_status_error_con_errors() -> None:
    response = build_response(
        request_id="test-002",
        fetch_results=[FAKE_FETCH_RESULT],
        result=[],
        errors=["algo salió mal"],
    )
    assert response["status"] == "error", response["status"]
    print("OK: status 'error' cuando errors no está vacía")


def test_truncated_con_max_items() -> None:
    response = build_response(
        request_id="test-003",
        fetch_results=[FAKE_FETCH_RESULT],
        result=[{"contract_id": "A"}, {"contract_id": "B"}],
        max_items=2,
    )
    assert response["truncated"] is True, response["truncated"]

    response_sin_truncar = build_response(
        request_id="test-004",
        fetch_results=[FAKE_FETCH_RESULT],
        result=[{"contract_id": "A"}],
        max_items=2,
    )
    assert response_sin_truncar["truncated"] is False
    print("OK: truncated True/False según max_items")


def main() -> None:
    test_forma_esperada_ok()
    test_status_error_con_errors()
    test_truncated_con_max_items()
    print("\nTodas las pruebas pasaron.")


if __name__ == "__main__":
    main()
