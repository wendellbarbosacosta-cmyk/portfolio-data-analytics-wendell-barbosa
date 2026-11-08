#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes automatizados do módulo PulseSaaS (SaaS B2B, NRR & Health Score)."""

import os
import sys
import pytest
import pandas as pd
import numpy as np

# Adiciona o diretório do módulo ao path de execução
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "03_pulsesaas_b2b_subscriptions")))

from pipeline_saas_metrics import (
    gerar_dataset_saas,
    aplicar_feature_engineering_saas,
    responder_pergunta_1,
    responder_pergunta_2,
    responder_pergunta_3,
    REGRAS_SAAS,
)


def test_gerar_dataset_saas_schema():
    """Valida formato, schema e tipos na base sintética de SaaS."""
    df = gerar_dataset_saas(n_clientes=100, random_seed=42)
    assert len(df) == 100
    assert not df.isnull().values.any()
    colunas_obrigatorias = [
        "id_cliente", "plano", "segmento_mercado", "tenure_meses",
        "mrr_base", "assentos_contratados", "assentos_ativos",
        "login_freq_semana", "features_adotadas_pct", "chamados_criticos",
        "expansao_mrr", "contracao_mrr", "status_cliente"
    ]
    for col in colunas_obrigatorias:
        assert col in df.columns
    assert (df["mrr_base"] > 0).all()
    assert (df["assentos_ativos"] <= df["assentos_contratados"]).all()


def test_aplicar_feature_engineering_saas_health_score():
    """Verifica limites do Health Score e faixas de risco."""
    df_teste = pd.DataFrame({
        "id_cliente": ["CLI-1", "CLI-2", "CLI-3"],
        "plano": ["Starter", "Growth", "Enterprise"],
        "segmento_mercado": ["Tecnologia"] * 3,
        "tenure_meses": [2, 6, 24],
        "mrr_base": [600.0, 2500.0, 10000.0],
        "assentos_contratados": [10, 50, 100],
        "assentos_ativos": [2, 40, 95],
        "login_freq_semana": [1.0, 5.0, 7.0],
        "features_adotadas_pct": [20.0, 65.0, 95.0],
        "chamados_criticos": [4, 1, 0],
        "expansao_mrr": [0.0, 200.0, 1000.0],
        "contracao_mrr": [0.0, 0.0, 0.0],
        "status_cliente": ["Cancelado (Churn)", "Ativo", "Ativo"],
    })

    df_res = aplicar_feature_engineering_saas(df_teste)

    # Health Score deve estar entre 5 e 100
    assert (df_res["health_score"] >= 5.0).all() and (df_res["health_score"] <= 100.0).all()

    # CLI-1: baixo uso e muitos chamados -> Vermelho (Risco Alto), is_churn=1, tenure Onboarding
    assert df_res.loc[0, "faixa_saude"] == "Vermelho (Risco Alto)"
    assert df_res.loc[0, "faixa_tenure"] == "Onboarding (0-3 meses)"
    assert df_res.loc[0, "is_churn"] == 1
    assert df_res.loc[0, "mrr_churned"] == 600.0
    assert df_res.loc[0, "mrr_atual"] == 0.0

    # CLI-3: alto uso e sem chamados -> Verde (Saudável), tenure Maduro
    assert df_res.loc[2, "faixa_saude"] == "Verde (Saudável)"
    assert df_res.loc[2, "faixa_tenure"] == "Maduro (>12 meses)"
    assert df_res.loc[2, "is_churn"] == 0
    assert df_res.loc[2, "mrr_atual"] == 11000.0


def test_perguntas_negocio_saas():
    """Valida métricas financeiras e storytelling de SaaS."""
    df_bruto = gerar_dataset_saas(n_clientes=200, random_seed=42)
    df_feat = aplicar_feature_engineering_saas(df_bruto)

    p1 = responder_pergunta_1(df_feat)
    assert isinstance(p1, pd.DataFrame)
    assert "taxa_churn_logo_pct" in p1.columns

    p2 = responder_pergunta_2(df_feat)
    assert isinstance(p2, pd.DataFrame)
    assert "media_health_score" in p2.columns

    p3 = responder_pergunta_3(df_feat)
    assert isinstance(p3, dict)
    assert "nrr_atual_pct" in p3
    assert "roi_multiplicador" in p3
    assert p3["roi_multiplicador"] > 0
