"""
divide_conquer.py - Divide and Conquer para pré-processamento logístico.

Aplica a estratégia D&C em dois contextos:

1. merge_sort_arestas: ordenação das arestas por custo usando
   Merge Sort clássico (D&C puro, O(n log n)).

2. menor_custo_divisao: encontra o trecho de menor custo em uma
   lista de arestas dividindo recursivamente ao meio (D&C para
   redução de problema).

Estes módulos são usados como pré-processamento na pipeline principal,
permitindo que Dijkstra e DP operem sobre estruturas já ordenadas.
"""

from __future__ import annotations

from typing import Callable, List, Tuple

from grafo import Aresta


# ---------------------------------------------------------------------------
# 1. Merge Sort — ordenação de arestas por chave arbitrária
# ---------------------------------------------------------------------------

def merge_sort_arestas(
    arestas: List[Aresta],
    chave: Callable[[Aresta], float] = lambda a: a.custo_reais,
) -> List[Aresta]:
    """
    Ordena uma lista de arestas usando Merge Sort (Divide and Conquer).

    Divide a lista ao meio recursivamente até listas unitárias,
    depois mescla em ordem — garantindo estabilidade e O(n log n).

    Args:
        arestas: lista de arestas a ordenar.
        chave:   função de chave para comparação (padrão: custo_reais).

    Returns:
        Nova lista ordenada (não modifica a original).
    """
    if len(arestas) <= 1:
        return list(arestas)

    meio = len(arestas) // 2
    esquerda = merge_sort_arestas(arestas[:meio], chave)
    direita = merge_sort_arestas(arestas[meio:], chave)

    return _merge(esquerda, direita, chave)


def _merge(
    esq: List[Aresta],
    dir: List[Aresta],
    chave: Callable[[Aresta], float],
) -> List[Aresta]:
    """Mescla duas listas ordenadas em uma única lista ordenada."""
    resultado: List[Aresta] = []
    i = j = 0

    while i < len(esq) and j < len(dir):
        if chave(esq[i]) <= chave(dir[j]):
            resultado.append(esq[i])
            i += 1
        else:
            resultado.append(dir[j])
            j += 1

    resultado.extend(esq[i:])
    resultado.extend(dir[j:])
    return resultado


# ---------------------------------------------------------------------------
# 2. Menor custo por D&C — redução recursiva
# ---------------------------------------------------------------------------

def menor_custo_dc(
    arestas: List[Aresta],
    chave: Callable[[Aresta], float] = lambda a: a.custo_composto(),
) -> Aresta:
    """
    Encontra a aresta de menor custo usando divisão recursiva (D&C).

    Divide a lista ao meio, resolve cada metade recursivamente e
    combina escolhendo o melhor dos dois resultados.

    Complexidade: O(n) — mas demonstra o paradigma D&C claramente.

    Args:
        arestas: lista não vazia de arestas.
        chave:   função de custo.

    Returns:
        Aresta de menor custo segundo 'chave'.
    """
    if len(arestas) == 1:
        return arestas[0]

    meio = len(arestas) // 2
    melhor_esq = menor_custo_dc(arestas[:meio], chave)
    melhor_dir = menor_custo_dc(arestas[meio:], chave)

    return melhor_esq if chave(melhor_esq) <= chave(melhor_dir) else melhor_dir


# ---------------------------------------------------------------------------
# 3. Decomposição de cenários por D&C
# ---------------------------------------------------------------------------

def decompor_cenarios(
    arestas_por_cenario: dict,
) -> List[Tuple[str, List[Aresta], Aresta]]:
    """
    Processa múltiplos cenários dividindo-os e aplicando análise
    independente em cada subconjunto (D&C estrutural).

    Args:
        arestas_por_cenario: dict {scenario_id -> lista de arestas}.

    Returns:
        Lista de (scenario_id, arestas_ordenadas, aresta_mais_barata).
    """
    resultados = []
    ids = list(arestas_por_cenario.keys())

    def processar_intervalo(inicio: int, fim: int) -> None:
        """Divide os IDs de cenário e processa cada metade."""
        if inicio > fim:
            return
        if inicio == fim:
            sid = ids[inicio]
            arestas = arestas_por_cenario[sid]
            ordenadas = merge_sort_arestas(arestas)
            mais_barata = menor_custo_dc(arestas)
            resultados.append((sid, ordenadas, mais_barata))
            return
        meio = (inicio + fim) // 2
        processar_intervalo(inicio, meio)
        processar_intervalo(meio + 1, fim)

    processar_intervalo(0, len(ids) - 1)
    return resultados
