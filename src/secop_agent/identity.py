"""Identidad del proveedor (contrato de interfaz §A6.1).

El contrato exige que tipo + número de documento del proveedor nunca salgan
en texto plano. En su lugar se calcula una llave HMAC-SHA-256 con una clave
secreta que solo vive en la variable de entorno CTRL_CONTRATA_SUPPLIER_KEY.
"""

from __future__ import annotations

import hashlib
import hmac
import os

SUPPLIER_KEY_ENV_VAR = "CTRL_CONTRATA_SUPPLIER_KEY"


def get_supplier_key_secret() -> bytes:
    """Lee la clave secreta de HMAC desde la variable de entorno.

    Nunca hay una clave por defecto: si la variable no existe, falla.
    """
    value = os.environ.get(SUPPLIER_KEY_ENV_VAR)
    if not value:
        raise RuntimeError(
            f"Falta la variable de entorno {SUPPLIER_KEY_ENV_VAR}: "
            "no hay clave por defecto para calcular supplier_key."
        )
    return value.encode("utf-8")


def supplier_key(doc_type: str, doc_number: str, key: bytes) -> str:
    """Calcula la llave de identidad del proveedor (nunca el documento en claro).

    Normaliza `doc_type` y `doc_number` (mayúsculas, sin espacios) antes de
    concatenarlos siempre en el mismo orden, y devuelve
    "hmac-sha256:" + hexdigest del HMAC-SHA-256 sobre ese texto con `key`.
    """
    normalized_type = doc_type.strip().upper().replace(" ", "")
    normalized_number = doc_number.strip().upper().replace(" ", "")
    message = f"{normalized_type}:{normalized_number}".encode("utf-8")

    digest = hmac.new(key, message, hashlib.sha256).hexdigest()
    return f"hmac-sha256:{digest}"
