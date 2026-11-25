"""Dados fictícios da Móveis Boreal, uma fábrica de móveis com 3 unidades e 4 lojas.

Use nos cadernos com `from dados import *` (a Preparação já faz isso).
Tudo aqui é pequeno de propósito: dá para conferir as contas à mão, como nos exemplos do livro.
"""
import numpy as np
import pandas as pd

EMPRESA = "Móveis Boreal"

# --- cap. 2: mix de produção (programação linear) ---------------------------------------------
PRODUTOS = pd.DataFrame({
    "lucro": [120, 45, 160, 210],                # R$ por unidade
    "carpintaria_h": [4, 1.5, 5, 6],
    "pintura_h": [2, 1, 3, 4],
    "montagem_h": [1, 0.5, 2, 2.5],
    "madeira_m2": [3, 1, 4, 5],
}, index=["mesa", "cadeira", "estante", "armario"])
CAPACIDADE = {"carpintaria_h": 1200, "pintura_h": 700, "montagem_h": 400, "madeira_m2": 900}
DEMANDA_MAX = {"mesa": 150, "cadeira": 500, "estante": 100, "armario": 80}
CADEIRAS_POR_MESA = 4                             # cada mesa vendida leva pelo menos 4 cadeiras

# --- cap. 3: transporte e designação ------------------------------------------------------------
FABRICAS = ["Curitiba", "Joinville", "Caxias"]
LOJAS = ["São Paulo", "Porto Alegre", "Florianópolis", "Londrina"]
CUSTO_FRETE = np.array([[42, 70, 31, 25],         # R$ por móvel, fábrica -> loja
                        [48, 52, 18, 40],
                        [75, 22, 35, 68]])
OFERTA = np.array([320, 260, 220])
DEMANDA = np.array([280, 180, 150, 140])
OPERARIOS = ["Ana", "Bruno", "Carla", "Davi", "Eva"]
MAQUINAS = ["serra", "plaina", "tupia", "lixadeira", "furadeira"]
TEMPO_TAREFA = np.array([[14, 5, 8, 7, 15],       # minutos por peça, operário x máquina
                         [2, 12, 6, 5, 10],
                         [7, 8, 3, 9, 11],
                         [2, 4, 6, 10, 9],
                         [12, 9, 14, 3, 8]])

# --- cap. 4: projeto da nova linha e redes -----------------------------------------------------
# atividade: (descrição, predecessoras, otimista, mais provável, pessimista) em dias
PROJETO = {
    "A": ("pesquisa de mercado", [], 4, 6, 10),
    "B": ("design dos móveis", ["A"], 5, 8, 14),
    "C": ("comprar máquinas", ["A"], 7, 10, 16),
    "D": ("protótipos", ["B"], 4, 5, 9),
    "E": ("instalar máquinas", ["C"], 3, 4, 8),
    "F": ("treinar equipe", ["E"], 2, 3, 4),
    "G": ("teste com clientes", ["D"], 3, 5, 7),
    "H": ("produção piloto", ["F", "G"], 4, 6, 9),
    "I": ("campanha de lançamento", ["B"], 6, 9, 15),
    "J": ("lançamento", ["H", "I"], 1, 2, 3),
}
# custo para encurtar (crashing): (dias mínimos, R$ por dia economizado)
ACELERAR = {"A": (4, 900), "B": (6, 1200), "C": (8, 500), "D": (4, 700), "E": (3, 400),
            "F": (2, 600), "G": (4, 800), "H": (4, 1500), "I": (7, 300), "J": (1, 2000)}
# estradas entre cidades (km)
ESTRADAS = [("Curitiba", "Joinville", 130), ("Curitiba", "Ponta Grossa", 115), ("Curitiba", "Paranaguá", 90),
            ("Joinville", "Florianópolis", 180), ("Joinville", "Blumenau", 95), ("Blumenau", "Florianópolis", 150),
            ("Ponta Grossa", "Londrina", 270), ("Curitiba", "Londrina", 380), ("Blumenau", "Lages", 230),
            ("Florianópolis", "Lages", 225), ("Lages", "Caxias", 210), ("Caxias", "Porto Alegre", 130),
            ("Florianópolis", "Porto Alegre", 470), ("Paranaguá", "Joinville", 110), ("Ponta Grossa", "Lages", 390)]
# rede de esteiras da fábrica: (de, para, capacidade em peças/hora)
ESTEIRAS = [("entrada", "corte", 60), ("entrada", "estoque", 40), ("corte", "estoque", 15), ("corte", "lixa", 30),
            ("corte", "furo", 25), ("estoque", "furo", 35), ("lixa", "pintura", 40), ("furo", "lixa", 10),
            ("furo", "pintura", 30), ("pintura", "saida", 70)]

# --- cap. 5: sequenciamento --------------------------------------------------------------------
PEDIDOS = pd.DataFrame({
    "corte": [5, 2, 9, 4, 7, 3, 8],              # horas na máquina 1
    "acabamento": [3, 6, 4, 8, 2, 5, 6],         # horas na máquina 2
    "embalagem": [2, 1, 3, 2, 1, 2, 2],          # horas na máquina 3
    "prazo_h": [12, 9, 30, 20, 25, 15, 40],
}, index=[f"P{i}" for i in range(1, 8)])

# --- cap. 6: substituição ----------------------------------------------------------------------
SERRA_PRECO = 60000
SERRA_MANUTENCAO = [3000, 4200, 5800, 8000, 11000, 15000, 20000, 26000]   # custo por ano de uso
SERRA_REVENDA = [42000, 31000, 24000, 18000, 14000, 11000, 9000, 8000]    # valor no fim de cada ano
LAMPADAS_SOBREVIVENCIA = [1.0, 0.95, 0.82, 0.60, 0.30, 0.10, 0.0]         # fração viva no início de cada mês

# --- cap. 7: jogos -----------------------------------------------------------------------------
# ganho de participação de mercado (pontos) da Boreal; linhas = estratégias da Boreal, colunas = do concorrente
ESTRATEGIAS_BOREAL = ["preço baixo", "propaganda", "qualidade", "frete grátis"]
ESTRATEGIAS_RIVAL = ["preço baixo", "propaganda", "lançamento"]
JOGO = np.array([[3, -1, 2],
                 [-1, 2, 1],
                 [1, -1, 1],
                 [-2, 1, 0]])

# --- cap. 8: filas -----------------------------------------------------------------------------
CHEGADAS_HORA = 9            # caminhões por hora na doca
ATENDIMENTO_HORA = 12        # caminhões que uma equipe descarrega por hora
CUSTO_CAMINHAO_PARADO = 180  # R$ por hora
CUSTO_EQUIPE = 95            # R$ por hora por equipe

# --- cap. 9: programação dinâmica e inteira ----------------------------------------------------
# lucro extra (R$ mil) ao investir 0..5 milhões em cada loja
RETORNO_INVESTIMENTO = pd.DataFrame({"São Paulo": [0, 28, 45, 65, 78, 90], "Porto Alegre": [0, 25, 47, 60, 70, 75],
                                     "Florianópolis": [0, 15, 40, 62, 80, 85]}, index=range(6))
PROJETOS_CAPITAL = pd.DataFrame({
    "custo_ano1": [500, 300, 450, 200, 380, 250, 600],
    "custo_ano2": [200, 350, 150, 250, 100, 300, 250],
    "vpl": [650, 480, 560, 300, 420, 380, 800],
}, index=["robô de pintura", "nova loja", "galpão", "e-commerce", "caldeira", "frota", "fábrica nova"])
ORCAMENTO = {"ano1": 1200, "ano2": 900}

# --- cap. 10: metas, AHP e decisão --------------------------------------------------------------
FORNECEDORES = ["Pinhal", "Serra Verde", "Madeirex"]
CRITERIOS = ["preço", "qualidade", "prazo", "sustentabilidade"]
# comparações par a par (escala de Saaty) dos critérios: linha é quantas vezes mais importante que a coluna
AHP_CRITERIOS = np.array([[1, 1 / 3, 3, 2],
                          [3, 1, 5, 3],
                          [1 / 3, 1 / 5, 1, 1 / 2],
                          [1 / 2, 1 / 3, 2, 1]])
AHP_NOTAS = {   # comparações dos fornecedores em cada critério
    "preço": np.array([[1, 3, 1 / 2], [1 / 3, 1, 1 / 4], [2, 4, 1]]),
    "qualidade": np.array([[1, 1 / 4, 2], [4, 1, 5], [1 / 2, 1 / 5, 1]]),
    "prazo": np.array([[1, 2, 3], [1 / 2, 1, 2], [1 / 3, 1 / 2, 1]]),
    "sustentabilidade": np.array([[1, 1 / 2, 4], [2, 1, 6], [1 / 4, 1 / 6, 1]]),
}
# lucro (R$ mil) de cada decisão de expansão em cada cenário de demanda
DECISAO = pd.DataFrame({"demanda baixa": [-200, -60, 20], "demanda média": [300, 180, 90], "demanda alta": [900, 450, 150]},
                       index=["fábrica nova", "turno extra", "terceirizar"])
PROB_CENARIOS = [0.3, 0.5, 0.2]
