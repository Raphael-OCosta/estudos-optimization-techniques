TITULO = "Programação dinâmica e inteira"
MISSAO = (
    "Duas decisões de investimento:\n"
    "1. Como dividir R$ 5 milhões entre 3 lojas, com retornos que **não são lineares**? Isso é **programação "
    "dinâmica**: resolva por estágios e reaproveite as respostas.\n"
    "2. Quais dos 7 projetos aprovar, com orçamento em 2 anos? Projeto não se aprova pela metade: é **programação "
    "inteira 0/1**.\n\n"
    "Você vai escrever o *branch and bound* do zero, ver por que arredondar a solução contínua engana e conferir "
    "com o `scipy.optimize.milp`."
)
ENTREGA = "o módulo `PKG/inteira.py` (DP de alocação por estágios, mochila por DP e branch-and-bound 0/1) e o portfólio de projetos ótimo."
LEITURA = [("9.1 Introduction to Dynamic Programming", 286), ("9.3 Characteristics of Dynamic Programming", 288),
           ("9.4 Introduction to Integer Programming", 298), ("9.6 Solution of Integer Programming Using the Branch-and-Bound Method", 305),
           ("9.7 Solution of Integer Programming Using the Cutting Plane Method", 312)]

PASSOS = [
    ("texto",
     "## Ideia em 30 segundos\n"
     "**Programação dinâmica:** o *princípio da otimalidade* de Bellman. Qualquer resto de uma decisão ótima também "
     "é ótimo. Por isso dá para calcular \"o melhor com k milhões nas lojas j em diante\" de trás para frente.\n\n"
     "***Branch and bound*:**\n"
     "1. resolva a versão contínua (é um limite superior);\n"
     "2. se uma variável deu fracionária, divida em dois ramos (=0 e =1);\n"
     "3. corte o ramo cujo limite já é pior que a melhor solução inteira conhecida."),

    ("arquivo",
     "**O módulo.** Crie `inteira.py` com:\n"
     "- `alocacao_dp(retornos)`, com um DataFrame investimento × loja: devolve o valor ótimo e quanto vai para cada "
     "loja, por recursão de trás para frente;\n"
     "- `mochila_dp(valores, pesos, capacidade)`: a tabela clássica, com os itens escolhidos;\n"
     "- `branch_and_bound(c, A, b)`, para `max c·x` com `A·x ≤ b` e `x ∈ {0,1}`: resolve as relaxações com o "
     "`linprog` (limites 0 a 1, fixando as variáveis já decididas), ramifica na variável mais fracionária, poda pelo "
     "limite e devolve `x`, o valor e o número de nós explorados.",
     "inteira.py",
     r'''"""Programação dinâmica e programação inteira 0/1 (branch and bound)."""
import numpy as np
from scipy.optimize import linprog


def alocacao_dp(retornos):
    lojas, niveis = list(retornos.columns), list(retornos.index)
    total = max(niveis)
    melhor = {(len(lojas), k): (0, []) for k in range(total + 1)}
    for j in range(len(lojas) - 1, -1, -1):
        for k in range(total + 1):
            opcoes = [(retornos.iloc[x, j] + melhor[(j + 1, k - x)][0], [x] + melhor[(j + 1, k - x)][1]) for x in range(k + 1)]
            melhor[(j, k)] = max(opcoes, key=lambda o: o[0])
    valor, plano = melhor[(0, total)]
    return float(valor), dict(zip(lojas, plano))


def mochila_dp(valores, pesos, capacidade):
    n = len(valores)
    T = np.zeros((n + 1, capacidade + 1))
    for i in range(1, n + 1):
        for w in range(capacidade + 1):
            T[i, w] = T[i - 1, w]
            if pesos[i - 1] <= w:
                T[i, w] = max(T[i, w], T[i - 1, w - pesos[i - 1]] + valores[i - 1])
    escolhidos, w = [], capacidade
    for i in range(n, 0, -1):
        if T[i, w] != T[i - 1, w]:
            escolhidos.append(i - 1)
            w -= pesos[i - 1]
    return float(T[n, capacidade]), sorted(escolhidos)


def branch_and_bound(c, A, b):
    c, A, b = np.asarray(c, float), np.asarray(A, float), np.asarray(b, float)
    melhor = {"valor": -np.inf, "x": None}
    nos = 0
    pilha = [dict()]
    while pilha:
        fixos = pilha.pop()
        nos += 1
        limites = [(fixos.get(i, 0), fixos.get(i, 1)) for i in range(len(c))]
        r = linprog(-c, A_ub=A, b_ub=b, bounds=limites, method="highs")
        if not r.success or -r.fun <= melhor["valor"] + 1e-9:
            continue                                     # inviável ou não pode superar a melhor: poda
        frac = np.abs(r.x - np.round(r.x))
        if frac.max() < 1e-6:
            melhor = {"valor": -r.fun, "x": np.round(r.x).astype(int)}
            continue
        i = int(frac.argmax())
        pilha += [{**fixos, i: 0}, {**fixos, i: 1}]
    return melhor["x"], melhor["valor"], nos'''),

    ("tarefa",
     "**Alocação por DP.** Divida R$ 5 milhões entre as 3 lojas (`RETORNO_INVESTIMENTO`). Confira por força bruta "
     "(todas as combinações que somam 5).",
     r'''from itertools import product
from PKG.inteira import alocacao_dp, mochila_dp, branch_and_bound
display(RETORNO_INVESTIMENTO)
print("DP:", alocacao_dp(RETORNO_INVESTIMENTO))
bruta = max((sum(RETORNO_INVESTIMENTO.iloc[x, j] for j, x in enumerate(c)), c) for c in product(range(6), repeat=3) if sum(c) == 5)
print("força bruta:", int(bruta[0]), bruta[1], "(empate: mais de uma divisão dá o mesmo retorno)")'''),

    ("tarefa",
     "**Mochila.** Simplifique os projetos para um único orçamento (só o ano 1, R$ 1.500 mil) e resolva com "
     "`mochila_dp`, usando os custos em dezenas de milhar para a tabela ficar pequena.",
     r'''val, esc = mochila_dp(PROJETOS_CAPITAL["vpl"].tolist(), (PROJETOS_CAPITAL["custo_ano1"] // 10).tolist(), ORCAMENTO["ano1"] // 10)
print("VPL:", val, "| projetos:", list(PROJETOS_CAPITAL.index[esc]))'''),

    ("tarefa",
     "**Os dois orçamentos: arredondar engana.** Resolva a relaxação contínua (0 ≤ x ≤ 1) com o `linprog` e mostre "
     "os x fracionários. Arredonde para baixo: a solução é viável? É ótima? Depois resolva com o seu "
     "`branch_and_bound` e mostre quantos nós ele explorou.",
     r'''c = PROJETOS_CAPITAL["vpl"].to_numpy(); A = PROJETOS_CAPITAL[["custo_ano1", "custo_ano2"]].to_numpy().T; b = np.array(list(ORCAMENTO.values()))
from scipy.optimize import linprog
rel = linprog(-c, A_ub=A, b_ub=b, bounds=[(0, 1)] * 7, method="highs")
print("relaxação:", rel.x.round(2), "VPL", round(-rel.fun, 1))
arred = np.floor(rel.x + 1e-9); print("arredondada para baixo: VPL", c @ arred, "| viável:", np.all(A @ arred <= b))
x, v, nos = branch_and_bound(c, A, b)
print("branch and bound:", list(PROJETOS_CAPITAL.index[x == 1]), "| VPL", v, "| nós:", nos)'''),

    ("tarefa",
     "**Confira com o `milp`** do SciPy e acrescente regras de negócio como restrições lineares:\n"
     "- \"fábrica nova\" exige \"galpão\": `x_fabrica ≤ x_galpao`;\n"
     "- \"nova loja\" e \"e-commerce\" são excludentes: `x_loja + x_ecommerce ≤ 1`.\n\n"
     "Quanto VPL essas regras custam?",
     r'''from scipy.optimize import milp, LinearConstraint, Bounds
nomes = list(PROJETOS_CAPITAL.index)
r1 = milp(-c, constraints=[LinearConstraint(A, -np.inf, b)], integrality=np.ones(7), bounds=Bounds(0, 1))
regra = np.zeros((2, 7)); regra[0, nomes.index("fábrica nova")], regra[0, nomes.index("galpão")] = 1, -1
regra[1, nomes.index("nova loja")] = regra[1, nomes.index("e-commerce")] = 1
r2 = milp(-c, constraints=[LinearConstraint(A, -np.inf, b), LinearConstraint(regra, -np.inf, [0, 1])], integrality=np.ones(7), bounds=Bounds(0, 1))
print("milp sem regras:", -r1.fun, [n for n, x in zip(nomes, r1.x) if x > .5])
print("milp com regras:", -r2.fun, [n for n, x in zip(nomes, r2.x) if x > .5], "| custo das regras:", -r1.fun + r2.fun)'''),
]
