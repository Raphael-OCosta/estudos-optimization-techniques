TITULO = "Filas: quantas equipes na doca"
MISSAO = (
    "Caminhões chegam à doca de carga, em média 9 por hora, e uma equipe descarrega 12 por hora. Caminhão parado "
    "custa R$ 180/h e cada equipe, R$ 95/h. Você vai calcular as medidas do **M/M/1** e do **M/M/c** com as "
    "fórmulas do livro, confirmar a **lei de Little**, escolher o número de equipes que minimiza o custo total e "
    "validar tudo com uma **simulação de eventos**."
)
ENTREGA = "o módulo `PKG/filas.py` (M/M/1, M/M/c com Erlang C e um simulador de fila) e a decisão de quantas equipes contratar."
LEITURA = [("8.1.1 Elements of the Queuing System", 265), ("8.1.2 Kendall Notation", 267),
           ("8.2 Single-Server Queuing Model with Poisson Arrivals and Exponential Service Times", 268),
           ("8.3 Multiple-Server Queuing Model", 274), ("8.4 Little's Relationships for Queuing Models", 281)]

PASSOS = [
    ("texto",
     "## Ideia em 30 segundos\n"
     "Na notação de Kendall M/M/c, as chegadas são de Poisson (taxa λ), o atendimento é exponencial (taxa μ) e há c "
     "servidores. A utilização é `ρ = λ/(cμ)` e precisa ser menor que 1.\n\n"
     "**No M/M/1:**\n"
     "- `L = ρ/(1-ρ)` caminhões no sistema;\n"
     "- `W = 1/(μ-λ)` horas no sistema;\n"
     "- `Lq = ρ²/(1-ρ)` caminhões na fila;\n"
     "- `Wq = ρ/(μ-λ)` horas na fila.\n\n"
     "**Lei de Little:** `L = λ·W` vale para quase qualquer fila."),

    ("arquivo",
     "**O módulo de filas.** Crie `filas.py` com:\n"
     "- `mm1(lam, mu)`: um dicionário com ρ, L, Lq, W, Wq e `P0`;\n"
     "- `mmc(lam, mu, c)`: com a fórmula de Erlang C para a probabilidade de esperar e "
     "`Lq = P(esperar)·ρ/(1-ρ)`; o resto pela lei de Little;\n"
     "- `simular(lam, mu, c, n_clientes, semente)`: sorteia as chegadas e os atendimentos exponenciais e devolve "
     "as médias de Wq e de W.",
     "filas.py",
     r'''"""Teoria das filas: fórmulas M/M/1 e M/M/c e um simulador simples."""
import heapq
from math import factorial

import numpy as np


def mm1(lam, mu):
    rho = lam / mu
    if rho >= 1:
        raise ValueError("fila instável: λ >= μ")
    return {"rho": rho, "P0": 1 - rho, "L": rho / (1 - rho), "Lq": rho ** 2 / (1 - rho),
            "W": 1 / (mu - lam), "Wq": rho / (mu - lam)}


def mmc(lam, mu, c):
    a, rho = lam / mu, lam / (c * mu)
    if rho >= 1:
        raise ValueError("fila instável: λ >= cμ")
    soma = sum(a ** k / factorial(k) for k in range(c))
    ultimo = a ** c / (factorial(c) * (1 - rho))
    p0 = 1 / (soma + ultimo)
    p_espera = ultimo * p0
    Lq = p_espera * rho / (1 - rho)
    Wq = Lq / lam
    return {"rho": rho, "P0": p0, "P_esperar": p_espera, "Lq": Lq, "Wq": Wq, "W": Wq + 1 / mu, "L": lam * (Wq + 1 / mu)}


def simular(lam, mu, c, n_clientes=50000, semente=0):
    r = np.random.default_rng(semente)
    chegadas = np.cumsum(r.exponential(1 / lam, n_clientes))
    servico = r.exponential(1 / mu, n_clientes)
    livres = [0.0] * c
    heapq.heapify(livres)
    esperas, sistema = np.empty(n_clientes), np.empty(n_clientes)
    for i, (t, s) in enumerate(zip(chegadas, servico)):
        livre = heapq.heappop(livres)
        inicio = max(t, livre)
        heapq.heappush(livres, inicio + s)
        esperas[i], sistema[i] = inicio - t, inicio + s - t
    return {"Wq": float(esperas.mean()), "W": float(sistema.mean())}'''),

    ("tarefa",
     "**M/M/1 com uma equipe.** Calcule as medidas com `CHEGADAS_HORA` e `ATENDIMENTO_HORA`, mostre as esperas em "
     "**minutos** e confira a lei de Little (`L = λW` e `Lq = λWq`).",
     r'''from PKG.filas import mm1, mmc, simular
lam, mu = CHEGADAS_HORA, ATENDIMENTO_HORA
m = mm1(lam, mu)
print({k: round(v, 3) for k, v in m.items()})
print(f"espera na fila {m['Wq'] * 60:.1f} min | no sistema {m['W'] * 60:.1f} min")
print("Little:", round(m["L"], 4), "=", round(lam * m["W"], 4), "|", round(m["Lq"], 4), "=", round(lam * m["Wq"], 4))'''),

    ("tarefa",
     "**Simulação confirma.** Rode o seu simulador com 1 equipe e compare Wq e W com as fórmulas. Depois desenhe "
     "como Wq explode quando ρ se aproxima de 1 (λ de 1 a 11,5).",
     r'''import matplotlib.pyplot as plt
s = simular(lam, mu, 1)
print("simulação Wq:", round(s["Wq"] * 60, 1), "min | fórmula:", round(m["Wq"] * 60, 1), "min")
lams = np.linspace(1, 11.5, 50)
plt.plot(lams / mu, [mm1(l, mu)["Wq"] * 60 for l in lams]); plt.xlabel("ρ = λ/μ"); plt.ylabel("espera na fila (min)")
plt.title("A fila explode perto de ρ = 1"); plt.show()'''),

    ("tarefa",
     "**Mais equipes: M/M/c.** Para c = 1 a 4, mostre ρ, a chance de esperar, Wq em minutos e o **custo total por "
     "hora** = `CUSTO_EQUIPE·c + CUSTO_CAMINHAO_PARADO·L`. Quantas equipes minimizam o custo? Confira o c ótimo com "
     "a simulação.",
     r'''linhas = []
for c in range(1, 5):
    r_ = mmc(lam, mu, c)
    linhas.append({"equipes": c, "rho": r_["rho"], "P_esperar": r_["P_esperar"], "Wq_min": r_["Wq"] * 60,
                   "custo_h": CUSTO_EQUIPE * c + CUSTO_CAMINHAO_PARADO * r_["L"]})
t = pd.DataFrame(linhas).set_index("equipes").round(3); display(t)
c_ot = int(t["custo_h"].idxmin())
print("melhor:", c_ot, "equipes | simulação Wq:", round(simular(lam, mu, c_ot)["Wq"] * 60, 2), "min | fórmula:", round(t.loc[c_ot, "Wq_min"], 2))'''),

    ("tarefa",
     "**Uma equipe rápida ou duas lentas?** Compare um M/M/1 com μ = 24 contra um M/M/2 com μ = 12 cada (a mesma "
     "capacidade total). Qual dá a menor espera na fila e qual dá o menor tempo no sistema? Explique num comentário.",
     r'''um_rapido, dois_lentos = mm1(lam, 24), mmc(lam, 12, 2)
print(f"1 rápida: Wq {um_rapido['Wq'] * 60:.2f} min | W {um_rapido['W'] * 60:.2f} min")
print(f"2 lentas: Wq {dois_lentos['Wq'] * 60:.2f} min | W {dois_lentos['W'] * 60:.2f} min")
# Duas equipes esperam menos na fila (raramente as duas estão ocupadas), mas cada descarga leva o dobro do tempo:
# no sistema, a equipe única e rápida ganha.'''),
]
