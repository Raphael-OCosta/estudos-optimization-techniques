TITULO = "Metas, AHP e decisão sob incerteza"
MISSAO = (
    "Decisões reais têm **vários objetivos** e **futuro incerto**. Você vai:\n"
    "- usar a **programação por metas** para equilibrar lucro, horas extras e uso de madeira;\n"
    "- escolher o fornecedor de madeira com o **AHP**, com autovetor e razão de consistência;\n"
    "- decidir a expansão da fábrica com os critérios de incerteza (maximax, maximin, Hurwicz, Laplace, "
    "arrependimento) e de risco (valor esperado e valor da informação perfeita);\n"
    "- montar uma **árvore de decisão** com uma pesquisa de mercado."
)
ENTREGA = "o módulo `PKG/decisao.py` (pesos do AHP com consistência, os critérios de decisão, VME e VEIP) e as três decisões da Boreal justificadas."
LEITURA = [("10.2 Goal Programming Formulation", 325), ("10.3 Graphical Solution Method of Goal Programming", 332),
           ("10.4 The Analytic Hierarchy Process (AHP)", 338), ("10.6.1 Decision Making under Uncertainty", 346),
           ("10.6.2 Decision Making under Risk", 354), ("10.7 Decision Trees", 359)]

PASSOS = [
    ("texto",
     "## Ideia em 30 segundos\n"
     "**Metas:** cada meta ganha variáveis de desvio, `d⁻` (faltou) e `d⁺` (passou). Minimize os desvios "
     "indesejados, ponderados por prioridade.\n\n"
     "**AHP:** compare os critérios dois a dois (escala de 1 a 9). Os pesos são o autovetor principal. A razão de "
     "consistência `CR = (λmax - n)/(n - 1)/RI` deve ficar abaixo de 0,10.\n\n"
     "**Risco:** o **VME** é a média ponderada pelas probabilidades. O **VEIP** é quanto valeria saber o futuro, e "
     "é o máximo que se deve pagar por uma pesquisa."),

    ("tarefa",
     "**Programação por metas.** Só mesas (`x`) e armários (`y`). As metas, em ordem de prioridade:\n"
     "1. lucro de pelo menos R$ 30 mil (`120x + 210y`);\n"
     "2. não passar de 450 horas de pintura (`2x + 4y`);\n"
     "3. usar pelo menos 600 m² de madeira (`3x + 5y`), para não perder o contrato.\n\n"
     "A montagem é rígida: `x + 2,5y ≤ 400`. Monte as variáveis de desvio e minimize "
     "`100·d1⁻ + 10·d2⁺ + 1·d3⁻` com o `linprog`.",
     r'''from scipy.optimize import linprog
# variáveis: x, y, d1-, d1+, d2-, d2+, d3-, d3+
custo = [0, 0, 100, 0, 0, 10, 1, 0]
A_eq = [[120, 210, 1, -1, 0, 0, 0, 0], [2, 4, 0, 0, 1, -1, 0, 0], [3, 5, 0, 0, 0, 0, 1, -1]]
b_eq = [30000, 450, 600]
r = linprog(custo, A_ub=[[1, 2.5, 0, 0, 0, 0, 0, 0]], b_ub=[400], A_eq=A_eq, b_eq=b_eq, method="highs")
x, y, d1m, d1p, d2m, d2p, d3m, d3p = r.x
print(f"mesas {x:.1f} | armários {y:.1f}")
print(f"lucro {120 * x + 210 * y:,.0f} (faltou {d1m:,.0f}) | pintura {2 * x + 4 * y:.0f} h (passou {d2p:.0f}) | madeira {3 * x + 5 * y:.0f} m² (faltou {d3m:.0f})")'''),

    ("arquivo",
     "**O módulo de decisão.** Crie `decisao.py` com:\n"
     "- `ahp_pesos(M)`: o autovetor principal normalizado, λmax, CI e CR (RI = 0,58, 0,90, 1,12 para n = 3, 4, "
     "5);\n"
     "- `criterios_incerteza(tabela, alfa=0.6)`: a melhor alternativa por maximax, maximin, Hurwicz, Laplace e "
     "Savage (mínimo do arrependimento máximo);\n"
     "- `vme(tabela, probs)` e `veip(tabela, probs)`.",
     "decisao.py",
     r'''"""Ferramentas de decisão: AHP, critérios sob incerteza e sob risco."""
import numpy as np
import pandas as pd

RI = {1: 0.0, 2: 0.0, 3: 0.58, 4: 0.90, 5: 1.12, 6: 1.24, 7: 1.32}


def ahp_pesos(M):
    M = np.asarray(M, float)
    val, vec = np.linalg.eig(M)
    k = int(np.argmax(val.real))
    w = np.abs(vec[:, k].real)
    w /= w.sum()
    n = len(M)
    lam = float(val[k].real)
    ci = (lam - n) / (n - 1) if n > 1 else 0.0
    return w, lam, ci, (ci / RI[n] if RI[n] else 0.0)


def criterios_incerteza(tabela, alfa=0.6):
    t = tabela
    arrep = t.max() - t
    return {"maximax": t.max(axis=1).idxmax(), "maximin": t.min(axis=1).idxmax(),
            f"Hurwicz (α={alfa})": (alfa * t.max(axis=1) + (1 - alfa) * t.min(axis=1)).idxmax(),
            "Laplace": t.mean(axis=1).idxmax(), "Savage (arrependimento)": arrep.max(axis=1).idxmin()}


def vme(tabela, probs):
    return tabela @ np.asarray(probs)


def veip(tabela, probs):
    com_info = float(tabela.max() @ np.asarray(probs))
    return com_info - float(vme(tabela, probs).max())'''),

    ("tarefa",
     "**AHP do fornecedor.** Calcule os pesos dos critérios (`AHP_CRITERIOS`) e a CR. Depois calcule os pesos de "
     "cada fornecedor em cada critério (`AHP_NOTAS`), confira a CR de cada matriz e combine tudo: nota final = "
     "Σ peso do critério × peso do fornecedor. Quem vence?",
     r'''from PKG.decisao import ahp_pesos, criterios_incerteza, vme, veip
w, lam, ci, cr = ahp_pesos(AHP_CRITERIOS)
print("pesos dos critérios:", dict(zip(CRITERIOS, w.round(3).tolist())), "| CR =", round(cr, 3))
notas = pd.DataFrame({c: ahp_pesos(AHP_NOTAS[c])[0] for c in CRITERIOS}, index=FORNECEDORES)
print("CR por critério:", {c: round(float(ahp_pesos(AHP_NOTAS[c])[3]), 3) for c in CRITERIOS})
final = notas @ w
display(notas.round(3).assign(nota_final=final.round(3)).sort_values("nota_final", ascending=False))'''),

    ("tarefa",
     "**Sob incerteza.** Para a tabela `DECISAO` (lucro de cada expansão em cada cenário), aplique os 5 critérios. "
     "Cada um combina com um perfil de gestor diferente: qual é o seu?",
     r'''display(DECISAO)
for criterio, escolha in criterios_incerteza(DECISAO).items():
    print(f"{criterio:<26}-> {escolha}")'''),

    ("tarefa",
     "**Sob risco.** Com `PROB_CENARIOS`, calcule o VME de cada alternativa e o VEIP. Uma consultoria cobra R$ 120 "
     "mil por uma pesquisa de demanda perfeita. Vale a pena?",
     r'''print(vme(DECISAO, PROB_CENARIOS).round(1).to_dict())
print("VEIP: R$", round(veip(DECISAO, PROB_CENARIOS), 1), "mil", "-> vale pagar 120?", veip(DECISAO, PROB_CENARIOS) > 120)'''),

    ("tarefa",
     "**Árvore de decisão com pesquisa imperfeita.** Uma pesquisa mais barata (R$ 30 mil) diz \"favorável\" ou "
     "\"desfavorável\". Ela acerta assim:\n"
     "- `P(fav | alta) = 0,9`;\n"
     "- `P(fav | média) = 0,6`;\n"
     "- `P(fav | baixa) = 0,2`.\n\n"
     "Use Bayes para as probabilidades dos cenários depois de cada resultado, escolha a melhor alternativa em cada "
     "ramo e calcule o valor esperado **com** a pesquisa. Vale mais que decidir sem ela?",
     r'''prior = np.array(PROB_CENARIOS); p_fav = np.array([0.2, 0.6, 0.9])
valor_com = 0.0
for resultado, verossimilhanca in [("favorável", p_fav), ("desfavorável", 1 - p_fav)]:
    p_res = float(prior @ verossimilhanca)
    post = prior * verossimilhanca / p_res
    melhor = vme(DECISAO, post).idxmax(); v = vme(DECISAO, post).max()
    valor_com += p_res * v
    print(f"{resultado:<13} P={p_res:.2f} | cenários {post.round(2)} -> {melhor} (VME {v:.0f})")
sem = vme(DECISAO, prior).max()
print(f"com pesquisa: {valor_com - 30:.1f} (já descontados 30) | sem: {sem:.1f} | vale: {valor_com - 30 > sem}")'''),
]
