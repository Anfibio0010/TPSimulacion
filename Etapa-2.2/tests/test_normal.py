import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'Etapa-2.1'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from distribuciones import normal_box_muller, normal_rechazo
from scipy.stats import chi2 as chi2_dist, kstest, norm
import math, numpy as np

N        = 1000
ALPHA    = 0.05
K        = 10
SEMILLAS = [1273, 3728, 7198]

def test_chi2_normal(datos, mu, sigma, k=K, alpha=ALPHA):
    n = len(datos)
    limites = [norm.ppf(j/k, loc=mu, scale=sigma) for j in range(k)] + [float('inf')]
    limites[0] = float('-inf')
    observado, _ = np.histogram(datos, bins=limites)
    esperado = n / k
    stat = float(np.sum((observado - esperado)**2 / esperado))
    gl   = k - 1
    crit = float(chi2_dist.ppf(1 - alpha, gl))
    return {"estadistico": stat, "valor_critico": crit,
            "aprueba": stat <= crit, "p_valor": float(1 - chi2_dist.cdf(stat, gl))}

def test_ks_normal(datos, mu, sigma, alpha=ALPHA):
    stat, p = kstest(datos, "norm", args=(mu, sigma))
    crit = 1.36 / math.sqrt(len(datos))
    return {"estadistico": float(stat), "valor_critico": crit,
            "aprueba": float(stat) <= crit, "p_valor": float(p)}

def correr(nombre, muestras):
    chi = test_chi2_normal(muestras, 0, 1)
    ks  = test_ks_normal(muestras, 0, 1)
    print(f"  {nombre}")
    print(f"    Chi2 : stat={chi['estadistico']:.4f}  crit={chi['valor_critico']:.4f}  p={chi['p_valor']:.4f}  -> {'APRUEBA' if chi['aprueba'] else 'RECHAZA'}")
    print(f"    KS   : stat={ks['estadistico']:.4f}   crit={ks['valor_critico']:.4f}  p={ks['p_valor']:.4f}  -> {'APRUEBA' if ks['aprueba'] else 'RECHAZA'}")

print("=" * 60)
print("  TEST NORMAL N(0,1)  —  N=1000, alpha=0.05")
print("=" * 60)

for s in SEMILLAS:
    print(f"\nSemilla: {s}")
    correr("Box-Muller", normal_box_muller(0, 1, N, s))
    correr("Rechazo   ", normal_rechazo(0, 1, N, s))

print("\n" + "=" * 60)
