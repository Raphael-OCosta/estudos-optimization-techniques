TITULO = "Programação linear: o mix de produção"
MISSAO = (
    "Quantas mesas, cadeiras, estantes e armários a Boreal deve fazer por mês? As horas de carpintaria, pintura e "
    "montagem e a madeira são limitadas. Você vai:\n"
    "- formular o problema;\n"
    "- resolver no gráfico uma versão com 2 produtos;\n"
    "- escrever o **método simplex** em tabela, do zero;\n"
    "- conferir com o `scipy.optimize.linprog`;\n"
    "- ler o **dual**, os preços-sombra, que dizem quanto vale uma hora a mais de cada setor."
)
ENTREGA = "o módulo `PKG/simplex.py`, com o simplex em tabela que mostra cada iteração, e o plano de produção ótimo com a análise de sensibilidade."
LEITURA = [("2.3 Formulation of LPP", 32), ("2.6 Solutions to LPP (Graphical Method)", 39), ("2.8 Simplex Method", 43),
           ("2.9 Big M Method", 49), ("2.11 Duality in LPP", 56), ("2.12 Sensitivity Analysis", 59)]

PASSOS = [
    ("texto",
     "## Ideia em 30 segundos\n"
     "Maximizar `cᵀx` com `A·x ≤ b` e `x ≥ 0`. A região viável é um poliedro, e o ótimo está sempre num "
     "**vértice**. O simplex anda de vértice em vértice vizinho, sempre melhorando:\n"
     "1. escolha quem **entra** (o coeficiente mais negativo na linha do objetivo);\n"
     "2. escolha quem **sai** (o teste da menor razão);\n"
     "3. faça o pivoteamento.\n\n"
     "Na tabela final, o valor das folgas no objetivo é o **preço-sombra** de cada recurso."),

    ("tarefa",
     "**Versão 2D no gráfico.** Só mesas (`x`) e estantes (`y`), com a carpintaria (`4x + 5y ≤ 1200`), a pintura "
     "(`2x + 3y ≤ 700`) e a montagem (`x + 2y ≤ 400`). Desenhe as retas, pinte a região viável, calcule o lucro "
     "`120x + 160y` em cada vértice e marque o melhor.",
     r'''import matplotlib.pyplot as plt
from itertools import combinations
A = np.array([[4, 5], [2, 3], [1, 2]]); b = np.array([1200, 700, 400])
xs = np.linspace(0, 320, 400)
for (a1, a2), bi, nome in zip(A, b, ["carpintaria", "pintura", "montagem"]):
    plt.plot(xs, (bi - a1 * xs) / a2, label=nome)
gx, gy = np.meshgrid(xs, np.linspace(0, 260, 300))
plt.contourf(gx, gy, np.all([A[i, 0] * gx + A[i, 1] * gy <= b[i] for i in range(3)], axis=0), levels=[.5, 1], alpha=.3)
linhas = np.vstack([A, [[-1, 0], [0, -1]]]); rhs = np.r_[b, 0, 0]
vertices = []
for i, j in combinations(range(5), 2):
    try:
        v = np.linalg.solve(linhas[[i, j]], rhs[[i, j]])
    except np.linalg.LinAlgError:
        continue
    if np.all(linhas @ v <= rhs + 1e-9):
        vertices.append(v)
for v in vertices:
    print(f"vértice ({v[0]:6.1f}, {v[1]:6.1f}) lucro {120 * v[0] + 160 * v[1]:8.0f}")
best = max(vertices, key=lambda v: 120 * v[0] + 160 * v[1]); plt.plot(*best, "r*", ms=15)
plt.xlim(0, 320); plt.ylim(0, 260); plt.legend(); plt.xlabel("mesas"); plt.ylabel("estantes"); plt.show()'''),

    ("arquivo",
     "**O simplex em tabela.** Crie `simplex.py` com `simplex(c, A, b, verbose=False)` para `max cᵀx` com `Ax ≤ b`, "
     "`b ≥ 0`:\n"
     "- monte a tabela com as folgas;\n"
     "- a cada iteração, escolha a coluna mais negativa da linha z e a linha pelo teste da menor razão (só com "
     "elementos positivos), e pivoteie;\n"
     "- pare quando não houver negativos, ou acuse \"ilimitado\";\n"
     "- devolva `x`, o valor ótimo, os **preços-sombra** (os coeficientes das folgas na linha z final) e o número "
     "de iterações.",
     "simplex.py",
     r'''"""Método simplex em tabela (para max c·x, A·x <= b, x >= 0, b >= 0)."""
import numpy as np


def simplex(c, A, b, verbose=False, max_iter=100):
    A, b, c = np.asarray(A, float), np.asarray(b, float), np.asarray(c, float)
    m, n = A.shape
    T = np.zeros((m + 1, n + m + 1))
    T[:m, :n], T[:m, n:n + m], T[:m, -1] = A, np.eye(m), b
    T[-1, :n] = -c
    base = list(range(n, n + m))
    for it in range(1, max_iter + 1):
        col = int(np.argmin(T[-1, :-1]))
        if T[-1, col] >= -1e-12:
            break
        coluna = T[:m, col]
        razoes = np.where(coluna > 1e-12, T[:m, -1] / np.where(coluna > 1e-12, coluna, 1), np.inf)
        if np.all(np.isinf(razoes)):
            raise ValueError("problema ilimitado")
        lin = int(np.argmin(razoes))
        if verbose:
            print(f"iteração {it}: entra x{col + 1}, sai a variável da linha {lin + 1} (razão {razoes[lin]:.2f})")
        T[lin] /= T[lin, col]
        for i in range(m + 1):
            if i != lin:
                T[i] -= T[i, col] * T[lin]
        base[lin] = col
    x = np.zeros(n + m)
    for i, j in enumerate(base):
        x[j] = T[i, -1]
    return {"x": x[:n], "valor": T[-1, -1], "precos_sombra": T[-1, n:n + m], "iteracoes": it - 1}'''),

    ("tarefa",
     "**O mix completo.** Use o seu simplex com os 4 produtos (`PRODUTOS`), as 4 restrições de `CAPACIDADE` e as "
     "4 de demanda máxima (`DEMANDA_MAX`), com `verbose=True`. Mostre o plano, o lucro e os preços-sombra de cada "
     "restrição.",
     r'''from PKG.simplex import simplex
c = PRODUTOS["lucro"].to_numpy()
A = np.vstack([PRODUTOS[r].to_numpy() for r in CAPACIDADE] + [np.eye(4)])
b = np.r_[list(CAPACIDADE.values()), list(DEMANDA_MAX.values())]
res = simplex(c, A, b, verbose=True)
print(dict(zip(PRODUTOS.index, res["x"].round(2).tolist())), "| lucro R$", round(res["valor"], 2))
nomes = list(CAPACIDADE) + [f"demanda {p}" for p in PRODUTOS.index]
print({n: round(float(v), 2) for n, v in zip(nomes, res["precos_sombra"]) if v > 1e-9})'''),

    ("tarefa",
     "**Confira com o `linprog`.** O `linprog` minimiza, então use `-c`. Acrescente a regra comercial "
     "\"cadeiras ≥ 4 × mesas\" (`4·mesa - cadeira ≤ 0`) e mostre como o plano muda. Os **duais** (os preços-sombra) "
     "estão em `res.ineqlin.marginals`, com o sinal trocado.",
     r'''from scipy.optimize import linprog
r1 = linprog(-c, A_ub=A, b_ub=b, method="highs")
print("sem a regra:", r1.x.round(2), "lucro", round(-r1.fun, 2))
A2 = np.vstack([A, [CADEIRAS_POR_MESA, -1, 0, 0]]); b2 = np.r_[b, 0]
r2 = linprog(-c, A_ub=A2, b_ub=b2, method="highs")
print("com a regra:", dict(zip(PRODUTOS.index, r2.x.round(2).tolist())), "lucro", round(-r2.fun, 2))
print("preços-sombra:", dict(zip(nomes + ["cadeiras/mesa"], (-r2.ineqlin.marginals).round(2).tolist())))'''),

    ("tarefa",
     "**Sensibilidade.** Use o modelo com a regra das cadeiras:\n"
     "1. Aumente a pintura em 10 e em 100 horas. Com +10, o lucro sobe exatamente preço-sombra × 10. Com +100 não: o "
     "preço-sombra só vale dentro de uma **faixa**, enquanto as mesmas restrições continuam limitando.\n"
     "2. Varie o lucro do armário de 150 a 300 e veja em que ponto o plano muda.",
     r'''for extra in (10, 100):
    b3 = b2.copy(); b3[1] = 700 + extra
    r3 = linprog(-c, A_ub=A2, b_ub=b3, method="highs")
    print(f"+{extra} h de pintura: ganho real {-r3.fun - (-r2.fun):.2f} | previsto pelo preço-sombra {-r2.ineqlin.marginals[1] * extra:.2f}")
# Com +10 bate; com +100 outra restrição passa a limitar (a base muda) e o preço-sombra deixa de valer.
for lucro_arm in range(150, 301, 25):
    cc = c.astype(float).copy(); cc[3] = lucro_arm
    x = linprog(-cc, A_ub=A2, b_ub=b2, method="highs").x
    print(f"lucro do armário {lucro_arm}: plano {x.round(1)}")'''),

    ("tarefa",
     "**Dualidade.** Escreva o **dual** do problema sem a regra: minimizar `bᵀy` com `Aᵀy ≥ c` e `y ≥ 0`. Resolva "
     "com o `linprog` e mostre que o valor ótimo do dual é igual ao do primal e que `y` são os preços-sombra do seu "
     "simplex.",
     r'''dual = linprog(b, A_ub=-A.T, b_ub=-c, method="highs")
print("primal:", round(res["valor"], 2), "| dual:", round(dual.fun, 2))
print("y do dual:     ", dual.x.round(2)); print("preços-sombra: ", res["precos_sombra"].round(2))'''),
]
