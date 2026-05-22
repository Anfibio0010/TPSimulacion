"""
TP 2.1 - Generadores Pseudoaleatorios
Universidad Tecnologica Nacional - FRRO  |  Simulacion 2026

Generadores : GCL (ANSI C), Von Neumann (4 digitos), Python random, NumPy PCG64
Tests       : Chi-Cuadrado, Kolmogorov-Smirnov, Rachas, Poker
Extras      : Graficos coordenados (Test de Series) y tabla resumen
"""

import random as _random
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from collections import Counter
from scipy import stats
from scipy.stats import chi2 as chi2_dist, kstest

warnings.filterwarnings("ignore")
plt.rcParams.update({"font.family": "DejaVu Sans", "figure.dpi": 110})

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURACION GLOBAL
# ──────────────────────────────────────────────────────────────────────────────
N        = 1000    # Numeros a generar por generador
ALPHA    = 0.05    # Nivel de significancia
K        = 10      # Intervalos para Chi-Cuadrado
SEED     = 1001      # Semilla global — vale cualquier entero >= 0
#SEED_VN  = 1234    # Semilla Von Neumann — debe ser exactamente 4 digitos [1000-9999]

COLORES = {
    "GCL (ANSI C)":  "#2196F3",
    "Von Neumann":   "#FF5722",
    "Python random": "#4CAF50",
    "NumPy PCG64":   "#9C27B0",
}

# ==============================================================================
# GENERADORES
# ==============================================================================

class GeneradorGCL:
    """
    Generador Congruencial Lineal (LCG / GCL)
    Recurrencia : X_{n+1} = (a * X_n + c) mod m
    Normalizacion: u_n = X_n / m  en [0, 1)

    Parametros ANSI C (Hull-Dobell):
        a = 1 664 525
        c = 1 013 904 223
        m = 2^32
    Cumplen las condiciones de periodo maximo para m potencia de 2.
    """
    NOMBRE = "GCL (ANSI C)"

    def __init__(self, semilla=SEED, a=1_664_525, c=1_013_904_223, m=2**32):
        self.semilla = semilla
        self.estado  = semilla
        self.a, self.c, self.m = a, c, m

    def siguiente(self):
        self.estado = (self.a * self.estado + self.c) % self.m
        return self.estado / self.m

    def generar(self, n=N):
        self.estado = self.semilla
        return np.array([self.siguiente() for _ in range(n)])


class GeneradorVonNeumann:
    """
    Metodo de los Cuadrados Medios de Von Neumann (4 digitos).

    Algoritmo:
      1. Partir de semilla X de 4 digitos.
      2. Calcular X^2 (hasta 8 digitos; se rellena con ceros a la izquierda).
      3. Extraer los 4 digitos centrales -> nuevo X.
      4. u_n = X / 10000  en [0, 1).

    Debilidades conocidas:
      - Puede degenerar rapidamente (estado -> 0).
      - Puede entrar en ciclos cortos.
      - Periodo maximo teorico: 10 000 (pero en la practica mucho menor).
    """
    NOMBRE = "Von Neumann (4 digitos)"

    def __init__(self, semilla=1234):
        assert 1000 <= semilla <= 9999, "La semilla debe tener exactamente 4 digitos"
        self.semilla       = semilla
        self.estado        = semilla
        self.degenerado_en = None   # paso en que el estado llego a 0
        self.ciclo_en      = None   # paso en que se detecto un ciclo

    def siguiente(self):
        cuadrado = self.estado ** 2
        sq8      = str(cuadrado).zfill(8)   # garantizar 8 digitos
        self.estado = int(sq8[2:6])         # 4 digitos centrales
        return self.estado / 10_000.0

    def generar(self, n=N):
        self.estado        = self.semilla
        self.degenerado_en = None
        self.ciclo_en      = None
        resultado = []
        vistos    = {}

        for i in range(n):
            if self.estado in vistos and self.ciclo_en is None:
                self.ciclo_en = i + 1
            vistos[self.estado] = i

            val = self.siguiente()
            resultado.append(val)

            if self.estado == 0:
                self.degenerado_en = len(resultado)
                resultado.extend([0.0] * (n - len(resultado)))
                break

        return np.array(resultado)


def generar_python_random(n=N, semilla=SEED):
    """Python stdlib random — Mersenne Twister MT19937."""
    rng = _random.Random(semilla)
    return np.array([rng.random() for _ in range(n)])


def generar_numpy_pcg64(n=N, semilla=SEED):
    """NumPy default_rng — Permuted Congruential Generator 64-bit (PCG64)."""
    rng = np.random.default_rng(semilla)
    return rng.random(n)


# ==============================================================================
# TESTS ESTADISTICOS
# ==============================================================================

def test_chi_cuadrado(datos, k=K, alpha=ALPHA):
    """
    Test Chi-Cuadrado para uniformidad en [0, 1].
    H0: los datos provienen de U(0, 1).

    Estadistico: chi2 = sum( (Oi - Ei)^2 / Ei )  con (k-1) grados de libertad.
    Se rechaza H0 si chi2 > chi2_{alpha, k-1}.
    """
    n = len(datos)
    observado, _ = np.histogram(datos, bins=k, range=(0.0, 1.0))
    esperado      = n / k

    chi2_stat = float(np.sum((observado - esperado) ** 2 / esperado))
    gl        = k - 1
    p_valor   = float(1.0 - chi2_dist.cdf(chi2_stat, gl))
    critico   = float(chi2_dist.ppf(1.0 - alpha, gl))

    return {
        "estadistico":    chi2_stat,
        "valor_critico":  critico,
        "p_valor":        p_valor,
        "gl":             gl,
        "observado":      observado,
        "esperado_uni":   esperado,
        "aprueba":        chi2_stat <= critico,
    }


def test_ks(datos, alpha=ALPHA):
    """
    Test de Kolmogorov-Smirnov.
    H0: los datos provienen de U(0, 1).

    D_n = max | F_n(x) - F(x) |  donde F(x) = x para la uniforme.
    Valor critico aproximado para alpha = 0.05: 1.36 / sqrt(n).
    Se rechaza H0 si D_n > D_critico.
    """
    n = len(datos)
    stat, p_valor = kstest(datos, "uniform", args=(0, 1))
    critico = 1.36 / np.sqrt(n)

    return {
        "estadistico":   float(stat),
        "valor_critico": float(critico),
        "p_valor":       float(p_valor),
        "aprueba":       float(stat) <= float(critico),
    }


def test_rachas(datos, alpha=ALPHA):
    """
    Test de Rachas (arriba / abajo de la mediana).
    H0: los datos son independientes (no hay tendencia).

    Procedimiento:
      - Mediana teorica = 0.5 para U(0, 1).
      - Signo_i = +1 si x_i > 0.5,  -1 si x_i <= 0.5.
      - n1 = cantidad de positivos, n2 = cantidad de negativos.
      - R = numero de rachas (segmentos consecutivos del mismo signo).
      - mu_R    = 2*n1*n2 / (n1+n2) + 1
      - sigma_R = sqrt( 2*n1*n2*(2*n1*n2 - n1 - n2) / ((n1+n2)^2*(n1+n2-1)) )
      - Z = (R - mu_R) / sigma_R  ~  N(0, 1)

    Se rechaza H0 si |Z| > z_{alpha/2}.
    """
    signos = np.where(datos > 0.5, 1, -1)
    n1 = int(np.sum(signos == 1))
    n2 = int(np.sum(signos == -1))
    n  = n1 + n2

    R = 1 + int(np.sum(signos[1:] != signos[:-1]))

    mu_R    = 2 * n1 * n2 / n + 1
    sigma2  = (2 * n1 * n2 * (2 * n1 * n2 - n)) / (n ** 2 * (n - 1))
    sigma_R = float(np.sqrt(sigma2))
    Z       = float((R - mu_R) / sigma_R)

    z_crit  = float(stats.norm.ppf(1 - alpha / 2))
    p_valor = float(2 * (1 - stats.norm.cdf(abs(Z))))

    return {
        "n1":              n1,
        "n2":              n2,
        "rachas":          R,
        "mu_R":            float(mu_R),
        "sigma_R":         sigma_R,
        "estadistico_Z":   Z,
        "valor_critico_Z": z_crit,
        "p_valor":         p_valor,
        "aprueba":         abs(Z) <= z_crit,
    }


# Probabilidades teoricas para d=5 digitos en base 10 (calculadas combinatoriamente)
#   Total de combinaciones: 10^5 = 100 000
#   Cinco distintos : C(10,5)*5!      = 30 240  -> p = 0.3024
#   Un par          : 10*C(9,3)*5!/2! = 50 400  -> p = 0.5040
#   Dos pares       : C(10,2)*8*5!/2!2! = 10 800  -> p = 0.1080
#   Tercia          : 10*C(9,2)*5!/3!  =  7 200  -> p = 0.0720
#   Full            : 10*9*5!/3!2!     =    900  -> p = 0.0090
#   Poker (4)       : 10*9*5!/4!       =    450  -> p = 0.0045
#   Quintilla       : 10               =     10  -> p = 0.0001
POKER_PROBS = {
    "Cinco distintos": 0.3024,
    "Un par":          0.5040,
    "Dos pares":       0.1080,
    "Tercia":          0.0720,
    "Full":            0.0090,
    "Poker":           0.0045,
    "Quintilla":       0.0001,
}


def _clasificar_mano(digitos_grupo):
    """Clasifica un arreglo de 5 digitos [0-9] como mano de poker."""
    freqs = sorted(Counter(digitos_grupo).values(), reverse=True)
    tabla = {
        (1, 1, 1, 1, 1): "Cinco distintos",
        (2, 1, 1, 1):    "Un par",
        (2, 2, 1):        "Dos pares",
        (3, 1, 1):        "Tercia",
        (3, 2):           "Full",
        (4, 1):           "Poker",
        (5,):             "Quintilla",
    }
    return tabla.get(tuple(freqs), "Desconocido")


def test_poker(datos, d=5, alpha=ALPHA):
    """
    Test de Poker.
    H0: los datos son independientes y uniformes.

    Procedimiento:
      - Agrupar los N numeros de d en d (d = 5).
      - Convertir cada numero a digito: dig_i = floor(x_i * 10)  en {0, ..., 9}.
      - Clasificar cada grupo segun el patron de sus digitos (como en poker).
      - Comparar frecuencias observadas con las esperadas mediante un test chi2.

    Nota: las categorias con frecuencia esperada < 5 se agrupan automaticamente
    desde el extremo de menor probabilidad para cumplir el requisito del chi2.
    """
    n_grupos = len(datos) // d
    datos_r  = datos[: n_grupos * d].reshape(n_grupos, d)
    digitos  = np.clip((datos_r * 10).astype(int), 0, 9)

    conteos  = dict.fromkeys(POKER_PROBS, 0)
    for g in digitos:
        conteos[_clasificar_mano(g)] += 1

    esperados = {k: p * n_grupos for k, p in POKER_PROBS.items()}

    cats    = list(POKER_PROBS.keys())
    obs_arr = np.array([conteos[c]   for c in cats], dtype=float)
    exp_arr = np.array([esperados[c] for c in cats], dtype=float)

    # Agrupar desde el final mientras el esperado acumulado sea < 5
    labels_agr, obs_agr, exp_agr = [], [], []
    cola_obs = cola_exp = 0.0
    cola_lbl = []

    for i in range(len(cats) - 1, -1, -1):
        cola_obs += obs_arr[i]
        cola_exp += exp_arr[i]
        cola_lbl.insert(0, cats[i])
        if cola_exp >= 5 or i == 0:
            lbl = "/".join(cola_lbl) if len(cola_lbl) > 1 else cola_lbl[0]
            labels_agr.insert(0, lbl)
            obs_agr.insert(0, cola_obs)
            exp_agr.insert(0, cola_exp)
            cola_obs = cola_exp = 0.0
            cola_lbl = []

    obs_agr = np.array(obs_agr)
    exp_agr = np.array(exp_agr)

    chi2_stat = float(np.sum((obs_agr - exp_agr) ** 2 / exp_agr))
    gl        = len(obs_agr) - 1
    p_valor   = float(1.0 - chi2_dist.cdf(chi2_stat, gl))
    critico   = float(chi2_dist.ppf(1.0 - alpha, gl))

    return {
        "estadistico":      chi2_stat,
        "valor_critico":    critico,
        "p_valor":          p_valor,
        "gl":               gl,
        "aprueba":          chi2_stat <= critico,
        "conteos":          conteos,
        "esperados":        esperados,
        "labels_agrupados": labels_agr,
        "obs_agrupados":    obs_agr,
        "exp_agrupados":    exp_agr,
        "n_grupos":         n_grupos,
    }


# ==============================================================================
# VISUALIZACION
# ==============================================================================

def _icono(aprueba: bool) -> str:
    return "APRUEBA" if aprueba else "RECHAZA"


def plot_histogramas(datos_dict):
    """Histogramas de distribucion — verifica si los valores se distribuyen uniformemente."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))
    fig.suptitle(f"Distribucion de Numeros Generados  (N = {N})",
                 fontsize=13, fontweight="bold")

    for ax, (nombre, seq) in zip(axes.flat, datos_dict.items()):
        color = COLORES[nombre]
        ax.hist(seq, bins=K, range=(0, 1), color=color, edgecolor="white", alpha=0.85)
        ax.axhline(N / K, color="red", linestyle="--", lw=1.5,
                   label=f"Esperado ({N // K})")
        ax.set_title(nombre, fontsize=11, fontweight="bold")
        ax.set_xlabel("Valor generado")
        ax.set_ylabel("Frecuencia")
        ax.set_xlim(0, 1)
        ax.legend(fontsize=9)

    plt.tight_layout()
    plt.savefig("fig1_histogramas.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("  Guardado: fig1_histogramas.png")


def plot_coordenados(datos_dict):
    """
    Graficos coordenados (xi, xi+1) — Test de Series.

    Cada punto representa el par de numeros consecutivos (x_i, x_{i+1}).
    Un generador de calidad muestra dispersion uniforme en el cuadrado unitario.
    Patrones visibles (lineas, clusters, bandas) indican correlacion serial.

    Nota: este grafico corresponde al Test de Series, NO al Test de Poker.
    Se incluye porque es muy informativo, especialmente para detectar debilidades
    en Von Neumann.
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle("Graficos Coordenados  (xi, xi+1) — Test de Series",
                 fontsize=13, fontweight="bold")

    for ax, (nombre, seq) in zip(axes.flat, datos_dict.items()):
        color = COLORES[nombre]
        ax.scatter(seq[:-1], seq[1:], s=4, alpha=0.5, color=color, linewidths=0)
        ax.set_title(nombre, fontsize=11, fontweight="bold")
        ax.set_xlabel("xi")
        ax.set_ylabel("xi+1")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_aspect("equal")

    plt.tight_layout()
    plt.savefig("fig2_coordenados.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("  Guardado: fig2_coordenados.png")


def plot_poker(resultados_dict):
    """Diagramas de barras: frecuencias observadas vs esperadas por tipo de mano."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Test de Poker — Observado vs Esperado  (d = 5 digitos)",
                 fontsize=13, fontweight="bold")

    for ax, (nombre, tests) in zip(axes.flat, resultados_dict.items()):
        pok    = tests["poker"]
        labels = pok["labels_agrupados"]
        obs    = pok["obs_agrupados"]
        exp    = pok["exp_agrupados"]
        color  = COLORES[nombre]

        x     = np.arange(len(labels))
        ancho = 0.35
        ax.bar(x - ancho / 2, obs, ancho, label="Observado", color=color, alpha=0.85)
        ax.bar(x + ancho / 2, exp, ancho, label="Esperado",  color="gray",  alpha=0.60)
        ax.set_xticks(x)
        ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=8)
        ax.set_title(
            f"{nombre}\nchi2 = {pok['estadistico']:.3f}  |  {_icono(pok['aprueba'])}  "
            f"(p = {pok['p_valor']:.4f})",
            fontsize=9, fontweight="bold",
        )
        ax.set_ylabel("Frecuencia")
        ax.legend(fontsize=9)

    plt.tight_layout()
    plt.savefig("fig3_poker.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("  Guardado: fig3_poker.png")


def plot_tabla_resumen(resultados_dict):
    """Tabla visual con todos los resultados de los cuatro tests."""
    headers = [
        "Generador",
        "Chi2 stat", "Chi2 p", "Chi2?",
        "KS stat",   "KS p",   "KS?",
        "Rachas Z",  "Rachas p", "Rachas?",
        "Poker stat","Poker p", "Poker?",
    ]
    filas = []
    for nombre, tests in resultados_dict.items():
        c = tests["chi2"]
        k = tests["ks"]
        r = tests["rachas"]
        p = tests["poker"]
        filas.append([
            nombre,
            f"{c['estadistico']:.3f}",  f"{c['p_valor']:.4f}", "SI" if c["aprueba"] else "NO",
            f"{k['estadistico']:.4f}",  f"{k['p_valor']:.4f}", "SI" if k["aprueba"] else "NO",
            f"{r['estadistico_Z']:.3f}",f"{r['p_valor']:.4f}", "SI" if r["aprueba"] else "NO",
            f"{p['estadistico']:.3f}",  f"{p['p_valor']:.4f}", "SI" if p["aprueba"] else "NO",
        ])

    fig, ax = plt.subplots(figsize=(17, 3.5))
    ax.axis("off")
    tabla = ax.table(cellText=filas, colLabels=headers, cellLoc="center", loc="center")
    tabla.auto_set_font_size(False)
    tabla.set_fontsize(8.5)
    tabla.scale(1.0, 2.1)

    # Estilo cabecera
    for c in range(len(headers)):
        tabla[0, c].set_facecolor("#1565C0")
        tabla[0, c].set_text_props(color="white", fontweight="bold")

    # Filas alternas + colorear SI/NO
    cols_veredicto = [3, 6, 9, 12]
    for r in range(1, len(filas) + 1):
        bg = "#F5F5F5" if r % 2 == 0 else "white"
        for c in range(len(headers)):
            tabla[r, c].set_facecolor(bg)
        for c in cols_veredicto:
            txt = filas[r - 1][c]
            tabla[r, c].set_facecolor("#C8E6C9" if txt == "SI" else "#FFCDD2")
            tabla[r, c].set_text_props(fontweight="bold")

    fig.suptitle(f"Resumen de Tests Estadisticos  (N = {N}, alpha = {ALPHA})",
                 fontsize=12, fontweight="bold", y=1.08)
    plt.tight_layout()
    plt.savefig("fig4_tabla_resumen.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("  Guardado: fig4_tabla_resumen.png")


# ==============================================================================
# MAIN
# ==============================================================================

def main():
    sep = "=" * 68

    print(sep)
    print("  TP 2.1 - Generadores Pseudoaleatorios")
    print(f"  N = {N}  |  alpha = {ALPHA}  |  k (Chi2) = {K}  |  semilla = {SEED}")
    print(sep)

    # ── 1. Generacion ──────────────────────────────────────────────────────
    gcl = GeneradorGCL(semilla=SEED)
    vn  = GeneradorVonNeumann(semilla=SEED)

    print("\n[1] Generando secuencias...")
    datos = {
        "GCL (ANSI C)":  gcl.generar(N),
        "Von Neumann":   vn.generar(N),
        "Python random": generar_python_random(N),
        "NumPy PCG64":   generar_numpy_pcg64(N),
    }

    if vn.degenerado_en:
        print(f"    AVISO: Von Neumann degenero en el paso {vn.degenerado_en} "
              f"(los restantes se rellenaron con 0.0)")
    if vn.ciclo_en:
        print(f"    AVISO: Von Neumann entro en ciclo en el paso {vn.ciclo_en}")

    # Mostrar primeros 5 valores de cada generador
    print()
    for nombre, seq in datos.items():
        muestra = ", ".join(f"{v:.6f}" for v in seq[:5])
        print(f"    {nombre:<20}: [{muestra}, ...]")

    # ── 2. Tests estadisticos ──────────────────────────────────────────────
    print(f"\n[2] Aplicando tests (alpha = {ALPHA})...\n")
    resultados = {}

    for nombre, seq in datos.items():
        r_chi = test_chi_cuadrado(seq)
        r_ks  = test_ks(seq)
        r_rac = test_rachas(seq)
        r_pok = test_poker(seq)

        resultados[nombre] = {
            "chi2":   r_chi,
            "ks":     r_ks,
            "rachas": r_rac,
            "poker":  r_pok,
        }

        def v(t): return _icono(t["aprueba"])

        print(f"  {nombre}")
        print(f"    Chi2  : stat = {r_chi['estadistico']:8.4f}  crit = {r_chi['valor_critico']:.4f}"
              f"  p = {r_chi['p_valor']:.4f}  -> {v(r_chi)}")
        print(f"    KS    : stat = {r_ks['estadistico']:8.4f}  crit = {r_ks['valor_critico']:.4f}"
              f"  p = {r_ks['p_valor']:.4f}  -> {v(r_ks)}")
        print(f"    Rachas: Z    = {r_rac['estadistico_Z']:8.4f}  crit = +/-{r_rac['valor_critico_Z']:.4f}"
              f"  p = {r_rac['p_valor']:.4f}  -> {v(r_rac)}")
        print(f"    Poker : stat = {r_pok['estadistico']:8.4f}  crit = {r_pok['valor_critico']:.4f}"
              f"  p = {r_pok['p_valor']:.4f}  -> {v(r_pok)}")
        print()

    # ── 3. Tabla resumen con Pandas ────────────────────────────────────────
    filas_df = []
    for nombre, tests in resultados.items():
        c = tests["chi2"]
        k = tests["ks"]
        r = tests["rachas"]
        p = tests["poker"]
        filas_df.append({
            "Generador":      nombre,
            "Chi2 stat":      round(c["estadistico"], 4),
            "Chi2 p-valor":   round(c["p_valor"], 4),
            "Chi2 aprueba":   c["aprueba"],
            "KS stat":        round(k["estadistico"], 4),
            "KS p-valor":     round(k["p_valor"], 4),
            "KS aprueba":     k["aprueba"],
            "Rachas Z":       round(r["estadistico_Z"], 4),
            "Rachas p-valor": round(r["p_valor"], 4),
            "Rachas aprueba": r["aprueba"],
            "Poker stat":     round(p["estadistico"], 4),
            "Poker p-valor":  round(p["p_valor"], 4),
            "Poker aprueba":  p["aprueba"],
        })

    df_resumen = pd.DataFrame(filas_df)
    print(sep)
    print("TABLA RESUMEN COMPLETA")
    print(sep)
    pd.set_option("display.max_columns", None)
    pd.set_option("display.width", 200)
    print(df_resumen.to_string(index=False))
    df_resumen.to_csv("resultados_tests.csv", index=False, encoding="utf-8")
    print("\nGuardado: resultados_tests.csv")

    # ── 4. Graficos ────────────────────────────────────────────────────────
    print("\n[3] Generando graficos...")
    plot_histogramas(datos)
    plot_coordenados(datos)
    plot_poker(resultados)
    plot_tabla_resumen(resultados)

    # ── 5. Conclusiones automaticas ────────────────────────────────────────
    print(f"\n{sep}")
    print("CONCLUSIONES")
    print(sep)
    for nombre, tests in resultados.items():
        aprobados = sum(t["aprueba"] for t in tests.values())
        print(f"  {nombre:<22}: {aprobados}/4 tests aprobados "
              f"{'[BUENA calidad]' if aprobados >= 3 else '[BAJA calidad]'}")

    print(f"\nListo. Archivos generados en el directorio actual.")
    return datos, resultados, df_resumen


if __name__ == "__main__":
    datos, resultados, df = main()
