# secop-agent

Lee datos de contratos públicos de **SECOP II** (datos abiertos de Colombia Compra Eficiente, publicados en datos.gov.co) para analizarlos con un agente de IA.

**Estado:** paso 1, conector de datos. El agente (LLM) viene después.

## Fuente de datos

- Dataset: *SECOP II - Contratos Electrónicos*
- Portal: datos.gov.co, identificador `jbjy-vk9h`
- Acceso: API de Socrata (SODA), lenguaje de consulta SoQL
- No requiere cuenta. Un *app token* gratuito es opcional y sube el límite de peticiones.

## Requisitos

- Python 3.12
- Conexión a internet

## Uso

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# opcional: token de aplicación de Socrata
export SOCRATA_APP_TOKEN="tu_token"

python scripts/explore.py
```

`explore.py` trae 5 contratos, imprime las columnas reales del dataset y guarda la respuesta cruda en `data/raw/` junto con su procedencia (URL, parámetros y hora de descarga).

## Estructura

```
src/secop_agent/connector.py   # conector: pide datos a la API y registra la procedencia
scripts/explore.py             # primer contacto con el dataset
data/                          # descargas locales (no se sube a Git)
```

## Notas

- El dataset tiene millones de filas. Usa siempre `limit` y filtros (`where`) para que el filtrado ocurra en el servidor.
- Verifica los nombres de columnas con `explore.py` antes de escribir filtros.

## Siguientes pasos

1. Elegir las columnas que importan y escribir filtros `where`.
2. Agregar el agente: el modelo decide qué consulta hacer (tool calling) y resume los resultados citando las filas.
