class Jugador:
    # Tabla de pagos por categoría de apuesta
    PAGOS = {
        "color": 2,      # 1 a 1 (recupera lo apostado + gana lo mismo)
        "paridad": 2,    # 1 a 1
        "tercio": 3,     # 2 a 1 (recupera lo apostado + gana el doble)
        "fila": 3,       # 2 a 1
        "numero": 36     # 35 a 1 (recupera lo apostado + gana 35 veces)
    }

    def __init__(self, nombre, presupuesto, categoria="color", valor="rojo"):
        self.nombre = nombre
        self.categoria_apuesta = categoria
        self.valor_apuesta = valor

        # Manejo del presupuesto ilimitado usando infinito (float('inf'))
        if presupuesto == "ilimitado" or presupuesto == float('inf'):
            self.presupuesto = float('inf')
        else:
            self.presupuesto = float(presupuesto)

        self.ultimo_resultado_gano = None
        self.ultima_apuesta_monto = 0
        self.en_bancarrota = False

    def obtener_monto_apuesta(self):
        """Método abstracto que deben implementar las subclases."""
        raise NotImplementedError(
            "La estrategia debe definir el monto a apostar.")

    def actualizar_estado_estrategia(self):
        """Método abstracto para recalcular la apuesta según si se ganó o perdió."""
        raise NotImplementedError(
            "La estrategia debe actualizarse tras el resultado.")

    def jugar_turno(self, ruleta, resultado_giro):
        """
        El jugador calcula su apuesta, se descuenta de su presupuesto, 
        evalúa si ganó con la ruleta y actualiza su saldo.
        """
        if self.en_bancarrota:
            return {"monto": 0, "estado": "Bancarrota"}

        monto_ideal = self.obtener_monto_apuesta()

        # Verificar si el jugador tiene saldo suficiente
        if self.presupuesto < monto_ideal:
            if self.presupuesto <= 0:
                self.en_bancarrota = True
                return {"monto": 0, "estado": "Sin fondos"}
            # Si no le alcanza para la estrategia, hace un "All-in" con lo que le queda
            monto_real = self.presupuesto
        else:
            monto_real = monto_ideal

        # 1. Hacer la apuesta (descontar del presupuesto)
        self.presupuesto -= monto_real
        self.ultima_apuesta_monto = monto_real

        # 2. Evaluar el resultado del giro de la ruleta
        gano = ruleta.evaluar_apuesta(
            self.categoria_apuesta, self.valor_apuesta, resultado_giro)
        self.ultimo_resultado_gano = gano


        # 3. Cobrar si ganó (pago según la categoría de apuesta)
        if gano:
            pago = self.PAGOS.get(self.categoria_apuesta, 2)
            self.presupuesto += (monto_real * pago)

        # 4. Ajustar la estrategia para el próximo turno
        self.actualizar_estado_estrategia()

        return {"monto_apostado": monto_real, "gano": gano, "saldo_actual": self.presupuesto}


# ==========================================
# ESTRATEGIAS DE JUEGO (Subclases)
# ==========================================

class Martingala(Jugador):
    """Duplica la apuesta cada vez que pierde. Vuelve a la base si gana."""

    def __init__(self, nombre, presupuesto, apuesta_base=10, **kwargs):
        super().__init__(nombre, presupuesto, **kwargs)
        self.apuesta_base = apuesta_base
        self.apuesta_actual = apuesta_base

    def obtener_monto_apuesta(self):
        return self.apuesta_actual

    def actualizar_estado_estrategia(self):
        if self.ultimo_resultado_gano:
            self.apuesta_actual = self.apuesta_base
        else:
            self.apuesta_actual *= 2


class Fibonacci(Jugador):
    """Sigue la secuencia de Fibonacci. Avanza 1 paso si pierde, retrocede 2 pasos si gana."""

    def __init__(self, nombre, presupuesto, unidad_base=10, **kwargs):
        super().__init__(nombre, presupuesto, **kwargs)
        self.unidad_base = unidad_base
        self.secuencia = [1, 1]
        self.indice = 0

    def _obtener_fibonacci(self, n):
        # Genera la secuencia sobre la marcha si es necesario
        while len(self.secuencia) <= n:
            self.secuencia.append(self.secuencia[-1] + self.secuencia[-2])
        return self.secuencia[n]

    def obtener_monto_apuesta(self):
        return self.unidad_base * self._obtener_fibonacci(self.indice)

    def actualizar_estado_estrategia(self):
        if self.ultimo_resultado_gano:
            # Retrocede 2 posiciones, mínimo 0
            self.indice = max(0, self.indice - 2)
        else:
            self.indice += 1  # Avanza 1 posición


class Paroli(Jugador):
    """(Martingala Inversa) Duplica al ganar. Vuelve a la base al perder o tras 3 victorias seguidas."""

    def __init__(self, nombre, presupuesto, apuesta_base=10, limite_victorias=3, **kwargs):
        super().__init__(nombre, presupuesto, **kwargs)
        self.apuesta_base = apuesta_base
        self.apuesta_actual = apuesta_base
        self.victorias_consecutivas = 0
        self.limite_victorias = limite_victorias

    def obtener_monto_apuesta(self):
        return self.apuesta_actual

    def actualizar_estado_estrategia(self):
        if self.ultimo_resultado_gano:
            self.victorias_consecutivas += 1
            if self.victorias_consecutivas >= self.limite_victorias:
                # Reiniciar tras alcanzar el límite de ganancias
                self.apuesta_actual = self.apuesta_base
                self.victorias_consecutivas = 0
            else:
                self.apuesta_actual *= 2
        else:
            self.apuesta_actual = self.apuesta_base
            self.victorias_consecutivas = 0


class DAlembert(Jugador):
    """Aumenta 1 unidad al perder. Disminuye 1 unidad al ganar."""

    def __init__(self, nombre, presupuesto, unidad_base=10, **kwargs):
        super().__init__(nombre, presupuesto, **kwargs)
        self.unidad_base = unidad_base
        self.apuesta_actual = unidad_base

    def obtener_monto_apuesta(self):
        return self.apuesta_actual

    def actualizar_estado_estrategia(self):
        if self.ultimo_resultado_gano:
            # Disminuye 1 unidad, no puede ser menor que la unidad base
            self.apuesta_actual = max(
                self.unidad_base, self.apuesta_actual - self.unidad_base)
        else:
            # Aumenta 1 unidad
            self.apuesta_actual += self.unidad_base
