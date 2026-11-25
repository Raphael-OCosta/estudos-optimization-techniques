TITULO = "Substituição: quando trocar a máquina"
MISSAO = (
    "A serra principal custou R$ 60 mil. A cada ano a manutenção sobe e o valor de revenda cai. Quando trocar?\n"
    "- **Sem juros**, a resposta é o ano que minimiza o custo médio anual.\n"
    "- **Com juros**, entra o valor presente.\n\n"
    "Depois, o outro tipo de item, o que **quebra de repente**, como as lâmpadas do galpão: trocar uma a uma "
    "quando queimam, ou todas de uma vez a cada k meses (**substituição em grupo**)?"
)
ENTREGA = "o módulo `PKG/substituicao.py` (custo médio anual, custo anual equivalente com juros e a política de troca em grupo) com o ano e o mês ótimos."
LEITURA = [("6.2.1 Replacement Policy When the Value of Money Does Not Change with Time", 211),
           ("6.2.2 Replacement Policy When the Value of Money Changes with Time", 219),
           ("6.3 Replacement When the Equipment/Assets Fail Completely All of a Sudden", 224)]

PASSOS = [
    ("texto",
     "## Ideia em 30 segundos\n"
     "**Sem juros:**\n"
     "- o custo de ficar n anos com a máquina é `C - S_n + Σ manutenção(1..n)`;\n"
     "- o **custo médio anual** é esse total dividido por n;\n"
     "- troque no ano em que ele é mínimo, quando a manutenção do ano seguinte passa a média.\n\n"
     "**Com juros:** desconte cada gasto por `(1 + i)^t` e converta num **custo anual equivalente**.\n\n"
     "**Em grupo:** compare o custo por mês de trocar todas a cada k meses (mais as que queimam no meio) com o de "
     "trocar só as que queimam."),

    ("arquivo",
     "**O módulo de substituição.** Crie `substituicao.py` com:\n"
     "- `custo_medio_anual(preco, manutencao, revenda)`: um DataFrame por ano n com a manutenção acumulada, o "
     "custo total e o custo médio;\n"
     "- `custo_anual_equivalente(preco, manutencao, revenda, juros)`: o VP dos custos até n, convertido em "
     "parcela anual pelo fator `i / (1 - (1 + i)^-n)`;\n"
     "- `trocas_esperadas(sobrevivencia, n_itens, meses)`: a recursão do livro. Com `p_k` a probabilidade de queimar "
     "no mês k, o número de trocas no mês t é `N_t = N0·p_t + Σ N_{t-k}·p_k`.",
     "substituicao.py",
     r'''"""Modelos de substituição de equipamentos."""
import numpy as np
import pandas as pd


def custo_medio_anual(preco, manutencao, revenda):
    n = np.arange(1, len(manutencao) + 1)
    acum = np.cumsum(manutencao)
    total = preco - np.asarray(revenda) + acum
    return pd.DataFrame({"manutencao_acum": acum, "custo_total": total, "custo_medio": total / n}, index=n)


def custo_anual_equivalente(preco, manutencao, revenda, juros):
    linhas = {}
    for n in range(1, len(manutencao) + 1):
        vp = preco + sum(m / (1 + juros) ** (t + 1) for t, m in enumerate(manutencao[:n])) - revenda[n - 1] / (1 + juros) ** n
        fator = juros / (1 - (1 + juros) ** -n)
        linhas[n] = {"vp_custos": vp, "custo_anual_equivalente": vp * fator}
    return pd.DataFrame(linhas).T


def trocas_esperadas(sobrevivencia, n_itens, meses):
    s = np.asarray(sobrevivencia, float)
    p = -np.diff(s)                       # p[k-1] = probabilidade de queimar no mês k
    N = np.zeros(meses + 1)
    for t in range(1, meses + 1):
        N[t] = n_itens * (p[t - 1] if t - 1 < len(p) else 0)
        N[t] += sum(N[t - k] * p[k - 1] for k in range(1, min(t, len(p) + 1)))
    return N[1:]'''),

    ("tarefa",
     "**Sem juros.** Monte a tabela da serra com `custo_medio_anual` e ache o ano ótimo de troca. Confira a regra "
     "do livro: no ano ótimo, a manutenção do ano **seguinte** passa a ser maior que o custo médio.",
     r'''from PKG.substituicao import custo_medio_anual, custo_anual_equivalente, trocas_esperadas
tab = custo_medio_anual(SERRA_PRECO, SERRA_MANUTENCAO, SERRA_REVENDA)
display(tab.round(0))
n_otimo = int(tab["custo_medio"].idxmin())
print("trocar a cada", n_otimo, "anos | manutenção do ano seguinte:", SERRA_MANUTENCAO[n_otimo], "> média", round(tab.loc[n_otimo, "custo_medio"]))'''),

    ("tarefa",
     "**Com juros.** Refaça com juros de 0%, 8% e 15% ao ano usando `custo_anual_equivalente`. O ano ótimo muda? Por "
     "que juros maiores tendem a **adiar** a troca?",
     r'''for i in (0.0001, 0.08, 0.15):
    t = custo_anual_equivalente(SERRA_PRECO, SERRA_MANUTENCAO, SERRA_REVENDA, i)
    print(f"juros {i:.0%}: trocar a cada {int(t['custo_anual_equivalente'].idxmin())} anos | custo anual equivalente R$ {t['custo_anual_equivalente'].min():,.0f}")
# Com juros altos, o dinheiro de comprar a máquina nova "pesa" mais hoje; o custo futuro de manutenção pesa menos.'''),

    ("tarefa",
     "**Lâmpadas que queimam.** O galpão tem 1.000 lâmpadas (`LAMPADAS_SOBREVIVENCIA` dá a fração viva no início "
     "de cada mês). Calcule as trocas esperadas por mês (12 meses) e desenhe. As trocas se estabilizam em `N / "
     "vida média`. Confira esse valor.",
     r'''import matplotlib.pyplot as plt
N = trocas_esperadas(LAMPADAS_SOBREVIVENCIA, 1000, 12)
p = -np.diff(LAMPADAS_SOBREVIVENCIA); vida_media = sum((k + 1) * pk for k, pk in enumerate(p))
plt.bar(range(1, 13), N); plt.axhline(1000 / vida_media, c="r", ls="--", label="N / vida média"); plt.legend(); plt.show()
print("vida média:", round(vida_media, 2), "meses | estável ≈", round(1000 / vida_media, 1), "por mês")'''),

    ("tarefa",
     "**Individual × em grupo.** Trocar uma lâmpada que queimou custa R$ 12 (com a mão de obra avulsa). Na troca em "
     "grupo, cada uma sai por R$ 4. Calcule o custo médio mensal de:\n"
     "- (a) só trocar quando queima: `12 × N / vida média`;\n"
     "- (b) trocar todas a cada k meses, para k de 1 a 6: `(4·1000 + 12·Σ N_t até k-1) / k`.\n\n"
     "Qual a melhor política?",
     r'''indiv = 12 * 1000 / vida_media
print(f"individual: R$ {indiv:,.0f}/mês")
for k in range(1, 7):
    grupo = (4 * 1000 + 12 * N[:k - 1].sum()) / k
    print(f"grupo a cada {k} meses: R$ {grupo:,.0f}/mês")'''),
]
