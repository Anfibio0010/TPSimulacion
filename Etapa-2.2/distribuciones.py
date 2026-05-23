"""
TP 2.2 - Generadores de Distribuciones de Probabilidad
Universidad Tecnológica Nacional - FRRO  |  Simulación 2026

Referencia: Naylor, T.H. — Técnicas de Simulación en Computadoras, 1982, Cap. 4
"""

import sys
import os
import math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Etapa-2.1'))

from generadores import GeneradorGCL


# ==============================================================================
# DISTRIBUCIÓN UNIFORME CONTINUA  U(a, b)
# ==============================================================================

def uniforme_inversa(a, b, n, semilla):
    """Genera n muestras de U(a,b) por Transformada Inversa: X = a + U*(b-a)."""
    gcl = GeneradorGCL(semilla=semilla)
    return [a + gcl.siguiente() * (b - a) for _ in range(n)]


def uniforme_rechazo(a, b, n, semilla):
    """Genera n muestras de U(a,b) por Método de Rechazo.
    Para U(a,b) el ratio f/g = 1, por lo que nunca se rechaza ningún candidato."""
    gcl = GeneradorGCL(semilla=semilla)
    gcl_criterio = GeneradorGCL(semilla=semilla + 1)
    muestras = []
    while len(muestras) < n:
        x = a + gcl.siguiente() * (b - a)
        u2 = gcl_criterio.siguiente()
        if u2 <= 1.0:           # siempre verdadero — incluido para mostrar el mecanismo
            muestras.append(x)
    return muestras


# ==============================================================================
# DISTRIBUCIÓN NORMAL  N(μ, σ²)
# ==============================================================================

def normal_box_muller(mu, sigma, n, semilla):
    """Genera n muestras de N(mu, sigma²) por transformada de Box-Muller.
    Cada iteración produce 2 normales estándar independientes."""
    gcl1 = GeneradorGCL(semilla=semilla)
    gcl2 = GeneradorGCL(semilla=semilla + 1)
    muestras = []
    while len(muestras) < n:
        u1 = gcl1.siguiente()
        u2 = gcl2.siguiente()
        z1 = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
        z2 = math.sqrt(-2 * math.log(u1)) * math.sin(2 * math.pi * u2)
        muestras.append(mu + sigma * z1)
        if len(muestras) < n:
            muestras.append(mu + sigma * z2)
    return muestras


def normal_rechazo(mu, sigma, n, semilla):
    """Genera n muestras de N(mu, sigma²) por Método de Rechazo.
    Envolvente: Exp(1). Eficiencia: ~76%. Simetría asignada por U3."""
    gcl1 = GeneradorGCL(semilla=semilla)
    gcl2 = GeneradorGCL(semilla=semilla + 1)
    gcl3 = GeneradorGCL(semilla=semilla + 2)
    muestras = []
    while len(muestras) < n:
        y = -math.log(gcl1.siguiente())
        if gcl2.siguiente() <= math.exp(-(y - 1) ** 2 / 2):
            z = y if gcl3.siguiente() < 0.5 else -y
            muestras.append(mu + sigma * z)
    return muestras
