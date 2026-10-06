"""
Práctica 1: Generación de datos sintéticos y almacenamiento de información
Autores: Iñaki Gutiérrez-Mantilla López y Lucas Miranda Lopez

Punto de entrada por línea de comandos. La conexión a los SGBD servidor se indica
con una URI (--uri) que incluye host, puerto, credenciales y base de datos.
"""

import time
import argparse
from faker import Faker

from proveedor import ProveedorEspana
from generador import cargar_datos_base, generador_datos
from estrategias import ESTRATEGIAS, SGBD_SERVIDOR, obtener_estrategia


def main():
    parser = argparse.ArgumentParser(description="Generador de Datos Sintéticos BDIA")
    parser.add_argument('-n', '--num_usuarios', type=int, required=True, help="Número de usuarios a generar")
    parser.add_argument('-f', '--formato', type=str, required=True, choices=list(ESTRATEGIAS), help="Formato de salida o SGBD")
    parser.add_argument('-o', '--output', type=str, default='datasets', help="Directorio base de salida (formatos de fichero y SQLite)")
    parser.add_argument('--uri', type=str,
                        help="URI de conexión para postgres o mongodb, p. ej. mongodb://user:pass@localhost:27017/bdia "
                             "(por defecto mongodb://localhost:27017/bdia y postgresql://postgres@localhost:5432/bdia)")
    args = parser.parse_args()

    # Inicialización
    print(f"Iniciando generación de {args.num_usuarios} registros en formato {args.formato}...")
    fake = Faker('es_ES')
    fake.add_provider(ProveedorEspana)
    catalogo, geo_data, dict_provincias = cargar_datos_base()

    # Generación y guardado
    gen = generador_datos(args.num_usuarios, catalogo, geo_data, dict_provincias, fake)
    estrategia = obtener_estrategia(args.formato, args.uri)

    inicio = time.perf_counter()
    estrategia.guardar(gen, args.output)
    duracion = time.perf_counter() - inicio

    destino = "el servidor" if args.formato in SGBD_SERVIDOR else f"la carpeta: {args.output}/{args.formato}"
    print(f"Proceso completado en {duracion:.2f} s. Datos guardados en {destino}")

if __name__ == "__main__":
    main()
