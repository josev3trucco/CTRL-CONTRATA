"""Pruebas simples de supplier_key (sin pytest, el repo todavía no lo usa).

Corre: python scripts/test_identity.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from secop_agent.identity import (  # noqa: E402
    SUPPLIER_KEY_ENV_VAR,
    get_supplier_key_secret,
    supplier_key,
)

FAKE_KEY = b"clave-de-prueba-no-real"


def test_misma_entrada_misma_llave() -> None:
    a = supplier_key("CC", "123456789", FAKE_KEY)
    b = supplier_key("CC", "123456789", FAKE_KEY)
    assert a == b, f"esperaba llaves iguales, obtuve {a!r} != {b!r}"
    assert a.startswith("hmac-sha256:")
    print("OK: misma entrada + misma clave -> misma llave")


def test_entradas_distintas_llaves_distintas() -> None:
    a = supplier_key("CC", "123456789", FAKE_KEY)
    b = supplier_key("CC", "987654321", FAKE_KEY)
    c = supplier_key("NIT", "123456789", FAKE_KEY)
    assert a != b, "documentos distintos no deberían dar la misma llave"
    assert a != c, "tipos de documento distintos no deberían dar la misma llave"
    print("OK: entradas distintas -> llaves distintas")


def test_sin_variable_de_entorno_falla() -> None:
    import os

    original = os.environ.pop(SUPPLIER_KEY_ENV_VAR, None)
    try:
        try:
            get_supplier_key_secret()
        except RuntimeError:
            print("OK: sin variable de entorno -> RuntimeError (esperado)")
        else:
            raise AssertionError(
                f"esperaba RuntimeError sin {SUPPLIER_KEY_ENV_VAR}, no falló"
            )
    finally:
        if original is not None:
            os.environ[SUPPLIER_KEY_ENV_VAR] = original


def main() -> None:
    test_misma_entrada_misma_llave()
    test_entradas_distintas_llaves_distintas()
    test_sin_variable_de_entorno_falla()
    print("\nTodas las pruebas pasaron.")


if __name__ == "__main__":
    main()
