"""
Práctica 1: Generación de datos sintéticos y almacenamiento de información
Autores: Iñaki Gutiérrez-Mantilla López y Lucas Miranda Lopez

"""

import os
import sqlite3

from .base import Estrategia


class EstrategiaSQLite(Estrategia):
    def guardar(self, generador, ruta_base):
        os.makedirs(f"{ruta_base}/sqlite", exist_ok=True)
        con = sqlite3.connect(f'{ruta_base}/sqlite/datos.db')
        cur = con.cursor()
        # Se recrean las tablas para que ejecuciones sucesivas no choquen con las claves primarias
        cur.execute("DROP TABLE IF EXISTS vehiculos")
        cur.execute("DROP TABLE IF EXISTS usuarios")
        cur.execute("CREATE TABLE usuarios (dni TEXT PRIMARY KEY, nombre TEXT, email TEXT, movil TEXT, telefono_fijo TEXT, direccion TEXT, ciudad TEXT, codigo_postal TEXT, provincia TEXT)")
        cur.execute("CREATE TABLE vehiculos (matricula TEXT PRIMARY KEY, bastidor TEXT, anio INTEGER, fabricante TEXT, modelo TEXT, categoria TEXT, usuario_dni TEXT REFERENCES usuarios(dni))")

        for u, vs in generador:
            cur.execute("INSERT INTO usuarios VALUES (:dni, :nombre, :email, :movil, :telefono_fijo, :direccion, :ciudad, :codigo_postal, :provincia)", u)
            cur.executemany("INSERT INTO vehiculos VALUES (:matricula, :bastidor, :anio, :fabricante, :modelo, :categoria, :usuario_dni)", vs)
        con.commit()
        con.close()
