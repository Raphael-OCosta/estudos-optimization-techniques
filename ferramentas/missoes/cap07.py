TITULO = "Teoria dos jogos: a disputa com o concorrente"
MISSAO = (
    "A Boreal e a rival disputam participação de mercado. Cada uma escolhe uma estratégia (preço, propaganda, "
    "qualidade...) sem saber a da outra. O ganho de uma é a perda da outra: um **jogo de soma zero**. Você vai:\n"
    "- procurar o **ponto de sela** (maximin = minimax);\n"
    "- eliminar estratégias **dominadas**;\n"
    "- resolver os jogos sem ponto de sela com **estratégias mistas**, pelo método gráfico e por programação "
    "linear."
)
ENTREGA = "o módulo `PKG/jogos.py` (ponto de sela, dominância e estratégia mista ótima via programação linear) e o \"mix\" de estratégias da Boreal."
LEITURA = [("7.2 Two-Person, Zero-Sum Games (with Saddle Point)", 238), ("7.3 The Maximin-Minimax Principle", 239),
           ("7.4 Two-Person, Zero-Sum Games (without Saddle Point)", 243), ("7.5 The Principle of Dominance", 248),
           ("7.6 Graphical Method for Solving Games", 253)]

PASSOS = [
    ("texto",
     "## Ideia em 30 segundos\n"
     "O jogador das linhas (a Boreal) pensa \"qual o pior que me acontece em cada linha?\" e escolhe a melhor delas: "
     "o **maximin**. O das colunas faz o contrário: o **minimax**. Se os dois coincidem, há **ponto de sela** e a "
     "estratégia pura resolve.\n\n"
     "Se não coincidem, cada um deve **sortear** as estratégias com certas probabilidades. Achar essas "
     "probabilidades é um problema de programação linear (von Neumann)."),

    ("arquivo",
     "**O módulo de jogos.** Crie `jogos.py` com:\n"
     "- `ponto_de_sela(A)`: devolve `(maximin, minimax, posicao ou None)`;\n"
     "- `remover_dominadas(A, linhas, colunas)`: repete até não mudar. Remove a linha que é ≤ outra em tudo e a "
     "coluna que é ≥ outra em tudo, e devolve a matriz reduzida com os nomes;\n"
     "- `mista(A)`: some uma constante para deixar tudo positivo, resolva `min Σx` com `Aᵀx ≥ 1` e `x ≥ 0` "
     "(`linprog`) e devolva as probabilidades da linha e o **valor do jogo**. Faça o mesmo para as colunas.",
     "jogos.py",
     r'''"""Jogos de soma zero com dois jogadores."""
import numpy as np
from scipy.optimize import linprog


def ponto_de_sela(A):
    A = np.asarray(A, float)
    maximin, minimax = A.min(axis=1).max(), A.max(axis=0).min()
    if maximin == minimax:
        i = int(A.min(axis=1).argmax())
        j = int(A.max(axis=0).argmin())
        return float(maximin), float(minimax), (i, j)
    return float(maximin), float(minimax), None


def remover_dominadas(A, linhas, colunas):
    A, linhas, colunas = np.asarray(A, float), list(linhas), list(colunas)
    mudou = True
    while mudou:
        mudou = False
        for i in range(len(A)):
            if any(k != i and np.all(A[i] <= A[k]) for k in range(len(A))):
                A, linhas, mudou = np.delete(A, i, 0), linhas[:i] + linhas[i + 1:], True
                break
        if mudou:
            continue
        for j in range(A.shape[1]):
            if any(k != j and np.all(A[:, j] >= A[:, k]) for k in range(A.shape[1])):
                A, colunas, mudou = np.delete(A, j, 1), colunas[:j] + colunas[j + 1:], True
                break
    return A, linhas, colunas


def mista(A):
    A = np.asarray(A, float)
    k = 1 - A.min()
    B = A + k
    m, n = B.shape
    lin = linprog(np.ones(m), A_ub=-B.T, b_ub=-np.ones(n), method="highs")
    col = linprog(-np.ones(n), A_ub=B, b_ub=np.ones(m), method="highs")
    v = 1 / lin.x.sum()
    return lin.x * v, col.x * (1 / col.x.sum()), v - k'''),

    ("tarefa",
     "**Ponto de sela?** Mostre o `JOGO` com os nomes das estratégias, o mínimo de cada linha, o máximo de cada "
     "coluna, o maximin e o minimax. Existe ponto de sela?",
     r'''from PKG.jogos import ponto_de_sela, remover_dominadas, mista
tab = pd.DataFrame(JOGO, index=ESTRATEGIAS_BOREAL, columns=ESTRATEGIAS_RIVAL)
display(tab.assign(min_linha=tab.min(axis=1)))
print("máximo das colunas:", tab.max().to_dict())
print(ponto_de_sela(JOGO))'''),

    ("tarefa",
     "**Um jogo com sela.** Teste também a matriz `[[4, 2, 5], [3, 1, 2], [6, 3, 4]]`: o ponto de sela diz a "
     "estratégia pura de cada um e o valor do jogo.",
     r'''print(ponto_de_sela([[4, 2, 5], [3, 1, 2], [6, 3, 4]]))'''),

    ("tarefa",
     "**Dominância.** Reduza o `JOGO` removendo as estratégias dominadas. Que estratégias da Boreal e da rival "
     "**nunca** devem ser usadas?",
     r'''Ar, lin, col = remover_dominadas(JOGO, ESTRATEGIAS_BOREAL, ESTRATEGIAS_RIVAL)
display(pd.DataFrame(Ar, index=lin, columns=col))
print("Boreal descarta:", set(ESTRATEGIAS_BOREAL) - set(lin), "| rival descarta:", set(ESTRATEGIAS_RIVAL) - set(col))'''),

    ("tarefa",
     "**Estratégia mista.** Resolva o `JOGO` completo com `mista`. Mostre com que probabilidade a Boreal deve usar "
     "cada estratégia, o mesmo para a rival e o valor do jogo. Confira que o resultado é o mesmo usando a matriz "
     "reduzida.",
     r'''px, py, v = mista(JOGO)
print("Boreal:", dict(zip(ESTRATEGIAS_BOREAL, px.round(3).tolist()))); print("rival:", dict(zip(ESTRATEGIAS_RIVAL, py.round(3).tolist())))
print("valor do jogo:", round(v, 3))
print("reduzida, valor:", round(mista(Ar)[2], 3))'''),

    ("tarefa",
     "**Método gráfico (2 × n).** Na matriz reduzida, se a Boreal ficou com 2 estratégias, desenhe o ganho esperado "
     "contra cada coluna da rival em função de `p` (a probabilidade da 1ª linha). O ótimo é o **ponto mais alto da "
     "envoltória inferior**. Compare com o `mista`.",
     r'''import matplotlib.pyplot as plt
if Ar.shape[0] == 2:
    ps = np.linspace(0, 1, 201)
    linhas_j = [p_ * Ar[0, j] + (1 - p_) * Ar[1, j] for j in range(Ar.shape[1]) for p_ in [ps]]
    for j, y in enumerate(linhas_j):
        plt.plot(ps, y, label=f"rival: {col[j]}")
    env = np.min(linhas_j, axis=0); k = int(env.argmax())
    plt.plot(ps, env, "k", lw=3); plt.plot(ps[k], env[k], "r*", ms=15); plt.xlabel(f"p = P({lin[0]})"); plt.legend(); plt.show()
    print("gráfico: p =", round(ps[k], 3), "| valor", round(env[k], 3), "| mista:", mista(Ar)[0].round(3))
else:
    print("a matriz reduzida tem", Ar.shape[0], "linhas; o método gráfico vale para 2 × n")'''),
]
