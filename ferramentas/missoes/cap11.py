TITULO = "Modelagem aberta: do Python para a planilha"
MISSAO = (
    "O último capítulo do livro resolve tudo no Excel (Solver). Aqui você faz o caminho de quem trabalha com "
    "Python: modela e resolve no código e entrega uma **planilha** que o gerente abre. Você vai:\n"
    "- juntar os modelos dos capítulos anteriores numa classe `PlanoBoreal`;\n"
    "- rodar cenários (\"e se a madeira ficar 20% mais escassa?\");\n"
    "- exportar um relatório Excel com várias abas;\n"
    "- conferir que a planilha bate com o modelo."
)
ENTREGA = "o módulo `PKG/relatorio.py` (`PlanoBoreal`: mix de produção, frete e escala da doca, com análise de cenários e exportação para `saidas/plano_boreal.xlsx`)."
LEITURA = [("11.1 Introduction", 368), ("Examples based on the linear programming simplex method using Excel", 376),
           ("Examples based on transportation and assignment problems using Excel", 382),
           ("Example based on integer programming using Excel", 405), ("Example based on decision making using Excel", 408)]

PASSOS = [
    ("texto",
     "## Ideia em 30 segundos\n"
     "O Solver do Excel e o `linprog` resolvem o mesmo problema. A diferença está no fluxo de trabalho:\n"
     "- no Python, o modelo é **código versionado**: dá para testar, rodar 100 cenários e automatizar;\n"
     "- no Excel, o resultado é **familiar** para quem decide.\n\n"
     "O melhor dos dois: modele em Python e entregue a planilha."),

    ("arquivo",
     "**O plano integrado.** Crie `relatorio.py` com a classe `PlanoBoreal(produtos, capacidade, demanda_max)`:\n"
     "- `mix()`: o `linprog` com as capacidades, as demandas máximas e a regra das cadeiras; devolve um DataFrame "
     "de produção e o lucro;\n"
     "- `frete(custo, oferta, demanda)`: o transporte ótimo, devolvido como DataFrame;\n"
     "- `doca(lam, mu, custo_equipe, custo_parado)`: o número de equipes de menor custo (o `mmc` do cap. 8);\n"
     "- `cenario(**mudancas)`: devolve um novo plano com as capacidades alteradas;\n"
     "- `exportar(caminho, frete_df, cenarios)`: grava um `.xlsx` com as abas `mix`, `frete`, `cenarios` e "
     "`premissas` (`pd.ExcelWriter`).",
     "relatorio.py",
     r'''"""Plano integrado da Móveis Boreal e exportação para Excel."""
import numpy as np
import pandas as pd
from scipy.optimize import linprog

from .filas import mmc


class PlanoBoreal:
    def __init__(self, produtos, capacidade, demanda_max, cadeiras_por_mesa=4):
        self.produtos, self.capacidade = produtos, dict(capacidade)
        self.demanda_max, self.cpm = demanda_max, cadeiras_por_mesa

    def mix(self):
        p = self.produtos
        A = [p[r].to_numpy() for r in self.capacidade] + [[self.cpm, -1, 0, 0]]
        b = list(self.capacidade.values()) + [0]
        r = linprog(-p["lucro"].to_numpy(), A_ub=A, b_ub=b, bounds=[(0, self.demanda_max[k]) for k in p.index], method="highs")
        df = pd.DataFrame({"quantidade": r.x.round(2), "lucro_unit": p["lucro"]}, index=p.index)
        df["lucro_total"] = (df.quantidade * df.lucro_unit).round(2)
        return df, round(-r.fun, 2)

    @staticmethod
    def frete(custo, oferta, demanda, fabricas, lojas):
        m, n = custo.shape
        A_ub = [np.kron(np.eye(m)[i], np.ones(n)) for i in range(m)]
        A_eq = [np.kron(np.ones(m), np.eye(n)[j]) for j in range(n)]
        r = linprog(custo.ravel(), A_ub=A_ub, b_ub=oferta, A_eq=A_eq, b_eq=demanda, method="highs")
        return pd.DataFrame(r.x.reshape(m, n).round(0), index=fabricas, columns=lojas), round(r.fun, 2)

    @staticmethod
    def doca(lam, mu, custo_equipe, custo_parado, max_c=6):
        custos = {c: custo_equipe * c + custo_parado * mmc(lam, mu, c)["L"] for c in range(1, max_c + 1) if lam < c * mu}
        c = min(custos, key=custos.get)
        return c, round(custos[c], 2)

    def cenario(self, **mudancas):
        cap = {k: v * mudancas.get(k, 1.0) for k, v in self.capacidade.items()}
        return PlanoBoreal(self.produtos, cap, self.demanda_max, self.cpm)

    def exportar(self, caminho, frete_df, cenarios):
        mix_df, lucro = self.mix()
        with pd.ExcelWriter(caminho) as w:
            mix_df.to_excel(w, sheet_name="mix")
            frete_df.to_excel(w, sheet_name="frete")
            cenarios.to_excel(w, sheet_name="cenarios")
            pd.Series({**self.capacidade, "lucro_otimo": lucro}).to_frame("valor").to_excel(w, sheet_name="premissas")
        return caminho'''),

    ("tarefa",
     "**O plano-base.** Crie o `PlanoBoreal` com os dados do cap. 2 e mostre o mix e o lucro. Calcule também o "
     "frete ótimo (com a oferta como **limite**, `≤`, e a demanda exata) e o número de equipes da doca.",
     r'''from PKG.relatorio import PlanoBoreal
plano = PlanoBoreal(PRODUTOS, CAPACIDADE, DEMANDA_MAX, CADEIRAS_POR_MESA)
mix_df, lucro = plano.mix(); display(mix_df); print("lucro R$", lucro)
frete_df, custo_frete = PlanoBoreal.frete(CUSTO_FRETE, OFERTA, DEMANDA, FABRICAS, LOJAS)
display(frete_df); print("frete R$", custo_frete)
print("doca:", PlanoBoreal.doca(CHEGADAS_HORA, ATENDIMENTO_HORA, CUSTO_EQUIPE, CUSTO_CAMINHAO_PARADO))'''),

    ("tarefa",
     "**Cenários.** Rode quatro cenários e monte uma tabela de lucro e produção:\n"
     "- madeira -20%;\n"
     "- pintura +15%;\n"
     "- montagem -10%;\n"
     "- madeira -20% **e** pintura +15%.\n\n"
     "Qual cenário mais preocupa?",
     r'''cenarios = {"base": {}, "madeira -20%": {"madeira_m2": .8}, "pintura +15%": {"pintura_h": 1.15},
            "montagem -10%": {"montagem_h": .9}, "madeira -20% e pintura +15%": {"madeira_m2": .8, "pintura_h": 1.15}}
linhas = {}
for nome, mud in cenarios.items():
    df, l = plano.cenario(**mud).mix()
    linhas[nome] = {"lucro": l, **df["quantidade"].to_dict()}
tab_cen = pd.DataFrame(linhas).T; display(tab_cen)'''),

    ("tarefa",
     "**Exportar e conferir.** Exporte para `../saidas/plano_boreal.xlsx`, leia de volta todas as abas com "
     "`pd.read_excel(..., sheet_name=None)` e confira que o lucro da aba `mix` bate com o do modelo. Abra o arquivo "
     "no Excel para ver como o gerente o recebe.",
     r'''caminho = plano.exportar("../saidas/plano_boreal.xlsx", frete_df, tab_cen)
abas = pd.read_excel(caminho, sheet_name=None, index_col=0)
print("abas:", list(abas))
print("lucro na planilha:", round(abas["mix"]["lucro_total"].sum()), "| no modelo:", round(lucro), "(centavos de diferença vêm das quantidades arredondadas)")'''),

    ("tarefa",
     "**Resumo executivo.** Escreva 5 linhas para a diretoria, com os números calculados: o plano de produção, o "
     "lucro, o custo de frete, as equipes na doca e o cenário de maior risco.",
     r'''pior = tab_cen["lucro"].idxmin()
print(f"1. Produzir {', '.join(f'{q:.0f} {p}' for p, q in mix_df['quantidade'].items() if q > 0)} por mês.")
print(f"2. Lucro previsto: R$ {lucro:,.0f}/mês.")
print(f"3. Frete ótimo: R$ {custo_frete:,.0f}/mês.")
print(f"4. Doca: {PlanoBoreal.doca(CHEGADAS_HORA, ATENDIMENTO_HORA, CUSTO_EQUIPE, CUSTO_CAMINHAO_PARADO)[0]} equipes.")
print(f"5. Maior risco: '{pior}' (lucro cai para R$ {tab_cen.loc[pior, 'lucro']:,.0f}).")'''),
]
