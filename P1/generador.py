"""
Práctica 1: Generación de datos sintéticos y almacenamiento de información
Autores: Iñaki Gutiérrez-Mantilla López y Lucas Miranda Lopez

Carga de datos base y generador (yield) de usuarios con sus vehículos.
"""

import os
import csv
import json
import math
import random


DIR_DATOS = os.path.dirname(os.path.abspath(__file__))


def cargar_datos_base():
    with open(os.path.join(DIR_DATOS, "vehicles.json"), "r", encoding="utf-8") as f:
        # Se conservan todos los periodos de producción de cada modelo (algunos tienen varios)
        catalogo = [
            {"fabricante": f, "modelo": m, "categoria": info["category"],
             "periodos": [(p["inicio"], p["fin"] if p["fin"] != 9999 else 2026) for p in info["production"]]}
            for f, modelos in json.load(f).items() for m, info in modelos.items()
        ]
    with open(os.path.join(DIR_DATOS, "codigos_postales_municipios.csv"), newline="", encoding="utf-8") as f:
        geo_data = list(csv.DictReader(f))

    dict_provincias = {
        "01": "Álava", "02": "Albacete", "03": "Alicante", "04": "Almería", "05": "Ávila",
        "06": "Badajoz", "07": "Baleares", "08": "Barcelona", "09": "Burgos", "10": "Cáceres",
        "11": "Cádiz", "12": "Castellón", "13": "Ciudad Real", "14": "Córdoba", "15": "La Coruña",
        "16": "Cuenca", "17": "Gerona", "18": "Granada", "19": "Guadalajara", "20": "Guipúzcoa",
        "21": "Huelva", "22": "Huesca", "23": "Jaén", "24": "León", "25": "Lérida",
        "26": "La Rioja", "27": "Lugo", "28": "Madrid", "29": "Málaga", "30": "Murcia",
        "31": "Navarra", "32": "Orense", "33": "Asturias", "34": "Palencia", "35": "Las Palmas",
        "36": "Pontevedra", "37": "Salamanca", "38": "Santa Cruz de Tenerife", "39": "Cantabria",
        "40": "Segovia", "41": "Sevilla", "42": "Soria", "43": "Tarragona", "44": "Teruel",
        "45": "Toledo", "46": "Valencia", "47": "Valladolid", "48": "Vizcaya", "49": "Zamora",
        "50": "Zaragoza", "51": "Ceuta", "52": "Melilla"}
    return catalogo, geo_data, dict_provincias


def generador_datos(n, catalogo, geo_data, dict_provincias, fake):
    pesos_poisson = [(math.exp(-0.9) * (0.9 ** k)) / math.factorial(k) for k in range(5)]
    dominios = ['@uam.es', '@estudiante.uam.es', '@gmail.com']

    for _ in range(n):
        geo = random.choice(geo_data)
        dni_usuario = fake.unique.dni_valido()

        usuario = {
            'dni': dni_usuario, 'nombre': fake.name(),
            'email': f"{fake.user_name()}{random.choice(dominios)}",
            'movil': f"+34 6{fake.numerify('########')}",
            'telefono_fijo': f"+34 9{fake.numerify('########')}" if random.random() < 0.53 else None,
            'direccion': fake.street_address(),
            'ciudad': geo["municipio_nombre"], 'codigo_postal': geo["codigo_postal"],
            'provincia': dict_provincias.get(geo["codigo_postal"][:2], "Desconocida")
        }

        num_coches = random.choices([0, 1, 2, 3, 4], weights=pesos_poisson)[0]
        vehiculos = []
        for _ in range(num_coches):
            c = random.choice(catalogo)
            inicio, fin = random.choice(c["periodos"])
            anio = fake.random_int(min=inicio, max=fin)
            vehiculos.append({
                'matricula': fake.unique.matricula(anio), 'bastidor': fake.bastidor(),
                'anio': anio, 'fabricante': c["fabricante"], 'modelo': c["modelo"],
                'categoria': c["categoria"], 'usuario_dni': dni_usuario
            })
        yield usuario, vehiculos
