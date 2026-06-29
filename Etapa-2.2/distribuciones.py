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
    # Se escala cada valor U∈(0,1) al intervalo [a,b] mediante la transformación lineal
    return [a + gcl.siguiente() * (b - a) for _ in range(n)]


def uniforme_rechazo(a, b, n, semilla):
    """Genera n muestras de U(a,b) por Método de Rechazo.
    Para U(a,b) el ratio f/g = 1, por lo que nunca se rechaza ningún candidato."""
    gcl = GeneradorGCL(semilla=semilla)
    gcl_criterio = GeneradorGCL(semilla=semilla + 1)  # segundo generador independiente
    muestras = []
    while len(muestras) < n:
        # Se genera un candidato uniformemente en [a,b]
        x = a + gcl.siguiente() * (b - a)
        # Se evalúa el criterio de aceptación u₂ ≤ f(x)/(c·g(x))
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
        # Transformación de coordenadas polares: R² = -2ln(u₁) y θ = 2πu₂
        z1 = math.sqrt(-2 * math.log(u1)) * math.cos(2 * math.pi * u2)
        z2 = math.sqrt(-2 * math.log(u1)) * math.sin(2 * math.pi * u2)
        # Se traslada y escala: X = μ + σ·Z para obtener N(μ, σ²)
        muestras.append(mu + sigma * z1)
        if len(muestras) < n:
            muestras.append(mu + sigma * z2)
    return muestras


def normal_rechazo(mu, sigma, n, semilla):
    """Genera n muestras de N(mu, sigma²) por Método de Rechazo.
    Envolvente: Exp(1). Eficiencia: ~76%. Simetría asignada por U3."""
    gcl1 = GeneradorGCL(semilla=semilla)      # genera candidatos desde Exp(1)
    gcl2 = GeneradorGCL(semilla=semilla + 1)  # evalúa criterio de aceptación
    gcl3 = GeneradorGCL(semilla=semilla + 2)  # asigna aleatoriamente el signo
    muestras = []
    while len(muestras) < n:
        # Generador de candidatos Y ~ Exp(1) mediante transformada inversa
        y = -math.log(gcl1.siguiente())
        # Criterio de aceptación: u₂ ≤ exp(-(y-1)²/2) = f⁺(y)/(c·g(y))
        if gcl2.siguiente() <= math.exp(-(y - 1) ** 2 / 2):
            # Se asigna aleatoriamente el signo aprovechando la simetría de N(0,1)
            z = y if gcl3.siguiente() < 0.5 else -y
            # Se escala y traslada: X = μ + σ·Z
            muestras.append(mu + sigma * z)
    return muestras
