import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'Etapa-2.1'))

from generadores import GeneradorGCL
from scipy.stats import chi2 as chi2_dist
import math

N, ALPHA, SEMILLAS = 1000, 0.05, [1273, 3728, 7198]


def generar_poisson(lam, n_muestras, semilla):
    gcl = GeneradorGCL(semilla=semilla)
    umbral = math.exp(-lam)
    muestras = []
    for _ in range(n_muestras):
        P = gcl.siguiente()
        k = 0
        while P >= umbral:
            P *= gcl.siguiente()
            k += 1
        muestras.append(k)
    return muestras


def pmf_poisson(k, lam):
    return math.exp(-lam) * (lam ** k) / math.factorial(k)


def test_chi2_poisson(datos, lam, alpha=ALPHA):
    n = len(datos)
    k_max = max(datos) + 1
    valores = list(range(k_max))

    obs = [datos.count(k) for k in valores]
    exp = [n * pmf_poisson(k, lam) for k in valores]

    # fusionar cola izquierda (k pequeños con exp < 5)
    while exp[0] < 5 and len(exp) > 2:
        obs[1] += obs[0]; exp[1] += exp[0]
        obs, exp = obs[1:], exp[1:]

    # fusionar cola derecha (k grandes con exp < 5)
    while exp[-1] < 5 and len(exp) > 2:
        obs[-2] += obs[-1]; exp[-2] += exp[-1]
        obs, exp = obs[:-1], exp[:-1]

    stat = sum((o - e) ** 2 / e for o, e in zip(obs, exp))
    gl   = len(obs) - 1
    crit = chi2_dist.ppf(1 - alpha, gl)
    return {
        "estadistico": stat,
        "valor_critico": crit,
        "aprueba": stat <= crit,
        "p_valor": float(1 - chi2_dist.cdf(stat, gl)),
        "grados_libertad": gl,
    }


print("=" * 60)
print("  TEST POISSON (lambda=4)  —  N=1000, alpha=0.05")
print("=" * 60)
for s in SEMILLAS:
    datos = generar_poisson(4, N, s)
    r = test_chi2_poisson(datos, 4)
    print(f"\nSemilla: {s}")
    print(f"  Chi2 : stat={r['estadistico']:.4f}  crit={r['valor_critico']:.4f}"
          f"  gl={r['grados_libertad']}  p={r['p_valor']:.4f}"
          f"  -> {'APRUEBA' if r['aprueba'] else 'RECHAZA'}")
print("\n" + "=" * 60)
