import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'Etapa-2.1'))

from generadores import GeneradorGCL
from scipy.stats import chi2 as chi2_dist, kstest
import math, numpy as np

N        = 1000
ALPHA    = 0.05
K        = 10
SEMILLAS = [1273, 3728, 7198]

def generar_exponencial(lam, n, semilla):
    gcl = GeneradorGCL(semilla=semilla)
    return [-math.log(gcl.siguiente()) / lam for _ in range(n)]

def test_chi2_exp(datos, lam, k=K, alpha=ALPHA):
    n = len(datos)
    limites = [-math.log(1 - j/k) / lam for j in range(k)] + [float('inf')]
    observado, _ = np.histogram(datos, bins=limites)
    esperado = n / k
    stat = float(np.sum((observado - esperado)**2 / esperado))
    gl   = k - 1
    crit = float(chi2_dist.ppf(1 - alpha, gl))
    return {"estadistico": stat, "valor_critico": crit,
            "aprueba": stat <= crit, "p_valor": float(1 - chi2_dist.cdf(stat, gl))}

def test_ks_exp(datos, lam, alpha=ALPHA):
    stat, p = kstest(datos, "expon", args=(0, 1/lam))
    crit = 1.36 / math.sqrt(len(datos))
    return {"estadistico": float(stat), "valor_critico": crit,
            "aprueba": float(stat) <= crit, "p_valor": float(p)}

print("=" * 60)
print("  TEST EXPONENCIAL Exp(λ=1)  —  N=1000, alpha=0.05")
print("=" * 60)

for s in SEMILLAS:
    muestras = generar_exponencial(1.0, N, s)
    chi = test_chi2_exp(muestras, 1.0)
    ks  = test_ks_exp(muestras, 1.0)
    print(f"\nSemilla: {s}")
    print(f"  Chi2 : stat={chi['estadistico']:.4f}  crit={chi['valor_critico']:.4f}  p={chi['p_valor']:.4f}  -> {'APRUEBA' if chi['aprueba'] else 'RECHAZA'}")
    print(f"  KS   : stat={ks['estadistico']:.4f}   crit={ks['valor_critico']:.4f}  p={ks['p_valor']:.4f}  -> {'APRUEBA' if ks['aprueba'] else 'RECHAZA'}")

print("\n" + "=" * 60)
