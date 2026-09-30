"""
Práctica 1: Generación de datos sintéticos y almacenamiento de información
Autores: Iñaki Gutiérrez-Mantilla López y Héctor Rodón Llaberia
"""

import os
import csv
import json
import math
import random
import argparse
import sqlite3
import pyarrow as pa
import pyarrow.parquet as pq
from faker import Faker
from faker.providers import BaseProvider

# 1. PROVIDER PERSONALIZADO FAKER
class ProveedorEspana(BaseProvider):
    def dni_valido(self):
        num = self.random_int(min=11111111, max=99999999)
        return f"{num:08d}-{'TRWAGMYFPDXBNJZSQVHLCKE'[num % 23]}"

    def matricula(self, anio):
        if anio <= 1999:
            prov = self.random_element(["A", "AB", "AL", "AV", "B", "BA", "BI", "BU", "C", "CA", 
                                        "CC", "CE", "CO", "CR", "CS", "CU", "GC", "GE", "GI", "GR", 
                                        "GU", "H", "HU", "IB", "J", "L", "LE", "LO", "LU", "M", "MA", 
                                        "ML", "MU", "NA", "O", "OR", "OU", "P", "PM", "PO", "S", 
                                        "SA", "SE", "SG", "SO", "SS", "T", "TE", "TF", "TO", "V", 
                                        "VA", "VI", "Z", "ZA"])
            return f"{prov}-{self.numerify('####')}-{self.lexify('??', letters='ABCDEFG')}"
        return f"{self.numerify('####')}-{self.lexify('???', letters='BCDFGHJKLMNPRSTVWXYZ')}"

    def bastidor(self):
        return self.lexify('?' * 17, letters='0123456789ABCDEFGHJKLMNPRSTUVWXYZ')

# 2. GENERADOR DE DATOS (YIELD)
def cargar_datos_base():
    with open("vehicles.json", "r", encoding="utf-8") as f:
        catalogo = [
            {"fabricante": f, "modelo": m, "categoria": info["category"],
             "inicio": info["production"][0]["inicio"],
             "fin": info["production"][0]["fin"] if info["production"][0]["fin"] != 9999 else 2026}
            for f, modelos in json.load(f).items() for m, info in modelos.items()
        ]
    with open("codigos_postales_municipios.csv", newline="", encoding="utf-8") as f:
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
            'direccion': fake.street_address(),
            'ciudad': geo["municipio_nombre"], 'codigo_postal': geo["codigo_postal"],
            'provincia': dict_provincias.get(geo["codigo_postal"][:2], "Desconocida")
        }

        num_coches = random.choices([0, 1, 2, 3, 4], weights=pesos_poisson)[0]
        vehiculos = []
        for _ in range(num_coches):
            c = random.choice(catalogo)
            anio = fake.random_int(min=c["inicio"], max=c["fin"])
            vehiculos.append({
                'matricula': fake.matricula(anio), 'bastidor': fake.bastidor(),
                'anio': anio, 'fabricante': c["fabricante"], 'modelo': c["modelo"],
                'categoria': c["categoria"], 'usuario_dni': dni_usuario 
            })
        yield usuario, vehiculos

# 3. PATRÓN STRATEGY (PERSISTENCIA)
class EstrategiaCSV:
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

class EstrategiaParquet:
    def guardar(self, generador, ruta_base):
        os.makedirs(f"{ruta_base}/parquet", exist_ok=True)
        lote_u, lote_v = [], []
        wu, wv = None, None
        
        for u, vs in generador:
            lote_u.append(u)
            lote_v.extend(vs)
            if len(lote_u) >= 10000:
                wu, wv = self._escribir_lote(lote_u, lote_v, wu, wv, ruta_base)
                lote_u.clear(); lote_v.clear()
        
        if lote_u: self._escribir_lote(lote_u, lote_v, wu, wv, ruta_base)
        if wu: wu.close()
        if wv: wv.close()

    def _escribir_lote(self, lu, lv, wu, wv, ruta):
        if lu:
            tb = pa.Table.from_pylist(lu)
            if not wu: wu = pq.ParquetWriter(f'{ruta}/parquet/usuarios.parquet', tb.schema)
            wu.write_table(tb)
        if lv:
            tb = pa.Table.from_pylist(lv)
            if not wv: wv = pq.ParquetWriter(f'{ruta}/parquet/vehiculos.parquet', tb.schema)
            wv.write_table(tb)
        return wu, wv

class EstrategiaJSON:
    def guardar(self, generador, ruta_base):
        os.makedirs(f"{ruta_base}/json", exist_ok=True)
        # JSONL (JSON Lines) es más eficiente para grandes volúmenes y escritura al vuelo
        with open(f'{ruta_base}/json/datos_anidados.jsonl', 'w', encoding='utf-8') as f:
            for u, vs in generador:
                u['vehiculos'] = vs # Estructura jerárquica
                f.write(json.dumps(u, ensure_ascii=False) + '\n')

class EstrategiaSQLite:
    def guardar(self, generador, ruta_base):
        os.makedirs(f"{ruta_base}/sqlite", exist_ok=True)
        con = sqlite3.connect(f'{ruta_base}/sqlite/datos.db')
        cur = con.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS usuarios (dni TEXT PRIMARY KEY, nombre TEXT, email TEXT, movil TEXT, direccion TEXT, ciudad TEXT, codigo_postal TEXT, provincia TEXT)")
        cur.execute("CREATE TABLE IF NOT EXISTS vehiculos (matricula TEXT PRIMARY KEY, bastidor TEXT, anio INTEGER, fabricante TEXT, modelo TEXT, categoria TEXT, usuario_dni TEXT)")
        
        for u, vs in generador:
            cur.execute("INSERT INTO usuarios VALUES (:dni, :nombre, :email, :movil, :direccion, :ciudad, :codigo_postal, :provincia)", u)
            for v in vs:
                cur.execute("INSERT INTO vehiculos VALUES (:matricula, :bastidor, :anio, :fabricante, :modelo, :categoria, :usuario_dni)", v)
        con.commit()
        con.close()

# 4. FACTORY METHOD Y CLI
def obtener_estrategia(formato):
    estrategias = {
        'csv': EstrategiaCSV(),
        'parquet': EstrategiaParquet(),
        'json': EstrategiaJSON(),
        'sqlite': EstrategiaSQLite()
    }
    return estrategias.get(formato.lower())

def main():
    parser = argparse.ArgumentParser(description="Generador de Datos Sintéticos BDIA")
    parser.add_argument('-n', '--num_usuarios', type=int, required=True, help="Número de usuarios a generar")
    parser.add_argument('-f', '--formato', type=str, required=True, choices=['csv', 'parquet', 'json', 'sqlite'], help="Formato de salida o SGBD")
    parser.add_argument('-o', '--output', type=str, default='datasets', help="Directorio base de salida")
    args = parser.parse_args()

    # Inicialización
    print(f"Iniciando generación de {args.num_usuarios} registros en formato {args.formato}...")
    fake = Faker('es_ES')
    fake.add_provider(ProveedorEspana)
    catalogo, geo_data, dict_provincias = cargar_datos_base()
    
    # Generación y guardado
    gen = generador_datos(args.num_usuarios, catalogo, geo_data, dict_provincias, fake)
    estrategia = obtener_estrategia(args.formato)
    
    if estrategia:
        estrategia.guardar(gen, args.output)
        print(f"Proceso completado. Datos guardados en la carpeta: {args.output}/{args.formato}")
    else:
        print("Estrategia no implementada.")

if __name__ == "__main__":
    main()