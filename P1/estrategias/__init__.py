"""
Práctica 1: Generación de datos sintéticos y almacenamiento de información
Autores: Iñaki Gutiérrez-Mantilla López y Lucas Miranda Lopez

Estrategias de persistencia y Factory Method para seleccionarlas.

Para añadir un formato o SGBD nuevo basta con crear su módulo con una subclase de
Estrategia y registrarlo aquí; el resto de la aplicación no cambia.
"""

from importlib import import_module

from .base import Estrategia

# Registro formato -> (módulo, clase). Los módulos se importan solo al pedirlos, así que
# la falta de un driver (p. ej. psycopg2) no impide usar el resto de formatos.
ESTRATEGIAS = {
    'csv': ('estrategia_csv', 'EstrategiaCSV'),
    'parquet': ('estrategia_parquet', 'EstrategiaParquet'),
    'json': ('estrategia_json', 'EstrategiaJSON'),
    'avro': ('estrategia_avro', 'EstrategiaAvro'),
    'sqlite': ('estrategia_sqlite', 'EstrategiaSQLite'),
    'postgres': ('estrategia_postgres', 'EstrategiaPostgres'),
    'mongodb': ('estrategia_mongo', 'EstrategiaMongo'),
}

# Estrategias que guardan en un servidor y no en el directorio de salida
SGBD_SERVIDOR = {'postgres', 'mongodb'}


def obtener_estrategia(formato, uri=None):
    entrada = ESTRATEGIAS.get(formato.lower())
    if not entrada:
        return None
    modulo, clase = entrada
    return getattr(import_module(f'.{modulo}', __name__), clase)(uri)
