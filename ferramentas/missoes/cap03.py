TITULO = "Transporte e designação"
MISSAO = (
    "Dois problemas clássicos com estrutura especial:\n"
    "- **transporte**: quanto mandar de cada uma das 3 fábricas para cada uma das 4 lojas, gastando o mínimo de "
    "frete;\n"
    "- **designação**: qual operário fica com qual máquina, para o menor tempo total.\n\n"
    "Você vai escrever o **método de Vogel** para a solução inicial e a otimização pelos custos reduzidos (método "
    "MODI/u-v), resolver a designação com o **método húngaro** e tratar os casos desbalanceados e de maximização."
)
ENTREGA = "o módulo `PKG/transporte.py` (canto noroeste, Vogel, otimalidade u-v e designação por força bruta) e os planos ótimos conferidos com o SciPy."
LEITURA = [("3.2 Mathematical Form of the Transportation Problem", 63), ("3.3.2 Vogel's Approximation Method", 65),
           ("3.3.3 Methods to Find an Optimal Solution", 71), ("3.5 Unbalanced Transportation Problem", 83),
           ("3.9 Assignment Algorithm (Hungarian Assignment Method)", 87), ("3.10 The Maximal Assignment Problem", 100),
           ("3.11 Unbalanced Assignment Problem", 105)]

PASSOS = [
    ("texto",
     "## Ideia em 30 segundos\n"
     "**Transporte:** `min Σ c_ij·x_ij`, onde cada fábrica envia no máximo a sua oferta e cada loja recebe a sua "
     "demanda.\n"
     "1. A solução inicial vem do canto noroeste (simples) ou do **Vogel**, mais esperto: em cada linha e coluna, a "
     "diferença entre os 2 menores custos é a \"penalidade\" de não usar a mais barata.\n"
     "2. Depois o **u-v** calcula os custos reduzidos `c_ij - u_i - v_j` das rotas vazias. Se algum é negativo, "
     "ainda dá para melhorar.\n\n"
     "**Designação:** é um transporte com tudo igual a 1. O método húngaro subtrai os mínimos de linha e de coluna "
     "e cobre os zeros."),

    ("arquivo",
     "**O módulo de transporte.** Crie `transporte.py` com:\n"
     "- `canto_noroeste(oferta, demanda)` e `vogel(custo, oferta, demanda)`: os planos iniciais;\n"
     "- `custo_total(custo, plano)`;\n"
     "- `custos_reduzidos(custo, plano)`: resolve `u_i + v_j = c_ij` nas rotas usadas (com `u_0 = 0`, por "
     "propagação) e devolve a matriz `c - u - v`;\n"
     "- `designacao_bruta(tempo)`: testa todas as permutações (vale para até ~8 pessoas).",
     "transporte.py",
     r'''"""Problemas de transporte e designação."""
from itertools import permutations

import numpy as np


def canto_noroeste(oferta, demanda):
    o, d = list(oferta), list(demanda)
    plano = np.zeros((len(o), len(d)))
    i = j = 0
    while i < len(o) and j < len(d):
        q = min(o[i], d[j])
        plano[i, j] = q
        o[i] -= q
        d[j] -= q
        if o[i] == 0:
            i += 1
        else:
            j += 1
    return plano


def vogel(custo, oferta, demanda):
    c = np.asarray(custo, float)
    o, d = np.array(oferta, float), np.array(demanda, float)
    plano = np.zeros_like(c)
    linhas, colunas = set(range(len(o))), set(range(len(d)))

    def penal(v):
        v = np.sort(v)
        return v[1] - v[0] if len(v) > 1 else v[0]

    while linhas and colunas:
        pl = {i: penal([c[i, j] for j in colunas]) for i in linhas}
        pc = {j: penal([c[i, j] for i in linhas]) for j in colunas}
        if max(pl.values()) >= max(pc.values()):
            i = max(pl, key=pl.get)
            j = min(colunas, key=lambda jj: c[i, jj])
        else:
            j = max(pc, key=pc.get)
            i = min(linhas, key=lambda ii: c[ii, j])
        q = min(o[i], d[j])
        plano[i, j] += q
        o[i] -= q
        d[j] -= q
        if o[i] == 0:
            linhas.discard(i)
        if d[j] == 0:
            colunas.discard(j)
    return plano


def custo_total(custo, plano):
    return float(np.sum(np.asarray(custo) * plano))


def custos_reduzidos(custo, plano):
    c = np.asarray(custo, float)
    m, n = c.shape
    u, v = [None] * m, [None] * n
    u[0] = 0.0
    usadas = [(i, j) for i in range(m) for j in range(n) if plano[i, j] > 0]
    mudou = True
    while mudou:
        mudou = False
        for i, j in usadas:
            if u[i] is not None and v[j] is None:
                v[j] = c[i, j] - u[i]
                mudou = True
            elif v[j] is not None and u[i] is None:
                u[i] = c[i, j] - v[j]
                mudou = True
    u = np.array([0.0 if x is None else x for x in u])
    v = np.array([0.0 if x is None else x for x in v])
    return c - u[:, None] - v[None, :]


def designacao_bruta(tempo):
    t = np.asarray(tempo)
    melhor = min(permutations(range(len(t))), key=lambda p: sum(t[i, p[i]] for i in range(len(t))))
    return list(melhor), int(sum(t[i, melhor[i]] for i in range(len(t))))'''),

    ("tarefa",
     "**Balanceado?** Compare a oferta total com a demanda total. Se a oferta for maior, crie uma **loja fictícia** "
     "com custo 0 que recebe a sobra. Mostre a matriz de custos já balanceada.",
     r'''from PKG.transporte import canto_noroeste, vogel, custo_total, custos_reduzidos, designacao_bruta
print("oferta", OFERTA.sum(), "| demanda", DEMANDA.sum())
sobra = OFERTA.sum() - DEMANDA.sum()
custo = np.column_stack([CUSTO_FRETE, np.zeros(3)]); demanda = np.r_[DEMANDA, sobra]
display(pd.DataFrame(custo, index=FABRICAS, columns=LOJAS + ["fictícia"]))'''),

    ("tarefa",
     "**Soluções iniciais.** Calcule o plano e o custo do canto noroeste e do Vogel. Quanto o Vogel economiza já "
     "de saída? Depois calcule os custos reduzidos do plano de Vogel: se nenhum for negativo, ele já é ótimo.",
     r'''no = canto_noroeste(OFERTA, demanda); vg = vogel(custo, OFERTA, demanda)
print("canto noroeste: R$", custo_total(custo, no), "| Vogel: R$", custo_total(custo, vg))
display(pd.DataFrame(vg, index=FABRICAS, columns=LOJAS + ["fictícia"]))
cr = custos_reduzidos(custo, vg)
print("menor custo reduzido:", cr.min().round(2), "->", "ótimo" if cr.min() >= -1e-9 else "ainda dá para melhorar")'''),

    ("tarefa",
     "**O ótimo com o `linprog`.** Formule o transporte como programação linear (uma variável por rota, igualdade "
     "na oferta e na demanda do problema balanceado) e compare o custo com o Vogel.",
     r'''from scipy.optimize import linprog
m, n = custo.shape
A_eq, b_eq = [], []
for i in range(m):
    lin = np.zeros(m * n); lin[i * n:(i + 1) * n] = 1; A_eq.append(lin); b_eq.append(OFERTA[i])
for j in range(n):
    col = np.zeros(m * n); col[j::n] = 1; A_eq.append(col); b_eq.append(demanda[j])
lp = linprog(custo.ravel(), A_eq=A_eq, b_eq=b_eq, method="highs")
otimo = lp.x.reshape(m, n)
print("ótimo: R$", round(lp.fun, 2), "| Vogel: R$", custo_total(custo, vg))
display(pd.DataFrame(otimo.round(0), index=FABRICAS, columns=LOJAS + ["fictícia"]))'''),

    ("tarefa",
     "**Designação.** Resolva a designação dos 5 operários às 5 máquinas (`TEMPO_TAREFA`) por força bruta e com o "
     "`scipy.optimize.linear_sum_assignment` (o método húngaro). Mostre quem fica com qual máquina e o tempo total.",
     r'''from scipy.optimize import linear_sum_assignment
pares, total = designacao_bruta(TEMPO_TAREFA)
lin, col = linear_sum_assignment(TEMPO_TAREFA)
print("força bruta:", total, "| húngaro:", TEMPO_TAREFA[lin, col].sum())
for o, mq in zip(lin, col):
    print(f"{OPERARIOS[o]:<6}-> {MAQUINAS[mq]:<10}({TEMPO_TAREFA[o, mq]} min)")'''),

    ("tarefa",
     "**Maximização e desbalanceado.** Primeiro, uma tabela de **produtividade** (peças por hora = 60 / tempo): "
     "para maximizar com o húngaro, use `linear_sum_assignment(..., maximize=True)`. Depois, a Eva saiu de férias "
     "(4 operários e 5 máquinas): qual máquina fica parada?",
     r'''prod = 60 / TEMPO_TAREFA
l2, c2 = linear_sum_assignment(prod, maximize=True)
print("produtividade máxima:", round(prod[l2, c2].sum(), 1), "peças/h", [(OPERARIOS[a], MAQUINAS[b]) for a, b in zip(l2, c2)])
sem_eva = TEMPO_TAREFA[:4]
l3, c3 = linear_sum_assignment(sem_eva)
print("sem a Eva:", [(OPERARIOS[a], MAQUINAS[b]) for a, b in zip(l3, c3)], "| parada:", set(MAQUINAS) - {MAQUINAS[b] for b in c3})'''),
]
