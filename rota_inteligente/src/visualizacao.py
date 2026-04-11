"""
visualizacao.py - Geração de figuras para análise logística.

Produz:
1. Grafo logístico com arestas coloridas por tipo de trecho.
2. Rota ótima destacada sobre o grafo.
3. Gráfico de barras comparando estratégias (Guloso vs DP vs Dijkstra).
4. Mapa de calor de risco × custo por trecho.
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple

import matplotlib
matplotlib.use("Agg")  # backend sem display
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
import numpy as np

from grafo import Aresta, Grafo


# Paleta de cores por tipo de trecho
CORES_MODAL = {
    "rodoviario": "#3498DB",
    "ferroviario": "#E67E22",
    "cabotagem":   "#2ECC71",
    "aereo":       "#9B59B6",
}
COR_PADRAO = "#95A5A6"


def _construir_nx(grafo: Grafo) -> nx.DiGraph:
    """Converte o Grafo interno em um DiGraph do NetworkX."""
    G = nx.DiGraph()
    for no in grafo.nos:
        G.add_node(no)
    for origem, arestas in grafo.arestas.items():
        for a in arestas:
            G.add_edge(
                a.origem, a.destino,
                weight=a.custo_composto(),
                custo=a.custo_reais,
                tempo=a.tempo_horas,
                tipo=a.tipo_trecho,
                capacidade=a.capacidade_ton,
                risco=a.risco_atraso,
                perda=a.perda_percentual,
            )
    return G


def plotar_grafo(
    grafo: Grafo,
    titulo: str = "Malha Logística",
    caminho_destaque: Optional[List[str]] = None,
    salvar: Optional[str] = None,
) -> None:
    """
    Plota o grafo logístico com arestas coloridas por modal.

    Args:
        grafo:             grafo a visualizar.
        titulo:            título do gráfico.
        caminho_destaque:  lista de nós que formam a rota ótima.
        salvar:            caminho de arquivo para salvar (PNG/PDF).
    """
    G = _construir_nx(grafo)

    fig, ax = plt.subplots(figsize=(12, 8))

    # Layout spring para grafos pequenos
    pos = nx.spring_layout(G, seed=42, k=2.5)

    # Colorir arestas por tipo de modal
    edge_colors = []
    edge_widths = []
    arestas_rota = set()
    if caminho_destaque:
        for i in range(len(caminho_destaque) - 1):
            arestas_rota.add((caminho_destaque[i], caminho_destaque[i + 1]))

    for u, v, data in G.edges(data=True):
        cor = CORES_MODAL.get(data.get("tipo", ""), COR_PADRAO)
        if (u, v) in arestas_rota:
            edge_colors.append("#E74C3C")  # vermelho = rota ótima
            edge_widths.append(4.0)
        else:
            edge_colors.append(cor)
            edge_widths.append(1.5)

    nx.draw_networkx_edges(
        G, pos, ax=ax,
        edge_color=edge_colors, width=edge_widths,
        arrows=True, arrowsize=15, connectionstyle="arc3,rad=0.1",
    )
    nx.draw_networkx_nodes(
        G, pos, ax=ax,
        node_color="#2C3E50", node_size=600, alpha=0.9,
    )

    # Destacar nós da rota
    if caminho_destaque:
        nx.draw_networkx_nodes(
            G, pos, ax=ax,
            nodelist=caminho_destaque,
            node_color="#E74C3C", node_size=800,
        )

    # Rótulos dos nós (quebra sublinhado para legibilidade)
    labels = {n: n.replace("_", "\n") for n in G.nodes()}
    nx.draw_networkx_labels(G, pos, labels, ax=ax, font_size=7, font_color="white")

    # Rótulos de custo nas arestas
    edge_labels = {
        (u, v): f"R${d['custo']:.0f}\n{d['tempo']}h"
        for u, v, d in G.edges(data=True)
    }
    nx.draw_networkx_edge_labels(
        G, pos, edge_labels, ax=ax, font_size=6, label_pos=0.35,
    )

    # Legenda de modais
    patches = [
        mpatches.Patch(color=c, label=m.capitalize())
        for m, c in CORES_MODAL.items()
    ]
    patches.append(mpatches.Patch(color="#E74C3C", label="Rota ótima"))
    ax.legend(handles=patches, loc="upper left", fontsize=8)

    ax.set_title(titulo, fontsize=14, fontweight="bold", pad=15)
    ax.axis("off")
    plt.tight_layout()

    if salvar:
        plt.savefig(salvar, dpi=150, bbox_inches="tight")
        print(f"Grafo salvo: {salvar}")
    else:
        plt.show()
    plt.close()


def plotar_comparacao(
    resultados: Dict[str, Dict[str, float]],
    titulo: str = "Comparação de Estratégias",
    salvar: Optional[str] = None,
) -> None:
    """
    Gráfico de barras comparando custo composto por estratégia.

    Args:
        resultados: {cenario -> {estrategia -> custo_composto}}
        titulo:     título do gráfico.
        salvar:     caminho para salvar.
    """
    cenarios = list(resultados.keys())
    estrategias = list(next(iter(resultados.values())).keys())
    x = np.arange(len(cenarios))
    largura = 0.25
    cores_barra = ["#3498DB", "#E67E22", "#2ECC71"]

    fig, ax = plt.subplots(figsize=(10, 6))

    for i, (estrategia, cor) in enumerate(zip(estrategias, cores_barra)):
        valores = [resultados[c].get(estrategia, 0) for c in cenarios]
        bars = ax.bar(x + i * largura, valores, largura, label=estrategia, color=cor, alpha=0.85)
        for bar, v in zip(bars, valores):
            if v < math.inf and v > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height() + 0.02,
                    f"{v:.2f}",
                    ha="center", va="bottom", fontsize=8,
                )

    ax.set_xlabel("Cenário", fontsize=11)
    ax.set_ylabel("Custo Composto", fontsize=11)
    ax.set_title(titulo, fontsize=13, fontweight="bold")
    ax.set_xticks(x + largura)
    ax.set_xticklabels([f"Cenário {c}" for c in cenarios])
    ax.legend(fontsize=9)
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()

    if salvar:
        plt.savefig(salvar, dpi=150, bbox_inches="tight")
        print(f"Comparação salva: {salvar}")
    else:
        plt.show()
    plt.close()


def plotar_mapa_calor_risco(
    arestas: List[Aresta],
    titulo: str = "Risco vs Custo por Trecho",
    salvar: Optional[str] = None,
) -> None:
    """
    Scatter plot risco × custo com capacidade como tamanho do ponto.

    Args:
        arestas: lista de arestas a analisar.
        titulo:  título do gráfico.
        salvar:  caminho para salvar.
    """
    fig, ax = plt.subplots(figsize=(9, 6))

    for a in arestas:
        cor = CORES_MODAL.get(a.tipo_trecho, COR_PADRAO)
        ax.scatter(
            a.custo_reais, a.risco_atraso,
            s=a.capacidade_ton * 5,
            color=cor, alpha=0.7, edgecolors="white", linewidth=0.5,
        )
        ax.annotate(
            f"{a.origem[:3]}→{a.destino[:3]}",
            (a.custo_reais, a.risco_atraso),
            fontsize=7, ha="center", va="bottom",
        )

    ax.set_xlabel("Custo (R$)", fontsize=11)
    ax.set_ylabel("Risco de Atraso", fontsize=11)
    ax.set_title(titulo, fontsize=13, fontweight="bold")
    ax.grid(alpha=0.3)

    patches = [
        mpatches.Patch(color=c, label=m.capitalize())
        for m, c in CORES_MODAL.items()
        if any(a.tipo_trecho == m for a in arestas)
    ]
    ax.legend(handles=patches, fontsize=8)
    plt.tight_layout()

    if salvar:
        plt.savefig(salvar, dpi=150, bbox_inches="tight")
        print(f"Mapa de calor salvo: {salvar}")
    else:
        plt.show()
    plt.close()
