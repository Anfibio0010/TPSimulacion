import random
import pandas as pd

class Ruleta:
    def __init__(self):
        # En la ruleta, la distribución de colores no sigue un patrón matemático simple,
        # por lo que definimos los números rojos en un conjunto (set).
        self.numeros_rojos = {1, 3, 5, 7, 9, 12, 14,
                              16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}

    def girar(self):
        """
        Simula el giro de la ruleta (elige un número del 0 al 36) 
        y devuelve un diccionario con las características del número ganador.
        """
        numero = random.randint(0, 36)
        return self._analizar_numero(numero)

    def _analizar_numero(self, numero):
        """Calcula a qué categorías pertenece un número específico."""

        # El 0 es un caso especial: es verde y hace que se pierdan las apuestas a suertes sencillas.
        if numero == 0:
            return {
                "numero": 0,
                "color": "verde",
                "paridad": None,  # No se considera par ni impar para apuestas
                "tercio": None,   # No pertenece a ninguna docena
                "fila": None      # No pertenece a ninguna columna/fila
            }

        # 1. Determinar Color
        color = "rojo" if numero in self.numeros_rojos else "negro"

        # 2. Determinar Paridad
        paridad = "par" if numero % 2 == 0 else "impar"

        # 3. Determinar Tercio (Docenas: 1-12, 13-24, 25-36)
        if 1 <= numero <= 12:
            tercio = 1
        elif 13 <= numero <= 24:
            tercio = 2
        else:
            tercio = 3

        # 4. Determinar Fila (Columnas en el tapete)
        # Los números 1, 4, 7... dan resto 1 al dividir por 3
        # Los números 2, 5, 8... dan resto 2
        # Los números 3, 6, 9... son múltiplos exactos de 3 (resto 0)
        if numero % 3 == 1:
            fila = 1
        elif numero % 3 == 2:
            fila = 2
        else:
            fila = 3

        return {
            "numero": numero,
            "color": color,
            "paridad": paridad,
            "tercio": tercio,
            "fila": fila
        }

    def evaluar_apuesta(self, categoria, valor, resultado_giro):
        """
        Comprueba si una apuesta es ganadora basándose en el giro.
        
        Parámetros:
        - categoria (str): 'numero', 'color', 'paridad', 'tercio', o 'fila'
        - valor (any): Lo que el jugador eligió (ej. 'rojo', 'par', 1, 32)
        - resultado_giro (dict): El resultado devuelto por girar()
        """
        # Si la categoría no existe en nuestro sistema, la apuesta es inválida
        if categoria not in resultado_giro:
            return False

        # Si sale 0 y la apuesta no fue directamente al número 0 o al color verde, se pierde.
        if resultado_giro["numero"] == 0 and categoria not in ["numero", "color"]:
            return False

        # Comprobamos si el valor apostado coincide con la característica del número que salió
        return resultado_giro[categoria] == valor




