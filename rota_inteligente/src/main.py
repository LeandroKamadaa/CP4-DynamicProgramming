"""
main.py - Pipeline principal: Rota Inteligente Brasil.

Executa toda a análise logística para os três cenários (A, B, C):
  1. Carrega CSV e constrói grafos.
  2. Pré-processa com Divide and Conquer (ordenação Merge Sort).
  3. Encontra caminhos mínimos com Dijkstra.
  4. Aplica Programação Dinâmica (memoization e alocação de carga).
  5. Aplica abordagem Gulosa como baseline.
  6. Compara resultados e gera relatório + visualizações.

Uso:
    python main.py [--csv <caminho>] [--carga <toneladas>] [--cenario <A|B|C>]
"""

from __future__ import annotations

import argparse
import math
import os
import sys
import time

# Adiciona src/ ao path para importações relativas
sys.path.insert(0, os.path.dirname(__file__))

from grafo import carregar_csv
from dijkstra import dijkstra, resumo_caminho
from dp import dp_caminho_minimo, dp_alocacao_carga, resumo_alocacao
from guloso import guloso_caminho, guloso_alocacao
from divide_conquer import merge_sort_arestas, decompor_cenarios
from visualizacao import plotar_grafo, plotar_comparacao, plotar_mapa_calor_risco


# ---------------------------------------------------------------------------
# Pares origem→destino por cenário (baseados no CSV).
# ---------------------------------------------------------------------------
PARES_CENARIO = {
    "A": ("Ribeirao_Preto", "Belo_Horizonte"),
    "B": ("Sorriso_MT", "Santos"),
    "C": ("Petrolina", "Salvador"),
}


def executar_cenario(
    cenario_id: str,
    grafo,
    arestas_planas,
    carga_total: float,
    dir_saida: str,
) -> dict:
    """
    Executa todas as análises para um cenário e retorna métricas.

    Returns:
        dict com custos compostos de cada estratégia.
    """
    origem, destino = PARES_CENARIO[cenario_id]
    print(f"\n{'='*60}")
    print(f"  CENÁRIO {cenario_id}: {origem} → {destino}")
    print(f"{'='*60}")
    print(grafo.resumo())

    # ------------------------------------------------------------------
    # 1. Pré-processamento D&C: ordena arestas por custo
    # ------------------------------------------------------------------
    arestas_ordenadas = merge_sort_arestas(arestas_planas)
    print(f"\n[D&C] Merge Sort: {len(arestas_ordenadas)} arestas ordenadas.")
    print(f"  Mais barata: {arestas_ordenadas[0].origem} → "
          f"{arestas_ordenadas[0].destino} R$ {arestas_ordenadas[0].custo_reais:.0f}")

    resultados = {}

    # ------------------------------------------------------------------
    # 2. Dijkstra
    # ------------------------------------------------------------------
    t0 = time.perf_counter()
    custo_d, nos_d, arestas_d = dijkstra(grafo, origem, destino)
    t_d = time.perf_counter() - t0

    print(f"\n[DIJKSTRA] ({t_d*1000:.2f} ms)")
    print(resumo_caminho(custo_d, nos_d, arestas_d))
    resultados["Dijkstra"] = custo_d

    # ------------------------------------------------------------------
    # 3. DP top-down (memoization)
    # ------------------------------------------------------------------
    t0 = time.perf_counter()
    custo_dp, nos_dp = dp_caminho_minimo(grafo, origem, destino)
    t_dp = time.perf_counter() - t0

    print(f"\n[DP Memoization] ({t_dp*1000:.2f} ms)")
    print(f"Rota: {' → '.join(nos_dp)}")
    print(f"Custo composto: {custo_dp:.4f}")
    resultados["DP (memo)"] = custo_dp

    # ------------------------------------------------------------------
    # 4. Guloso
    # ------------------------------------------------------------------
    t0 = time.perf_counter()
    custo_g, nos_g, arestas_g = guloso_caminho(grafo, origem, destino)
    t_g = time.perf_counter() - t0

    print(f"\n[GULOSO] ({t_g*1000:.2f} ms)")
    if nos_g:
        print(resumo_caminho(custo_g, nos_g, arestas_g))
    else:
        print("  Abordagem gulosa não encontrou caminho (armadilha de custo local).")
    resultados["Guloso"] = custo_g if not math.isinf(custo_g) else 999

    # ------------------------------------------------------------------
    # 5. Comparação de tempo entre estratégias
    # ------------------------------------------------------------------
    print(f"\n[COMPARAÇÃO] Custo composto:")
    for estrategia, custo in resultados.items():
        diff = ""
        if estrategia != "Dijkstra" and not math.isinf(custo_d):
            delta = ((custo - custo_d) / custo_d) * 100
            diff = f"  ({delta:+.1f}% vs Dijkstra)"
        print(f"  {estrategia:15s}: {custo:.4f}{diff}")

    # ------------------------------------------------------------------
    # 6. Alocação de carga
    # ------------------------------------------------------------------
    print(f"\n[ALOCAÇÃO] Distribuindo {carga_total} ton nos trechos do caminho ótimo")
    if arestas_d:
        custo_aloc_dp, aloc_dp = dp_alocacao_carga(arestas_d, carga_total)
        print("[DP Knapsack]")
        print(resumo_alocacao(custo_aloc_dp, aloc_dp, carga_total))

        custo_aloc_g, aloc_g = guloso_alocacao(arestas_d, carga_total)
        print(f"\n[Guloso] Custo alocação: R$ {custo_aloc_g:.2f}")

    # ------------------------------------------------------------------
    # 7. Visualizações
    # ------------------------------------------------------------------
    rota_nos = nos_d if nos_d else nos_g
    plotar_grafo(
        grafo,
        titulo=f"Cenário {cenario_id}: {origem} → {destino}",
        caminho_destaque=rota_nos,
        salvar=os.path.join(dir_saida, f"grafo_cenario_{cenario_id}.png"),
    )
    plotar_mapa_calor_risco(
        arestas_planas,
        titulo=f"Risco vs Custo — Cenário {cenario_id}",
        salvar=os.path.join(dir_saida, f"risco_custo_cenario_{cenario_id}.png"),
    )

    return resultados


def main():
    parser = argparse.ArgumentParser(description="Rota Inteligente Brasil")
    parser.add_argument("--csv", default="../data/rotas_logisticas.csv")
    parser.add_argument("--carga", type=float, default=30.0, help="Carga em toneladas")
    parser.add_argument("--cenario", default=None, help="Filtrar cenário: A, B ou C")
    args = parser.parse_args()

    csv_path = os.path.join(os.path.dirname(__file__), args.csv)
    dir_saida = os.path.join(os.path.dirname(__file__), "../reports")
    os.makedirs(dir_saida, exist_ok=True)

    print("=" * 60)
    print("  ROTA INTELIGENTE BRASIL — Dynamic Programming FIAP")
    print("  Grupo: Cilas Macedo | Ian Matsushita | Pedro Baquini |")
    print("         Leandro Dimov")
    print("=" * 60)

    grafos = carregar_csv(csv_path, cenario=args.cenario)
    print(f"\nCenários carregados: {list(grafos.keys())}")

    # D&C estrutural: decompõe todos os cenários
    arestas_por_cenario = {
        sid: [a for ars in g.arestas.values() for a in ars]
        for sid, g in grafos.items()
    }
    decompostos = decompor_cenarios(arestas_por_cenario)
    print(f"\n[D&C] Cenários decompostos: {[d[0] for d in decompostos]}")

    # Executa análise por cenário
    todos_resultados = {}
    for sid, grafo in grafos.items():
        arestas_planas = [a for ars in grafo.arestas.values() for a in ars]
        todos_resultados[sid] = executar_cenario(
            sid, grafo, arestas_planas, args.carga, dir_saida
        )

    # Gráfico comparativo geral
    plotar_comparacao(
        todos_resultados,
        titulo="Comparação de Estratégias por Cenário",
        salvar=os.path.join(dir_saida, "comparacao_estrategias.png"),
    )

    print("\n✓ Análise concluída. Relatórios em:", dir_saida)


if __name__ == "__main__":
    main()
