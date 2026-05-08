import random
import matplotlib.pyplot as plt
import argparse

class Ruleta:

  NUMEROS = list(range(37))
  PROMEDIO = (0 + 36) / 2
  VARIANZA = ((36 - 0 + 1) ** 2 - 1) / 12
  DESVIO = VARIANZA ** 0.5

  def __init__(self, num_esperado=7):
      if num_esperado not in self.NUMEROS:
          raise ValueError("El numero elegido debe estar entre 0 y 36.")
      self.num_esperado = num_esperado


  def girar(self):
    return random.randint(0, 36)

class Resultado:
  def __init__(self,aciertos,tiradas):
    self.fAbsoluta = aciertos
    self.fRelativa = aciertos / tiradas

  def __str__(self):
    return f"Aciertos Absolutos: {self.fAbsoluta}, Aciertos Relativos: {self.fRelativa:.2f}"


class SIMULACION:

  def __init__(self, tiradas=1500, corridas=100, num_esperado=7):
      if tiradas <= 0 or corridas <= 0:
          raise ValueError("Tiradas y corridas deben ser mayores a 0.")
      self.TIRADAS = tiradas
      self.CORRIDAS = corridas
      self.ruleta = Ruleta(num_esperado=num_esperado)
      self.resultados = []
      self.numeros = []

  def ejecutar(self):
    for _ in range(self.CORRIDAS):
      aciertos = 0
      numeros_corrida = []
      for _ in range(self.TIRADAS):
        numero = self.ruleta.girar()
        numeros_corrida.append(numero)
        if numero == self.ruleta.num_esperado:
          aciertos += 1
      resultado = Resultado(aciertos, self.TIRADAS)
      self.resultados.append(resultado)
      self.numeros.append(numeros_corrida)
    return self.resultados

  def grafico_frecuencia_relativa_acumulada(self, ax=None):
    fre = 1 / len(Ruleta.NUMEROS)
    tiradas_eje = list(range(1, self.TIRADAS + 1))

    # Acumuladores por corrida
    aciertos_por_corrida = [0] * self.CORRIDAS
    frn_acum = []
    for t in range(self.TIRADAS):
        for i, corrida in enumerate(self.numeros):
            if corrida[t] == self.ruleta.num_esperado:
                aciertos_por_corrida[i] += 1
        fr_t = sum(a / (t + 1) for a in aciertos_por_corrida) / self.CORRIDAS
        frn_acum.append(fr_t)

    standalone = ax is None
    if standalone:
        _, ax = plt.subplots(figsize=(12, 6))

    ax.plot(tiradas_eje, frn_acum, color='red', linewidth=1.5,
            label=f'frn (frecuencia relativa acumulada de {self.ruleta.num_esperado})')
    ax.axhline(y=fre, color='blue', linewidth=2, label=f'fre: {fre:.4f} (1/37)')
    ax.set_xlim(1, self.TIRADAS)
    ax.set_xlabel('n (número de tiradas)')
    ax.set_ylabel('fr (frecuencia relativa)')
    ax.set_title('Frecuencia Relativa Acumulada')
    ax.legend()
    ax.grid(alpha=0.3)

    if standalone:
        plt.show()

  def grafico_promedio(self, ax=None):
      vpe = Ruleta.PROMEDIO
      tiradas_eje = list(range(1, self.TIRADAS + 1))

      suma_por_corrida = [0.0] * self.CORRIDAS
      vpn_acum = []
      for t in range(self.TIRADAS):
          for i, corrida in enumerate(self.numeros):
              suma_por_corrida[i] += corrida[t]
          prom_t = sum(s / (t + 1) for s in suma_por_corrida) / self.CORRIDAS
          vpn_acum.append(prom_t)

      standalone = ax is None
      if standalone:
          _, ax = plt.subplots(figsize=(12, 6))

      ax.plot(tiradas_eje, vpn_acum, color='red', linewidth=1.5, label='vpn (promedio acumulado)')
      ax.axhline(y=vpe, color='blue', linewidth=2, label=f'vpe: {vpe:.2f}')
      ax.set_xlim(1, self.TIRADAS)
      ax.set_xlabel('n (número de tiradas)')
      ax.set_ylabel('vp (valor promedio)')
      ax.set_title('Promedio Acumulado')
      ax.legend()
      ax.grid(alpha=0.3)

      if standalone:
          plt.show()

  def grafico_desvio(self, ax=None):
      vde = Ruleta.DESVIO
      tiradas_eje = list(range(1, self.TIRADAS + 1))

      suma_por_corrida = [0.0] * self.CORRIDAS
      suma_sq_por_corrida = [0.0] * self.CORRIDAS
      vd_acum = []
      for t in range(self.TIRADAS):
          for i, corrida in enumerate(self.numeros):
              suma_por_corrida[i] += corrida[t]
              suma_sq_por_corrida[i] += corrida[t] ** 2
          desvios = []
          for i in range(self.CORRIDAS):
              media = suma_por_corrida[i] / (t + 1)
              var = suma_sq_por_corrida[i] / (t + 1) - media ** 2
              desvios.append(var ** 0.5)
          vd_acum.append(sum(desvios) / self.CORRIDAS)

      standalone = ax is None
      if standalone:
          _, ax = plt.subplots(figsize=(12, 6))

      ax.plot(tiradas_eje, vd_acum, color='red', linewidth=1.5, label='vd (desvío acumulado)')
      ax.axhline(y=vde, color='blue', linewidth=2, label=f'vde: {vde:.2f}')
      ax.set_xlim(1, self.TIRADAS)
      ax.set_xlabel('n (número de tiradas)')
      ax.set_ylabel('vd (valor del desvío)')
      ax.set_title('Desvío Acumulado')
      ax.legend()
      ax.grid(alpha=0.3)

      if standalone:
          plt.show()

  def grafico_varianza(self, ax=None):
      vve = Ruleta.VARIANZA
      tiradas_eje = list(range(1, self.TIRADAS + 1))

      suma_por_corrida = [0.0] * self.CORRIDAS
      suma_sq_por_corrida = [0.0] * self.CORRIDAS
      vvn_acum = []
      for t in range(self.TIRADAS):
          # enumerate nos da el indice 'i' (0,1,2..) y el iterado 'corrida' (array de tiradas)
          for i, corrida in enumerate(self.numeros):
              suma_por_corrida[i] += corrida[t]
              suma_sq_por_corrida[i] += corrida[t] ** 2
          varianzas = []
          for i in range(self.CORRIDAS):
              media = suma_por_corrida[i] / (t + 1)
              var = suma_sq_por_corrida[i] / (t + 1) - media ** 2
              varianzas.append(var)
          vvn_acum.append(sum(varianzas) / self.CORRIDAS)

      # Si se pasa un 'ax' desde afuera, no es standalone. Caso contrario lo es y hay que crear un gràfico propio (figura propia).
      standalone = ax is None
      if standalone:
          # Linea 168: plt.subplots devuelve (Figura, Axes).
          # Usamos '_' porque la variable Figura no la necesitamos acá (porque no configuramos nada de ella). 'ax' es el lienzo donde dibujaremos (y el que imprime).
          _, ax = plt.subplots(figsize=(12, 6))

      ax.plot(tiradas_eje, vvn_acum, color='red', linewidth=1.5, label='vvn (varianza acumulada)')
      ax.axhline(y=vve, color='blue', linewidth=2, label=f'vve: {vve:.2f}')
      ax.set_xlim(1, self.TIRADAS)
      ax.set_xlabel('n (número de tiradas)')
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
              if numero == self.ruleta.num_esperado:
                  aciertos += 1
              frn.append(aciertos / (i + 1))
          ax.plot(tiradas, frn, linewidth=0.5, alpha=0.4)

      ax.axhline(y=fre, color='black', linestyle='--', linewidth=1.5, label=f'fre: {fre:.4f} (1/37)')
      ax.set_ylim(-0.1, 0.4)
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

      fr_simulada = sum(1 for n in todos_los_numeros if n == self.ruleta.num_esperado) / total
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
      # plt.subplots genera la figura principal (fig) general de matplotlib 
      # y los 'axes' (una matriz 2x4 en este caso) donde van los subgraficos especificos.
      # Devuelve fig = ventana general, axes = array de subgraficos (de 2 filas, 4 columnas). 
      # axes [1,3] = ventana fila 2, columna 4.  Recordemos que el indice empieza en 0, por eso es [1,3] y no [2,4].
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

  def parse_args():
          # Un parser procesa los argumentos que se le pasan por consola al script, 
          # validando tipos (ej: int) y generando un objeto con esos valores.
          parser = argparse.ArgumentParser(
              description="Simulacion de ruleta europea"
          )
          # Cada add_argument define una opcion esperada en consola.
          # -c / --corridas: nombre corto y largo de la bandera.
          # type=int: trata de convertir el texto de la consola a entero.
          # default=100: si no se pasa, asume este valor.
          parser.add_argument("-c", "--corridas", type=int, default=100,
                              help="Cantidad de corridas")
          parser.add_argument("-n", "--tiradas", type=int, default=1500,
                              help="Cantidad de tiradas por corrida")
          parser.add_argument("-e", "--elegido", type=int, default=7,
                              help="Numero elegido (0 a 36)")
          return parser.parse_args()

# Forma de correr el script:   python Etapa-1/main.py -c 20 -n 100 -e 14
if __name__ == "__main__":
  args = SIMULACION.parse_args()
  simulacion = SIMULACION(corridas=args.corridas, tiradas=args.tiradas, num_esperado=args.elegido)
  simulacion.ejecutar()
  simulacion.mostrar_estadisticos()
  simulacion.mostrar_resultados()
