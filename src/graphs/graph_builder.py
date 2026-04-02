import pandas as pd
import networkx as nx


def csv_para_grafo(caminho_arquivo, coluna_origem, coluna_destino, direcionado=False):
    # Carrega o CSV
    df = pd.read_csv(caminho_arquivo)
    
    # Inicializa o tipo de grafo
    G = nx.DiGraph() if direcionado else nx.Graph()
    
    # Adiciona as arestas e todos os atributos das colunas restantes
    # O método from_pandas_edgelist é extremamente eficiente para isso
    colunas_atributos = [col for col in df.columns if col not in [coluna_origem, coluna_destino]]
    
    G = nx.from_pandas_edgelist(
        df, 
        source=coluna_origem, 
        target=coluna_destino, 
        edge_attr=colunas_atributos,
        create_using=G
    )
    
    return G

# Exemplo de uso:
grafo = csv_para_grafo('data/rotas.csv', 'origem', 'destino')
print(grafo.edges(data=True))