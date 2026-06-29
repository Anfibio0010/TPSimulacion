"""
mm1_main.py
════════════════════════════════════════════════════════
Interfaz principal del simulador M/M/1.
Ejecuta los 30 experimentos, imprime tablas comparativas,
genera 6 figuras y exporta CSVs para completar con AnyLogic.

Uso
───
    python mm1_main.py

TP Simulación — UTN Rosario — Ingeniería en Sistemas
════════════════════════════════════════════════════════
"""

import csv
import warnings
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.gridspec import GridSpec

warnings.filterwarnings("ignore")

from mm1_simulador import correr_experimento, teoria_mm1, teoria_mm1k

# ════════════════════════════════════════════════════════
# CONSTANTES GLOBALES
# ════════════════════════════════════════════════════════

RHOS     = [0.25, 0.50, 0.75, 1.00, 1.25]   # factores de carga
KS_COLA  = [0, 2, 5, 10, 50]                 # tamaños de cola (slots de espera)
KS_TOTAL   = [k + 1 for k in KS_COLA]         # capacidad total = K_cola + 1
N_CORRIDAS = 10                               # fijo por consigna

# Paleta de colores por ρ
PALETA = {
    0.25: "#1565C0",   # azul profundo
    0.50: "#2E7D32",   # verde bosque
    0.75: "#E65100",   # naranja quemado
    1.00: "#B71C1C",   # rojo alerta
    1.25: "#4A148C",   # violeta crítico
}

plt.rcParams.update({
    "figure.facecolor":  "#FAFAFA",
    "axes.facecolor":    "#F5F5F5",
    "axes.grid":         True,
    "grid.alpha":        0.35,
    "grid.linestyle":    "--",
    "axes.spines.top":   False,
    "axes.spines.right": False,
    "font.size":         10,
    "axes.titlesize":    10,
    "axes.labelsize":    9,
})


# ════════════════════════════════════════════════════════
# 1.  ENTRADA DE PARÁMETROS
# ════════════════════════════════════════════════════════

def pedir_parametros() -> tuple:
    """Solicita parámetros de configuración con valores por defecto."""
    print()
    print("╔══════════════════════════════════════════════════════╗")
    print("║   SIMULADOR M/M/1 — TP Simulación — UTN Rosario     ║")
    print("╚══════════════════════════════════════════════════════╝")
    print()
    print("  Ingresá los parámetros (Enter = valor por defecto):")
    print()

    DEFS = {"mu": 10.0, "tiempo_sim": 5_000.0, "semilla": 42}

    def leer(prompt: str, tipo, defecto):
        try:
            raw = input(f"    {prompt} [{defecto}]: ").strip()
            return tipo(raw) if raw else defecto
        except (ValueError, EOFError):
            return defecto

    mu         = leer("Tasa de servicio  μ",              float, DEFS["mu"])
    tiempo_sim = leer("Tiempo de simulación [unid. tpo.]", float, DEFS["tiempo_sim"])
    semilla    = leer("Semilla base",                      int,   DEFS["semilla"])

    lams = [round(rho * mu, 4) for rho in RHOS]
    n_exp_total = len(RHOS) * (1 + len(KS_COLA))

    print()
    print(f"  ✔ μ = {mu}  |  T_sim = {tiempo_sim}  |  corridas = {N_CORRIDAS} (fijo)  |  semilla = {semilla}")
    print(f"  ✔ λ: {lams}")
    print(f"  ✔ ρ: {RHOS}")
    print(f"  ✔ K_cola: {KS_COLA}")
    print(f"  ✔ Experimentos totales: {n_exp_total}  (×{N_CORRIDAS} corridas c/u)")
    print()

    return mu, tiempo_sim, semilla


# ════════════════════════════════════════════════════════
# 2.  EJECUCIÓN DE TODOS LOS EXPERIMENTOS
# ════════════════════════════════════════════════════════

def correr_todos(mu, tiempo_sim, semilla):
    """
    Experimento A : M/M/1 cola infinita   → 5 corridas (una por ρ)
    Experimento B : M/M/1/K cola finita   → 25 combos  (5 ρ × 5 K)
    Total: 30 experimentos × n_corridas réplicas
    """
    # ── Experimento A ──────────────────────────────────────────────
    print("  ┌─ Experimento A: M/M/1 cola infinita ─────────────────")
    res_A_sim, res_A_teo = {}, {}

    for rho in RHOS:
        lam = rho * mu
        print(f"  │  ρ={rho:.2f}  λ={lam:.4f} ... ", end="", flush=True)
        res_A_sim[rho] = correr_experimento(
            lam, mu, K_total=None,
            tiempo_sim=tiempo_sim, n_corridas=N_CORRIDAS, semilla_base=semilla
        )
        res_A_teo[rho] = teoria_mm1(lam, mu)
        print("✓")

    print("  └──────────────────────────────────────────────────────")

    # ── Experimento B ──────────────────────────────────────────────
    print("  ┌─ Experimento B: M/M/1/K — 25 combinaciones ──────────")
    res_B = {}   # res_B[rho][K_cola] = {"sim": ..., "teo": ...}

    for rho in RHOS:
        lam = rho * mu
        res_B[rho] = {}
        print(f"  │  ρ={rho:.2f}: ", end="", flush=True)

        for K_cola, K_total in zip(KS_COLA, KS_TOTAL):
            print(f"K={K_cola} ", end="", flush=True)
            sim = correr_experimento(
                lam, mu, K_total=K_total,
                tiempo_sim=tiempo_sim, n_corridas=N_CORRIDAS, semilla_base=semilla
            )
            teo = teoria_mm1k(lam, mu, K_total)
            res_B[rho][K_cola] = {"sim": sim, "teo": teo}
        print("✓")

    print("  └──────────────────────────────────────────────────────")

    return res_A_sim, res_A_teo, res_B


# ════════════════════════════════════════════════════════
# 3.  TABLAS DE RESULTADOS
# ════════════════════════════════════════════════════════

def tabla_A(res_sim, res_teo):
    """Tabla Teórico vs Python — M/M/1 cola infinita."""
    metricas = [
        ("L",   "Promedio en sistema   L"),
        ("Lq",  "Promedio en cola     Lq"),
        ("W",   "Tiempo en sistema     W"),
        ("Wq",  "Tiempo en cola       Wq"),
        ("rho", "Utilización           ρ"),
    ]

    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║       TABLA A — M/M/1 cola infinita: Teórico vs Python (IC 95 %)    ║")
    print("╠══════════════════════════════════════════════════════════════════════╣")

    for clave, nombre in metricas:
        print(f"║  {nombre}")
        print(f"║  {'ρ':>5}  {'Teórico':>10}  {'Simulado':>10}  "
              f"{'IC inf':>10}  {'IC sup':>10}  {'Error':>8}")
        print(f"║  {'─'*5}  {'─'*10}  {'─'*10}  {'─'*10}  {'─'*10}  {'─'*8}")

        for rho in RHOS:
            teo_v = res_teo[rho].get(clave)
            sim_d = res_sim[rho][clave]

            teo_s = f"{teo_v:>10.4f}" if teo_v is not None else "  N/A(ρ≥1)"
            sim_s = f"{sim_d['media']:>10.4f}"
            ic_i  = f"{sim_d['ic_inf']:>10.4f}"
            ic_s  = f"{sim_d['ic_sup']:>10.4f}"

            if teo_v is not None and abs(teo_v) > 1e-10:
                err = abs(sim_d["media"] - teo_v) / abs(teo_v) * 100
                err_s = f"{err:>7.1f}%"
            else:
                err_s = "       —"

            print(f"║  {rho:>5.2f}  {teo_s}  {sim_s}  {ic_i}  {ic_s}  {err_s}")
        print("║")

    print("╚══════════════════════════════════════════════════════════════════════╝")


def tabla_B(res_B):
    """Tabla probabilidad de denegación — M/M/1/K."""
    print()
    print("╔═══════════════════════════════════════════════════════════════╗")
    print("║      TABLA B — M/M/1/K: Probabilidad de denegación           ║")
    print("╠═══════════════════════════════════════════════════════════════╣")
    print(f"║  {'ρ':>5}  {'K_cola':>6}  {'Teórico':>12}  "
          f"{'Simulado':>12}  {'IC inf':>10}  {'Error':>8}")
    print(f"║  {'─'*5}  {'─'*6}  {'─'*12}  {'─'*12}  {'─'*10}  {'─'*8}")

    for rho in RHOS:
        for K_cola in KS_COLA:
            teo = res_B[rho][K_cola]["teo"]["denial_prob"]
            sim = res_B[rho][K_cola]["sim"]["denial_prob"]

            ic_i  = sim["ic_inf"]
            err_s = (f"{abs(sim['media'] - teo) / teo * 100:>7.1f}%"
                     if teo > 1e-10 else "       —")

            print(f"║  {rho:>5.2f}  {K_cola:>6d}  {teo:>12.6f}  "
                  f"{sim['media']:>12.6f}  {ic_i:>10.6f}  {err_s}")
        print("║")

    print("╚═══════════════════════════════════════════════════════════════╝")


# ════════════════════════════════════════════════════════
# 4.  FIGURAS
# ════════════════════════════════════════════════════════

# ─── Figura 1: Panel de métricas vs ρ ────────────────────────────────────────
def fig1_metricas_vs_rho(res_sim, res_teo, mu):
    fig = plt.figure(figsize=(15, 9))
    fig.suptitle("M/M/1 — Métricas de rendimiento vs factor de carga ρ",
                 fontsize=13, fontweight="bold", y=1.01)

    gs = GridSpec(2, 3, figure=fig, hspace=0.50, wspace=0.38)

    specs = [
        ("L",   "L — Promedio clientes en sistema",   "Clientes"),
        ("Lq",  "Lq — Promedio clientes en cola",     "Clientes"),
        ("W",   "W — Tiempo promedio en sistema",     "Unidades de tiempo"),
        ("Wq",  "Wq — Tiempo promedio en cola",       "Unidades de tiempo"),
        ("rho", "ρ_sim — Utilización del servidor",   "Fracción [0,1]"),
    ]
    pos = [gs[0,0], gs[0,1], gs[0,2], gs[1,0], gs[1,1]]
    rhos_v = [r for r in RHOS if r < 1]

    for (clave, titulo, ylabel), subplot_pos in zip(specs, pos):
        ax = fig.add_subplot(subplot_pos)

        # Curva teórica (solo ρ estables)
        teo_x = [r for r in rhos_v if res_teo[r][clave] is not None]
        teo_y = [res_teo[r][clave] for r in teo_x]
        ax.plot(teo_x, teo_y, "--", color="#0D47A1", lw=2.5, label="Teórico", zorder=6)

        # Simulación + IC
        medias = [res_sim[r][clave]["media"]  for r in RHOS]
        ic_inf = [res_sim[r][clave]["ic_inf"] for r in RHOS]
        ic_sup = [res_sim[r][clave]["ic_sup"] for r in RHOS]

        ax.plot(RHOS, medias, "o-", color="#E53935", lw=2, ms=7,
                label="Python DES", zorder=5)
        ax.fill_between(RHOS, ic_inf, ic_sup, alpha=0.18, color="#E53935",
                        label="IC 95 %")
        ax.axvline(x=1.0, color="#FF6F00", ls=":", lw=1.5,
                   label="ρ=1 (inestable)")

        ax.set_title(titulo, fontweight="bold")
        ax.set_xlabel("ρ = λ / μ")
        ax.set_ylabel(ylabel)
        ax.legend(fontsize=7.5)
        ax.set_xlim([0.1, 1.38])
        ylim = ax.get_ylim()
        ax.axvspan(1.0, 1.38, alpha=0.07, color="#B71C1C", zorder=0)
        ax.text(1.02, ylim[1] * 0.90, "sin\nteórico\n(ρ≥1)", fontsize=7,
                color="#B71C1C", va="top", style="italic")

    # Panel de fórmulas
    ax_f = fig.add_subplot(gs[1,2])
    ax_f.axis("off")
    texto = (
        "Marco teórico  M/M/1\n"
        "─────────────────────\n"
        "  ρ   = λ / μ\n"
        "  L   = ρ / (1 − ρ)\n"
        "  Lq  = ρ² / (1 − ρ)\n"
        "  W   = 1 / (μ − λ)\n"
        "  Wq  = λ / [μ(μ−λ)]\n"
        "  P(n)= (1−ρ)·ρⁿ\n\n"
        f"  μ = {mu}\n"
        "  Válido sólo para ρ < 1"
    )
    ax_f.text(0.05, 0.97, texto, transform=ax_f.transAxes,
              fontsize=9, va="top", family="monospace",
              bbox=dict(boxstyle="round,pad=0.6",
                        facecolor="#E3F2FD", edgecolor="#90CAF9", alpha=0.9))

    plt.savefig("fig1_metricas_vs_rho.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("    → fig1_metricas_vs_rho.png")


# ─── Figura 2: Evolución temporal ────────────────────────────────────────────
def fig2_evolucion_temporal(res_sim):
    fig, axes = plt.subplots(len(RHOS), 1, figsize=(13, 11))
    fig.suptitle("M/M/1 — Evolución de n(t): clientes en el sistema (1 corrida por ρ)",
                 fontsize=12, fontweight="bold")

    for i, rho in enumerate(RHOS):
        ax     = axes[i]
        color  = PALETA[rho]
        hist   = res_sim[rho]["hist"]
        t_arr  = np.array(hist["t"])
        n_arr  = np.array(hist["n"])
        L_med  = res_sim[rho]["L"]["media"]

        ax.step(t_arr, n_arr, where="post", color=color, lw=0.9, alpha=0.85)
        ax.axhline(y=L_med, color="black", ls="--", lw=1.8,
                   label=f"L_prom = {L_med:.2f}")

        estado = "SISTEMA INESTABLE ⚠" if rho >= 1.0 else "Estable"
        col_t  = "red" if rho >= 1.0 else "black"
        ax.set_title(f"ρ = {rho:.2f}  [{estado}]", color=col_t,
                     fontsize=9, fontweight="bold", loc="left")
        ax.set_ylabel("n(t)", fontsize=8)
        ax.legend(loc="upper right", fontsize=8)

    axes[-1].set_xlabel("Tiempo de simulación", fontsize=10)
    plt.tight_layout()
    plt.savefig("fig2_evolucion_temporal.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("    → fig2_evolucion_temporal.png")


# ─── Figura 3: Denegación de servicio ────────────────────────────────────────
def fig3_denegacion(res_B):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle("M/M/1/K — Probabilidad de Denegación de Servicio",
                 fontsize=12, fontweight="bold")

    # Curvas P_den vs K_cola
    for rho in RHOS:
        color = PALETA[rho]
        teo   = [res_B[rho][K]["teo"]["denial_prob"]          for K in KS_COLA]
        sim   = [res_B[rho][K]["sim"]["denial_prob"]["media"]  for K in KS_COLA]
        ic_i  = [res_B[rho][K]["sim"]["denial_prob"]["ic_inf"] for K in KS_COLA]
        ic_s  = [res_B[rho][K]["sim"]["denial_prob"]["ic_sup"] for K in KS_COLA]

        ax1.plot(KS_COLA, teo, "--", color=color, lw=1.4, alpha=0.6)
        ax1.plot(KS_COLA, sim, "o-", color=color, lw=2.2, ms=7, label=f"ρ={rho:.2f}")
        ax1.fill_between(KS_COLA, ic_i, ic_s, alpha=0.10, color=color)

    ax1.set_xlabel("Tamaño de cola K")
    ax1.set_ylabel("P(denegación)")
    ax1.set_title("P_den vs K\n(punteado=teórico, sólido=Python DES)")
    ax1.legend(fontsize=9)
    ax1.set_xticks(KS_COLA)
    ax1.set_ylim([-0.02, 1.05])

    # Mapa de calor (valores teóricos)
    mat = np.array([[res_B[rho][K]["teo"]["denial_prob"]
                     for K in KS_COLA] for rho in RHOS])
    cmap = mcolors.LinearSegmentedColormap.from_list(
        "gyr", ["#1B5E20", "#FFEB3B", "#B71C1C"])

    im = ax2.imshow(mat, cmap=cmap, aspect="auto", vmin=0, vmax=1)
    ax2.set_xticks(range(len(KS_COLA)))
    ax2.set_xticklabels([f"K={k}" for k in KS_COLA], fontsize=9)
    ax2.set_yticks(range(len(RHOS)))
    ax2.set_yticklabels([f"ρ={r:.2f}" for r in RHOS], fontsize=9)
    ax2.set_title("Mapa de calor — P_den teórico\n"
                  "Verde = baja denegación · Rojo = alta denegación")

    for i in range(len(RHOS)):
        for j in range(len(KS_COLA)):
            v  = mat[i, j]
            tc = "white" if v > 0.5 else "black"
            ax2.text(j, i, f"{v:.3f}", ha="center", va="center",
                     fontsize=8.5, color=tc, fontweight="bold")

    plt.colorbar(im, ax=ax2, label="P(denegación)")
    plt.tight_layout()
    plt.savefig("fig3_denegacion.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("    → fig3_denegacion.png")


# ─── Figura 4: Distribución P(n) ─────────────────────────────────────────────
def fig4_distribucion_pn(res_sim, res_teo):
    rhos_plot = [0.25, 0.50, 0.75]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    fig.suptitle(
        "M/M/1 — Distribución P(n): probabilidad de n clientes en sistema\n"
        "(P(n) simulado = promedio de 10 corridas independientes)",
        fontsize=11, fontweight="bold")

    for ax, rho in zip(axes, rhos_plot):
        Pn_fn  = res_teo[rho]["Pn"]
        Pn_sim = res_sim[rho]["Pn"]

        max_n = min(max(Pn_sim.keys(), default=10), 18)
        ns = list(range(max_n + 1))

        teo_v = [Pn_fn(n) for n in ns]
        sim_v = [Pn_sim.get(n, 0.0) for n in ns]

        x, w = np.arange(len(ns)), 0.35
        ax.bar(x - w/2, teo_v, w, label="Teórico",    color="#1565C0", alpha=0.88)
        ax.bar(x + w/2, sim_v, w, label="Python DES", color="#2E7D32", alpha=0.88)

        ax.set_title(f"ρ = {rho:.2f}", fontweight="bold")
        ax.set_xlabel("n  (clientes en sistema)")
        ax.set_ylabel("P(n)")
        ax.legend(fontsize=8.5)
        ax.set_xticks(x[::2])
        ax.set_xticklabels(ns[::2])

    plt.tight_layout()
    plt.savefig("fig4_pn.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("    → fig4_pn.png")


# ─── Figura 5: No linealidad ──────────────────────────────────────────────────
def fig5_no_linealidad(res_teo):
    fig, ax = plt.subplots(figsize=(9, 5))

    rho_c = np.linspace(0.01, 0.989, 600)
    L_c   = rho_c / (1 - rho_c)
    Lq_c  = rho_c**2 / (1 - rho_c)

    ax.plot(rho_c, L_c,  lw=2.5, color="#1565C0", label="L = ρ/(1−ρ)")
    ax.plot(rho_c, Lq_c, lw=2.5, color="#B71C1C", ls="--", label="Lq = ρ²/(1−ρ)")

    for rho in [0.25, 0.50, 0.75]:
        teo = res_teo[rho]
        ax.plot(rho, teo["L"],  "o", ms=10, color="#1565C0", zorder=5)
        ax.plot(rho, teo["Lq"], "s", ms=10, color="#B71C1C", zorder=5)

    # Anotaciones
    L75 = res_teo[0.75]["L"]
    ax.annotate(f"ρ=0.75 → L={L75:.1f}",
                xy=(0.75, L75), xytext=(0.52, L75 + 3.5),
                arrowprops=dict(arrowstyle="->", color="#1565C0", lw=1.5),
                color="#1565C0", fontsize=9)
    L90 = 0.90 / (1 - 0.90)
    ax.annotate(f"ρ=0.90 → L={L90:.1f}\n(3× más que ρ=0.75!)",
                xy=(0.90, L90), xytext=(0.65, L90 + 1.5),
                arrowprops=dict(arrowstyle="->", color="#1565C0", lw=1.5),
                color="#1565C0", fontsize=9)

    ax.axvline(x=1.0, color="black", ls=":", lw=1.5)
    ax.text(1.005, 22, "ρ=1\n(inestable)", fontsize=9, va="top")

    ax.set_xlim([0, 1.12])
    ax.set_ylim([0, 26])
    ax.set_xlabel("ρ = λ / μ", fontsize=11)
    ax.set_ylabel("Clientes en promedio", fontsize=11)
    ax.set_title("No linealidad del M/M/1 — Incrementar ρ de 0.75 a 0.90 "
                 "triplica la cola", fontsize=11, fontweight="bold")
    ax.legend(fontsize=10)

    plt.tight_layout()
    plt.savefig("fig5_no_linealidad.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("    → fig5_no_linealidad.png")


# ─── Figura 6: Barras comparativas Teórico vs Python ─────────────────────────
def fig6_barras_comparativas(res_sim, res_teo):
    metricas = ["L", "Lq", "W", "Wq"]
    nombres  = ["L (clientes en sistema)", "Lq (clientes en cola)",
                "W (tiempo en sistema)",   "Wq (tiempo en cola)"]
    rhos_v   = [r for r in RHOS if r < 1]

    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle("M/M/1 — Comparación directa: Teórico vs Python DES (ρ < 1)",
                 fontsize=12, fontweight="bold")

    x, w = np.arange(len(rhos_v)), 0.35

    for ax, clave, nombre in zip(axes.flat, metricas, nombres):
        teo_v = [res_teo[r][clave] for r in rhos_v]
        sim_v = [res_sim[r][clave]["media"]  for r in rhos_v]
        err_lo = [res_sim[r][clave]["media"] - res_sim[r][clave]["ic_inf"] for r in rhos_v]
        err_hi = [res_sim[r][clave]["ic_sup"] - res_sim[r][clave]["media"] for r in rhos_v]

        ax.bar(x - w/2, teo_v, w, label="Teórico",    color="#1565C0", alpha=0.9)
        ax.bar(x + w/2, sim_v, w, label="Python DES", color="#E53935", alpha=0.9,
               yerr=[err_lo, err_hi], capsize=5, error_kw={"linewidth": 1.5})

        ax.set_title(nombre, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels([f"ρ={r:.2f}" for r in rhos_v])
        ax.legend(fontsize=9)
        ax.set_ylabel(clave)

    plt.tight_layout()
    plt.savefig("fig6_barras.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("    → fig6_barras.png")


# ════════════════════════════════════════════════════════
# 5.  EXPORTAR CSV (para completar con datos de AnyLogic)
# ════════════════════════════════════════════════════════

def exportar_csv(res_A_sim, res_A_teo, res_B):
    """
    Genera dos CSV con columna vacía 'anylogic_media' para
    completar manualmente con los resultados de AnyLogic.
    """
    # Cola infinita
    with open("resultados_cola_infinita.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rho", "metrica", "teorico", "python_media",
                    "python_ic_inf", "python_ic_sup", "anylogic_media"])
        for rho in RHOS:
            for met in ["L", "Lq", "W", "Wq", "rho"]:
                teo = res_A_teo[rho].get(met)
                sim = res_A_sim[rho][met]
                w.writerow([
                    rho, met,
                    round(teo, 6) if teo is not None else "N/A",
                    round(sim["media"], 6),
                    round(sim["ic_inf"], 6),
                    round(sim["ic_sup"], 6),
                    ""   # ← completar con AnyLogic
                ])

    # Cola finita — denegación
    with open("resultados_denegacion.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["rho", "K_cola", "K_total", "teo_denial",
                    "python_media", "python_ic_inf", "python_ic_sup", "anylogic_media"])
        for rho in RHOS:
            for K_cola, K_total in zip(KS_COLA, KS_TOTAL):
                teo = res_B[rho][K_cola]["teo"]["denial_prob"]
                sim = res_B[rho][K_cola]["sim"]["denial_prob"]
                w.writerow([
                    rho, K_cola, K_total,
                    round(teo, 6),
                    round(sim["media"], 6),
                    round(sim["ic_inf"], 6),
                    round(sim["ic_sup"], 6),
                    ""   # ← completar con AnyLogic
                ])

    print("    → resultados_cola_infinita.csv")
    print("    → resultados_denegacion.csv")
    print("       (Columna 'anylogic_media' disponible para completar)")


# ════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════

def main():
    mu, tiempo_sim, semilla = pedir_parametros()

    print()
    print("═" * 56)
    print("  Ejecutando experimentos...")
    print("═" * 56)
    res_A_sim, res_A_teo, res_B = correr_todos(mu, tiempo_sim, semilla)

    print()
    print("═" * 56)
    print("  Resultados")
    print("═" * 56)
    tabla_A(res_A_sim, res_A_teo)
    tabla_B(res_B)

    print()
    print("═" * 56)
    print("  Generando 6 figuras...")
    print("═" * 56)
    fig1_metricas_vs_rho(res_A_sim, res_A_teo, mu)
    fig2_evolucion_temporal(res_A_sim)
    fig3_denegacion(res_B)
    fig4_distribucion_pn(res_A_sim, res_A_teo)
    fig5_no_linealidad(res_A_teo)
    fig6_barras_comparativas(res_A_sim, res_A_teo)

    print()
    print("═" * 56)
    print("  Exportando CSV...")
    print("═" * 56)
    exportar_csv(res_A_sim, res_A_teo, res_B)

    print()
    print("╔═══════════════════════════════════════════════════════╗")
    print("║  ✓ Simulación completada                              ║")
    print("║  6 figuras + 2 CSV generados en el directorio actual  ║")
    print("╚═══════════════════════════════════════════════════════╝")


if __name__ == "__main__":
    main()
