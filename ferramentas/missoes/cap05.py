TITULO = "Sequenciamento: em que ordem produzir"
MISSAO = (
    "Sete pedidos (`PEDIDOS`) esperam na fábrica. Em que ordem processá-los? Você vai:\n"
    "- comparar as regras de uma máquina (SPT, EDD, FIFO) em tempo médio no sistema e em atraso;\n"
    "- escrever a **regra de Johnson** para duas máquinas e estendê-la para três;\n"
    "- desenhar o **gráfico de Gantt**;\n"
    "- conferir com força bruta quando dá."
)
ENTREGA = "o módulo `PKG/sequencia.py` (métricas de uma máquina, regra de Johnson, *makespan* em m máquinas e Gantt)."
LEITURA = [("5.1.2 Terms Used in Sequencing", 173), ("5.2 Gantt Chart", 174), ("5.3 Sequencing of n Jobs through One Machine", 176),
           ("5.4 Sequencing of n Jobs through Two Machines", 189), ("5.5 Sequencing of n Jobs through Three Machines", 197),
           ("5.6 Sequencing of n Jobs through m Machines", 201)]

PASSOS = [
    ("texto",
     "## Ideia em 30 segundos\n"
     "**Numa máquina:**\n"
     "- **SPT** (o mais curto primeiro) minimiza o tempo médio no sistema;\n"
     "- **EDD** (o prazo mais cedo primeiro) minimiza o maior atraso.\n\n"
     "**Em duas máquinas em série (A → B), a regra de Johnson:**\n"
     "1. ache o menor tempo de todos;\n"
     "2. se ele está na máquina A, o pedido vai para o **começo** da fila; se está na B, vai para o **fim**;\n"
     "3. risque o pedido e repita.\n\n"
     "Isso minimiza o *makespan*, o tempo até o último pedido sair. Para três máquinas, quando a do meio é "
     "\"dominada\", some A+B e B+C e aplique Johnson."),

    ("arquivo",
     "**O módulo de sequenciamento.** Crie `sequencia.py` com:\n"
     "- `metricas_uma_maquina(tempos, prazos, ordem)`: o tempo médio no sistema, o atraso total, o maior atraso e o "
     "número de pedidos atrasados;\n"
     "- `johnson(a, b)`, com as listas de tempos nas máquinas A e B: devolve a ordem (índices);\n"
     "- `makespan(matriz, ordem)`, com a matriz pedidos × máquinas: devolve o *makespan* e as tabelas de início e "
     "fim de cada pedido em cada máquina;\n"
     "- `gantt(matriz, ordem, nomes, maquinas)`: barras horizontais com Matplotlib.",
     "sequencia.py",
     r'''"""Sequenciamento de pedidos: regras de uma máquina, Johnson e makespan."""
import matplotlib.pyplot as plt
import numpy as np


def metricas_uma_maquina(tempos, prazos, ordem):
    t, fim, atrasos = 0, [], []
    for i in ordem:
        t += tempos[i]
        fim.append(t)
        atrasos.append(max(0, t - prazos[i]))
    return {"tempo_medio": float(np.mean(fim)), "atraso_total": float(sum(atrasos)),
            "maior_atraso": float(max(atrasos)), "atrasados": int(sum(a > 0 for a in atrasos))}


def johnson(a, b):
    restantes, inicio, fim = set(range(len(a))), [], []
    while restantes:
        i = min(restantes, key=lambda k: min(a[k], b[k]))
        (inicio.append(i) if a[i] <= b[i] else fim.insert(0, i))
        restantes.remove(i)
    return inicio + fim


def makespan(matriz, ordem):
    M = np.asarray(matriz, float)[list(ordem)]
    ini, fim = np.zeros_like(M), np.zeros_like(M)
    for j in range(M.shape[0]):
        for k in range(M.shape[1]):
            ini[j, k] = max(fim[j - 1, k] if j else 0, fim[j, k - 1] if k else 0)
            fim[j, k] = ini[j, k] + M[j, k]
    return float(fim[-1, -1]), ini, fim


def gantt(matriz, ordem, nomes, maquinas):
    _, ini, fim = makespan(matriz, ordem)
    fig, ax = plt.subplots(figsize=(10, 0.6 * len(maquinas) + 1))
    cores = plt.cm.tab10(np.arange(len(ordem)) % 10)
    for j, p in enumerate(ordem):
        for k in range(len(maquinas)):
            ax.barh(k, fim[j, k] - ini[j, k], left=ini[j, k], color=cores[j], edgecolor="k")
            ax.text((ini[j, k] + fim[j, k]) / 2, k, nomes[p], ha="center", va="center", fontsize=8)
    ax.set_yticks(range(len(maquinas)), maquinas)
    ax.invert_yaxis()
    ax.set_xlabel("horas")
    return fig'''),

    ("tarefa",
     "**Uma máquina (só o corte).** Compare FIFO (a ordem de chegada P1..P7), SPT e EDD com as `metricas`. Qual "
     "regra ganha em cada métrica?",
     r'''from PKG.sequencia import metricas_uma_maquina, johnson, makespan, gantt
t, prazo = PEDIDOS["corte"].to_numpy(), PEDIDOS["prazo_h"].to_numpy()
regras = {"FIFO": list(range(7)), "SPT": list(np.argsort(t, kind="stable")), "EDD": list(np.argsort(prazo, kind="stable"))}
display(pd.DataFrame({r: metricas_uma_maquina(t, prazo, o) for r, o in regras.items()}).T.round(2))'''),

    ("tarefa",
     "**Johnson em duas máquinas (corte → acabamento).** Aplique a regra, mostre a ordem com os nomes e o "
     "*makespan*, e compare com o FIFO. Depois confira com **força bruta** (7! = 5.040 ordens) que Johnson é ótimo.",
     r'''from itertools import permutations
M2 = PEDIDOS[["corte", "acabamento"]].to_numpy()
oj = johnson(M2[:, 0], M2[:, 1])
print("Johnson:", [PEDIDOS.index[i] for i in oj], "| makespan", makespan(M2, oj)[0])
print("FIFO makespan:", makespan(M2, range(7))[0])
print("força bruta:", min(makespan(M2, p)[0] for p in permutations(range(7))))'''),

    ("tarefa",
     "**Gantt.** Desenhe o Gantt do Johnson e o do FIFO, um embaixo do outro. Onde o acabamento fica **ocioso** "
     "esperando o corte?",
     r'''import matplotlib.pyplot as plt
for nome, ordem in [("Johnson", oj), ("FIFO", list(range(7)))]:
    gantt(M2, ordem, list(PEDIDOS.index), ["corte", "acabamento"]); plt.title(nome); plt.show()'''),

    ("tarefa",
     "**Três máquinas.** Confira se a condição do livro vale: `min(corte) ≥ max(acabamento)` ou "
     "`min(embalagem) ≥ max(acabamento)`. Mesmo que não valha, aplique Johnson em `(corte + acabamento, acabamento + "
     "embalagem)` como **heurística** e compare com a força bruta e com o FIFO nas 3 máquinas.",
     r'''M3 = PEDIDOS[["corte", "acabamento", "embalagem"]].to_numpy()
print("condição:", M3[:, 0].min() >= M3[:, 1].max() or M3[:, 2].min() >= M3[:, 1].max())
oj3 = johnson(M3[:, 0] + M3[:, 1], M3[:, 1] + M3[:, 2])
print("heurística de Johnson:", makespan(M3, oj3)[0], "| FIFO:", makespan(M3, range(7))[0],
      "| ótimo (força bruta):", min(makespan(M3, p)[0] for p in permutations(range(7))))'''),

    ("tarefa",
     "**m máquinas e uma heurística moderna.** Para 3 máquinas e um lote de 9 pedidos aleatórios (`semente 3`, "
     "tempos de 1 a 9), compare:\n"
     "- (a) a heurística de Johnson;\n"
     "- (b) a heurística **NEH**: ordene os pedidos pela soma dos tempos, do maior para o menor, e insira cada um "
     "na posição da sequência parcial que dá o menor *makespan*;\n"
     "- (c) o ótimo (9! = 362.880; pode levar alguns segundos).",
     r'''r = np.random.default_rng(3); M9 = r.integers(1, 10, (9, 3))
def neh(M):
    seq = []
    for j in np.argsort(-M.sum(1)):
        seq = min((seq[:k] + [j] + seq[k:] for k in range(len(seq) + 1)), key=lambda s: makespan(M, s)[0])
    return seq
oj9 = johnson(M9[:, 0] + M9[:, 1], M9[:, 1] + M9[:, 2])
print("Johnson:", makespan(M9, oj9)[0], "| NEH:", makespan(M9, neh(M9))[0])
print("ótimo:", min(makespan(M9, p)[0] for p in permutations(range(9))))'''),
]
