# Rota Inteligente Brasil
### Otimização Logística com Algoritmos — FIAP Dynamic Programming

**Grupo:**
- Cilas Pinto Macedo — RM560745
- Ian Junji Maluvayshi Matsushita — RM560588
- Pedro Arão Baquini — RM559580
- Leandro Kamada Pesce Dimov — RM560381

**Professor:** André Marques | **Curso:** FIAP Dynamic Programming

---

## Visão Geral

Solução computacional para apoio a decisões logísticas no Brasil, modelando a malha de distribuição como um **grafo ponderado** e aplicando múltiplas estratégias algorítmicas para encontrar rotas eficientes e alocar cargas entre produtores, armazéns e capitais consumidoras.

### Algoritmos Implementados

| Módulo | Técnica | Arquivo |
|---|---|---|
| Modelagem do grafo | Leitura CSV + grafo dirigido | `src/grafo.py` |
| Caminho mínimo | **Dijkstra** (heap binário) | `src/dijkstra.py` |
| Caminho mínimo | **DP top-down** com memoization | `src/dp.py` |
| Alocação de carga | **DP bottom-up** (Knapsack adaptado) | `src/dp.py` |
| Baseline | Algoritmo **Guloso** | `src/guloso.py` |
| Pré-processamento | **Divide and Conquer** (Merge Sort) | `src/divide_conquer.py` |
| Visualizações | Grafo, barras, scatter | `src/visualizacao.py` |

---

## Estrutura do Projeto

```
rota_inteligente/
├── data/
│   └── rotas_logisticas.csv        # Dados de entrada (18 trechos, 3 cenários)
├── src/
│   ├── grafo.py                    # Modelagem: Grafo, Aresta, carregar_csv()
│   ├── dijkstra.py                 # Dijkstra com heap + função de custo injetável
│   ├── dp.py                       # DP memoization + DP knapsack (alocação)
│   ├── guloso.py                   # Greedy para comparação
│   ├── divide_conquer.py           # Merge Sort + decomposição de cenários
│   ├── visualizacao.py             # Plots com matplotlib e networkx
│   └── main.py                     # Pipeline principal
├── tests/
│   └── test_algoritmos.py          # 10 testes automatizados
├── reports/                        # Figuras geradas (PNG) e relatório PDF
├── requirements.txt
└── README.md
```

---

## Instalação e Execução

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Executar pipeline completo (todos os cenários, 30 ton de carga)
cd src
python main.py

# 3. Filtrar por cenário
python main.py --cenario A

# 4. Alterar carga total
python main.py --carga 50

# 5. Rodar testes
cd tests
python test_algoritmos.py
```

---

## Cenários e Resultados

### Cenário A — Triângulo Mineiro (Ribeirão Preto → BH)
- **Rota ótima (Dijkstra/DP):** Ribeirão Preto → Campinas → Belo Horizonte
- **Custo composto:** 10.70
- **Guloso:** 15.40 (+43.9% pior) — escolhe caminho mais longo via São Paulo

### Cenário B — Corredor de Grãos (Sorriso/MT → Santos)
- **Rota ótima:** Sorriso → Lucas do Rio Verde → Rondonópolis → Campinas → Santos
- **Custo composto:** 24.70
- **Guloso:** empata com Dijkstra (topologia linear favorece guloso)

### Cenário C — Nordeste (Petrolina → Salvador)
- **Rota ótima:** Petrolina → Salvador (direto)
- **Custo composto:** 6.60
- **Guloso:** 7.93 (+20.1% pior) — vai via Feira de Santana por ganho local imediato

---

## Decisões de Projeto

### Por que Dijkstra + DP?
Dijkstra garante otimalidade em O((V+E) log V). A DP com memoization confirma o mesmo resultado via subsoluções reutilizadas — útil para demonstrar que o princípio de otimalidade de Bellman se aplica ao problema.

### Quando o Guloso falha?
O Cenário A demonstra claramente: o guloso escolhe Campinas→São Paulo (R$ 900, barato localmente) e depois precisa de São Paulo→BH (R$ 3600), totalizando R$ 6300 vs R$ 5200 da rota ótima.

### Alocação como Knapsack
A distribuição de carga entre trechos com restrições de capacidade é formulada como um Knapsack de minimização: "qual combinação de trechos absorve W toneladas com menor custo total?"

### Divide and Conquer
Aplicado como Merge Sort O(n log n) para ordenar trechos antes da análise, e como decomposição recursiva de cenários para processamento paralelo estrutural.

---

## Função de Custo Multi-critério

```python
custo_composto = 0.50 * (custo_reais / 1000)
               + 0.30 * tempo_horas
               + 0.20 * (risco_atraso * 100)
```

Os pesos são configuráveis via parâmetros da função `custo_composto()` em `grafo.py`.
