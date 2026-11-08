#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes automatizados do módulo NexusRisk (Crédito & Resolução BACEN 2.682)."""

import os
import sys
import pytest
import pandas as pd
import numpy as np

# Adiciona o diretório do módulo ao path de execução
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "01_nexusrisk_fintech_credit")))

from pipeline_credit_risk import (
    gerar_dataset_carteira_credito,
    aplicar_feature_engineering,
    responder_pergunta_1,
    responder_pergunta_2,
    responder_pergunta_3,
    REGRAS_BACEN,
)


def test_gerar_dataset_carteira_credito_estrutura():
    """Valida formato, integridade de schema e ausência de nulos na geração de dados."""
    df = gerar_dataset_carteira_credito(n_registros=100, random_seed=42)
    assert len(df) == 100
    assert not df.isnull().values.any()
    colunas_obrigatorias = [
        "id_cliente", "canal_aquisicao", "produto", "score_credito",
        "renda_mensal", "limite_concedido", "saldo_devedor", "dias_atraso",
        "taxa_juros_mensal", "meses_relacionamento"
    ]
    for col in colunas_obrigatorias:
        assert col in df.columns
    assert (df["score_credito"] >= 300).all() and (df["score_credito"] <= 950).all()
    assert (df["renda_mensal"] >= 1412.0).all()


def test_aplicar_feature_engineering_regras_bacen():
    """Verifica regras regulatórias BACEN 2.682 e mapeamento correto de PCLD."""
    df_teste = pd.DataFrame({
        "id_cliente": ["CLI-1", "CLI-2", "CLI-3", "CLI-4", "CLI-5", "CLI-6", "CLI-7", "CLI-8"],
        "canal_aquisicao": ["Organico"] * 8,
        "produto": ["Cartão de Crédito"] * 8,
        "score_credito": [800, 650, 500, 700, 700, 700, 700, 700],
        "renda_mensal": [5000.0] * 8,
        "limite_concedido": [3000.0] * 8,
        "saldo_devedor": [1000.0] * 8,
        "dias_atraso": [0, 0, 0, 10, 20, 45, 100, 200],
        "taxa_juros_mensal": [0.03] * 8,
        "meses_relacionamento": [12] * 8,
    })

    df_resultado = aplicar_feature_engineering(df_teste)

    # CLI-1: 0 dias, score 800 -> Rating AA (0%)
    assert df_resultado.loc[0, "rating_bacen"] == "AA"
    assert df_resultado.loc[0, "aliquota_pcld"] == 0.000
    assert df_resultado.loc[0, "pcld_reais"] == 0.0

    # CLI-2: 0 dias, score 650 -> Rating A (0.5%)
    assert df_resultado.loc[1, "rating_bacen"] == "A"
    assert df_resultado.loc[1, "aliquota_pcld"] == 0.005

    # CLI-3: 0 dias, score 500 -> Rating B (1.0%)
    assert df_resultado.loc[2, "rating_bacen"] == "B"
    assert df_resultado.loc[2, "aliquota_pcld"] == 0.010

    # CLI-4: 10 dias atraso -> Rating B (1.0%)
    assert df_resultado.loc[3, "rating_bacen"] == "B"

    # CLI-5: 20 dias atraso -> Rating C (3.0%)
    assert df_resultado.loc[4, "rating_bacen"] == "C"
    assert df_resultado.loc[4, "aliquota_pcld"] == 0.030

    # CLI-6: 45 dias atraso -> Rating D (10.0%)
    assert df_resultado.loc[5, "rating_bacen"] == "D"
    assert df_resultado.loc[5, "aliquota_pcld"] == 0.100

    # CLI-7: 100 dias atraso -> Rating F (50.0%)
    assert df_resultado.loc[6, "rating_bacen"] == "F"
    assert df_resultado.loc[6, "aliquota_pcld"] == 0.500
    assert df_resultado.loc[6, "flag_d90"] == 1

    # CLI-8: 200 dias atraso -> Rating H (100.0%)
    assert df_resultado.loc[7, "rating_bacen"] == "H"
    assert df_resultado.loc[7, "aliquota_pcld"] == 1.000
    assert df_resultado.loc[7, "pcld_reais"] == 1000.0


def test_perguntas_negocio_credito():
    """Valida retornos das funções executivas de storytelling."""
    df_bruto = gerar_dataset_carteira_credito(n_registros=200, random_seed=42)
    df_feat = aplicar_feature_engineering(df_bruto)

    p1 = responder_pergunta_1(df_feat)
    assert isinstance(p1, pd.DataFrame)
    assert "taxa_default_pct" in p1.columns

    p2 = responder_pergunta_2(df_feat)
    assert isinstance(p2, pd.DataFrame)
    assert "dti_medio" in p2.columns

    p3 = responder_pergunta_3(df_feat)
    assert isinstance(p3, dict)
    assert "roi_multiplicador" in p3
    assert p3["custo_implementacao"] > 0
