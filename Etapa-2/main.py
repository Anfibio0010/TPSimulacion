from Logica.Ruleta import Ruleta

class SIMULACION:

  def __init__(self, tiradas=150, corridas=10, num_esperado=7):
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

if __name__ == "__main__":
    print("Hello, World!")