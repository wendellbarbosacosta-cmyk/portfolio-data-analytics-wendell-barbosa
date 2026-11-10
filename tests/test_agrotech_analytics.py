#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes automatizados do módulo AgroPrecision (AgTech, VRT & Produtividade Agrícola)."""

import os
import sys
import pytest
import pandas as pd
import numpy as np

# Adiciona o diretório do módulo ao path de execução
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "05_agroprecision_agtech_analytics")))

from pipeline_agrotech_analytics import (
    AgroConfig,
    AgroAnalyticsPipeline,
    responder_pergunta_1,
    responder_pergunta_2,
    responder_pergunta_3,
)


def test_gerar_dados_sinteticos_estrutura():
    """Valida formato, integridade de schema e ausência de nulos na base de talhões agrícolas."""
    config = AgroConfig(n_talhoes=100, seed=42)
    pipeline = AgroAnalyticsPipeline(config)
    df = pipeline.gerar_dados_sinteticos()

    assert len(df) == 100
    assert not df.isnull().values.any()

    colunas_esperadas = [
        "talhao_id", "regiao", "cultura", "area_ha", "textura_solo",
        "tipo_manejo", "saturacao_bases_v_pct", "ph_solo_cacl2",
        "dose_npk_kgha", "custo_insumos_rs_ha", "precipitacao_ciclo_mm",
        "ndvi_medio_vegetativo", "produtividade_scha"
    ]
    for col in colunas_esperadas:
        assert col in df.columns

    assert (df["area_ha"] > 0).all()
    assert (df["produtividade_scha"] > 0).all()
    assert (df["saturacao_bases_v_pct"] >= 30.0).all() and (df["saturacao_bases_v_pct"] <= 85.0).all()
    assert (df["ph_solo_cacl2"] >= 4.0).all() and (df["ph_solo_cacl2"] <= 7.0).all()


def test_engenharia_features_e_kpis_regras_agronomicas():
    """Verifica regras de precificação de grãos, cálculo de margens e fertilidade de solo."""
    df_teste = pd.DataFrame({
        "talhao_id": ["TAL-1", "TAL-2", "TAL-3"],
        "regiao": ["Cerrado / Mato Grosso"] * 3,
        "cultura": ["Soja Safra Principal", "Milho 2ª Safra (Safrinha)", "Soja Safra Principal"],
        "area_ha": [100.0, 100.0, 100.0],
        "textura_solo": ["Argiloso (>35% argila)"] * 3,
        "tipo_manejo": ["Manejo em Taxa Variável (VRT)", "Aplicação Convencional (Taxa Fixa)", "Manejo em Taxa Variável (VRT)"],
        "saturacao_bases_v_pct": [45.0, 58.0, 72.0],  # Crítica, Média, Excelente
        "ph_solo_cacl2": [4.8, 5.4, 6.2],
        "dose_npk_kgha": [350.0, 420.0, 310.0],
        "custo_insumos_rs_ha": [2500.0, 3200.0, 2400.0],
        "precipitacao_ciclo_mm": [650.0, 650.0, 650.0],
        "ndvi_medio_vegetativo": [0.60, 0.68, 0.80],
        "produtividade_scha": [50.0, 100.0, 75.0],
    })

    pipeline = AgroAnalyticsPipeline()
    pipeline.df = df_teste
    df_res = pipeline.engenharia_features_e_kpis()

    # TAL-1: Soja (R$ 135/sc), prod 50 sc -> receita = 6.750, custo = 2.500 -> margem = 4.250, V=45% -> Crítica
    assert df_res.loc[0, "preco_saca_rs"] == 135.00
    assert df_res.loc[0, "receita_bruta_rs_ha"] == 6750.00
    assert df_res.loc[0, "margem_liquida_rs_ha"] == 4250.00
    assert df_res.loc[0, "faixa_fertilidade_solo"] == "Crítica / Ácida (V < 50%)"

    # TAL-2: Milho (R$ 62/sc), prod 100 sc -> receita = 6.200, custo = 3.200 -> margem = 3.000, V=58% -> Média
    assert df_res.loc[1, "preco_saca_rs"] == 62.00
    assert df_res.loc[1, "receita_bruta_rs_ha"] == 6200.00
    assert df_res.loc[1, "margem_liquida_rs_ha"] == 3000.00
    assert df_res.loc[1, "faixa_fertilidade_solo"] == "Média / Regular (V 50-65%)"

    # TAL-3: Soja, V=72% -> Excelente
    assert df_res.loc[2, "faixa_fertilidade_solo"] == "Excelente / Corrigida (V > 65%)"


def test_perguntas_negocio_agrotech():
    """Valida as respostas executivas do storytelling de AgTech."""
    config = AgroConfig(n_talhoes=150, seed=42)
    pipeline = AgroAnalyticsPipeline(config)
    pipeline.gerar_dados_sinteticos()
    df_feat = pipeline.engenharia_features_e_kpis()

    p1 = responder_pergunta_1(df_feat)
    assert isinstance(p1, pd.DataFrame)
    assert "produtividade_media_scha" in p1.columns

    p2 = responder_pergunta_2(df_feat)
    assert isinstance(p2, pd.DataFrame)
    assert "margem_liquida_media_ha" in p2.columns

    p3 = responder_pergunta_3(df_feat)
    assert isinstance(p3, dict)
    assert "roi_multiplicador" in p3
    assert p3["roi_multiplicador"] > 0
    assert "beneficio_total_safra_rs" in p3
