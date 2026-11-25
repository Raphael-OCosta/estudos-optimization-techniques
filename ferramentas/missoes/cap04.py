TITULO = "Redes: projeto da nova linha, rotas e fluxos"
MISSAO = (
    "A Boreal vai lançar uma linha de móveis. Você vai calcular o **caminho crítico** (CPM) do projeto, a chance "
    "de terminar no prazo (PERT) e o jeito mais barato de encurtar (*crashing*). Depois, nas estradas e esteiras:\n"
    "- **Dijkstra** para a rota mais curta;\n"
    "- **árvore geradora mínima** para a rede de fibra entre as filiais;\n"
    "- **fluxo máximo** nas esteiras;\n"
    "- **caixeiro-viajante** para a visita do vendedor."
)
ENTREGA = "o módulo `PKG/redes.py` (CPM com folgas, PERT, Dijkstra, Prim e fluxo máximo de Edmonds-Karp, escritos à mão) e os números conferidos com o networkx."
LEITURA = [("4.3.1 CPM Computations", 124), ("4.3.2 Forward Pass and a Backward Pass", 126), ("4.3.3 PERT Computations", 132),
           ("4.3.5 Project Crashing", 138), ("4.4.1 Dijkstra's Shortest Path Method", 145), ("4.4.2 Minimum Spanning Tree Algorithm", 146),
           ("4.5 The Maximum Flow Problem", 152), ("4.6 A Travelling Salesman Problem (TSP)", 154)]

PASSOS = [
    ("texto",
     "## Ideia em 30 segundos\n"
     "**CPM:**\n"
     "- a **ida** calcula o início mais cedo de cada atividade;\n"
     "- a **volta** calcula o término mais tarde;\n"
     "- **folga** = mais tarde − mais cedo; as atividades com folga 0 formam o **caminho crítico**.\n\n"
     "**PERT:** a duração esperada é `(a + 4m + b)/6` e a variância é `((b - a)/6)²`. A soma no caminho crítico dá "
     "uma normal, que responde \"qual a chance de terminar em X dias?\".\n\n"
     "**Dijkstra:** sempre expande o nó ainda não fechado mais próximo da origem."),

    ("arquivo",
     "**O módulo de redes.** Crie `redes.py` com:\n"
     "- `cpm(atividades)`, com `atividades = {nome: (duracao, [predecessoras])}`: devolve um DataFrame com ES, EF, "
     "LS, LF e a folga, e a duração do projeto;\n"
     "- `dijkstra(arestas, origem)`: com `heapq`, para um grafo não direcionado, devolve as distâncias e os "
     "anteriores;\n"
     "- `caminho(anteriores, destino)`;\n"
     "- `prim(arestas)`: a árvore geradora mínima;\n"
     "- `fluxo_maximo(arestas, s, t)`: Edmonds-Karp, com BFS no grafo residual.",
     "redes.py",
     r'''"""Modelos de rede escritos à mão: CPM, Dijkstra, Prim e fluxo máximo."""
import heapq
from collections import defaultdict, deque

import pandas as pd


def cpm(atividades):
    ordem, feitas = [], set()
    while len(ordem) < len(atividades):
        for a, (_, pred) in atividades.items():
            if a not in feitas and all(p in feitas for p in pred):
                ordem.append(a)
                feitas.add(a)
    es, ef = {}, {}
    for a in ordem:
        d, pred = atividades[a]
        es[a] = max((ef[p] for p in pred), default=0)
        ef[a] = es[a] + d
    fim = max(ef.values())
    sucessores = defaultdict(list)
    for a, (_, pred) in atividades.items():
        for p in pred:
            sucessores[p].append(a)
    lf, ls = {}, {}
    for a in reversed(ordem):
        lf[a] = min((ls[s] for s in sucessores[a]), default=fim)
        ls[a] = lf[a] - atividades[a][0]
    df = pd.DataFrame({"duracao": {a: atividades[a][0] for a in ordem}, "ES": es, "EF": ef, "LS": ls, "LF": lf}).loc[ordem]
    df["folga"] = df["LS"] - df["ES"]
    return df, fim


def _vizinhos(arestas):
    g = defaultdict(list)
    for a, b, w in arestas:
        g[a].append((b, w))
        g[b].append((a, w))
    return g


def dijkstra(arestas, origem):
    g = _vizinhos(arestas)
    dist, ant, fila, fechados = {origem: 0}, {origem: None}, [(0, origem)], set()
    while fila:
        d, u = heapq.heappop(fila)
        if u in fechados:
            continue
        fechados.add(u)
        for v, w in g[u]:
            if d + w < dist.get(v, float("inf")):
                dist[v], ant[v] = d + w, u
                heapq.heappush(fila, (d + w, v))
    return dist, ant


def caminho(anteriores, destino):
    c = []
    while destino is not None:
        c.append(destino)
        destino = anteriores[destino]
    return c[::-1]


def prim(arestas):
    g = _vizinhos(arestas)
    inicio = arestas[0][0]
    dentro, arvore = {inicio}, []
    fila = [(w, inicio, v) for v, w in g[inicio]]
    heapq.heapify(fila)
    while fila and len(dentro) < len(g):
        w, a, b = heapq.heappop(fila)
        if b in dentro:
            continue
        dentro.add(b)
        arvore.append((a, b, w))
        for v, w2 in g[b]:
            if v not in dentro:
                heapq.heappush(fila, (w2, b, v))
    return arvore


def fluxo_maximo(arestas, s, t):
    cap = defaultdict(lambda: defaultdict(int))
    for a, b, c in arestas:
        cap[a][b] += c
    total = 0
    while True:
        ant, fila = {s: None}, deque([s])
        while fila and t not in ant:
            u = fila.popleft()
            for v, c in cap[u].items():
                if c > 0 and v not in ant:
                    ant[v] = u
                    fila.append(v)
        if t not in ant:
            return total
        gargalo, v = float("inf"), t
        while ant[v] is not None:
            gargalo = min(gargalo, cap[ant[v]][v])
            v = ant[v]
        v = t
        while ant[v] is not None:
            cap[ant[v]][v] -= gargalo
            cap[v][ant[v]] += gargalo
            v = ant[v]
        total += gargalo'''),

    ("tarefa",
     "**CPM.** Use a duração mais provável (`m`) de cada atividade de `PROJETO`, rode o `cpm` e mostre a tabela, a "
     "duração do projeto e o caminho crítico (folga 0).",
     r'''from PKG.redes import cpm, dijkstra, caminho, prim, fluxo_maximo
ativ = {a: (m, pred) for a, (_, pred, o, m, p) in PROJETO.items()}
tab, dur = cpm(ativ)
display(tab)
print("duração:", dur, "dias | caminho crítico:", " -> ".join(tab.index[tab.folga == 0]))'''),

    ("tarefa",
     "**PERT e probabilidade.** Recalcule com as durações esperadas `(a + 4m + b)/6`. Some as variâncias do "
     "caminho crítico e calcule, com a normal (`scipy.stats.norm`), a chance de terminar em 35, 38 e 42 dias. "
     "Confira com uma **simulação** de 20 mil projetos com durações triangulares (`rng.triangular`).",
     r'''from scipy.stats import norm
esp = {a: ((o + 4 * m + p) / 6, pred) for a, (_, pred, o, m, p) in PROJETO.items()}
tab2, dur2 = cpm(esp)
critico = tab2.index[tab2.folga.abs() < 1e-9]
var = sum(((PROJETO[a][4] - PROJETO[a][2]) / 6) ** 2 for a in critico)
for prazo in (35, 38, 42):
    print(f"P(terminar em {prazo} dias) = {norm.cdf(prazo, dur2, np.sqrt(var)):.2f}")
r = np.random.default_rng(0); fins = []
for _ in range(20000):
    sim = {a: (r.triangular(o, m, p), pred) for a, (_, pred, o, m, p) in PROJETO.items()}
    ef = {}
    for a in tab2.index:
        ef[a] = max((ef[x] for x in sim[a][1]), default=0) + sim[a][0]
    fins.append(max(ef.values()))
print("simulação: P(≤ 38 dias) =", round(np.mean(np.array(fins) <= 38), 2))
# A simulação dá menos que a fórmula: o PERT olha só o caminho crítico, mas caminhos quase críticos
# (C-E-F tem folga de 1 dia) às vezes atrasam mais e viram o crítico. É o "viés de junção" do PERT.'''),

    ("tarefa",
     "**Crashing.** A diretoria quer o projeto em 30 dias (com as durações `m`). Repita: ache o caminho crítico, "
     "encurte em 1 dia a atividade crítica mais barata que ainda pode encurtar (`ACELERAR`) e recalcule, até chegar "
     "a 30 ou não dar mais. Mostre o custo total e o que foi encurtado.",
     r'''dur_atual = {a: m for a, (_, pred, o, m, p) in PROJETO.items()}
gasto, log = 0, []
while True:
    t, fim = cpm({a: (dur_atual[a], PROJETO[a][1]) for a in PROJETO})
    if fim <= 30:
        break
    cand = [a for a in t.index[t.folga == 0] if dur_atual[a] > ACELERAR[a][0]]
    if not cand:
        break
    a = min(cand, key=lambda x: ACELERAR[x][1])
    dur_atual[a] -= 1; gasto += ACELERAR[a][1]; log.append(a)
print("duração final:", fim, "| custo extra R$", gasto, "| encurtadas:", pd.Series(log).value_counts().to_dict())'''),

    ("tarefa",
     "**Rotas, fibra e esteiras.**\n"
     "- **Dijkstra:** a rota mais curta de Curitiba a Porto Alegre.\n"
     "- **Prim:** ligar todas as cidades com o mínimo de cabo.\n"
     "- **Edmonds-Karp:** o fluxo máximo de peças da `entrada` à `saida` nas `ESTEIRAS`.\n\n"
     "Confira os três com o `networkx`.",
     r'''import networkx as nx
dist, ant = dijkstra(ESTRADAS, "Curitiba")
print("rota:", " -> ".join(caminho(ant, "Porto Alegre")), "|", dist["Porto Alegre"], "km")
arv = prim(ESTRADAS)
print("fibra:", sum(w for *_, w in arv), "km em", len(arv), "trechos")
print("fluxo máximo:", fluxo_maximo(ESTEIRAS, "entrada", "saida"), "peças/h")
G = nx.Graph(); G.add_weighted_edges_from(ESTRADAS)
D = nx.DiGraph(); D.add_edges_from((a, b, {"capacity": c}) for a, b, c in ESTEIRAS)
print("networkx:", nx.dijkstra_path_length(G, "Curitiba", "Porto Alegre"),
      int(nx.minimum_spanning_tree(G).size(weight="weight")), nx.maximum_flow_value(D, "entrada", "saida"))'''),

    ("tarefa",
     "**Caixeiro-viajante.** O vendedor sai de Curitiba e visita Joinville, Blumenau, Florianópolis, Lages e "
     "Ponta Grossa, voltando no fim. Use as distâncias de caminho mínimo (Dijkstra) entre cada par. Compare a "
     "força bruta (todas as ordens) com a heurística do **vizinho mais próximo**.",
     r'''from itertools import permutations
cidades = ["Curitiba", "Joinville", "Blumenau", "Florianópolis", "Lages", "Ponta Grossa"]
d = {c: dijkstra(ESTRADAS, c)[0] for c in cidades}
custo_rota = lambda r: sum(d[a][b] for a, b in zip(r, r[1:]))
melhor = min((["Curitiba", *p, "Curitiba"] for p in permutations(cidades[1:])), key=custo_rota)
print("ótimo:", " -> ".join(melhor), custo_rota(melhor), "km")
rota, falta = ["Curitiba"], set(cidades[1:])
while falta:
    prox = min(falta, key=lambda c: d[rota[-1]][c]); rota.append(prox); falta.remove(prox)
rota.append("Curitiba")
print("vizinho mais próximo:", " -> ".join(rota), custo_rota(rota), "km")'''),
]
