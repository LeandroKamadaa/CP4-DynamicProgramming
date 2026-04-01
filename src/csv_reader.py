import csv

caminho_arquivo = 'data/rotas.csv'

with open(caminho_arquivo, mode='r', encoding='utf-8') as arquivo:
    leitor_csv = csv.reader(arquivo)
    
    # Se o arquivo tiver cabeçalho, ele ignorá ou capturá:
    cabecalho = next(leitor_csv)
    print(f"Colunas: {cabecalho}")
    
    for linha in leitor_csv:
        # Cada linha é uma lista de strings
        print(linha)