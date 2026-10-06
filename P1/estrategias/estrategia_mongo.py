"""
Práctica 1: Generación de datos sintéticos y almacenamiento de información
Autores: Iñaki Gutiérrez-Mantilla López y Lucas Miranda Lopez
"""

from pymongo import MongoClient

from .base import Estrategia


class EstrategiaMongo(Estrategia):
    TAM_LOTE = 10000
    URI_POR_DEFECTO = 'mongodb://localhost:27017/bdia'

    def guardar(self, generador, ruta_base):
        # La URI incluye host, puerto, credenciales y base de datos: mongodb://user:pass@host:port/bd
        cliente = MongoClient(self.uri or self.URI_POR_DEFECTO)
        try:
            col = cliente.get_default_database('bdia')['usuarios']
            col.drop()  # Se recrea la colección en cada ejecución

            lote = []
            for u, vs in generador:
                lote.append({'_id': u['dni'], **u, 'vehiculos': vs})
                if len(lote) >= self.TAM_LOTE:
                    col.insert_many(lote); lote.clear()
            if lote: col.insert_many(lote)

            # Índice para búsquedas por matrícula dentro del array embebido
            col.create_index('vehiculos.matricula')
        finally:
            cliente.close()
