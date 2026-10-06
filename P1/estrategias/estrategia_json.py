"""
Práctica 1: Generación de datos sintéticos y almacenamiento de información
Autores: Iñaki Gutiérrez-Mantilla López y Lucas Miranda Lopez

Persistencia en JSONL de los dos modos pedidos, en una sola pasada del generador:
  - Anidado: un único fichero con los vehículos dentro de cada usuario.
  - Referenciado: un fichero por conjunto de datos, enlazados por usuario_dni.

Se usa JSON Lines (un objeto por línea) en lugar de un array JSON porque permite
escribir registro a registro sin mantener todo el conjunto en memoria, y leerlo
igualmente en streaming.
"""

import os
import json

from .base import Estrategia


class EstrategiaJSON(Estrategia):
    def guardar(self, generador, ruta_base):
        os.makedirs(f"{ruta_base}/json", exist_ok=True)
        with open(f'{ruta_base}/json/datos_anidados.jsonl', 'w', encoding='utf-8') as fa, \
             open(f'{ruta_base}/json/usuarios.jsonl', 'w', encoding='utf-8') as fu, \
             open(f'{ruta_base}/json/vehiculos.jsonl', 'w', encoding='utf-8') as fv:
            for u, vs in generador:
                # Modo anidado: estructura jerárquica usuario -> vehiculos
                fa.write(json.dumps({**u, 'vehiculos': vs}, ensure_ascii=False) + '\n')
                # Modo referenciado
                fu.write(json.dumps(u, ensure_ascii=False) + '\n')
                for v in vs:
                    fv.write(json.dumps(v, ensure_ascii=False) + '\n')
