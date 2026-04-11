"""
dp.py - Programação Dinâmica para alocação de carga.

Implementa dois subproblemas:

1. dp_caminho_minimo: menor custo origem→destino com memoization
   (top-down, recursão + cache).  Demonstra reutilização de subsoluções
   em oposição à busca ingênua.

2. dp_alocacao_carga: knapsack adaptado para distribuição de carga
   entre múltiplos trechos com restrição de capacidade e minimização
   de custo+penalidade (bottom-up com tabela).
"""

from __future__ import annotations

import math
from functools import lru_cache
from typing import Dict, List, Optional, Tuple

from grafo import Aresta, Grafo


# ---------------------------------------------------------------------------
# 1. Caminho mínimo com memoization (top-down DP)
# ---------------------------------------------------------------------------

def dp_caminho_minimo(
    grafo: Grafo,
    origem: str,
    destino: str,
    capacidade_minima: float = 0.0,
) -> Tuple[float, List[str]]:
    """
    Calcula o caminho de menor custo usando DP top-down com memoization.

    A cada chamada recursiva dp(no) responde: "qual o menor custo de
    'no' até 'destino'?".  Subsoluções são guardadas em memo[] para
    evitar recomputações — técnica central de Programação Dinâmica.

    Complexidade: O(V * E) no pior caso, onde V = nós e E = arestas.

    Args:
        grafo:             grafo logístico.
        origem:            nó de partida.
        destino:           nó de chegada.
        capacidade_minima: filtra arestas abaixo desta capacidade (ton).

    Returns:
        (custo_total, lista_de_nos_no_caminho)
    """
    memo: Dict[str, float] = {}
    prev: Dict[str, Optional[str]] = {}

    def dp(no: str, visitados: frozenset) -> float:
        """Retorna menor custo de 'no' até 'destino'."""
        if no == destino:
            return 0.0

        # Cache hit — reutiliza subsolução já computada
        if no in memo:
            return memo[no]

        melhor = math.inf

        for aresta in grafo.vizinhos(no):
            prox = aresta.destino
            if prox in visitados:
                continue  # evita ciclos
            if aresta.capacidade_ton < capacidade_minima:
                continue

            custo_trecho = aresta.custo_composto()
            custo_resto = dp(prox, visitados | {prox})
            custo_total = custo_trecho + custo_resto

            if custo_total < melhor:
                melhor = custo_total
                prev[no] = prox

        memo[no] = melhor
        return melhor

    custo = dp(origem, frozenset({origem}))

    # Reconstrução do caminho a partir de prev[]
    caminho = [origem]
    no = origem
    while no != destino and no in prev:
        no = prev[no]
        caminho.append(no)

    if caminho[-1] != destino:
        return math.inf, []

    return custo, caminho


# ---------------------------------------------------------------------------
# 2. Alocação de carga — Knapsack adaptado (bottom-up DP)
# ---------------------------------------------------------------------------

def dp_alocacao_carga(
    arestas_disponiveis: List[Aresta],
    carga_total: float,
    granularidade: float = 1.0,
) -> Tuple[float, List[Tuple[Aresta, float]]]:
    """
    Distribui carga_total entre os trechos disponíveis minimizando
    custo + penalidades de perda.

    Modela o problema como um Knapsack de minimização de custo:
    - "itens" = trechos (arestas)
    - "peso"  = carga alocada (variável contínua discretizada)
    - "valor" = custo_reais * fracao + perda_percentual * carga

    A tabela DP bottom-up tem dimensão [len(trechos)+1][capacidade+1].

    Args:
        arestas_disponiveis: lista de trechos candidatos.
        carga_total:         carga em toneladas a ser distribuída.
        granularidade:       passo de discretização em toneladas (padrão 1 ton).

    Returns:
        (custo_total_alocacao, [(aresta, carga_alocada), ...])
    """
    # Discretiza a carga para indexação inteira
    W = int(carga_total / granularidade)
    n = len(arestas_disponiveis)

    # dp[i][w] = menor custo usando os primeiros i trechos com w unidades de carga
    INF = float("inf")
    dp_table = [[INF] * (W + 1) for _ in range(n + 1)]
    dp_table[0][0] = 0.0

    # Propaga capacidades: cada trecho pode receber 0..cap_i unidades
    for i in range(1, n + 1):
        aresta = arestas_disponiveis[i - 1]
        cap_i = int(aresta.capacidade_ton / granularidade)

        for w in range(W + 1):
            # Opção 1: não aloca nada neste trecho
            dp_table[i][w] = dp_table[i - 1][w]

            # Opção 2: aloca k unidades neste trecho
            for k in range(1, min(cap_i, w) + 1):
                carga_k = k * granularidade
                custo_k = (
                    aresta.custo_reais * (carga_k / aresta.capacidade_ton)
                    + aresta.perda_percentual * carga_k
                )
                anterior = dp_table[i - 1][w - k]
                if anterior < INF:
                    candidato = anterior + custo_k
                    if candidato < dp_table[i][w]:
                        dp_table[i][w] = candidato

    custo_otimo = dp_table[n][W]

    # Backtracking para descobrir quanto foi alocado em cada trecho
    alocacao: List[Tuple[Aresta, float]] = []
    w = W
    for i in range(n, 0, -1):
        aresta = arestas_disponiveis[i - 1]
        cap_i = int(aresta.capacidade_ton / granularidade)
        alocado = 0
        for k in range(1, min(cap_i, w) + 1):
            carga_k = k * granularidade
            custo_k = (
                aresta.custo_reais * (carga_k / aresta.capacidade_ton)
                + aresta.perda_percentual * carga_k
            )
            anterior = dp_table[i - 1][w - k]
            if anterior < INF and abs(anterior + custo_k - dp_table[i][w]) < 1e-6:
                alocado = k
        if alocado > 0:
            alocacao.append((aresta, alocado * granularidade))
            w -= alocado

    alocacao.reverse()
    return custo_otimo, alocacao


def resumo_alocacao(
    custo: float,
    alocacao: List[Tuple[Aresta, float]],
    carga_total: float,
) -> str:
    """Formata a saída da alocação DP."""
    linhas = [
        f"Carga total a distribuir: {carga_total} ton",
        f"Custo total de alocação:  R$ {custo:.2f}",
        "Distribuição por trecho:",
    ]
    alocado = 0.0
    for aresta, carga in alocacao:
        linhas.append(
            f"  {aresta.origem} → {aresta.destino}: "
            f"{carga:.1f} ton  (cap. {aresta.capacidade_ton} ton, "
            f"custo R$ {aresta.custo_reais:.0f})"
        )
        alocado += carga
    linhas.append(f"Total alocado: {alocado:.1f} / {carga_total} ton")
    return "\n".join(linhas)
