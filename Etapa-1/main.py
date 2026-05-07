import random
import matplotlib.pyplot as plt

class Ruleta:

  NUMEROS = list(range(37))
  NUM_ESPERADO = 7
  PROMEDIO = (0 + 36) / 2
  VARIANZA = ((36 - 0 + 1) ** 2 - 1) / 12
  DESVIO = VARIANZA ** 0.5

  def __init__(self):
    pass

  def girar(self):
    return random.randint(0, 36)

class Resultado:
  def __init__(self,aciertos,tiradas):
    self.fAbsoluta = aciertos
    self.fRelativa = aciertos / tiradas

  def __str__(self):
    return f"Aciertos Absolutos: {self.fAbsoluta}, Aciertos Relativos: {self.fRelativa:.2f}"


class SIMULACION:

  TIRADAS = 100
  CORRIDAS = 1500

  def __init__(self):
    self.ruleta = Ruleta()
    self.resultados = []
    self.numeros = []

  def ejecutar(self):
    for _ in range(self.CORRIDAS):
      aciertos = 0
      numeros_corrida = []
      for _ in range(self.TIRADAS):
        numero = self.ruleta.girar()
        numeros_corrida.append(numero)
        if numero == Ruleta.NUM_ESPERADO:
          aciertos += 1
      resultado = Resultado(aciertos, self.TIRADAS)
      self.resultados.append(resultado)
      self.numeros.append(numeros_corrida)
    return self.resultados

  def grafico_frecuencia_relativa_acumulada(self, ax=None):
      fre = 1 / len(Ruleta.NUMEROS)

      frn_acum = []
      aciertos_total = 0
      tiradas_total = 0
      for corrida in self.numeros:
          for numero in corrida:
              tiradas_total += 1
              if numero == Ruleta.NUM_ESPERADO:
                  aciertos_total += 1
          frn_acum.append(aciertos_total / tiradas_total)

      corridas = list(range(1, len(frn_acum) + 1))

      standalone = ax is None
      if standalone:
          _, ax = plt.subplots(figsize=(12, 6))

      ax.plot(corridas, frn_acum, color='red', linewidth=1.5, label=f'frn (frecuencia relativa acumulada de {Ruleta.NUM_ESPERADO})')
      ax.axhline(y=fre, color='blue', linewidth=2, label=f'fre: {fre:.4f} (1/37)')
      ax.set_xlim(1, self.CORRIDAS)
      ax.set_xlabel('n (número de corridas)')
      ax.set_ylabel('fr (frecuencia relativa)')
      ax.set_title('Frecuencia Relativa Acumulada')
      ax.legend()
      ax.grid(alpha=0.3)

      if standalone:
          plt.show()

  def grafico_promedio(self, ax=None):
      vpe = Ruleta.PROMEDIO

      vpn_acum = []
      suma = 0
      count = 0
      for corrida in self.numeros:
          for n in corrida:
              suma += n
              count += 1
          vpn_acum.append(suma / count)

      corridas = list(range(1, len(vpn_acum) + 1))

      standalone = ax is None
      if standalone:
          _, ax = plt.subplots(figsize=(12, 6))

      ax.plot(corridas, vpn_acum, color='red', linewidth=1.5, label='vpn (promedio acumulado)')
      ax.axhline(y=vpe, color='blue', linewidth=2, label=f'vpe: {vpe:.2f}')
      ax.set_xlim(1, self.CORRIDAS)
      ax.set_xlabel('n (número de corridas)')
      ax.set_ylabel('vp (valor promedio)')
      ax.set_title('Promedio Acumulado')
      ax.legend()
      ax.grid(alpha=0.3)

      if standalone:
          plt.show()

  def grafico_desvio(self, ax=None):
      vde = Ruleta.DESVIO

      vd_acum = []
      suma = 0
      suma_sq = 0
      count = 0
      for corrida in self.numeros:
          for n in corrida:
              suma += n
              suma_sq += n ** 2
              count += 1
          media = suma / count
          varianza = suma_sq / count - media ** 2
          vd_acum.append(varianza ** 0.5)

      corridas = list(range(1, len(vd_acum) + 1))

      standalone = ax is None
      if standalone:
          _, ax = plt.subplots(figsize=(12, 6))

      ax.plot(corridas, vd_acum, color='red', linewidth=1.5, label='vd (desvío acumulado)')
      ax.axhline(y=vde, color='blue', linewidth=2, label=f'vde: {vde:.2f}')
      ax.set_xlim(1, self.CORRIDAS)
      ax.set_xlabel('n (número de corridas)')
      ax.set_ylabel('vd (valor del desvío)')
      ax.set_title('Desvío Acumulado')
      ax.legend()
      ax.grid(alpha=0.3)

      if standalone:
          plt.show()

  def grafico_varianza(self, ax=None):
      vve = Ruleta.VARIANZA

      vvn_acum = []
      suma = 0
      suma_sq = 0
      count = 0
      for corrida in self.numeros:
          for n in corrida:
              suma += n
              suma_sq += n ** 2
              count += 1
          media = suma / count
          varianza = suma_sq / count - media ** 2
          vvn_acum.append(varianza)

      corridas = list(range(1, len(vvn_acum) + 1))

      standalone = ax is None
      if standalone:
          _, ax = plt.subplots(figsize=(12, 6))

      ax.plot(corridas, vvn_acum, color='red', linewidth=1.5, label='vvn (varianza acumulada)')
      ax.axhline(y=vve, color='blue', linewidth=2, label=f'vve: {vve:.2f}')
      ax.set_xlim(1, self.CORRIDAS)
      ax.set_xlabel('n (número de corridas)')
      ax.set_ylabel('vv (valor de la varianza)')
      ax.set_title('Varianza Acumulada')
      ax.legend()
      ax.grid(alpha=0.3)

      if standalone:
          plt.show()

  def nube_frecuencia_relativa(self, ax=None):
      fre = 1 / len(Ruleta.NUMEROS)
      tiradas = list(range(1, self.TIRADAS + 1))

      standalone = ax is None
      if standalone:
          _, ax = plt.subplots(figsize=(12, 6))

      for corrida in self.numeros:
          frn = []
          aciertos = 0
          for i, numero in enumerate(corrida):
              if numero == Ruleta.NUM_ESPERADO:
                  aciertos += 1
              frn.append(aciertos / (i + 1))
          ax.plot(tiradas, frn, linewidth=0.5, alpha=0.4)

      ax.axhline(y=fre, color='black', linestyle='--', linewidth=1.5, label=f'fre: {fre:.4f} (1/37)')
      ax.set_xlim(1, self.TIRADAS)
      ax.set_xlabel('Tirada')
      ax.set_ylabel('Frecuencia Relativa')
      ax.set_title('Nube de Curvas - Frecuencia Relativa')
      ax.legend()
      ax.grid(alpha=0.3)

      if standalone:
          plt.show()

  def nube_promedio(self, ax=None):
      vpe = Ruleta.PROMEDIO
      tiradas = list(range(1, self.TIRADAS + 1))

      standalone = ax is None
      if standalone:
          _, ax = plt.subplots(figsize=(12, 6))

      for corrida in self.numeros:
          vpn = []
          suma = 0
          for i, numero in enumerate(corrida):
              suma += numero
              vpn.append(suma / (i + 1))
          ax.plot(tiradas, vpn, linewidth=0.5, alpha=0.4)

      ax.axhline(y=vpe, color='black', linestyle='--', linewidth=1.5, label=f'vpe: {vpe:.2f}')
      ax.set_xlim(1, self.TIRADAS)
      ax.set_xlabel('Tirada')
      ax.set_ylabel('Promedio')
      ax.set_title('Nube de Curvas - Promedio')
      ax.legend()
      ax.grid(alpha=0.3)

      if standalone:
          plt.show()

  def nube_desvio(self, ax=None):
      vde = Ruleta.DESVIO
      tiradas = list(range(1, self.TIRADAS + 1))

      standalone = ax is None
      if standalone:
          _, ax = plt.subplots(figsize=(12, 6))

      for corrida in self.numeros:
          vdn = []
          suma = 0
          suma_sq = 0
          for i, numero in enumerate(corrida):
              suma += numero
              suma_sq += numero ** 2
              media = suma / (i + 1)
              varianza = suma_sq / (i + 1) - media ** 2
              vdn.append(varianza ** 0.5)
          ax.plot(tiradas, vdn, linewidth=0.5, alpha=0.4)

      ax.axhline(y=vde, color='black', linestyle='--', linewidth=1.5, label=f'vde: {vde:.2f}')
      ax.set_xlim(1, self.TIRADAS)
      ax.set_xlabel('Tirada')
      ax.set_ylabel('Desvío')
      ax.set_title('Nube de Curvas - Desvío')
      ax.legend()
      ax.grid(alpha=0.3)

      if standalone:
          plt.show()

  def nube_varianza(self, ax=None):
      vve = Ruleta.VARIANZA
      tiradas = list(range(1, self.TIRADAS + 1))

      standalone = ax is None
      if standalone:
          _, ax = plt.subplots(figsize=(12, 6))

      for corrida in self.numeros:
          vvn = []
          suma = 0
          suma_sq = 0
          for i, numero in enumerate(corrida):
              suma += numero
              suma_sq += numero ** 2
              media = suma / (i + 1)
              varianza = suma_sq / (i + 1) - media ** 2
              vvn.append(varianza)
          ax.plot(tiradas, vvn, linewidth=0.5, alpha=0.4)

      ax.axhline(y=vve, color='black', linestyle='--', linewidth=1.5, label=f'vve: {vve:.2f}')
      ax.set_xlim(1, self.TIRADAS)
      ax.set_xlabel('Tirada')
      ax.set_ylabel('Varianza')
      ax.set_title('Nube de Curvas - Varianzas')
      ax.legend()
      ax.grid(alpha=0.3)

      if standalone:
          plt.show()

  def mostrar_estadisticos(self):
      todos_los_numeros = [n for corrida in self.numeros for n in corrida]
      total = len(todos_los_numeros)

      fr_simulada = sum(1 for n in todos_los_numeros if n == Ruleta.NUM_ESPERADO) / total
      promedio_simulado = sum(todos_los_numeros) / total
      varianza_simulada = sum((n - promedio_simulado) ** 2 for n in todos_los_numeros) / total
      desvio_simulado = varianza_simulada ** 0.5

      print("--- Estadísticos Esperados ---")
      print(f"Frecuencia relativa (fr):   {1 / len(Ruleta.NUMEROS):.3f}")
      print(f"Valor promedio (x̄):         {Ruleta.PROMEDIO}")
      print(f"Desvío estándar (s):        {Ruleta.DESVIO:.4f}")
      print(f"Varianza (σ²):              {Ruleta.VARIANZA:.1f}")
      print()
      print("--- Estadísticos Simulados ---")
      print(f"Frecuencia relativa simulada:   {fr_simulada:.4f}")
      print(f"Valor promedio simulado:        {promedio_simulado:.4f}")
      print(f"Desvío estándar simulado:       {desvio_simulado:.4f}")
      print(f"Varianza simulada:              {varianza_simulada:.4f}")

  def mostrar_resultados(self):
      fig, axes = plt.subplots(2, 4, figsize=(24, 10))
      fig.suptitle('Simulación Ruleta Europea', fontsize=14)

      self.nube_frecuencia_relativa(ax=axes[0, 0])
      self.grafico_frecuencia_relativa_acumulada(ax=axes[0, 1])
      self.nube_promedio(ax=axes[0, 2])
      self.grafico_promedio(ax=axes[0, 3])

      self.nube_desvio(ax=axes[1, 0])
      self.grafico_desvio(ax=axes[1, 1])
      self.nube_varianza(ax=axes[1, 2])
      self.grafico_varianza(ax=axes[1, 3])

      plt.tight_layout()
      plt.show()


if __name__ == "__main__":
  simulacion = SIMULACION()
  resultados = simulacion.ejecutar()
  simulacion.mostrar_estadisticos()
  simulacion.mostrar_resultados()
