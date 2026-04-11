"""
test_algoritmos.py - Testes automatizados para os módulos principais.

Cobre:
- Construção do grafo a partir de dados mock.
- Dijkstra: caminho ótimo e restrição de capacidade.
- DP memoization: consistência com Dijkstra.
- Guloso: falha esperada em armadilha de custo.
- Merge Sort (D&C): ordenação correta.
- Alocação DP Knapsack: carga distribuída corretamente.
"""

import math
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../src"))

from grafo import Aresta, Grafo
from dijkstra import dijkstra
from dp import dp_caminho_minimo, dp_alocacao_carga
from guloso import guloso_caminho, guloso_alocacao
from divide_conquer import merge_sort_arestas, menor_custo_dc


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def criar_grafo_simples() -> Grafo:
    """
    Grafo triangular: A→B→C e A→C (mais longo direto).
    Caminho ótimo: A→B→C (custo menor que A→C direto).
    """
    g = Grafo()
    g.adicionar_aresta(Aresta("A", "B", 100, 1000, 2.0, 20, 0.1, 0.5, "rodoviario"))
    g.adicionar_aresta(Aresta("B", "C", 100, 1000, 2.0, 20, 0.1, 0.5, "rodoviario"))
    g.adicionar_aresta(Aresta("A", "C", 300, 5000, 8.0, 10, 0.3, 1.0, "rodoviario"))
    return g


def criar_grafo_armadilha() -> Grafo:
    """
    Grafo onde o guloso falha:
    A→B (barato), mas B→C não existe.
    A→C existe, mas o guloso escolhe A→B primeiro e fica preso.
    """
    g = Grafo()
    g.adicionar_aresta(Aresta("A", "B", 10, 100, 1.0, 20, 0.05, 0.2, "rodoviario"))
    g.adicionar_aresta(Aresta("A", "C", 200, 3000, 5.0, 20, 0.1, 0.5, "rodoviario"))
    # B não tem saída para C → guloso fica preso
    return g


# ---------------------------------------------------------------------------
# Testes de Dijkstra
# ---------------------------------------------------------------------------

def test_dijkstra_caminho_simples():
    """Dijkstra deve preferir A→B→C ao invés de A→C direto."""
    g = criar_grafo_simples()
    custo, nos, arestas = dijkstra(g, "A", "C")
    assert nos == ["A", "B", "C"], f"Caminho esperado A→B→C, obtido {nos}"
    assert custo < math.inf, "Custo deve ser finito"
    print("✓ test_dijkstra_caminho_simples")


def test_dijkstra_destino_inacessivel():
    """Dijkstra deve retornar inf quando destino não é acessível."""
    g = Grafo()
    g.adicionar_aresta(Aresta("A", "B", 100, 1000, 2.0, 20, 0.1, 0.5, "rodoviario"))
    custo, nos, arestas = dijkstra(g, "A", "Z")
    assert math.isinf(custo), "Custo deve ser inf para destino inacessível"
    assert nos == [], "Lista de nós deve estar vazia"
    print("✓ test_dijkstra_destino_inacessivel")


def test_dijkstra_restricao_capacidade():
    """Dijkstra deve ignorar arestas abaixo da capacidade mínima."""
    g = criar_grafo_simples()
    # A→B→C tem capacidade 20, A→C tem capacidade 10
    # Com min_cap=15, apenas A→B→C é válido
    custo, nos, arestas = dijkstra(g, "A", "C", capacidade_minima=15.0)
    assert nos == ["A", "B", "C"], f"Com restrição, deve usar A→B→C. Obtido: {nos}"
    print("✓ test_dijkstra_restricao_capacidade")


# ---------------------------------------------------------------------------
# Testes de DP
# ---------------------------------------------------------------------------

def test_dp_consistente_com_dijkstra():
    """DP memoization deve encontrar rota de custo equivalente ao Dijkstra."""
    g = criar_grafo_simples()
    custo_d, nos_d, _ = dijkstra(g, "A", "C")
    custo_dp, nos_dp = dp_caminho_minimo(g, "A", "C")
    assert abs(custo_dp - custo_d) < 1e-6, (
        f"DP ({custo_dp:.4f}) deve ser igual a Dijkstra ({custo_d:.4f})"
    )
    print("✓ test_dp_consistente_com_dijkstra")


def test_dp_sem_caminho():
    """DP deve retornar inf quando não há caminho."""
    g = criar_grafo_armadilha()
    custo, nos = dp_caminho_minimo(g, "B", "C")
    assert math.isinf(custo), "Deve retornar inf para B→C sem saída"
    print("✓ test_dp_sem_caminho")


# ---------------------------------------------------------------------------
# Testes de Guloso
# ---------------------------------------------------------------------------

def test_guloso_armadilha():
    """Guloso deve falhar na armadilha onde B não tem saída para C."""
    g = criar_grafo_armadilha()
    custo, nos, arestas = guloso_caminho(g, "A", "C")
    assert math.isinf(custo), "Guloso deve falhar (armadilha de custo local)"
    print("✓ test_guloso_armadilha (falha esperada confirmada)")


# ---------------------------------------------------------------------------
# Testes de D&C (Merge Sort)
# ---------------------------------------------------------------------------

def test_merge_sort_ordenado():
    """Merge Sort deve ordenar arestas por custo crescente."""
    arestas = [
        Aresta("X", "Y", 100, 3000, 2.0, 20, 0.1, 0.5, "rodoviario"),
        Aresta("A", "B", 200, 1000, 3.0, 15, 0.2, 0.7, "rodoviario"),
        Aresta("C", "D", 150, 2000, 4.0, 18, 0.15, 0.6, "ferroviario"),
    ]
    ordenadas = merge_sort_arestas(arestas, chave=lambda a: a.custo_reais)
    custos = [a.custo_reais for a in ordenadas]
    assert custos == sorted(custos), f"Esperava ordenado, obteve {custos}"
    print("✓ test_merge_sort_ordenado")


def test_menor_custo_dc():
    """D&C deve identificar aresta de menor custo composto."""
    arestas = [
        Aresta("X", "Y", 100, 5000, 10.0, 20, 0.3, 1.0, "rodoviario"),
        Aresta("A", "B", 50, 500, 1.0, 20, 0.05, 0.2, "rodoviario"),  # mais barata
        Aresta("C", "D", 200, 3000, 5.0, 18, 0.2, 0.7, "ferroviario"),
    ]
    mais_barata = menor_custo_dc(arestas)
    assert mais_barata.origem == "A", f"Esperava A→B, obteve {mais_barata.origem}"
    print("✓ test_menor_custo_dc")


# ---------------------------------------------------------------------------
# Testes de Alocação de Carga
# ---------------------------------------------------------------------------

def test_alocacao_dp_distribui_carga():
    """DP Knapsack deve alocar carga total entre os trechos."""
    arestas = [
        Aresta("A", "B", 100, 1000, 2.0, 15, 0.1, 0.5, "rodoviario"),
        Aresta("B", "C", 100, 1200, 3.0, 20, 0.1, 0.4, "rodoviario"),
    ]
    custo, alocacao = dp_alocacao_carga(arestas, carga_total=20.0)
    total_alocado = sum(c for _, c in alocacao)
    assert abs(total_alocado - 20.0) < 1.0, (
        f"Esperava ~20 ton alocadas, obteve {total_alocado}"
    )
    print(f"✓ test_alocacao_dp_distribui_carga (custo R$ {custo:.2f})")


def test_alocacao_gulosa_mais_barata_primeiro():
    """Guloso deve alocar no trecho mais barato por tonelada primeiro."""
    arestas = [
        Aresta("A", "B", 100, 2000, 2.0, 20, 0.1, 0.5, "rodoviario"),  # 100/ton
        Aresta("C", "D", 200, 500, 3.0, 25, 0.1, 0.3, "rodoviario"),   # 20/ton ← mais barato
    ]
    custo, alocacao = guloso_alocacao(arestas, carga_total=10.0)
    primeiro_trecho = alocacao[0][0]
    assert primeiro_trecho.origem == "C", "Guloso deve alocar no trecho C→D primeiro"
    print("✓ test_alocacao_gulosa_mais_barata_primeiro")


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    testes = [
        test_dijkstra_caminho_simples,
        test_dijkstra_destino_inacessivel,
        test_dijkstra_restricao_capacidade,
        test_dp_consistente_com_dijkstra,
        test_dp_sem_caminho,
        test_guloso_armadilha,
        test_merge_sort_ordenado,
        test_menor_custo_dc,
        test_alocacao_dp_distribui_carga,
        test_alocacao_gulosa_mais_barata_primeiro,
    ]

    falhas = 0
    for teste in testes:
        try:
            teste()
        except Exception as e:
            print(f"✗ {teste.__name__}: {e}")
            falhas += 1

    print(f"\n{len(testes)-falhas}/{len(testes)} testes passaram.")
    sys.exit(falhas)
