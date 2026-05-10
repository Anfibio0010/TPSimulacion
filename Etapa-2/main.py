"""
Simulación de Ruleta — Etapa 2
Compara 4 estrategias de apuesta: Martingala, D'Alembert, Fibonacci, Paroli.

Ejemplos de uso
---------------
  # Color (rojo / negro):
  python main.py -c 10 -n 1000 -e color   -v rojo  -a 100000

  # Paridad (par / impar):
  python main.py -c 10 -n 100 -e paridad -v par   -a 100000

  # Tercio — docenas (1 / 2 / 3):
  python main.py -c 10 -n 100 -e tercio  -v 1     -a 100000

  # Fila — columnas del tapete (1 / 2 / 3):
  python main.py -c 10 -n 100 -e fila    -v 2     -a 100000

  # Número directo (0-36):
  python main.py -c 10 -n 100 -e numero  -v 17    -a 100000

  # Capital infinito — la casa siempre puede pagar:
  python main.py -c 10 -n 100 -e color   -v rojo  -a 0

  # Sin -v el valor se elige interactivamente:
  python main.py -c 10 -n 100 -e color -a 100000
"""

import argparse
import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from Logica.Ruleta import Ruleta
from Logica.Jugador import Martingala, DAlembert, Fibonacci, Paroli

APUESTA_BASE = 1000

APUESTAS_DISPONIBLES = {
    "color":   {"valores": ["rojo", "negro"],  "prob": 18 / 37},
    "paridad": {"valores": ["par", "impar"],   "prob": 18 / 37},
    "tercio":  {"valores": [1, 2, 3],          "prob": 12 / 37},
    "fila":    {"valores": [1, 2, 3],          "prob": 12 / 37},
    "numero":  {"valores": list(range(37)),    "prob":  1 / 37},
}

COLORES_ESTRATEGIA = {
    "Martingala": "#E63946",
    "DAlembert":  "#2196F3",
    "Fibonacci":  "#4CAF50",
    "Paroli":     "#FF9800",
}

ETIQUETAS = {
    "Martingala": "Martingala",
    "DAlembert":  "D'Alembert",
    "Fibonacci":  "Fibonacci",
    "Paroli":     "Paroli",
}


# ── CLI ───────────────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description="Simulación de Ruleta con 4 estrategias de apuesta.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "-e", "--tipo", type=str, required=True,
        choices=list(APUESTAS_DISPONIBLES.keys()), metavar="TIPO",
        help="Tipo de apuesta: color | paridad | tercio | fila | numero",
    )
    parser.add_argument(
        "-v", "--valor", type=str, default=None,
        help="Valor apostado. Si se omite, se pide interactivamente.",
    )
    parser.add_argument(
        "-c", "--corridas", type=int, default=10,
        help="Número de corridas (default: 10)",
    )
    parser.add_argument(
        "-n", "--tiradas", type=int, default=100,
        help="Número de tiradas por corrida (default: 100)",
    )
    parser.add_argument(
        "-a", "--capital", type=str, default="100000",
        help="Capital inicial por jugador. Use 0 para capital infinito (default: 100000)",
    )
    return parser.parse_args()


def _resolver_capital(capital_str):
    """Devuelve (capital_float, capital_inicial_int, es_infinito)."""
    s = capital_str.strip().lower()
    if s in ("0", "infinito", "inf"):
        return float("inf"), 0, True
    try:
        v = int(s)
        if v <= 0:
            raise ValueError
        return float(v), v, False
    except ValueError:
        print(f"Error: capital '{capital_str}' inválido. Use un entero positivo o 0 para infinito.")
        sys.exit(1)


def _resolver_valor(tipo, valor_str):
    """Convierte el string del argumento al tipo correcto y valida."""
    valores_validos = APUESTAS_DISPONIBLES[tipo]["valores"]
    if tipo in ("tercio", "fila", "numero"):
        try:
            v = int(valor_str)
        except (ValueError, TypeError):
            return None
    else:
        v = valor_str
    return v if v in valores_validos else None


def _pedir_valor_interactivo(tipo):
    valores = APUESTAS_DISPONIBLES[tipo]["valores"]
    print(f"\nValores disponibles para '{tipo}':")
    for i, v in enumerate(valores, 1):
        print(f"  {i}. {v}")
    while True:
        try:
            op = int(input(f"Seleccione valor (1-{len(valores)}): "))
            if 1 <= op <= len(valores):
                return valores[op - 1]
        except ValueError:
            pass
        print("  Opción inválida.")


# ── Simulación ────────────────────────────────────────────────────────────────

def _crear_jugadores(categoria, valor, capital):
    kw = {"categoria": categoria, "valor": valor}
    return {
        "Martingala": Martingala("Martingala", capital, apuesta_base=APUESTA_BASE, **kw),
        "DAlembert":  DAlembert("D'Alembert",  capital, unidad_base=APUESTA_BASE,  **kw),
        "Fibonacci":  Fibonacci("Fibonacci",   capital, unidad_base=APUESTA_BASE,  **kw),
        "Paroli":     Paroli("Paroli",         capital, apuesta_base=APUESTA_BASE, **kw),
    }


def simular(categoria, valor, num_corridas, num_tiradas, capital):
    """Devuelve un DataFrame con un registro por (corrida × tirada × estrategia)."""
    ruleta  = Ruleta()
    records = []

    for corrida in range(1, num_corridas + 1):
        jugadores = _crear_jugadores(categoria, valor, capital)

        for tirada in range(1, num_tiradas + 1):
            resultado_giro = ruleta.girar()

            for nombre, jugador in jugadores.items():
                saldo_antes = jugador.presupuesto  # ANTES de jugar
                res         = jugador.jugar_turno(ruleta, resultado_giro)
                gano        = res.get("gano", False)
                apuesta     = res.get("monto_apostado", 0.0)
                saldo       = res.get("saldo_actual", jugador.presupuesto)

                # Para capital infinito saldo_antes - saldo = inf - inf = NaN
                # entonces calculamos directo con el multiplicador de pago
                if saldo_antes == float('inf'):
                    pago = jugador.PAGOS.get(jugador.categoria_apuesta, 2)
                    delta_casino = -apuesta * (pago - 1) if gano else apuesta
                else:
                    delta_casino = saldo_antes - saldo
                    
                records.append({
                    "corrida":       corrida,
                    "tirada":        tirada,
                    "estrategia":    nombre,
                    "capital":       saldo,
                    "gano":          gano,
                    "apuesta":       apuesta,
                    "delta_casino":  delta_casino,
                    "en_bancarrota": jugador.en_bancarrota,
                })

    df = pd.DataFrame(records)
    df["pnl_delta"] = np.where(df["gano"], df["apuesta"], -df["apuesta"])
    df["pnl_acum"]  = df.groupby(["estrategia", "corrida"])["pnl_delta"].cumsum()
    return df

# ── Helpers de métricas ───────────────────────────────────────────────────────

def _ganancia_casino(df):
    return (
        df.groupby(["corrida", "tirada"])["delta_casino"]
        .sum()
        .groupby(level=0)
        .cumsum()
        .reset_index(name="ganancia_acumulada")
    )


def _quebrados_por_estrategia(df):
    """Cantidad de corridas en que cada estrategia llegó a bancarrota."""
    return (
        df.groupby(["estrategia", "corrida"])["en_bancarrota"]
        .last()
        .groupby(level=0)
        .sum()
        .reindex(["Martingala", "DAlembert", "Fibonacci", "Paroli"], fill_value=0)
    )


# ── Graficación ───────────────────────────────────────────────────────────────

def _plot_frsa(ax, df, nombre, num_tiradas, prob_teorica):
    frsa  = df[df["estrategia"] == nombre].groupby("tirada")["gano"].mean()
    color = COLORES_ESTRATEGIA[nombre]
    ax.bar(frsa.index, frsa.values, color=color, alpha=0.75, width=0.85)
    ax.axhline(prob_teorica, color="navy", linewidth=1.5, linestyle="--",
               label=f"P teórica ({prob_teorica:.3f})")
    ax.set_title(f"frsa  —  {ETIQUETAS[nombre]}", fontsize=9, fontweight="bold")
    ax.set_xlabel("n (número de tirada)", fontsize=8)
    ax.set_ylabel("fr (frecuencia relativa)", fontsize=8)
    ax.set_xlim(0, num_tiradas + 1)
    ax.set_ylim(0, 1)
    ax.legend(fontsize=7)
    ax.tick_params(labelsize=7)


def _plot_cc(ax, df, nombre, num_tiradas, capital_inicial, capital_infinito):
    sub   = df[df["estrategia"] == nombre]
    color = COLORES_ESTRATEGIA[nombre]

    if capital_infinito:
        col_y   = "pnl_acum"
        y_label = "Ganancia / Pérdida acumulada ($)"
        titulo  = f"P&L  —  {ETIQUETAS[nombre]}"
        ref_val = 0
        ref_lbl = "Referencia $0"
    else:
        col_y   = "capital"
        y_label = "cc (cantidad de capital)"
        titulo  = f"cc  —  {ETIQUETAS[nombre]}"
        ref_val = capital_inicial
        ref_lbl = f"fci (${capital_inicial:,})"

    for _, grupo in sub.groupby("corrida"):
        ax.plot(grupo["tirada"], grupo[col_y], color=color, alpha=0.20, linewidth=0.8)

    promedio = sub.groupby("tirada")[col_y].mean()
    ax.plot(promedio.index, promedio.values, color=color, linewidth=2.2, label="fc (promedio)")
    ax.axhline(ref_val, color="steelblue", linewidth=1.5, linestyle="-", label=ref_lbl)

    ax.set_title(titulo, fontsize=9, fontweight="bold")
    ax.set_xlabel("n (número de tiradas)", fontsize=8)
    ax.set_ylabel(y_label, fontsize=8)
    ax.set_xlim(0, num_tiradas + 1)
    ax.legend(fontsize=7)
    ax.tick_params(labelsize=7)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))


def _plot_casino(ax, casino_df, num_tiradas):
    prom = casino_df.groupby("tirada")["ganancia_acumulada"].mean()

    for _, grupo in casino_df.groupby("corrida"):
        ax.plot(grupo["tirada"], grupo["ganancia_acumulada"],
                color="#9C27B0", alpha=0.20, linewidth=0.9)

    ax.plot(prom.index, prom.values, color="#9C27B0", linewidth=2.5,
            label="Ganancia promedio casino")
    ax.axhline(0, color="black", linewidth=1, linestyle="--", alpha=0.6)
    ax.fill_between(prom.index, prom.values, 0,
                    where=(prom.values >= 0), alpha=0.12, color="green",
                    label="Casino ganando")
    ax.fill_between(prom.index, prom.values, 0,
                    where=(prom.values < 0), alpha=0.12, color="red",
                    label="Casino perdiendo")

    ax.set_title("Ganancia del Casino  vs  pérdida acumulada de las 4 estrategias",
                 fontsize=11, fontweight="bold")
    ax.set_xlabel("n (número de tiradas)", fontsize=9)
    ax.set_ylabel("Ganancia neta del casino ($)", fontsize=9)
    ax.set_xlim(0, num_tiradas + 1)
    ax.legend(fontsize=9)
    ax.tick_params(labelsize=8)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"${x:,.0f}"))


def _plot_quebrados(ax, df, num_corridas):
    orden    = ["Martingala", "DAlembert", "Fibonacci", "Paroli"]
    quebrados = _quebrados_por_estrategia(df)
    etiquetas = [ETIQUETAS[e] for e in quebrados.index]
    colores   = [COLORES_ESTRATEGIA[e] for e in quebrados.index]

    barras = ax.bar(etiquetas, quebrados.values, color=colores, alpha=0.80)
    for barra, v in zip(barras, quebrados.values):
        ax.text(
            barra.get_x() + barra.get_width() / 2,
            barra.get_height() + 0.05,
            str(int(v)), ha="center", va="bottom", fontsize=10, fontweight="bold",
        )

    ax.set_title("Corridas en\nbancarrota", fontsize=9, fontweight="bold")
    ax.set_ylabel(f"Corridas (/{num_corridas})", fontsize=8)
    ax.set_ylim(0, num_corridas + 1)
    ax.tick_params(labelsize=8)


def graficar(df, prob_teorica, categoria, valor,
             num_corridas, num_tiradas, capital_inicial, capital_infinito):
    estrategias = ["Martingala", "DAlembert", "Fibonacci", "Paroli"]
    cap_lbl     = "Infinito" if capital_infinito else f"${capital_inicial:,}"

    fig = plt.figure(figsize=(22, 16))
    fig.suptitle(
        f"Simulación Ruleta  |  Apuesta: {categoria} = {valor}  |  "
        f"{num_corridas} corridas × {num_tiradas} tiradas  |  Capital: {cap_lbl}",
        fontsize=13, fontweight="bold", y=0.99,
    )
    gs = gridspec.GridSpec(3, 4, figure=fig, hspace=0.50, wspace=0.35)

    # Fila 1 — frsa (igual en ambos modos)
    for col, nombre in enumerate(estrategias):
        _plot_frsa(fig.add_subplot(gs[0, col]), df, nombre, num_tiradas, prob_teorica)

    # Fila 2 — cc o P&L según modo
    for col, nombre in enumerate(estrategias):
        _plot_cc(fig.add_subplot(gs[1, col]), df, nombre,
                 num_tiradas, capital_inicial, capital_infinito)

    # Fila 3 — casino (3/4) + quebrados (1/4) si finito; casino full si infinito
    casino_df = _ganancia_casino(df)

    if capital_infinito:
        _plot_casino(fig.add_subplot(gs[2, :]), casino_df, num_tiradas)
    else:
        _plot_casino(fig.add_subplot(gs[2, :3]), casino_df, num_tiradas)
        _plot_quebrados(fig.add_subplot(gs[2, 3]), df, num_corridas)

    plt.tight_layout(rect=[0, 0, 1, 0.98])
    plt.show()


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    args = parse_args()

    capital, capital_inicial, capital_infinito = _resolver_capital(args.capital)

    if args.valor is not None:
        valor = _resolver_valor(args.tipo, args.valor)
        if valor is None:
            validos = APUESTAS_DISPONIBLES[args.tipo]["valores"]
            print(f"Error: '{args.valor}' no es válido para '{args.tipo}'. Válidos: {validos}")
            sys.exit(1)
    else:
        valor = _pedir_valor_interactivo(args.tipo)

    prob = APUESTAS_DISPONIBLES[args.tipo]["prob"]
    cap_lbl = "Infinito" if capital_infinito else f"${capital_inicial:,}"
    print(f"\nApuesta : {args.tipo} = {valor}  (P teórica = {prob:.4f})")
    print(f"Capital : {cap_lbl}")
    print(f"Corridas: {args.corridas} × {args.tiradas} tiradas")
    print("Ejecutando simulación...", flush=True)

    df = simular(args.tipo, valor, args.corridas, args.tiradas, capital)
    print(f"Completado — {len(df):,} registros generados.")

    graficar(df, prob, args.tipo, valor,
             args.corridas, args.tiradas, capital_inicial, capital_infinito)


if __name__ == "__main__":
    main()
