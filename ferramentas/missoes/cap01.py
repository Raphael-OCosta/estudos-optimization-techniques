TITULO = "Otimização: decidir o melhor com restrições"
MISSAO = (
    "Você virou o analista de **pesquisa operacional da Móveis Boreal**: 3 fábricas, 4 lojas, mesas, cadeiras, "
    "estantes e armários. Ao longo do livro você vai responder:\n"
    "- quanto produzir de cada móvel e de qual fábrica mandar para qual loja;\n"
    "- quem opera cada máquina e quando o projeto da nova linha termina;\n"
    "- quando trocar a serra e quantas equipes pôr na doca;\n"
    "- onde investir.\n\n"
    "Hoje: o vocabulário (objetivo, variáveis, restrições), a diferença entre achar o ótimo **testando** e "
    "**raciocinando**, e o planejamento de experimentos (DOE)."
)
ENTREGA = "o módulo `PKG/basico.py`, com a busca exaustiva, o ótimo por cálculo de uma função de uma variável e um planejamento fatorial 2³."
LEITURA = [("1.4 Optimization Terms/Parameters", 20), ("1.5 Types of Optimization", 21),
           ("1.7 Optimization by Design of Experiments (DOE)", 23), ("1.9 Limitations of Optimization Techniques", 26)]

PASSOS = [
    ("texto",
     "## Ideia em 30 segundos\n"
     "Todo problema de otimização tem três partes:\n"
     "- **variáveis de decisão**: o que você controla;\n"
     "- **função objetivo**: o que você quer maximizar ou minimizar;\n"
     "- **restrições**: o que limita.\n\n"
     "Os tipos (linear ou não linear, contínuo ou inteiro, com um ou vários objetivos) decidem qual técnica usar, "
     "e o resto do livro é isso."),

    ("tarefa",
     "**O primeiro problema.** A Boreal vende mesas a um preço `p`. A demanda é `q = 400 - 1,5·p` e o custo é "
     "R$ 80 por mesa. O lucro é `(p - 80)·q`. Calcule o lucro para `p` de 80 a 260, de 1 em 1, e ache o melhor "
     "preço **testando todos**. Desenhe a curva.",
     r'''import matplotlib.pyplot as plt
precos = np.arange(80, 261)
lucro = (precos - 80) * (400 - 1.5 * precos)
melhor = precos[np.argmax(lucro)]
plt.plot(precos, lucro); plt.axvline(melhor, ls="--", c="gray"); plt.xlabel("preço"); plt.ylabel("lucro"); plt.show()
print("melhor preço testando:", melhor, "| lucro:", lucro.max())'''),

    ("arquivo",
     "**O módulo básico.** Crie `basico.py` com:\n"
     "- `busca_exaustiva(f, candidatos, maximizar=True)`: devolve `(melhor_x, melhor_valor)`;\n"
     "- `otimo_quadratica(a, b)`: o vértice `-b/(2a)` de `a·x² + b·x + c`;\n"
     "- `fatorial_2k(k)`: a matriz de planejamento com todas as combinações de -1 e +1 para k fatores "
     "(`itertools.product`), como DataFrame;\n"
     "- `efeitos(plano, resposta)`: o efeito principal de cada fator, a média da resposta em +1 menos a média em "
     "-1.",
     "basico.py",
     r'''"""Ferramentas básicas: busca exaustiva, ótimo de quadrática e planejamento fatorial 2^k."""
from itertools import product

import numpy as np
import pandas as pd


def busca_exaustiva(f, candidatos, maximizar=True):
    valores = [f(x) for x in candidatos]
    i = int(np.argmax(valores) if maximizar else np.argmin(valores))
    return candidatos[i], valores[i]


def otimo_quadratica(a, b):
    return -b / (2 * a)


def fatorial_2k(k, nomes=None):
    nomes = nomes or [f"x{i + 1}" for i in range(k)]
    return pd.DataFrame(list(product([-1, 1], repeat=k)), columns=nomes)


def efeitos(plano, resposta):
    resposta = np.asarray(resposta, float)
    return {c: float(resposta[plano[c] == 1].mean() - resposta[plano[c] == -1].mean()) for c in plano.columns}'''),

    ("tarefa",
     "**Testar × raciocinar.** O lucro é `-1,5p² + 520p - 32000`. Use `otimo_quadratica` e confira que bate com a "
     "busca exaustiva. Depois imagine 4 variáveis com 200 valores cada: quantas combinações a busca exaustiva "
     "teria de testar? E com 10 variáveis?",
     r'''from PKG.basico import busca_exaustiva, otimo_quadratica, fatorial_2k, efeitos
print("pelo cálculo:", otimo_quadratica(-1.5, 520))
print("testando:", busca_exaustiva(lambda p: (p - 80) * (400 - 1.5 * p), list(range(80, 261))))
for k in (4, 10):
    print(f"{k} variáveis × 200 valores: {200 ** k:.2e} combinações")'''),

    ("tarefa",
     "**Planejamento de experimentos (DOE).** A pintura das mesas tem 3 fatores: temperatura (baixa/alta), "
     "camadas (1/2) e tempo de secagem (curto/longo). Monte o fatorial 2³ e use a \"fábrica\" "
     "`defeitos = 20 - 3·temp - 5·camadas - 1·secagem + 2·temp·camadas + ruído` para gerar os resultados "
     "(`semente 1`). Calcule os efeitos principais e o da interação temperatura × camadas.",
     r'''r = np.random.default_rng(1)
plano = fatorial_2k(3, ["temperatura", "camadas", "secagem"])
y = 20 - 3 * plano.temperatura - 5 * plano.camadas - plano.secagem + 2 * plano.temperatura * plano.camadas + r.normal(0, .5, 8)
display(plano.assign(defeitos=y.round(2)))
print({k: round(v, 2) for k, v in efeitos(plano, y).items()})
inter = plano.temperatura * plano.camadas
print("interação temp×camadas:", round(y[inter == 1].mean() - y[inter == -1].mean(), 2))'''),

    ("tarefa",
     "**Classifique os problemas.** Para cada pergunta da Boreal abaixo, escreva num dicionário o tipo de "
     "otimização (linear/não linear, contínua/inteira, um/vários objetivos) e o capítulo do livro que resolve:\n"
     "- quanto produzir de cada móvel;\n"
     "- qual fábrica abastece cada loja;\n"
     "- quem opera cada máquina;\n"
     "- quando trocar a serra;\n"
     "- quais projetos aprovar;\n"
     "- o equilíbrio entre lucro, emprego e meio ambiente.",
     r'''tipos = {
    "quanto produzir de cada móvel": ("linear, contínua, 1 objetivo", "cap. 2"),
    "qual fábrica abastece cada loja": ("linear (transporte), contínua", "cap. 3"),
    "quem opera cada máquina": ("linear (designação), inteira 0/1", "cap. 3"),
    "quando trocar a serra": ("dinâmica/enumeração, discreta", "cap. 6"),
    "quais projetos aprovar": ("programação inteira 0/1", "cap. 9"),
    "lucro × emprego × meio ambiente": ("vários objetivos (programação por metas)", "cap. 10"),
}
for pergunta, (tipo, cap) in tipos.items():
    print(f"{pergunta:<34}{tipo:<42}{cap}")'''),
]
