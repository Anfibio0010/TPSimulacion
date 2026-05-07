import random
import matplotlib.pyplot as plt
class Ruleta: 
  #Numeros de la ruleta como atributo de clase
  NUMEROS = list(range(37))
  NUM_ESPERADO = 7
  def __init__(self):
    pass

  def girar(self):
    #Selecciona un numero al azar de la ruleta
    numero = random.randint(0, 36)
    if numero == self.NUM_ESPERADO:
      return True
    else:
      return False
class Resultado:
  def __init__(self,aciertos,tiradas):
    self.fAbsoulta = aciertos
    self.fRelativa = aciertos / tiradas
  def __str__(self):
    return f"Aciertos Absolutos: {self.fAbsoulta}, Aciertos Relativos: {self.fRelativa:.2f}"
class SIMULACION:
  TIRADAS = 100
  CORRIDAS = 1500
  def __init__(self):
    self.ruleta = Ruleta()
    self.resultados = []
  def ejecutar(self):
    for _ in range(self.CORRIDAS):
      aciertos = 0
      for _ in range(self.TIRADAS):
        if self.ruleta.girar():
          aciertos += 1
      resultado = Resultado(aciertos,self.TIRADAS)
      self.resultados.append(resultado)
    return self.resultados
  def grafico_frecuencia_relativa(self):

      frecuencias_rel = [resultado.fRelativa for resultado in self.resultados]
      tiradas = list(range(1, len(frecuencias_rel) + 1))

      plt.figure(figsize=(12, 6))
      plt.plot(tiradas, frecuencias_rel, marker='o', linestyle='-', markersize=2)
      # Agregar línea de frecuencia relativa esperada
      prob_teorica = 1/37
      plt.axhline(y=prob_teorica, color='red', linestyle='--', linewidth=2, 
                  label=f'Frecuencia Esperada: {prob_teorica:.4f} (1/37)')
      # Establecer los límites del eje X
      plt.xlim(1, self.CORRIDAS)
      plt.ylim(0.00, 0.20)
      plt.xlabel('Número de Corrida')
      plt.ylabel('Frecuencia Relativa')
      plt.title('Frecuencia Relativa por Corrida')
      plt.grid(alpha=0.3)
      plt.show()


  def grafico_promedio_corrida(self):
      # Obtener la frecuencia absoluta de cada corrida
      frecuencias_abs = [resultado.fAbsoulta for resultado in self.resultados]

      # Calcular el promedio acumulado
      promedio_acum = []
      suma_acum = 0
      for i, freq in enumerate(frecuencias_abs):
          suma_acum += freq
          promedio_acum.append(suma_acum / (i + 1))

      corridas = list(range(1, len(promedio_acum) + 1))

      # Valor esperado teórico
      valor_esperado = self.TIRADAS / 37  # 100/37 ≈ 2.7 aciertos

      plt.figure(figsize=(12, 6))
      plt.plot(corridas, promedio_acum, linestyle='-', linewidth=1.5,
              color='blue', label='Promedio Acumulado')

      # Línea del valor esperado teórico
      plt.axhline(y=valor_esperado, color='red', linestyle='--', linewidth=2,
                  label=f'Valor Esperado: {valor_esperado:.2f} aciertos')

      plt.xlim(1, self.CORRIDAS)
      plt.xlabel('Número de Corrida')
      plt.ylabel('Promedio de Aciertos')
      plt.title('Promedio Acumulado de Aciertos por Corrida')
      plt.grid(alpha=0.3)
      plt.legend()
      plt.show()

  def mostrar_resultados(self):
    """ Graficos mínimos
     frecuencia relativa por tirada
     valor prom de las tiradas por tirada
     valor del desvio de la tirada por tirada
     valor de la varianza por tirada"""
    self.grafico_frecuencia_relativa()
    self.grafico_promedio_corrida()
      # Extraer frecuencias relativas de cada corrida




if __name__ == "__main__":
  simulacion = SIMULACION()
  resultados = simulacion.ejecutar()
  simulacion.mostrar_resultados()


