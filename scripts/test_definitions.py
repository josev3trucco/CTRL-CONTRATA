"""Pruebas simples de is_active (sin pytest, el repo todavía no lo usa).

Corre: python scripts/test_definitions.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from secop_agent.definitions import is_active  # noqa: E402

FUTURA = "2099-01-01T00:00:00.000"
PASADA = "2020-01-01T00:00:00.000"


def test_en_ejecucion_con_fin_futura() -> None:
    assert is_active("En ejecución", FUTURA) is True
    print("OK: En ejecución + fecha de fin futura -> True")


def test_en_ejecucion_con_fin_pasada() -> None:
    assert is_active("En ejecución", PASADA) is False
    print("OK: En ejecución + fecha de fin pasada -> False")


def test_estado_distinto_con_fin_futura() -> None:
    assert is_active("Cerrado", FUTURA) is False
    print("OK: estado distinto ('Cerrado') + fecha de fin futura -> False")


def test_fin_vacia_o_none() -> None:
    assert is_active("En ejecución", "") is False
    assert is_active("En ejecución", None) is False
    print("OK: fecha de fin vacía o None -> False, sin lanzar error")


def test_fin_formato_inesperado() -> None:
    assert is_active("En ejecución", "no aplica") is False
    print("OK: fecha de fin con formato inesperado -> False, sin lanzar error")


def main() -> None:
    test_en_ejecucion_con_fin_futura()
    test_en_ejecucion_con_fin_pasada()
    test_estado_distinto_con_fin_futura()
    test_fin_vacia_o_none()
    test_fin_formato_inesperado()
    print("\nTodas las pruebas pasaron.")


if __name__ == "__main__":
    main()
