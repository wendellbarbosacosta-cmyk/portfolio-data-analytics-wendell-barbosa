#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Projeto: PulseSaaS - Otimização de Net Revenue Retention (NRR) & Churn de MRR
Segmento: SaaS B2B & Economia de Assinatura (Cloud Software & Subscriptions)
Autor: Wendell Barbosa Costa (Portfólio de Data Analytics)
Norma: PEP 8 Compliant, Type Annotations estritas e Docstrings Google Style
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


@dataclass(frozen=True)
class RegrasNegocioSaaS:
    """Parâmetros e benchmarks de mercado para métricas de SaaS B2B."""
    BENCHMARK_NRR_EXCELENTE: float = 115.0
    BENCHMARK_NRR_MINIMO: float = 100.0
    BENCHMARK_QUICK_RATIO: float = 4.0
    MARGEM_BRUTA_SAAS: float = 0.82
    PESO_LOGIN_SEMANAL: float = 0.35
    PESO_USO_FEATURES: float = 0.35
    PESO_CHAMADOS_CRITICOS: float = 0.15
    PESO_ADOCAO_ASSENTOS: float = 0.15


REGRAS_SAAS = RegrasNegocioSaaS()


def gerar_dataset_saas(n_clientes: int = 500, random_seed: int = 42) -> pd.DataFrame:
    """Gera base de dados sintética realista de clientes de um SaaS B2B."""
    np.random.seed(random_seed)
    planos = ["Starter", "Growth", "Enterprise"]
    prob_planos = [0.55, 0.33, 0.12]
    segmentos = ["Tecnologia", "Serviços Financeiros", "Varejo & E-Commerce", "Saúde", "Indústria & Logística"]

    cliente_ids = [f"CLI-SaaS-{str(i).zfill(4)}" for i in range(1, n_clientes + 1)]
    planos_atribuidos = np.random.choice(planos, size=n_clientes, p=prob_planos)
    segmentos_atribuidos = np.random.choice(segmentos, size=n_clientes)
    tenure_meses = np.random.randint(1, 37, size=n_clientes)

    mrr_base: List[float] = []
    assentos_contratados: List[int] = []
    assentos_ativos: List[int] = []
    login_freq_semana: List[float] = []
    features_adotadas_pct: List[float] = []
    chamados_suporte_criticos: List[int] = []
    expansao_mrr: List[float] = []
    contracao_mrr: List[float] = []
    churn_status: List[str] = []

    for plano, tenure in zip(planos_atribuidos, tenure_meses):
        if plano == "Starter":
            mrr = float(np.random.uniform(490.0, 990.0))
            assentos = int(np.random.randint(3, 11))
            if tenure <= 3:
                login_freq = float(np.random.uniform(1.2, 4.5))
                feat_pct = float(np.random.uniform(20.0, 55.0))
                assentos_usados = int(max(1, round(assentos * np.random.uniform(0.2, 0.6))))
                prob_churn = 0.28
            else:
                login_freq = float(np.random.uniform(3.0, 6.0))
                feat_pct = float(np.random.uniform(45.0, 80.0))
                assentos_usados = int(max(1, round(assentos * np.random.uniform(0.5, 0.9))))
                prob_churn = 0.12
        elif plano == "Growth":
            mrr = float(np.random.uniform(1800.0, 3900.0))
            assentos = int(np.random.randint(15, 51))
            login_freq = float(np.random.uniform(4.0, 6.8))
            feat_pct = float(np.random.uniform(50.0, 88.0))
            assentos_usados = int(max(5, round(assentos * np.random.uniform(0.6, 0.95))))
            prob_churn = 0.08
        else:
            mrr = float(np.random.uniform(5500.0, 14500.0))
            assentos = int(np.random.randint(60, 250))
            login_freq = float(np.random.uniform(5.5, 7.0))
            feat_pct = float(np.random.uniform(70.0, 96.0))
            assentos_usados = int(max(30, round(assentos * np.random.uniform(0.75, 0.98))))
            prob_churn = 0.03

        chamados = int(np.random.poisson(lam=3.2 if prob_churn > 0.20 else 0.9))
        foi_churn = np.random.rand() < prob_churn
        status = "Cancelado (Churn)" if foi_churn else "Ativo"

        exp = round(mrr * float(np.random.uniform(0.15, 0.45)), 2) if (not foi_churn and feat_pct > 75 and np.random.rand() < 0.40) else 0.0
        cont = round(mrr * float(np.random.uniform(0.10, 0.30)), 2) if (not foi_churn and feat_pct < 40 and np.random.rand() < 0.25) else 0.0

        mrr_base.append(round(mrr, 2))
        assentos_contratados.append(assentos)
        assentos_ativos.append(min(assentos_usados, assentos))
        login_freq_semana.append(round(login_freq, 1))
        features_adotadas_pct.append(round(feat_pct, 1))
        chamados_suporte_criticos.append(chamados)
        expansao_mrr.append(exp)
        contracao_mrr.append(cont)
        churn_status.append(status)

    return pd.DataFrame({
        "id_cliente": cliente_ids,
        "plano": planos_atribuidos,
        "segmento_mercado": segmentos_atribuidos,
        "tenure_meses": tenure_meses,
        "mrr_base": mrr_base,
        "assentos_contratados": assentos_contratados,
        "assentos_ativos": assentos_ativos,
        "login_freq_semana": login_freq_semana,
        "features_adotadas_pct": features_adotadas_pct,
        "chamados_criticos": chamados_suporte_criticos,
        "expansao_mrr": expansao_mrr,
        "contracao_mrr": contracao_mrr,
        "status_cliente": churn_status,
    })


def aplicar_feature_engineering_saas(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica engenharia de atributos executiva e métricas de receita recorrente de forma vetorizada."""
    df_feat = df.copy()

    # Cálculo vetorizado de Health Score (0 a 100) ponderando as 4 dimensões
    comp_login = (df_feat["login_freq_semana"] / 7.0) * 100.0
    comp_feat = df_feat["features_adotadas_pct"]
    comp_assentos = (df_feat["assentos_ativos"] / df_feat["assentos_contratados"].clip(lower=1)) * 100.0
    penalidade_chamados = np.minimum(40.0, df_feat["chamados_criticos"] * 12.0)

    score_bruto = (
        (comp_login * REGRAS_SAAS.PESO_LOGIN_SEMANAL)
        + (comp_feat * REGRAS_SAAS.PESO_USO_FEATURES)
        + (comp_assentos * REGRAS_SAAS.PESO_ADOCAO_ASSENTOS)
        - (penalidade_chamados * REGRAS_SAAS.PESO_CHAMADOS_CRITICOS)
    )
    df_feat["health_score"] = np.clip(score_bruto, 5.0, 100.0).round(1)

    condicoes_saude = [
        df_feat["health_score"] >= 70.0,
        (df_feat["health_score"] >= 50.0) & (df_feat["health_score"] < 70.0),
        df_feat["health_score"] < 50.0,
    ]
    rotulos_saude = ["Verde (Saudável)", "Amarelo (Atenção)", "Vermelho (Risco Alto)"]
    df_feat["faixa_saude"] = np.select(condicoes_saude, rotulos_saude, default="Indefinido")

    condicoes_tenure = [
        df_feat["tenure_meses"] <= 3,
        (df_feat["tenure_meses"] > 3) & (df_feat["tenure_meses"] <= 12),
        df_feat["tenure_meses"] > 12,
    ]
    rotulos_tenure = ["Onboarding (0-3 meses)", "Crescimento (4-12 meses)", "Maduro (>12 meses)"]
    df_feat["faixa_tenure"] = np.select(condicoes_tenure, rotulos_tenure, default="Indefinido")

    df_feat["taxa_ocupacao_assentos"] = ((df_feat["assentos_ativos"] / df_feat["assentos_contratados"]) * 100.0).round(1)
    df_feat["is_churn"] = (df_feat["status_cliente"] == "Cancelado (Churn)").astype(int)
    df_feat["mrr_churned"] = np.where(df_feat["is_churn"] == 1, df_feat["mrr_base"], 0.0)
    df_feat["mrr_atual"] = np.where(
        df_feat["is_churn"] == 1, 0.0, df_feat["mrr_base"] + df_feat["expansao_mrr"] - df_feat["contracao_mrr"]
    ).round(2)

    return df_feat


# =============================================================================
# 4. STORYTELLING & RESPOSTA ÀS 3 PERGUNTAS CRÍTICAS DE NEGÓCIO
# =============================================================================

def responder_pergunta_1(df: pd.DataFrame) -> pd.DataFrame:
    """Pergunta 1: Qual plano e faixa de maturidade concentra a maior perda de MRR?"""
    resumo_plano_tenure = (
        df.groupby(["plano", "faixa_tenure"])
        .agg(
            total_clientes=("id_cliente", "count"),
            mrr_base_total=("mrr_base", "sum"),
            clientes_churn=("is_churn", "sum"),
            mrr_perdido=("mrr_churned", "sum"),
        )
        .reset_index()
    )
    resumo_plano_tenure["taxa_churn_logo_pct"] = (
        (resumo_plano_tenure["clientes_churn"] / resumo_plano_tenure["total_clientes"]) * 100.0
    ).round(2)
    mrr_churn_global = df["mrr_churned"].sum()
    resumo_plano_tenure["share_mrr_churn_pct"] = (
        (resumo_plano_tenure["mrr_perdido"] / max(1.0, mrr_churn_global)) * 100.0
    ).round(2)
    return resumo_plano_tenure.sort_values(by="mrr_perdido", ascending=False)


def responder_pergunta_2(df: pd.DataFrame) -> pd.DataFrame:
    """Pergunta 2: Como o Health Score e a ocupação de assentos antecipam o churn?"""
    resumo_saude = (
        df.groupby("faixa_saude")
        .agg(
            total_clientes=("id_cliente", "count"),
            taxa_churn_pct=("is_churn", "mean"),
            media_health_score=("health_score", "mean"),
            media_ocupacao_assentos=("taxa_ocupacao_assentos", "mean"),
            media_chamados=("chamados_criticos", "mean"),
            mrr_em_risco=("mrr_base", "sum"),
        )
        .reset_index()
    )
    resumo_saude["taxa_churn_pct"] = (resumo_saude["taxa_churn_pct"] * 100.0).round(2)
    resumo_saude["media_health_score"] = resumo_saude["media_health_score"].round(1)
    resumo_saude["media_ocupacao_assentos"] = resumo_saude["media_ocupacao_assentos"].round(1)
    resumo_saude["media_chamados"] = resumo_saude["media_chamados"].round(2)
    return resumo_saude.sort_values(by="taxa_churn_pct", ascending=False)


def responder_pergunta_3(df: pd.DataFrame) -> Dict[str, float]:
    """Pergunta 3: ROI de implantar playbook proativo de CS e recuperação de NRR."""
    mrr_base_total = df["mrr_base"].sum()
    expansao_total = df["expansao_mrr"].sum()
    contracao_total = df["contracao_mrr"].sum()
    churn_total = df["mrr_churned"].sum()

    nrr_atual_pct = ((mrr_base_total + expansao_total - contracao_total - churn_total) / mrr_base_total) * 100.0

    # Simulação: reversão de 55% do churn de onboarding
    churn_onboarding = df[(df["faixa_tenure"] == "Onboarding (0-3 meses)")]["mrr_churned"].sum()
    mrr_preservado_mensal = churn_onboarding * 0.55

    # Identificação proativa de clientes saudáveis para expansão (+25% em expansão)
    expansao_adicional_mensal = expansao_total * 0.25

    arr_adicional_anual = (mrr_preservado_mensal + expansao_adicional_mensal) * 12.0
    custo_cs_anual = 65000.0
    roi_multiplicador = round(arr_adicional_anual / custo_cs_anual, 2)

    novo_nrr_projetado_pct = (
        (mrr_base_total + (expansao_total + expansao_adicional_mensal) - contracao_total - (churn_total - mrr_preservado_mensal))
        / mrr_base_total
    ) * 100.0

    return {
        "mrr_base_total": round(mrr_base_total, 2),
        "nrr_atual_pct": round(nrr_atual_pct, 2),
        "mrr_churn_total": round(churn_total, 2),
        "mrr_preservado_mensal": round(mrr_preservado_mensal, 2),
        "expansao_adicional_mensal": round(expansao_adicional_mensal, 2),
        "novo_nrr_projetado_pct": round(novo_nrr_projetado_pct, 2),
        "arr_adicional_anual": round(arr_adicional_anual, 2),
        "custo_implementacao_cs": custo_cs_anual,
        "roi_multiplicador": roi_multiplicador,
    }


def main() -> None:
    if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 80)
    print("⚡ PULSESAAS: PIPELINE EXECUTIVO DE NRR, CHURN & HEALTH SCORE B2B")
    print("=" * 80)
    df_bruto = gerar_dataset_saas(n_clientes=500, random_seed=42)
    df_final = aplicar_feature_engineering_saas(df_bruto)

    mrr_total = df_final["mrr_base"].sum()
    taxa_churn_mrr = ((df_final["mrr_churned"].sum() / mrr_total) * 100).round(2)
    print(f"✓ Base gerada e processada com {len(df_final)} clientes B2B.")
    print(f"✓ MRR Inicial da Base: R$ {mrr_total:,.2f} (ARR: R$ {mrr_total * 12:,.2f})")
    print(f"✓ Gross Churn de MRR: {taxa_churn_mrr}% (R$ {df_final['mrr_churned'].sum():,.2f}/mês)")

    print("\n--- PERGUNTA 1: Concentração de Churn de MRR por Plano e Maturidade ---")
    p1 = responder_pergunta_1(df_final)
    print(p1.head(6).to_string(index=False))

    print("\n--- PERGUNTA 2: Health Score e Ocupação de Assentos como Preditor de Churn ---")
    p2 = responder_pergunta_2(df_final)
    print(p2.to_string(index=False))

    print("\n--- PERGUNTA 3: Simulação de Playbook de CS e Recuperação de NRR ---")
    p3 = responder_pergunta_3(df_final)
    for k, v in p3.items():
        print(f"  • {k}: {v:,.2f}" if isinstance(v, float) else f"  • {k}: {v}")

    # Salva dataset processado
    output_path = os.path.join(os.path.dirname(__file__), "dataset_saas_metrics_analisado.csv")
    df_final.to_csv(output_path, index=False, encoding="utf-8")
    print(f"\n✓ Dataset exportado com sucesso para: {os.path.basename(output_path)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
