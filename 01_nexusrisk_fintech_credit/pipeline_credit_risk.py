#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Projeto: NexusRisk - Otimização de Carteira de Crédito e Mitigação de Inadimplência D90+
Segmento: Fintech & Bancos Digitais (Crédito PF & Meios de Pagamento)
Autor: Wendell Barbosa Costa (Portfólio de Data Analytics)
Norma: PEP 8 Compliant, Type Annotations e Docstrings Executivas

Descrição:
    Este script orquestra a ingestão, feature engineering, análise exploratória
    e modelagem de regras de negócio para diagnóstico de risco de crédito,
    respondendo a 3 perguntas críticas de negócio e calculando provisões PCLD
    conforme a Resolução CMN/BACEN nº 2.682.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns


# =============================================================================
# 1. CONFIGURAÇÕES GLOBAIS E ESTILO PEP 8
# =============================================================================

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8


@dataclass(frozen=True)
class RegrasNegocioBacen:
    """Parâmetros regulatórios de provisão BACEN (Resolução CMN nº 2.682)."""

    ALÍQUOTAS_PCLD: Dict[str, float] = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "ALÍQUOTAS_PCLD",
            {
                "AA": 0.000,
                "A": 0.005,
                "B": 0.010,
                "C": 0.030,
                "D": 0.100,
                "E": 0.300,
                "F": 0.500,
                "G": 0.700,
                "H": 1.000,
            },
        )


REGRAS_BACEN = RegrasNegocioBacen()


# =============================================================================
# 2. GERAÇÃO E INGESTÃO DE DADOS SINTÉTICOS REALISTAS
# =============================================================================

def gerar_dataset_carteira_credito(
    n_registros: int = 1000, random_seed: int = 42
) -> pd.DataFrame:
    """Gera um conjunto de dados simulado e balanceado de uma carteira de crédito.

    Args:
        n_registros: Quantidade de clientes na carteira.
        random_seed: Semente pseudoaleatória para reprodutibilidade estrita.

    Returns:
        pd.DataFrame com colunas cadastrais, financeiras e comportamentais.
    """
    np.random.seed(random_seed)

    canais = [
        "Organico",
        "Trafego Pago",
        "Parcerias & Afiliados",
        "Member-get-Member",
    ]
    prob_canais = [0.28, 0.35, 0.22, 0.15]

    produtos = ["Cartão de Crédito", "Empréstimo Pessoal", "Cheque Especial"]
    prob_produtos = [0.65, 0.25, 0.10]

    cliente_ids = [f"CLI-{str(i).zfill(6)}" for i in range(1, n_registros + 1)]
    canais_atribuidos = np.random.choice(canais, size=n_registros, p=prob_canais)
    produtos_atribuidos = np.random.choice(
        produtos, size=n_registros, p=prob_produtos
    )

    scores_baixo = np.random.normal(loc=480, scale=60, size=int(n_registros * 0.3))
    scores_alto = np.random.normal(loc=720, scale=75, size=int(n_registros * 0.7))
    scores = np.concatenate([scores_baixo, scores_alto])
    np.random.shuffle(scores)
    scores = np.clip(np.round(scores), 300, 950).astype(int)

    rendas = np.round(
        np.exp(np.random.normal(loc=8.0, scale=0.55, size=n_registros))
        + (scores * 2.5),
        2,
    )
    rendas = np.clip(rendas, 1412.0, 35000.0)

    limites = []
    for canal, score, renda in zip(canais_atribuidos, scores, rendas):
        multiplicador = 0.5
        if canal == "Parcerias & Afiliados":
            multiplicador = 0.95
        elif canal == "Trafego Pago":
            multiplicador = 0.75
        elif score >= 750:
            multiplicador = 0.85
        elif score < 550:
            multiplicador = 0.35

        limite = renda * multiplicador * np.random.uniform(0.7, 1.4)
        limites.append(round(max(500.0, min(limite, 50000.0)), 2))

    limites_arr = np.array(limites)
    utilizacao = np.random.uniform(0.35, 0.98, size=n_registros)
    saldos_devedores = np.round(limites_arr * utilizacao, 2)

    dias_atraso = []
    for canal, score, limite, renda in zip(
        canais_atribuidos, scores, limites_arr, rendas
    ):
        dti = limite / renda
        prob_default = 0.05

        if canal == "Parcerias & Afiliados":
            prob_default += 0.18
        if score < 550:
            prob_default += 0.22
        if dti > 0.8:
            prob_default += 0.15

        prob_default = min(0.85, prob_default)

        if np.random.rand() < prob_default:
            atraso = int(np.random.choice([20, 45, 75, 115, 180, 240], p=[0.2, 0.2, 0.15, 0.25, 0.1, 0.1]))
        else:
            atraso = 0

        dias_atraso.append(atraso)

    taxas_juros_mensal = np.where(
        scores >= 750, 0.029, np.where(scores >= 600, 0.045, 0.079)
    )

    meses_relacionamento = np.random.randint(1, 48, size=n_registros)

    df = pd.DataFrame(
        {
            "id_cliente": cliente_ids,
            "canal_aquisicao": canais_atribuidos,
            "produto": produtos_atribuidos,
            "score_credito": scores,
            "renda_mensal": rendas,
            "limite_concedido": limites_arr,
            "saldo_devedor": saldos_devedores,
            "dias_atraso": dias_atraso,
            "taxa_juros_mensal": taxas_juros_mensal,
            "meses_relacionamento": meses_relacionamento,
        }
    )

    return df


# =============================================================================
# 3. FEATURE ENGINEERING & REGRAS DE NEGÓCIO
# =============================================================================

def aplicar_feature_engineering(df: pd.DataFrame) -> pd.DataFrame:
    """Enriquece o DataFrame com métricas regulatórias, DTI e buckets de atraso."""
    df_feat = df.copy()

    df_feat["dti"] = (
        df_feat["limite_concedido"] / df_feat["renda_mensal"]
    ).round(3)

    condicoes_score = [
        df_feat["score_credito"] < 550,
        (df_feat["score_credito"] >= 550) & (df_feat["score_credito"] < 700),
        (df_feat["score_credito"] >= 700) & (df_feat["score_credito"] < 850),
        df_feat["score_credito"] >= 850,
    ]
    rotulos_score = [
        "Baixo (<550)",
        "Médio (550-699)",
        "Alto (700-849)",
        "Excelente (>=850)",
    ]
    df_feat["faixa_score"] = np.select(
        condicoes_score, rotulos_score, default="Indefinido"
    )

    condicoes_renda = [
        df_feat["renda_mensal"] <= 2500,
        (df_feat["renda_mensal"] > 2500) & (df_feat["renda_mensal"] <= 5000),
        (df_feat["renda_mensal"] > 5000) & (df_feat["renda_mensal"] <= 10000),
        df_feat["renda_mensal"] > 10000,
    ]
    rotulos_renda = [
        "Até R$ 2.500",
        "R$ 2.501 - R$ 5.000",
        "R$ 5.001 - R$ 10.000",
        "Acima de R$ 10.000",
    ]
    df_feat["faixa_renda"] = np.select(
        condicoes_renda, rotulos_renda, default="Indefinido"
    )

    condicoes_atraso = [
        df_feat["dias_atraso"] == 0,
        (df_feat["dias_atraso"] >= 1) & (df_feat["dias_atraso"] <= 15),
        (df_feat["dias_atraso"] >= 16) & (df_feat["dias_atraso"] <= 60),
        (df_feat["dias_atraso"] >= 61) & (df_feat["dias_atraso"] <= 90),
        df_feat["dias_atraso"] > 90,
    ]
    rotulos_atraso = [
        "Em Dia (D0)",
        "Atraso Leve (D1-D15)",
        "Alerta (D16-D60)",
        "Crítico (D61-D90)",
        "Inadimplente (D90+)",
    ]
    df_feat["status_cobranca"] = np.select(
        condicoes_atraso, rotulos_atraso, default="Indefinido"
    )

    df_feat["flag_d90"] = (df_feat["dias_atraso"] > 90).astype(int)

    def definir_rating(row: pd.Series) -> str:
        dias = row["dias_atraso"]
        score = row["score_credito"]
        if dias > 180:
            return "H"
        if dias > 120:
            return "G"
        if dias > 90:
            return "F"
        if dias > 60:
            return "E"
        if dias > 30:
            return "D"
        if dias > 15:
            return "C"
        if dias > 0:
            return "B"
        if score >= 750:
            return "AA"
        if score >= 600:
            return "A"
        return "B"

    df_feat["rating_bacen"] = df_feat.apply(definir_rating, axis=1)

    df_feat["aliquota_pcld"] = df_feat["rating_bacen"].map(
        REGRAS_BACEN.ALÍQUOTAS_PCLD
    )
    df_feat["pcld_reais"] = (
        df_feat["saldo_devedor"] * df_feat["aliquota_pcld"]
    ).round(2)

    return df_feat


# =============================================================================
# 4. STORYTELLING & RESPOSTA ÀS 3 PERGUNTAS CRÍTICAS DE NEGÓCIO
# =============================================================================

def responder_pergunta_1(df: pd.DataFrame) -> pd.DataFrame:
    """Pergunta 1: Canal de aquisição e faixa de renda com maior taxa de default."""
    resumo_canal = (
        df.groupby(["canal_aquisicao", "faixa_renda"])
        .agg(
            total_clientes=("id_cliente", "count"),
            volume_carteira=("saldo_devedor", "sum"),
            inadimplentes_d90=("flag_d90", "sum"),
            pcld_acumulado=("pcld_reais", "sum"),
        )
        .reset_index()
    )

    resumo_canal["taxa_default_pct"] = (
        (resumo_canal["inadimplentes_d90"] / resumo_canal["total_clientes"]) * 100
    ).round(2)

    return resumo_canal.sort_values(by="taxa_default_pct", ascending=False)


def responder_pergunta_2(df: pd.DataFrame) -> pd.DataFrame:
    """Pergunta 2: Calibração de limite e score na carteira."""
    resumo_calibracao = (
        df.groupby("faixa_score")
        .agg(
            clientes=("id_cliente", "count"),
            limite_medio=("limite_concedido", "mean"),
            renda_media=("renda_mensal", "mean"),
            dti_medio=("dti", "mean"),
            taxa_default_pct=("flag_d90", "mean"),
            pcld_total=("pcld_reais", "sum"),
        )
        .reset_index()
    )

    resumo_calibracao["taxa_default_pct"] = (
        resumo_calibracao["taxa_default_pct"] * 100
    ).round(2)
    return resumo_calibracao


def responder_pergunta_3(df: pd.DataFrame) -> Dict[str, float]:
    """Pergunta 3: ROI da régua preventiva no estágio D16-D60."""
    clientes_alerta = df[df["status_cobranca"] == "Alerta (D16-D60)"]
    saldo_em_risco = clientes_alerta["saldo_devedor"].sum()
    pcld_atual_alerta = clientes_alerta["pcld_reais"].sum()

    perda_esperada_sem_intervencao = saldo_em_risco * 0.55 * 0.70
    perda_esperada_com_intervencao = saldo_em_risco * 0.16 * 0.70

    economia_estimada_anual = (
        perda_esperada_sem_intervencao - perda_esperada_com_intervencao
    )
    custo_implementacao_tech = 150000.0
    roi_estrategia = round(economia_estimada_anual / custo_implementacao_tech, 2)

    return {
        "saldo_em_alerta": round(saldo_em_risco, 2),
        "pcld_atual_alerta": round(pcld_atual_alerta, 2),
        "economia_projetada_pld": round(economia_estimada_anual, 2),
        "custo_implementacao": custo_implementacao_tech,
        "roi_multiplicador": roi_estrategia,
    }


def main() -> None:
    print("=" * 80)
    print("🚀 NEXUSRISK: PIPELINE EXECUTIVO DE ANÁLISE DE RISCO DE CRÉDITO PF")
    print("=" * 80)
    df_bruto = gerar_dataset_carteira_credito(n_registros=1200, random_seed=42)
    df_final = aplicar_feature_engineering(df_bruto)
    print("✓ Pipeline executado com sucesso.")


if __name__ == "__main__":
    main()
