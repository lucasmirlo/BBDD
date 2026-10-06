"""
Práctica 1: Generación de datos sintéticos y almacenamiento de información
Autores: Iñaki Gutiérrez-Mantilla López y Lucas Miranda Lopez

Persistencia en Parquet: un fichero por conjunto de datos, escritos por lotes.
"""

import os

import pyarrow as pa
import pyarrow.parquet as pq

from .base import Estrategia

# Esquemas explícitos: si se infirieran del primer lote, una columna con todo None quedaría como tipo null
ESQUEMA_USUARIOS = pa.schema([
    ('dni', pa.string()), ('nombre', pa.string()), ('email', pa.string()),
    ('movil', pa.string()), ('telefono_fijo', pa.string()), ('direccion', pa.string()),
    ('ciudad', pa.string()), ('codigo_postal', pa.string()), ('provincia', pa.string()),
])
ESQUEMA_VEHICULOS = pa.schema([
    ('matricula', pa.string()), ('bastidor', pa.string()), ('anio', pa.int32()),
    ('fabricante', pa.string()), ('modelo', pa.string()), ('categoria', pa.string()),
    ('usuario_dni', pa.string()),
])


class EstrategiaParquet(Estrategia):
    TAM_LOTE = 10000

    def guardar(self, generador, ruta_base):
        os.makedirs(f"{ruta_base}/parquet", exist_ok=True)
        lote_u, lote_v = [], []

        with pq.ParquetWriter(f'{ruta_base}/parquet/usuarios.parquet', ESQUEMA_USUARIOS) as wu, \
             pq.ParquetWriter(f'{ruta_base}/parquet/vehiculos.parquet', ESQUEMA_VEHICULOS) as wv:
            for u, vs in generador:
                lote_u.append(u)
                lote_v.extend(vs)
                if len(lote_u) >= self.TAM_LOTE:
                    self._escribir_lote(lote_u, lote_v, wu, wv)
            self._escribir_lote(lote_u, lote_v, wu, wv)

    def _escribir_lote(self, lu, lv, wu, wv):
        if lu: wu.write_table(pa.Table.from_pylist(lu, schema=ESQUEMA_USUARIOS))
        if lv: wv.write_table(pa.Table.from_pylist(lv, schema=ESQUEMA_VEHICULOS))
        lu.clear(); lv.clear()
