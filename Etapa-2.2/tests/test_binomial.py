import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'Etapa-2.1'))

from generadores import GeneradorGCL
from scipy.stats import chi2 as chi2_dist
import math, numpy as np

N, ALPHA, SEMILLAS = 1000, 0.05, [1273, 3728, 7198]

def generar_binomial(n_ensayos, p, n_muestras, semilla):
    gcl = GeneradorGCL(semilla=semilla)
    return [sum(1 for _ in range(n_ensayos) if gcl.siguiente() < p)
            for _ in range(n_muestras)]

def pmf_binomial(x, n, p):
    return math.comb(n, x) * p**x * (1-p)**(n-x)

def test_chi2_binomial(datos, n_ensayos, p, alpha=ALPHA):
    n = len(datos)
    valores = list(range(n_ensayos + 1))
    obs = np.array([datos.count(x) for x in valores], dtype=float)
    exp = np.array([n * pmf_binomial(x, n_ensayos, p) for x in valores], dtype=float)

    while exp[0] < 5 and len(exp) > 2:
        obs[1] += obs[0]; exp[1] += exp[0]
        obs, exp = obs[1:], exp[1:]
    while exp[-1] < 5 and len(exp) > 2:
        obs[-2] += obs[-1]; exp[-2] += exp[-1]
        obs, exp = obs[:-1], exp[:-1]

    stat = float(np.sum((obs - exp)**2 / exp))
    gl   = len(obs) - 1
    crit = float(chi2_dist.ppf(1 - alpha, gl))
    return {"estadistico": stat, "valor_critico": crit,
            "aprueba": stat <= crit, "p_valor": float(1 - chi2_dist.cdf(stat, gl))}

print("=" * 60)
print("  TEST BINOMIAL B(n=20, p=0.5)  —  N=1000, alpha=0.05")
print("=" * 60)
for s in SEMILLAS:
    datos = generar_binomial(20, 0.5, N, s)
    r = test_chi2_binomial(datos, 20, 0.5)
    print(f"\nSemilla: {s}")
    print(f"  Chi2 : stat={r['estadistico']:.4f}  crit={r['valor_critico']:.4f}  p={r['p_valor']:.4f}  -> {'APRUEBA' if r['aprueba'] else 'RECHAZA'}")
print("\n" + "=" * 60)
