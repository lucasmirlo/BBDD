"""
Práctica 1: Generación de datos sintéticos y almacenamiento de información
Autores: Iñaki Gutiérrez-Mantilla López y Lucas Miranda Lopez

Provider personalizado de Faker con datos españoles (DNI, matrículas, bastidores).
"""

from faker.providers import BaseProvider


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
