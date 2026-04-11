"""
dijkstra.py - Algoritmo de Dijkstra para caminho mínimo.

Implementa Dijkstra com heap binário (heapq) sobre o grafo
ponderado de rotas logísticas, respeitando restrições de
capacidade e usando função de custo composto multi-critério.
"""

from __future__ import annotations

import heapq
import math
from typing import Callable, Dict, List, Optional, Tuple

from grafo import Aresta, Grafo


def dijkstra(
    grafo: Grafo,
    origem: str,
    destino: str,
    funcao_custo: Optional[Callable[[Aresta], float]] = None,
    capacidade_minima: float = 0.0,
) -> Tuple[float, List[str], List[Aresta]]:
    """
    Encontra o caminho de menor custo entre origem e destino.

    Usa heap de mínimo para garantir O((V + E) log V) onde V = vértices
    e E = arestas.  A função de custo é injetável para permitir
    comparação entre estratégias (custo puro, tempo, custo composto etc.).

    Args:
        grafo:             grafo logístico já construído.
        origem:            nó de partida.
        destino:           nó de chegada.
        funcao_custo:      callable (Aresta) -> float.  Padrão: custo_composto.
        capacidade_minima: filtra arestas abaixo desta capacidade em toneladas.

    Returns:
        Tupla (custo_total, caminho_nos, caminho_arestas).
        custo_total = inf se destino inacessível.
    """
    if funcao_custo is None:
        funcao_custo = lambda a: a.custo_composto()

    # Destino não existe no grafo
    if destino not in grafo.nos:
        return math.inf, [], []

    # dist[no] = menor custo acumulado conhecido até 'no'
    dist: Dict[str, float] = {no: math.inf for no in grafo.nos}
    dist[origem] = 0.0

    # predecessores para reconstrução do caminho
    prev_no: Dict[str, Optional[str]] = {no: None for no in grafo.nos}
    prev_aresta: Dict[str, Optional[Aresta]] = {no: None for no in grafo.nos}

    # heap: (custo_acumulado, nó_atual)
    heap: List[Tuple[float, str]] = [(0.0, origem)]

    visitados: set = set()

    while heap:
        custo_atual, u = heapq.heappop(heap)

        if u in visitados:
            continue
        visitados.add(u)

        if u == destino:
            break

        for aresta in grafo.vizinhos(u):
            if aresta.capacidade_ton < capacidade_minima:
                continue  # restrição de capacidade

            v = aresta.destino
            novo_custo = custo_atual + funcao_custo(aresta)

            if novo_custo < dist[v]:
                dist[v] = novo_custo
                prev_no[v] = u
                prev_aresta[v] = aresta
                heapq.heappush(heap, (novo_custo, v))

    # Reconstrução do caminho
    caminho_nos: List[str] = []
    caminho_arestas: List[Aresta] = []

    if math.isinf(dist[destino]):
        return math.inf, [], []

    no = destino
    while no is not None:
        caminho_nos.append(no)
        if prev_aresta[no] is not None:
            caminho_arestas.append(prev_aresta[no])
        no = prev_no[no]

    caminho_nos.reverse()
    caminho_arestas.reverse()

    return dist[destino], caminho_nos, caminho_arestas


def resumo_caminho(
    custo: float,
    nos: List[str],
    arestas: List[Aresta],
) -> str:
    """Formata o resultado do Dijkstra para exibição."""
    if not nos:
        return "Caminho não encontrado."

    linhas = [
        f"Rota: {' → '.join(nos)}",
        f"Custo composto total: {custo:.4f}",
        f"Custo (R$): {sum(a.custo_reais for a in arestas):.2f}",
        f"Tempo total (h): {sum(a.tempo_horas for a in arestas):.1f}",
        f"Distância total (km): {sum(a.distancia_km for a in arestas):.0f}",
        f"Capacidade mínima (ton): {min(a.capacidade_ton for a in arestas):.0f}",
        "Trechos:",
    ]
    for a in arestas:
        linhas.append(
            f"  {a.origem} → {a.destino} | "
            f"R$ {a.custo_reais:.0f} | "
            f"{a.tempo_horas}h | "
            f"{a.tipo_trecho}"
        )
    return "\n".join(linhas)
