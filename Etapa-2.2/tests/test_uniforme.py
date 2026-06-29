import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'Etapa-2.1'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from generadores import test_chi_cuadrado, test_ks
from distribuciones import uniforme_inversa, uniforme_rechazo
import numpy as np

N        = 1000
ALPHA    = 0.05
SEMILLAS = [1273, 3728, 7198]

def correr_tests(nombre, muestras):
    arr = np.array(muestras)
    chi = test_chi_cuadrado(arr)
    ks  = test_ks(arr)
    print(f"  {nombre}")
    print(f"    Chi2 : stat={chi['estadistico']:.4f}  crit={chi['valor_critico']:.4f}  p={chi['p_valor']:.4f}  -> {'APRUEBA' if chi['aprueba'] else 'RECHAZA'}")
    print(f"    KS   : stat={ks['estadistico']:.4f}   crit={ks['valor_critico']:.4f}  p={ks['p_valor']:.4f}  -> {'APRUEBA' if ks['aprueba'] else 'RECHAZA'}")

print("=" * 60)
print("  TEST UNIFORME U(0,1)  —  N=1000, alpha=0.05")
print("=" * 60)

for s in SEMILLAS:
    print(f"\nSemilla: {s}")
    correr_tests("T. Inversa", uniforme_inversa(0, 1, N, s))
    correr_tests("Rechazo   ", uniforme_rechazo(0, 1, N, s))

print("\n" + "=" * 60)
