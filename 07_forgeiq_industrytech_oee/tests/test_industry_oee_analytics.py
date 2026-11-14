"""
Test Suite: ForgeIQ IndustryTech OEE Analytics Pipeline
Author: Wendell Barbosa Costa (Tech Lead / Senior Data Analytics)
Coverage: Data generation integrity, OEE mathematical logic, ISO 10816-3 vibration zones,
financial downtime/scrap metrics, vectorized feature classifications, and executive KPIs.
"""

import os
import sys
import pytest
import pandas as pd
import numpy as np

# Ensure root directory is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pipeline_industry_oee_analytics import (
    IndustryConfig,
    classificar_faixa_oee,
    classificar_zona_iso_vibracao,
    classificar_faixa_oee_vetorizado,
    classificar_zona_iso_vibracao_vetorizado,
    gerar_dataset_industrial,
    calcular_kpis_executivos,
    responder_perguntas_negocio,
)


@pytest.fixture(scope="module")
def industry_config() -> IndustryConfig:
    return IndustryConfig()


@pytest.fixture(scope="module")
def industrial_df(industry_config) -> pd.DataFrame:
    return gerar_dataset_industrial(industry_config)


# ==============================================================================
# 1. TEST CONFIGURATION & BENCHMARKS
# ==============================================================================
def test_industry_config_defaults(industry_config):
    """Verify production benchmarks and financial assumptions."""
    assert industry_config.n_maquinas == 500
    assert industry_config.random_seed == 42
    assert industry_config.horas_programadas_mes == 520.0
    assert industry_config.oee_world_class_pct == 85.0
    assert industry_config.oee_critico_pct == 65.0
    assert industry_config.vibracao_critica_mm_s == 6.0
    assert industry_config.custo_sensor_iot_maquina_rs == 18500.0
    assert industry_config.reducao_downtime_cbm == 0.58
    assert industry_config.reducao_scrap_cbm == 0.45


# ==============================================================================
# 2. TEST CLASSIFICATION RULES (SCALAR & VECTORIZED)
# ==============================================================================
def test_classificar_faixa_oee_scalar_and_vectorized():
    """Verify OEE tiers across boundaries."""
    test_values = pd.Series([88.5, 85.0, 78.4, 72.0, 68.2, 65.0, 54.1, 40.0])
    expected = [
        "World-Class (>= 85%)",
        "World-Class (>= 85%)",
        "Competitiva (72% - 84.9%)",
        "Competitiva (72% - 84.9%)",
        "Atenção (65% - 71.9%)",
        "Atenção (65% - 71.9%)",
        "Crítica (< 65%)",
        "Crítica (< 65%)",
    ]

    for val, exp in zip(test_values, expected):
        assert classificar_faixa_oee(val) == exp

    vectorized_res = classificar_faixa_oee_vetorizado(test_values).tolist()
    assert vectorized_res == expected


def test_classificar_zona_iso_vibracao_scalar_and_vectorized():
    """Verify ISO 10816-3 mechanical vibration zones."""
    test_values = pd.Series([8.2, 6.1, 6.0, 4.5, 2.9, 2.8, 1.4])
    expected = [
        "Zona D: Crítica (> 6.0 mm/s)",
        "Zona D: Crítica (> 6.0 mm/s)",
        "Zona C: Alerta (2.8 - 6.0 mm/s)",
        "Zona C: Alerta (2.8 - 6.0 mm/s)",
        "Zona C: Alerta (2.8 - 6.0 mm/s)",
        "Zona A/B: Normal (<= 2.8 mm/s)",
        "Zona A/B: Normal (<= 2.8 mm/s)",
    ]

    for val, exp in zip(test_values, expected):
        assert classificar_zona_iso_vibracao(val) == exp

    vectorized_res = classificar_zona_iso_vibracao_vetorizado(test_values).tolist()
    assert vectorized_res == expected


# ==============================================================================
# 3. TEST DATA GENERATION & PHYSICAL CONSTRAINTS
# ==============================================================================
def test_gerar_dataset_industrial_shape_and_nulls(industrial_df, industry_config):
    """Ensure dataset completeness and structure."""
    df = industrial_df
    assert len(df) == industry_config.n_maquinas
    assert df.isnull().sum().sum() == 0

    expected_cols = [
        "ativo_id",
        "planta_industrial",
        "setor_produtivo",
        "estrategia_manutencao",
        "sensores_iot_instalados",
        "disponibilidade_pct",
        "performance_pct",
        "qualidade_pct",
        "oee_pct",
        "scrap_rate_pct",
        "vibracao_rms_mm_s",
        "temperatura_mancal_c",
        "horas_parada_mes",
        "mtbf_horas",
        "mttr_horas",
        "custo_downtime_anual_rs",
        "custo_scrap_anual_rs",
        "custo_manutencao_anual_rs",
        "custo_hora_parada_rs",
        "faixa_oee",
        "zona_iso_vibracao",
        "perda_total_anual_rs",
    ]
    for col in expected_cols:
        assert col in df.columns, f"Column '{col}' is missing from industrial dataset."


def test_oee_mathematical_consistency(industrial_df):
    """Verify OEE equation: Availability * Performance * Quality."""
    df = industrial_df
    calc_oee = (
        (df["disponibilidade_pct"] / 100.0)
        * (df["performance_pct"] / 100.0)
        * (df["qualidade_pct"] / 100.0)
        * 100.0
    ).round(1)

    np.testing.assert_allclose(df["oee_pct"], calc_oee, atol=0.2)
    assert (df["oee_pct"] >= 0.0).all()
    assert (df["oee_pct"] <= 100.0).all()
    assert (df["qualidade_pct"] + df["scrap_rate_pct"]).round(2).eq(100.0).all()


def test_financial_calculations(industrial_df):
    """Verify financial formulas for downtime and scrap costs."""
    df = industrial_df

    # Downtime cost = horas_parada * custo_hora * 12
    expected_downtime = (df["horas_parada_mes"] * df["custo_hora_parada_rs"] * 12.0).round(2)
    np.testing.assert_allclose(df["custo_downtime_anual_rs"], expected_downtime, rtol=1e-4)

    # Perda total = downtime + scrap
    expected_total_loss = (df["custo_downtime_anual_rs"] + df["custo_scrap_anual_rs"]).round(2)
    np.testing.assert_allclose(df["perda_total_anual_rs"], expected_total_loss, rtol=1e-4)


# ==============================================================================
# 4. TEST EXECUTIVE KPIS CALCULATION
# ==============================================================================
def test_calcular_kpis_executivos(industrial_df):
    """Verify calculation of corporate industrial KPIs."""
    kpis = calcular_kpis_executivos(industrial_df)

    assert isinstance(kpis, dict)
    assert kpis["total_ativos"] == 500.0
    assert 50.0 < kpis["oee_medio_pct"] < 90.0
    assert 0.0 < kpis["scrap_rate_medio_pct"] < 15.0
    assert kpis["custo_downtime_total_rs"] > 0
    assert kpis["custo_scrap_total_rs"] > 0
    assert kpis["perda_total_operacional_rs"] == round(
        kpis["custo_downtime_total_rs"] + kpis["custo_scrap_total_rs"], 2
    )
    assert 0.0 <= kpis["adocao_iot_pct"] <= 100.0


# ==============================================================================
# 5. TEST BUSINESS QUESTIONS RESOLUTION
# ==============================================================================
def test_responder_pergunta_1_downtime_ranking(industrial_df, industry_config):
    """Verify Q1: Downtime ranking by plant."""
    q1_planta, _, _ = responder_perguntas_negocio(industrial_df, industry_config)

    assert isinstance(q1_planta, pd.DataFrame)
    assert len(q1_planta) == 5
    assert "share_downtime_pct" in q1_planta.columns
    assert "custo_downtime_anual" in q1_planta.columns

    # First plant must be the highest downtime cost
    assert q1_planta["custo_downtime_anual"].iloc[0] == q1_planta["custo_downtime_anual"].max()

    # Sum of shares must equal 100%
    assert pytest.approx(q1_planta["share_downtime_pct"].sum(), rel=1e-3) == 100.0


def test_responder_pergunta_2_vibracao_scrap(industrial_df, industry_config):
    """Verify Q2: ISO 10816-3 vibration vs. scrap rate correlation."""
    _, q2_vibracao, _ = responder_perguntas_negocio(industrial_df, industry_config)

    assert isinstance(q2_vibracao, pd.DataFrame)
    assert len(q2_vibracao) == 3
    assert "share_scrap_pct" in q2_vibracao.columns
    assert "scrap_medio_pct" in q2_vibracao.columns

    # Critical zone must have higher scrap rate than normal zone
    crit_row = q2_vibracao[q2_vibracao["zona_iso_vibracao"] == "Zona D: Crítica (> 6.0 mm/s)"]
    norm_row = q2_vibracao[q2_vibracao["zona_iso_vibracao"] == "Zona A/B: Normal (<= 2.8 mm/s)"]

    assert not crit_row.empty and not norm_row.empty
    assert crit_row["scrap_medio_pct"].values[0] > norm_row["scrap_medio_pct"].values[0]


def test_responder_pergunta_3_business_case_iot(industrial_df, industry_config):
    """Verify Q3: IoT CBM Retrofit ROI and Payback business case."""
    _, _, q3_roi = responder_perguntas_negocio(industrial_df, industry_config)

    assert isinstance(q3_roi, dict)
    assert q3_roi["ativos_elegiveis"] > 0
    assert q3_roi["capex_iot_rs"] > 0
    assert q3_roi["economia_downtime_rs"] > 0
    assert q3_roi["economia_scrap_rs"] > 0
    assert q3_roi["beneficio_anual_total_rs"] > q3_roi["capex_iot_rs"]
    assert 0 < q3_roi["payback_meses"] < 6.0
    assert q3_roi["roi_12m_x"] > 10.0
