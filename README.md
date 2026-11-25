# Estudos — *An Introduction to Optimization Techniques* (Vikrant Sharma et al.) · trilha prática

> **A melhor forma de estudar um livro técnico é ler e praticar ao mesmo tempo.**
> Aqui a prática vem primeiro. Cada capítulo é uma **missão** curta: você lê só o essencial e escreve o método com as próprias mãos.

O livro cobre a pesquisa operacional clássica: programação linear, transporte, redes, sequenciamento, substituição, jogos, filas, programação dinâmica e inteira, metas e decisão. Nas 11 missões, você é o analista de otimização da **Móveis Boreal** (fictícia) e entrega o plano final numa planilha Excel.

## A trilha (61 passos)

| Cap. | Missão | Você constrói |
|---|---|---|
| 1 | Introdução | busca exaustiva × cálculo, fatorial 2³ (DOE), classificação de problemas, `basico.py` |
| 2 | Programação linear | método gráfico, **simplex em tabela do zero**, `linprog`, sensibilidade, dualidade, `simplex.py` |
| 3 | Transporte e designação | canto noroeste, **Vogel**, custos reduzidos u-v, método húngaro, desbalanceado, `transporte.py` |
| 4 | Redes | **CPM e PERT**, simulação, crashing, **Dijkstra, Prim e fluxo máximo do zero**, caixeiro-viajante, `redes.py` |
| 5 | Sequenciamento | SPT/EDD, **regra de Johnson**, 3 máquinas, heurística NEH, Gantt, `sequencia.py` |
| 6 | Substituição | custo médio anual, juros, substituição em grupo, `substituicao.py` |
| 7 | Teoria dos jogos | ponto de sela, dominância, estratégias mistas por PL, método gráfico, `jogos.py` |
| 8 | Filas | M/M/1, M/M/c (Erlang C), lei de Little, **simulador de eventos**, custo ótimo, `filas.py` |
| 9 | Dinâmica e inteira | alocação por DP, mochila, **branch and bound do zero**, `milp`, `inteira.py` |
| 10 | Metas e decisão | programação por metas, **AHP com consistência**, critérios de incerteza, VME, VEIP, árvore de decisão, `decisao.py` |
| 11 | Modelagem aberta | plano integrado, cenários e **exportação para Excel**, `relatorio.py` |

## Diferenças em relação ao livro

- Os exemplos numéricos do livro foram trocados por **dados fictícios da Móveis Boreal** (`comum/dados.py`), pequenos o suficiente para conferir à mão.
- O Excel/Solver do capítulo 11 virou Python (SciPy) com exportação para `.xlsx`: o gerente recebe a planilha e o modelo fica versionado.
- As páginas indicadas nos cadernos são as do PDF em inglês. A leitura é **opcional** e só do essencial.

## Como usar

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-estudos.txt
.venv\Scripts\python.exe ferramentas\testar_cadernos.py   # opcional: roda o gabarito (0 erros)
```

Abra `praticar/cap01_*.ipynb` no VS Code e escolha o kernel `.venv`. O [Guia de Estudos (PDF)](Guia_de_Estudos.pdf) mostra o mapa e a rotina de 60 minutos.

## Direitos autorais

O livro **não** está neste repositório. Use a sua própria cópia.
As missões, os cadernos, os dados fictícios, os scripts e o guia são autorais, sob licença [MIT](LICENSE).
