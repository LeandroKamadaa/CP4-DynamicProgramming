"""
grafo.py - Modelagem da malha logística como grafo ponderado.

Lê o CSV de rotas e constrói uma representação de grafo com
suporte a múltiplos cenários e funções de custo customizáveis.
"""

from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


@dataclass
class Aresta:
    """Representa um trecho (aresta) da malha logística."""
    origem: str
    destino: str
    distancia_km: float
    custo_reais: float
    tempo_horas: float
    capacidade_ton: float
    risco_atraso: float
    perda_percentual: float
    tipo_trecho: str

    def custo_composto(
        self,
        peso_custo: float = 0.5,
        peso_tempo: float = 0.3,
        peso_risco: float = 0.2,
    ) -> float:
        """
        Função de custo multi-critério normalizada.

        Combina custo financeiro, tempo e risco em um único escalar
        para permitir comparação uniforme entre algoritmos.

        Args:
            peso_custo:  participação do custo monetário (padrão 0.50).
            peso_tempo:  participação do tempo de trânsito (padrão 0.30).
            peso_risco:  participação do risco de atraso (padrão 0.20).

        Returns:
            Valor escalar de custo composto da aresta.
        """
        custo_norm = self.custo_reais / 1000.0       # escala ~1-10
        tempo_norm = self.tempo_horas / 1.0           # horas diretas
        risco_norm = self.risco_atraso * 100.0        # 0-100 escala
        return (
            peso_custo * custo_norm
            + peso_tempo * tempo_norm
            + peso_risco * risco_norm
        )

    def penalidade(self) -> float:
        """Penalidade por perda de carga no trecho (%)."""
        return self.perda_percentual


@dataclass
class Grafo:
    """
    Grafo direcionado ponderado da malha logística.

    Atributos:
        nos:    conjunto de nós (cidades/polos) presentes no grafo.
        arestas: dict de listas de arestas agrupadas por nó de origem.
    """
    nos: set = field(default_factory=set)
    arestas: Dict[str, List[Aresta]] = field(default_factory=lambda: defaultdict(list))

    def adicionar_aresta(self, aresta: Aresta) -> None:
        """Insere uma aresta no grafo (grafo dirigido)."""
        self.nos.add(aresta.origem)
        self.nos.add(aresta.destino)
        self.arestas[aresta.origem].append(aresta)

    def vizinhos(self, no: str) -> List[Aresta]:
        """Retorna todas as arestas que partem do nó informado."""
        return self.arestas.get(no, [])

    def resumo(self) -> str:
        total_arestas = sum(len(v) for v in self.arestas.values())
        return (
            f"Grafo: {len(self.nos)} nós, {total_arestas} arestas"
        )


def carregar_csv(caminho: str, cenario: Optional[str] = None) -> Dict[str, Grafo]:
    """
    Lê o arquivo CSV e constrói grafos por cenário.

    Args:
        caminho:  caminho para o arquivo CSV.
        cenario:  se informado, carrega apenas aquele cenário ('A', 'B' ou 'C').

    Returns:
        Dicionário {scenario_id -> Grafo}.
    """
    grafos: Dict[str, Grafo] = {}

    with open(caminho, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sid = row["scenario_id"].strip()
            if cenario and sid != cenario:
                continue
            if sid not in grafos:
                grafos[sid] = Grafo()

            aresta = Aresta(
                origem=row["origem"].strip(),
                destino=row["destino"].strip(),
                distancia_km=float(row["distancia_km"]),
                custo_reais=float(row["custo_reais"]),
                tempo_horas=float(row["tempo_horas"]),
                capacidade_ton=float(row["capacidade_ton"]),
                risco_atraso=float(row["risco_atraso"]),
                perda_percentual=float(row["perda_percentual"]),
                tipo_trecho=row["tipo_trecho"].strip(),
            )
            grafos[sid].adicionar_aresta(aresta)

    return grafos
