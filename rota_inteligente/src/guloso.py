"""
guloso.py - Abordagem Gulosa para caminho mínimo e alocação de carga.

Serve como baseline de comparação com a Programação Dinâmica.

A estratégia gulosa escolhe sempre o trecho de menor custo local
sem considerar consequências futuras — o que pode levar a soluções
sub-ótimas em grafos com armadilhas de custo.
"""

from __future__ import annotations

import math
from typing import List, Optional, Set, Tuple

from grafo import Aresta, Grafo


def guloso_caminho(
    grafo: Grafo,
    origem: str,
    destino: str,
    capacidade_minima: float = 0.0,
) -> Tuple[float, List[str], List[Aresta]]:
    """
    Busca gulosa: a cada passo escolhe o vizinho de menor custo local.

    NÃO garante otimalidade global — pode ficar preso em becos sem
    saída ou escolher caminhos mais longos por ganho local imediato.

    Args:
        grafo:             grafo logístico.
        origem:            nó de partida.
        destino:           nó de chegada.
        capacidade_minima: filtra arestas abaixo desta capacidade.

    Returns:
        (custo_total, lista_de_nos, lista_de_arestas)
        Retorna (inf, [], []) se o destino não for alcançado.
    """
    no_atual = origem
    visitados: Set[str] = {origem}
    caminho_nos: List[str] = [origem]
    caminho_arestas: List[Aresta] = []
    custo_total = 0.0

    while no_atual != destino:
        vizinhos = [
            a for a in grafo.vizinhos(no_atual)
            if a.destino not in visitados
            and a.capacidade_ton >= capacidade_minima
        ]

        if not vizinhos:
            # Sem saída: abordagem gulosa falhou
            return math.inf, [], []

        # Escolha gulosa: menor custo composto imediato
        melhor_aresta = min(vizinhos, key=lambda a: a.custo_composto())
        custo_total += melhor_aresta.custo_composto()
        caminho_arestas.append(melhor_aresta)
        no_atual = melhor_aresta.destino
        visitados.add(no_atual)
        caminho_nos.append(no_atual)

    return custo_total, caminho_nos, caminho_arestas


def guloso_alocacao(
    arestas_disponiveis: List[Aresta],
    carga_total: float,
) -> Tuple[float, List[Tuple[Aresta, float]]]:
    """
    Alocação gulosa: preenche os trechos em ordem crescente de custo
    por tonelada até esgotar a carga total.

    Args:
        arestas_disponiveis: trechos candidatos para alocação.
        carga_total:         carga total em toneladas.

    Returns:
        (custo_total, [(aresta, carga_alocada), ...])
    """
    # Ordena trechos por custo por tonelada (menor primeiro)
    ordenados = sorted(
        arestas_disponiveis,
        key=lambda a: a.custo_reais / a.capacidade_ton,
    )

    restante = carga_total
    alocacao: List[Tuple[Aresta, float]] = []
    custo_total = 0.0

    for aresta in ordenados:
        if restante <= 0:
            break
        carga = min(aresta.capacidade_ton, restante)
        custo = aresta.custo_reais * (carga / aresta.capacidade_ton)
        custo += aresta.perda_percentual * carga
        alocacao.append((aresta, carga))
        custo_total += custo
        restante -= carga

    if restante > 0:
        custo_total = math.inf  # carga não totalmente alocada

    return custo_total, alocacao
