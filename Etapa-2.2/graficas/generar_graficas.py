"""
Genera histogramas comparativos (generado vs teórico) para las 9 distribuciones del TP 2.2.
Guarda cada gráfica como PNG en la misma carpeta que este script.

Parámetros usados:
  Uniforme      : U(0, 1)
  Exponencial   : Exp(lambda=1)
  Gamma         : Gamma(alpha=2, beta=1)  [Erlang-2]
  Normal        : N(mu=0, sigma=1)
  Pascal        : r=3, p=0.5  (fallos antes del r-ésimo éxito)
  Binomial      : B(n=20, p=0.5)
  Hipergeomética: H(N=50, K=20, n=10)
  Poisson       : Poisson(lambda=4)
  Empírica disc.: demanda diaria (Naylor, 1982)
"""

import sys, os, math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'Etapa-2.1'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from generadores import GeneradorGCL
from distribuciones import uniforme_inversa, normal_box_muller

OUTDIR = os.path.dirname(__file__)
N      = 1000
SEED   = 1273

AZUL   = "#2c7bb6"
ROJO   = "#d7191c"
GRIS   = "#cccccc"


def _guardar(fig, nombre):
    path = os.path.join(OUTDIR, nombre)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  guardada: {path}")


def _fig(titulo):
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.set_title(titulo, fontsize=13, pad=10)
    ax.grid(axis="y", color=GRIS, linewidth=0.7, zorder=0)
    ax.set_axisbelow(True)
    return fig, ax


# ──────────────────────────────────────────────────────────────────────────────
# 1. UNIFORME  U(0, 1)
# ──────────────────────────────────────────────────────────────────────────────
def grafica_uniforme():
    datos = uniforme_inversa(0, 1, N, SEED)
    fig, ax = _fig(r"Distribución Uniforme $\mathcal{U}(0,\,1)$")
    ax.hist(datos, bins=20, density=True, color=AZUL, alpha=0.7,
            edgecolor="white", label="Generado (GCL)")
    ax.axhline(1.0, color=ROJO, linewidth=2, label="PDF teórica")
    ax.set_xlabel("$x$"); ax.set_ylabel("Densidad")
    ax.legend(); ax.set_xlim(0, 1)
    _guardar(fig, "01_uniforme.png")


# ──────────────────────────────────────────────────────────────────────────────
# 2. EXPONENCIAL  Exp(λ=1)
# ──────────────────────────────────────────────────────────────────────────────
def grafica_exponencial():
    gcl = GeneradorGCL(semilla=SEED)
    datos = [-math.log(gcl.siguiente()) for _ in range(N)]
    fig, ax = _fig(r"Distribución Exponencial $\mathrm{Exp}(\lambda=1)$")
    ax.hist(datos, bins=30, density=True, color=AZUL, alpha=0.7,
            edgecolor="white", label="Generado (GCL)")
    xs = np.linspace(0, max(datos), 300)
    ax.plot(xs, np.exp(-xs), color=ROJO, linewidth=2, label="PDF teórica")
    ax.set_xlabel("$x$"); ax.set_ylabel("Densidad")
    ax.legend()
    _guardar(fig, "02_exponencial.png")


# ──────────────────────────────────────────────────────────────────────────────
# 3. GAMMA  Γ(α=2, β=1)  — Erlang-2
# ──────────────────────────────────────────────────────────────────────────────
def grafica_gamma():
    gcl = GeneradorGCL(semilla=SEED)
    datos = [-math.log(gcl.siguiente()) - math.log(gcl.siguiente())
             for _ in range(N)]
    fig, ax = _fig(r"Distribución Gamma $\Gamma(\alpha=2,\,\beta=1)$")
    ax.hist(datos, bins=30, density=True, color=AZUL, alpha=0.7,
            edgecolor="white", label="Generado (GCL, Erlang-2)")
    xs = np.linspace(0, max(datos), 300)
    pdf = xs * np.exp(-xs)          # f(x) = x e^{-x} para Gamma(2,1)
    ax.plot(xs, pdf, color=ROJO, linewidth=2, label="PDF teórica")
    ax.set_xlabel("$x$"); ax.set_ylabel("Densidad")
    ax.legend()
    _guardar(fig, "03_gamma.png")


# ──────────────────────────────────────────────────────────────────────────────
# 4. NORMAL  N(0, 1)
# ──────────────────────────────────────────────────────────────────────────────
def grafica_normal():
    datos = normal_box_muller(0, 1, N, SEED)
    fig, ax = _fig(r"Distribución Normal $\mathcal{N}(0,\,1)$")
    ax.hist(datos, bins=30, density=True, color=AZUL, alpha=0.7,
            edgecolor="white", label="Generado (Box-Muller)")
    xs = np.linspace(min(datos), max(datos), 300)
    pdf = np.exp(-xs**2 / 2) / math.sqrt(2 * math.pi)
    ax.plot(xs, pdf, color=ROJO, linewidth=2, label="PDF teórica")
    ax.set_xlabel("$x$"); ax.set_ylabel("Densidad")
    ax.legend()
    _guardar(fig, "04_normal.png")


# ──────────────────────────────────────────────────────────────────────────────
# 5. PASCAL  r=3, p=0.5  (fallos antes del r-ésimo éxito)
# ──────────────────────────────────────────────────────────────────────────────
def grafica_pascal():
    r, p = 3, 0.5
    gcl = GeneradorGCL(semilla=SEED)

    def geom_fallo():
        # número de fallos antes del primer éxito  (Geométrica - 1)
        k = 0
        while gcl.siguiente() >= p:
            k += 1
        return k

    datos = [sum(geom_fallo() for _ in range(r)) for _ in range(N)]
    k_max = max(datos)

    # PMF teórica: P(X=x) = C(x+r-1, x) * p^r * (1-p)^x
    def pmf(x):
        return math.comb(x + r - 1, x) * p**r * (1 - p)**x

    xs_teo = list(range(k_max + 1))
    ps_teo = [pmf(x) for x in xs_teo]

    obs_freq = [datos.count(x) / N for x in xs_teo]

    fig, ax = _fig(fr"Distribución Pascal ($r={r},\ p={p}$)")
    width = 0.4
    ax.bar([x - width/2 for x in xs_teo], obs_freq, width=width,
           color=AZUL, alpha=0.8, label="Generado (GCL)")
    ax.bar([x + width/2 for x in xs_teo], ps_teo, width=width,
           color=ROJO, alpha=0.8, label="PMF teórica")
    ax.set_xlabel("$x$"); ax.set_ylabel("Probabilidad")
    ax.legend()
    _guardar(fig, "05_pascal.png")


# ──────────────────────────────────────────────────────────────────────────────
# 6. BINOMIAL  B(n=20, p=0.5)
# ──────────────────────────────────────────────────────────────────────────────
def grafica_binomial():
    n_ens, p = 20, 0.5
    gcl = GeneradorGCL(semilla=SEED)
    datos = [sum(1 for _ in range(n_ens) if gcl.siguiente() < p)
             for _ in range(N)]

    xs = list(range(n_ens + 1))
    obs_freq = [datos.count(x) / N for x in xs]
    pmf_teo  = [math.comb(n_ens, x) * p**x * (1-p)**(n_ens-x) for x in xs]

    fig, ax = _fig(fr"Distribución Binomial ($n={n_ens},\ p={p}$)")
    width = 0.4
    ax.bar([x - width/2 for x in xs], obs_freq, width=width,
           color=AZUL, alpha=0.8, label="Generado (GCL)")
    ax.bar([x + width/2 for x in xs], pmf_teo, width=width,
           color=ROJO, alpha=0.8, label="PMF teórica")
    ax.set_xlabel("$x$"); ax.set_ylabel("Probabilidad")
    ax.legend()
    _guardar(fig, "06_binomial.png")


# ──────────────────────────────────────────────────────────────────────────────
# 7. HIPERGEOMÉTRICA  H(N=50, K=20, n=10)
# ──────────────────────────────────────────────────────────────────────────────
def grafica_hipergeometrica():
    N_pop, K, n_mu = 50, 20, 10
    x_min = max(0, n_mu + K - N_pop)
    x_max = min(n_mu, K)

    # PMF teórica
    def pmf(x):
        return math.comb(K, x) * math.comb(N_pop - K, n_mu - x) / math.comb(N_pop, n_mu)

    # Generador por T. Inversa (acumulación de PMF)
    gcl = GeneradorGCL(semilla=SEED)
    xs_range = list(range(x_min, x_max + 1))
    probs_acum = []
    acc = 0.0
    for x in xs_range:
        acc += pmf(x)
        probs_acum.append(acc)

    def generar_uno():
        u = gcl.siguiente()
        for i, f in enumerate(probs_acum):
            if u <= f:
                return xs_range[i]
        return xs_range[-1]

    datos = [generar_uno() for _ in range(N)]

    obs_freq = [datos.count(x) / N for x in xs_range]
    pmf_teo  = [pmf(x) for x in xs_range]

    fig, ax = _fig(fr"Distribución Hipergeométrica ($N={N_pop},\ K={K},\ n={n_mu}$)")
    width = 0.4
    ax.bar([x - width/2 for x in xs_range], obs_freq, width=width,
           color=AZUL, alpha=0.8, label="Generado (GCL)")
    ax.bar([x + width/2 for x in xs_range], pmf_teo, width=width,
           color=ROJO, alpha=0.8, label="PMF teórica")
    ax.set_xlabel("$x$"); ax.set_ylabel("Probabilidad")
    ax.legend()
    _guardar(fig, "07_hipergeometrica.png")


# ──────────────────────────────────────────────────────────────────────────────
# 8. POISSON  Poisson(λ=4)
# ──────────────────────────────────────────────────────────────────────────────
def grafica_poisson():
    lam = 4
    umbral = math.exp(-lam)
    gcl = GeneradorGCL(semilla=SEED)

    def gen_uno():
        P = gcl.siguiente()
        k = 0
        while P >= umbral:
            P *= gcl.siguiente()
            k += 1
        return k

    datos = [gen_uno() for _ in range(N)]
    k_max = max(datos)
    xs = list(range(k_max + 1))
    obs_freq = [datos.count(x) / N for x in xs]
    pmf_teo  = [math.exp(-lam) * lam**x / math.factorial(x) for x in xs]

    fig, ax = _fig(fr"Distribución de Poisson ($\lambda={lam}$)")
    width = 0.4
    ax.bar([x - width/2 for x in xs], obs_freq, width=width,
           color=AZUL, alpha=0.8, label="Generado (GCL)")
    ax.bar([x + width/2 for x in xs], pmf_teo, width=width,
           color=ROJO, alpha=0.8, label="PMF teórica")
    ax.set_xlabel("$x$"); ax.set_ylabel("Probabilidad")
    ax.legend()
    _guardar(fig, "08_poisson.png")


# ──────────────────────────────────────────────────────────────────────────────
# 9. EMPÍRICA DISCRETA  (demanda diaria)
# ──────────────────────────────────────────────────────────────────────────────
def grafica_empirica():
    valores = [0, 1, 2, 3, 4]
    probs   = [0.10, 0.20, 0.30, 0.25, 0.15]
    cdf     = []
    acc = 0.0
    for p in probs:
        acc += p
        cdf.append(acc)

    gcl = GeneradorGCL(semilla=SEED)

    def gen_uno():
        u = gcl.siguiente()
        for i, f in enumerate(cdf):
            if u <= f:
                return valores[i]
        return valores[-1]

    datos = [gen_uno() for _ in range(N)]
    obs_freq = [datos.count(x) / N for x in valores]

    fig, ax = _fig("Distribución Empírica Discreta (demanda diaria)")
    width = 0.4
    ax.bar([x - width/2 for x in valores], obs_freq, width=width,
           color=AZUL, alpha=0.8, label="Generado (GCL)")
    ax.bar([x + width/2 for x in valores], probs, width=width,
           color=ROJO, alpha=0.8, label="Probabilidad empírica")
    ax.set_xlabel("$x_i$ (unidades)"); ax.set_ylabel("Probabilidad")
    ax.set_xticks(valores)
    ax.legend()
    _guardar(fig, "09_empirica_discreta.png")


# ──────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"Generando gráficas en: {OUTDIR}\n")
    grafica_uniforme()
    grafica_exponencial()
    grafica_gamma()
    grafica_normal()
    grafica_pascal()
    grafica_binomial()
    grafica_hipergeometrica()
    grafica_poisson()
    grafica_empirica()
    print("\nListo. 9 gráficas generadas.")
