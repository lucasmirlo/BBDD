"""
Práctica 1: Generación de datos sintéticos y almacenamiento de información
Autores: Iñaki Gutiérrez-Mantilla López y Lucas Miranda Lopez
"""

import psycopg2
from psycopg2.extras import execute_values

from .base import Estrategia

COLS_USUARIO = ['dni', 'nombre', 'email', 'movil', 'telefono_fijo', 'direccion', 'ciudad', 'codigo_postal', 'provincia']
COLS_VEHICULO = ['matricula', 'bastidor', 'anio', 'fabricante', 'modelo', 'categoria', 'usuario_dni']


class EstrategiaPostgres(Estrategia):
    TAM_LOTE = 10000
    URI_POR_DEFECTO = 'postgresql://postgres@localhost:5432/bdia'

    def guardar(self, generador, ruta_base):
        # La URI incluye host, puerto, credenciales y base de datos: postgresql://user:pass@host:port/bd
        con = psycopg2.connect(self.uri or self.URI_POR_DEFECTO)
        try:
            with con, con.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS vehiculos, usuarios")
                cur.execute("""CREATE TABLE usuarios (
                    dni VARCHAR(10) PRIMARY KEY, nombre TEXT NOT NULL, email TEXT, movil VARCHAR(15),
                    telefono_fijo VARCHAR(15), direccion TEXT, ciudad TEXT, codigo_postal CHAR(5), provincia TEXT)""")
                cur.execute("""CREATE TABLE vehiculos (
                    matricula VARCHAR(12) PRIMARY KEY, bastidor CHAR(17) NOT NULL, anio SMALLINT,
                    fabricante TEXT, modelo TEXT, categoria TEXT,
                    usuario_dni VARCHAR(10) NOT NULL REFERENCES usuarios(dni))""")

                # Inserción por lotes con execute_values: muchas filas por sentencia en vez de una a una
                lote_u, lote_v = [], []
                for u, vs in generador:
                    lote_u.append(tuple(u[c] for c in COLS_USUARIO))
                    lote_v.extend(tuple(v[c] for c in COLS_VEHICULO) for v in vs)
                    if len(lote_u) >= self.TAM_LOTE:
                        self._insertar(cur, lote_u, lote_v)
                self._insertar(cur, lote_u, lote_v)
        finally:
            con.close()

    def _insertar(self, cur, lu, lv):
        # Primero usuarios para respetar la clave foránea de vehiculos
        if lu: execute_values(cur, f"INSERT INTO usuarios ({', '.join(COLS_USUARIO)}) VALUES %s", lu)
        if lv: execute_values(cur, f"INSERT INTO vehiculos ({', '.join(COLS_VEHICULO)}) VALUES %s", lv)
        lu.clear(); lv.clear()
