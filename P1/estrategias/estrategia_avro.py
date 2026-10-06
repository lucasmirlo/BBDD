"""
Práctica 1: Generación de datos sintéticos y almacenamiento de información
Autores: Iñaki Gutiérrez-Mantilla López y Lucas Miranda Lopez
"""

import os

from fastavro import parse_schema
from fastavro.write import Writer

from .base import Estrategia

# Avro exige esquema; telefono_fijo admite null porque no todos los usuarios tienen fijo
CAMPOS_USUARIO = [
    {'name': 'dni', 'type': 'string'},
    {'name': 'nombre', 'type': 'string'},
    {'name': 'email', 'type': 'string'},
    {'name': 'movil', 'type': 'string'},
    {'name': 'telefono_fijo', 'type': ['null', 'string'], 'default': None},
    {'name': 'direccion', 'type': 'string'},
    {'name': 'ciudad', 'type': 'string'},
    {'name': 'codigo_postal', 'type': 'string'},
    {'name': 'provincia', 'type': 'string'},
]
ESQUEMA_VEHICULO = {
    'type': 'record', 'name': 'Vehiculo', 'namespace': 'bdia.p1',
    'fields': [
        {'name': 'matricula', 'type': 'string'},
        {'name': 'bastidor', 'type': 'string'},
        {'name': 'anio', 'type': 'int'},
        {'name': 'fabricante', 'type': 'string'},
        {'name': 'modelo', 'type': 'string'},
        {'name': 'categoria', 'type': 'string'},
        {'name': 'usuario_dni', 'type': 'string'},
    ],
}
ESQUEMA_USUARIO = {
    'type': 'record', 'name': 'Usuario', 'namespace': 'bdia.p1', 'fields': CAMPOS_USUARIO,
}
ESQUEMA_ANIDADO = {
    'type': 'record', 'name': 'UsuarioConVehiculos', 'namespace': 'bdia.p1',
    'fields': CAMPOS_USUARIO + [
        {'name': 'vehiculos', 'type': {'type': 'array', 'items': ESQUEMA_VEHICULO}},
    ],
}


class EstrategiaAvro(Estrategia):
    def guardar(self, generador, ruta_base):
        os.makedirs(f"{ruta_base}/avro", exist_ok=True)
        with open(f'{ruta_base}/avro/datos_anidados.avro', 'wb') as fa, \
             open(f'{ruta_base}/avro/usuarios.avro', 'wb') as fu, \
             open(f'{ruta_base}/avro/vehiculos.avro', 'wb') as fv:
            # Writer permite escribir registro a registro (fastavro agrupa internamente en bloques)
            wa = Writer(fa, parse_schema(ESQUEMA_ANIDADO))
            wu = Writer(fu, parse_schema(ESQUEMA_USUARIO))
            wv = Writer(fv, parse_schema(ESQUEMA_VEHICULO))
            for u, vs in generador:
                wa.write({**u, 'vehiculos': vs})
                wu.write(u)
                for v in vs:
                    wv.write(v)
            for w in (wa, wu, wv):
                w.flush()
