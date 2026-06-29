"""
mm1_simulador.py
════════════════════════════════════════════════════════
Motor de Simulación de Eventos Discretos (DES) para
modelos M/M/1 y M/M/1/K, junto con las fórmulas
teóricas analíticas.

TP Simulación — UTN Rosario — Ingeniería en Sistemas
Referencias:
  · Averill M. Law, "Simulation Modeling and Analysis", 5ta ed.
  · AnyLogic, "The Art of Process-Centric Modeling"
════════════════════════════════════════════════════════
"""

import heapq
import random
import numpy as np
from collections import deque
from scipy import stats


# ════════════════════════════════════════════════════════
# 1.  FÓRMULAS TEÓRICAS
# ════════════════════════════════════════════════════════

def teoria_mm1(lam: float, mu: float) -> dict:
    """
    Métricas analíticas del modelo M/M/1 con cola infinita.

    Sólo válido para ρ = λ/μ < 1  (sistema estable).
    Para ρ ≥ 1 el sistema es inestable y las fórmulas divergen.

    Fórmulas
    ────────
      ρ   = λ / μ
      L   = ρ / (1 − ρ)          promedio de clientes en sistema
      Lq  = ρ² / (1 − ρ)         promedio de clientes en cola
      W   = 1 / (μ − λ)          tiempo promedio en sistema
      Wq  = λ / [μ(μ − λ)]       tiempo promedio en cola
      P(n)= (1 − ρ) · ρⁿ         probabilidad de n clientes en sistema

    Parámetros
    ----------
    lam : tasa de arribo   λ  [clientes / unidad de tiempo]
    mu  : tasa de servicio μ  [clientes / unidad de tiempo]

    Retorna
    -------
    dict con claves: rho, L, Lq, W, Wq, Pn (callable), estable
    """
    rho = lam / mu

    if rho >= 1.0:
        return {
            "rho": rho, "L": None, "Lq": None,
            "W": None,  "Wq": None, "Pn": None,
            "estable": False
        }

    L   = rho / (1.0 - rho)
    Lq  = rho**2 / (1.0 - rho)
    W   = 1.0 / (mu - lam)
    Wq  = lam / (mu * (mu - lam))
    Pn  = lambda n: (1.0 - rho) * rho**n   # P(N = n)

    return {
        "rho": rho, "L": L, "Lq": Lq,
        "W": W,     "Wq": Wq, "Pn": Pn,
        "estable": True
    }


def teoria_mm1k(lam: float, mu: float, K_total: int) -> dict:
    """
    Métricas analíticas del modelo M/M/1/K con cola finita.

    K_total = capacidad TOTAL del sistema (servidor + cola).
    Si la consigna dice "cola de tamaño k", entonces K_total = k + 1.
    Válido para cualquier ρ (sistema siempre estable con cola finita).

    Fórmulas
    ────────
      ρ      = λ / μ
      P(0)   = (1 − ρ) / (1 − ρ^(K+1))   si ρ ≠ 1
      P(0)   = 1 / (K + 1)                si ρ = 1
      P(n)   = P(0) · ρⁿ                  0 ≤ n ≤ K
      P_den  = P(K)                        probabilidad de denegación
      λ_ef   = λ · (1 − P(K))             tasa efectiva de arribo
      L      = Σ n·P(n)  para n=0..K
      Lq     = Σ (n−1)·P(n)  para n=1..K
      W      = L / λ_ef
      Wq     = Lq / λ_ef

    Parámetros
    ----------
    lam     : tasa de arribo λ
    mu      : tasa de servicio μ
    K_total : capacidad total del sistema  (≥ 1)
    """
    rho = lam / mu

    if abs(rho - 1.0) < 1e-9:
        # Caso especial ρ = 1: distribución uniforme sobre los estados
        P0 = 1.0 / (K_total + 1)
        Pn = lambda n: P0 if 0 <= n <= K_total else 0.0
    else:
        P0 = (1.0 - rho) / (1.0 - rho ** (K_total + 1))
        Pn = lambda n: P0 * rho**n if 0 <= n <= K_total else 0.0

    Pk     = Pn(K_total)                   # probabilidad de denegación
    lam_ef = lam * (1.0 - Pk)             # tasa efectiva
    rho_sv = 1.0 - Pn(0)                  # utilización real del servidor

    L  = sum(n * Pn(n)       for n in range(K_total + 1))
    Lq = sum((n - 1) * Pn(n) for n in range(1, K_total + 1))

    W  = L  / lam_ef if lam_ef > 1e-12 else float("inf")
    Wq = Lq / lam_ef if lam_ef > 1e-12 else float("inf")

    return {
        "rho":        rho,
        "rho_sv":     rho_sv,
        "L":          L,
        "Lq":         Lq,
        "W":          W,
        "Wq":         Wq,
        "Pn":         Pn,
        "denial_prob": Pk,
        "lam_ef":     lam_ef,
        "K_total":    K_total,
        "estable":    True
    }


# ════════════════════════════════════════════════════════
# 2.  MOTOR DE SIMULACIÓN DE EVENTOS DISCRETOS
# ════════════════════════════════════════════════════════

def simular_mm1(
    lam: float,
    mu: float,
    K_total: int = None,
    tiempo_sim: float = 5_000.0,
    semilla: int = None,
    n_muestras: int = 600,
) -> dict:
    """
    Ejecuta una corrida de simulación de eventos discretos para M/M/1
    o M/M/1/K usando tiempos exponenciales (proceso de Poisson).

    Eventos modelados
    -----------------
    'A'  → Arribo de cliente
    'D'  → Salida (fin de servicio) de cliente

    Estadísticas recolectadas
    -------------------------
    · Time-average  (área bajo la curva / T):  L, Lq, ρ
    · Sample-average (media de cada cliente):  W, Wq
    · Distribución de estados P(n)             (time-average)
    · Denegación de servicio                   (fracción rechazados)

    Parámetros
    ----------
    lam        : tasa de arribo
    mu         : tasa de servicio
    K_total    : capacidad total del sistema (None = infinita)
    tiempo_sim : duración de la corrida
    semilla    : semilla aleatoria para reproducibilidad
    n_muestras : puntos en la historia temporal (para graficar)
    """
    rng = random.Random(semilla)

    # ── Estado del sistema ─────────────────────────────────────────
    cola               = deque()    # tiempos de arribo de clientes en espera
    servidor_ocupado   = False
    arribo_en_servicio = None       # cuando llegó el cliente actual
    inicio_servicio    = None       # cuando empezó a ser atendido
    n = 0                           # clientes totales en sistema
    t = 0.0

    # ── Acumuladores para estadísticas de área (time-average) ──────
    area_n    = 0.0
    area_nq   = 0.0
    area_busy = 0.0
    t_estado  = {}                  # {estado_n: tiempo_acumulado}

    # ── Estadísticas de muestra por cliente ────────────────────────
    tiempos_sistema = []
    tiempos_cola    = []

    # ── Contadores ─────────────────────────────────────────────────
    n_arribos    = 0
    n_atendidos  = 0
    n_rechazados = 0

    # ── Historia temporal (submuestreada a n_muestras puntos) ──────
    intervalo   = tiempo_sim / n_muestras
    prox_sample = intervalo
    hist_t  = [0.0]
    hist_n  = [0]
    hist_nq = [0]

    # ── Lista de eventos ───────────────────────────────────────────
    eventos = []
    heapq.heappush(eventos, (rng.expovariate(lam), "A"))

    # ── Función auxiliar: acumular área ────────────────────────────
    def acumular(t0: float, t1: float) -> None:
        nonlocal area_n, area_nq, area_busy
        dt = t1 - t0
        nq = max(0, n - (1 if servidor_ocupado else 0))
        area_n    += n  * dt
        area_nq   += nq * dt
        area_busy += dt if servidor_ocupado else 0.0
        t_estado[n] = t_estado.get(n, 0.0) + dt

    # ── Loop principal ─────────────────────────────────────────────
    while eventos:
        t_ev, tipo = heapq.heappop(eventos)

        # ── Fin de simulación ──────────────────────────────────────
        if t_ev > tiempo_sim:
            acumular(t, tiempo_sim)
            # Completar historia hasta tiempo_sim
            nq_final = max(0, n - (1 if servidor_ocupado else 0))
            while prox_sample <= tiempo_sim + intervalo * 0.5:
                hist_t.append(min(prox_sample, tiempo_sim))
                hist_n.append(n)
                hist_nq.append(nq_final)
                prox_sample += intervalo
            break

        # ── Registrar muestras de historia para [t, t_ev] ─────────
        nq_actual = max(0, n - (1 if servidor_ocupado else 0))
        while prox_sample <= t_ev:
            hist_t.append(prox_sample)
            hist_n.append(n)
            hist_nq.append(nq_actual)
            prox_sample += intervalo

        acumular(t, t_ev)
        t = t_ev

        # ══ EVENTO: ARRIBO ═════════════════════════════════════════
        if tipo == "A":
            n_arribos += 1

            # Programar próximo arribo
            t_sig = t + rng.expovariate(lam)
            if t_sig <= tiempo_sim:
                heapq.heappush(eventos, (t_sig, "A"))

            # ¿Sistema lleno? → rechazar
            if K_total is not None and n >= K_total:
                n_rechazados += 1

            else:
                n += 1
                if not servidor_ocupado:
                    # Servidor libre → atención inmediata
                    servidor_ocupado   = True
                    arribo_en_servicio = t
                    inicio_servicio    = t
                    heapq.heappush(eventos, (t + rng.expovariate(mu), "D"))
                else:
                    # Servidor ocupado → entrar a cola (FIFO)
                    cola.append(t)

        # ══ EVENTO: SALIDA ══════════════════════════════════════════
        elif tipo == "D":
            n_atendidos += 1

            # Registrar tiempos del cliente que sale
            if arribo_en_servicio is not None:
                tiempos_sistema.append(t - arribo_en_servicio)
                tiempos_cola.append(inicio_servicio - arribo_en_servicio)

            n -= 1

            if cola:
                # Atender al siguiente en cola
                sig_arribo         = cola.popleft()
                arribo_en_servicio = sig_arribo
                inicio_servicio    = t
                servidor_ocupado   = True
                heapq.heappush(eventos, (t + rng.expovariate(mu), "D"))
            else:
                servidor_ocupado   = False
                arribo_en_servicio = None
                inicio_servicio    = None

    # ── Métricas finales ───────────────────────────────────────────
    L   = area_n    / tiempo_sim
    Lq  = area_nq   / tiempo_sim
    rho = area_busy / tiempo_sim

    W   = float(np.mean(tiempos_sistema)) if tiempos_sistema else 0.0
    Wq  = float(np.mean(tiempos_cola))    if tiempos_cola    else 0.0

    max_n  = max(t_estado.keys()) if t_estado else 0
    Pn_sim = {i: t_estado.get(i, 0.0) / tiempo_sim for i in range(max_n + 1)}

    denial = n_rechazados / n_arribos if n_arribos > 0 else 0.0

    return {
        "L": L, "Lq": Lq, "W": W, "Wq": Wq, "rho": rho,
        "Pn":           Pn_sim,
        "denial_prob":  denial,
        "n_arribos":    n_arribos,
        "n_atendidos":  n_atendidos,
        "n_rechazados": n_rechazados,
        "hist": {"t": hist_t, "n": hist_n, "nq": hist_nq},
    }


# ════════════════════════════════════════════════════════
# 3.  CORRIDA DE EXPERIMENTOS (RÉPLICAS)
# ════════════════════════════════════════════════════════

def correr_experimento(
    lam: float,
    mu: float,
    K_total: int = None,
    tiempo_sim: float = 5_000.0,
    n_corridas: int = 10,
    semilla_base: int = 42,
) -> dict:
    """
    Ejecuta n_corridas réplicas independientes y devuelve estadísticas
    agregadas con intervalo de confianza del 95 % (distribución t).

    Cada réplica usa semilla = semilla_base + i  (i = 0..n_corridas-1),
    garantizando independencia y reproducibilidad.

    Retorna
    -------
    dict  {métrica: {media, std, ic_inf, ic_sup, valores}}
    Además incluye 'hist' y 'Pn' de la primera corrida (para gráficas).
    """
    corridas = []
    for i in range(n_corridas):
        r = simular_mm1(
            lam, mu,
            K_total    = K_total,
            tiempo_sim = tiempo_sim,
            semilla    = semilla_base + i,
        )
        corridas.append(r)

    metricas = ["L", "Lq", "W", "Wq", "rho", "denial_prob"]
    resumen  = {}

    for met in metricas:
        vals   = np.array([r[met] for r in corridas])
        media  = float(np.mean(vals))
        desv   = float(np.std(vals, ddof=1)) if n_corridas > 1 else 0.0
        t_crit = stats.t.ppf(0.975, df=max(n_corridas - 1, 1))
        margen = t_crit * desv / np.sqrt(n_corridas)

        resumen[met] = {
            "media":   media,
            "std":     desv,
            "ic_inf":  media - margen,
            "ic_sup":  media + margen,
            "valores": vals.tolist(),
        }

    # Historia de la primera corrida; P(n) promediado sobre todas las réplicas
    all_keys = set()
    for r in corridas:
        all_keys.update(r["Pn"].keys())
    avg_pn = {n: float(np.mean([r["Pn"].get(n, 0.0) for r in corridas]))
              for n in all_keys}

    resumen["hist"]      = corridas[0]["hist"]
    resumen["Pn"]        = avg_pn
    resumen["n_corridas"] = n_corridas

    return resumen
