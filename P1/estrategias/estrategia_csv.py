"""
Práctica 1: Generación de datos sintéticos y almacenamiento de información
Autores: Iñaki Gutiérrez-Mantilla López y Lucas Miranda Lopez

Persistencia en CSV: un fichero por conjunto de datos, enlazados por usuario_dni.
"""

import os
import csv

from .base import Estrategia


class EstrategiaCSV(Estrategia):
    def guardar(self, generador, ruta_base):
        os.makedirs(f"{ruta_base}/csv", exist_ok=True)
        with open(f'{ruta_base}/csv/usuarios.csv', 'w', newline='', encoding='utf-8') as fu, \
             open(f'{ruta_base}/csv/vehiculos.csv', 'w', newline='', encoding='utf-8') as fv:

            wu, wv = None, None
            for u, vs in generador:
                if not wu:
                    wu = csv.DictWriter(fu, fieldnames=u.keys()); wu.writeheader()
                wu.writerow(u)
                for v in vs:
                    if not wv:
                        wv = csv.DictWriter(fv, fieldnames=v.keys()); wv.writeheader()
                    wv.writerow(v)
