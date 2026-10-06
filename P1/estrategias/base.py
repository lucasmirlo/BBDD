"""
Práctica 1: Generación de datos sintéticos y almacenamiento de información
Autores: Iñaki Gutiérrez-Mantilla López y Lucas Miranda Lopez

Interfaz común del patrón Strategy para la persistencia.
"""

from abc import ABC, abstractmethod


class Estrategia(ABC):
    def __init__(self, uri=None):
        # URI de conexión a un SGBD servidor. Las estrategias de ficheros la ignoran.
        self.uri = uri

    @abstractmethod
    def guardar(self, generador, ruta_base):
        """Consume el generador de (usuario, vehiculos) y persiste los datos en ruta_base."""
