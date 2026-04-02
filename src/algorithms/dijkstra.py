import networkx as nx
from csv_para_grafo import csv_para_grafo

def menor_caminho(G, origem, destino, peso):
    # Retorna o custo e o caminho mínimo usando Dijkstra (via NetworkX).
    caminho = nx.shortest_path(G, source=origem, target=destino, weight=peso)
    custo = nx.shortest_path_length(G, source=origem, target=destino, weight=peso)
    
    return custo, caminho

# cria o grafo a partir do CSV
G = csv_para_grafo('data/rotas.csv', 'origem', 'destino')

# calcula o menor caminho considerando custo em reais
custo, caminho = menor_caminho(G, 'Ribeirao_Preto', 'Santos', 'custo_reais')

print(custo)
print(caminho)