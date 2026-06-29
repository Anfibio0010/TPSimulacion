import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'Etapa-2.1'))

from generadores import GeneradorGCL
from scipy.stats import chi2 as chi2_dist

N, ALPHA, SEMILLAS = 1000, 0.05, [1273, 3728, 7198]

# Tabla de demanda diaria: valores y probabilidades
VALORES = [0, 1, 2, 3, 4]
PROBS   = [0.10, 0.20, 0.30, 0.25, 0.15]

# CDF acumulada
CDF = []
acum = 0.0
for p in PROBS:
    acum += p
    CDF.append(acum)


def generar_empirica(n_muestras, semilla):
    gcl = GeneradorGCL(semilla=semilla)
    muestras = []
    for _ in range(n_muestras):
        u = gcl.siguiente()
        for i, f in enumerate(CDF):
            if u <= f:
                muestras.append(VALORES[i])
                break
    return muestras


def test_chi2_empirica(datos, alpha=ALPHA):
    n = len(datos)
    obs = [datos.count(x) for x in VALORES]
    exp = [n * p for p in PROBS]

    stat = sum((o - e) ** 2 / e for o, e in zip(obs, exp))
    gl   = len(VALORES) - 1
    crit = chi2_dist.ppf(1 - alpha, gl)
    return {
        "estadistico": stat,
        "valor_critico": crit,
        "aprueba": stat <= crit,
        "p_valor": float(1 - chi2_dist.cdf(stat, gl)),
        "grados_libertad": gl,
    }


print("=" * 60)
print("  TEST EMPÍRICA DISCRETA (demanda diaria)  —  N=1000, alpha=0.05")
print("=" * 60)
for s in SEMILLAS:
    datos = generar_empirica(N, s)
    r = test_chi2_empirica(datos)
    print(f"\nSemilla: {s}")
    print(f"  Chi2 : stat={r['estadistico']:.4f}  crit={r['valor_critico']:.4f}"
          f"  gl={r['grados_libertad']}  p={r['p_valor']:.4f}"
          f"  -> {'APRUEBA' if r['aprueba'] else 'RECHAZA'}")
print("\n" + "=" * 60)
