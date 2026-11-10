#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes automatizados do módulo CarePulse (HealthTech, LACE Index & MLR)."""

import os
import sys
import pytest
import pandas as pd
import numpy as np

# Adiciona o diretório do módulo ao path de execução
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "04_carepulse_healthtech_analytics")))

from pipeline_healthcare_analytics import (
    HealthTechConfig,
    HealthcareAnalyticsPipeline,
    responder_pergunta_1,
    responder_pergunta_2,
    responder_pergunta_3,
)


def test_gerar_dados_sinteticos_estrutura():
    """Valida formato, integridade de schema e ausência de nulos na base de internações."""
    config = HealthTechConfig(n_registros=120, seed=42)
    pipeline = HealthcareAnalyticsPipeline(config)
    df = pipeline.gerar_dados_sinteticos()

    assert len(df) == 120
    assert not df.isnull().values.any()

    colunas_esperadas = [
        "paciente_id", "plano_saude", "faixa_etaria", "hospital_prestador",
        "tipo_internacao", "num_comorbidades", "dias_internacao", "dias_uti",
        "custo_sinistro_rs", "receita_anual_rs", "lace_index",
        "readmissao_30_dias", "taxa_glosa_pct"
    ]
    for col in colunas_esperadas:
        assert col in df.columns

    assert (df["dias_internacao"] >= 1).all()
    assert (df["dias_uti"] <= df["dias_internacao"]).all()
    assert (df["custo_sinistro_rs"] > 0).all()
    assert (df["receita_anual_rs"] > 0).all()


def test_engenharia_features_e_kpis_regras_lace():
    """Verifica regras de categorização de risco clínico LACE e cálculo de glosas."""
    df_teste = pd.DataFrame({
        "paciente_id": ["PAC-1", "PAC-2", "PAC-3"],
        "plano_saude": ["Plano Executivo Premium"] * 3,
        "faixa_etaria": ["18-35 anos", "51-65 anos", "Acima de 65 anos"],
        "hospital_prestador": ["Hospital Samaritano Central"] * 3,
        "tipo_internacao": ["Clínica Geral", "Cirúrgica Eletiva", "Cirúrgica Emergência"],
        "num_comorbidades": [0, 2, 4],
        "dias_internacao": [2, 5, 12],
        "dias_uti": [0, 1, 4],
        "custo_sinistro_rs": [5000.0, 20000.0, 45000.0],
        "receita_anual_rs": [10000.0, 20000.0, 30000.0],
        "lace_index": [3, 7, 14],  # Baixo, Médio, Alto
        "readmissao_30_dias": [False, False, True],
        "taxa_glosa_pct": [5.0, 10.0, 20.0],
    })

    pipeline = HealthcareAnalyticsPipeline()
    pipeline.df = df_teste
    df_res = pipeline.engenharia_features_e_kpis()

    # PAC-1: LACE 3 -> Baixo Risco (LACE 0-4), glosa = 5000 * 5% = 250, catastrofico = False
    assert df_res.loc[0, "faixa_risco_lace"] == "Baixo Risco (LACE 0-4)"
    assert df_res.loc[0, "valor_glosa_rs"] == 250.0
    assert not df_res.loc[0, "flag_custo_catastrofico"]
    assert df_res.loc[0, "sinistralidade_pct"] == 50.0

    # PAC-2: LACE 7 -> Médio Risco (LACE 5-9), glosa = 20000 * 10% = 2000
    assert df_res.loc[1, "faixa_risco_lace"] == "Médio Risco (LACE 5-9)"
    assert df_res.loc[1, "valor_glosa_rs"] == 2000.0
    assert not df_res.loc[1, "flag_custo_catastrofico"]

    # PAC-3: LACE 14 -> Alto Risco (LACE 10+), custo 45k >= 25k -> Catastrófico = True
    assert df_res.loc[2, "faixa_risco_lace"] == "Alto Risco (LACE 10+)"
    assert df_res.loc[2, "valor_glosa_rs"] == 9000.0
    assert df_res.loc[2, "flag_custo_catastrofico"]


def test_perguntas_negocio_saude():
    """Valida as respostas executivas do storytelling de Saúde Suplementar."""
    config = HealthTechConfig(n_registros=150, seed=42)
    pipeline = HealthcareAnalyticsPipeline(config)
    pipeline.gerar_dados_sinteticos()
    df_feat = pipeline.engenharia_features_e_kpis()

    p1 = responder_pergunta_1(df_feat)
    assert isinstance(p1, pd.DataFrame)
    assert "taxa_readmissao_pct" in p1.columns

    p2 = responder_pergunta_2(df_feat)
    assert isinstance(p2, pd.DataFrame)
    assert "total_glosas_rs" in p2.columns

    p3 = responder_pergunta_3(df_feat)
    assert isinstance(p3, dict)
    assert "roi_multiplicador" in p3
    assert p3["roi_multiplicador"] > 0
    assert "sinistralidade_mlr_projetada_pct" in p3
