"""
Test Suite: OptiFiber Telecom FTTH Analytics Pipeline
Author: Wendell Barbosa Costa (Tech Lead / Senior Data Analytics)
Coverage: Data generation integrity, optical RX attenuation health, CTO occupancy,
telecom financial formulas (truck roll and churn loss), executive KPIs, and business questions.
"""

import os
import sys
import pytest
import pandas as pd
import numpy as np

# Ensure module directory and root directory are importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "08_optifiber_telecom_ftth")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pipeline_telecom_ftth_analytics import (
    TelecomConfig,
    classify_optical_health,
    classify_cto_occupancy,
    classify_optical_health_vectorized,
    classify_cto_occupancy_vectorized,
    generate_telecom_dataset,
    compute_executive_kpis,
    answer_business_questions,
)


@pytest.fixture(scope="module")
def telecom_config() -> TelecomConfig:
    return TelecomConfig()


@pytest.fixture(scope="module")
def telecom_df(telecom_config) -> pd.DataFrame:
    return generate_telecom_dataset(
        n_clusters=telecom_config.total_clusters,
        seed=telecom_config.random_seed,
    )


# ==============================================================================
# 1. TEST CONFIGURATION & BENCHMARKS
# ==============================================================================
def test_telecom_config_defaults(telecom_config):
    """Verify Telecom regulatory parameters and business benchmarks."""
    assert telecom_config.total_clusters == 500
    assert telecom_config.random_seed == 42
    assert telecom_config.cost_per_truck_roll_rs == 240.0
    assert telecom_config.benchmark_churn_ftth_pct == 1.60
    assert telecom_config.rx_critico_dbm == -27.0
    assert telecom_config.rx_degradado_dbm == -23.0
    assert telecom_config.limiar_ociosidade_cto_pct == 45.0
    assert telecom_config.limiar_alta_densidade_cto_pct == 75.0


# ==============================================================================
# 2. TEST OPTICAL HEALTH CLASSIFICATION (SCALAR & VECTORIZED)
# ==============================================================================
def test_classify_optical_health_scalar_and_vectorized():
    """Verify optical RX attenuation classification across key boundaries."""
    test_rx = pd.Series([-31.2, -27.5, -27.0, -26.9, -23.5, -23.0, -22.9, -17.4])
    expected = [
        "Crítico (< -27.0 dBm)",
        "Crítico (< -27.0 dBm)",
        "Degradado (-23.1 a -27.0 dBm)",
        "Degradado (-23.1 a -27.0 dBm)",
        "Degradado (-23.1 a -27.0 dBm)",
        "Nominal (>= -23.0 dBm)",
        "Nominal (>= -23.0 dBm)",
        "Nominal (>= -23.0 dBm)",
    ]

    for val, exp in zip(test_rx, expected):
        assert classify_optical_health(val) == exp

    vectorized_res = classify_optical_health_vectorized(test_rx).tolist()
    assert vectorized_res == expected


# ==============================================================================
# 3. TEST CTO OCCUPANCY CLASSIFICATION (SCALAR & VECTORIZED)
# ==============================================================================
def test_classify_cto_occupancy_scalar_and_vectorized():
    """Verify CTO port occupancy categorization across key boundaries."""
    test_occ = pd.Series([88.0, 75.0, 74.9, 60.0, 45.0, 44.9, 28.0])
    expected = [
        "Alta Densidade (>= 75%)",
        "Alta Densidade (>= 75%)",
        "Maturação (45% - 74.9%)",
        "Maturação (45% - 74.9%)",
        "Maturação (45% - 74.9%)",
        "Ociosa (< 45%)",
        "Ociosa (< 45%)",
    ]

    for val, exp in zip(test_occ, expected):
        assert classify_cto_occupancy(val) == exp

    vectorized_res = classify_cto_occupancy_vectorized(test_occ).tolist()
    assert vectorized_res == expected


# ==============================================================================
# 4. TEST DATASET GENERATION & PHYSICAL CONSTRAINTS
# ==============================================================================
def test_generate_telecom_dataset_shape_and_nulls(telecom_df, telecom_config):
    """Ensure dataset completeness, schema compliance and absence of nulls."""
    df = telecom_df
    assert len(df) == telecom_config.total_clusters
    assert df.isnull().sum().sum() == 0

    expected_cols = [
        "cluster_id",
        "regional_uf",
        "tecnologia_acesso",
        "plano_predominante",
        "assinantes_ativos",
        "portas_cto_instaladas",
        "ocupacao_cto_pct",
        "potencia_rx_media_dbm",
        "possui_wifi6_mesh",
        "chamados_suporte_mes",
        "truck_rolls_mes",
        "custo_truck_roll_anual_rs",
        "arpu_mensal_rs",
        "churn_mensal_pct",
        "receita_perdida_churn_anual_rs",
        "nps_rede",
        "saude_optica",
        "faixa_ocupacao_cto",
        "perda_total_anual_rs",
    ]
    for col in expected_cols:
        assert col in df.columns, f"Column '{col}' is missing from telecom dataset."


def test_generate_telecom_dataset_domain_rules(telecom_df):
    """Validate physical telecom network constraints and subscriber metrics."""
    df = telecom_df

    # Optical RX power must be negative (dBm attenuation)
    assert (df["potencia_rx_media_dbm"] < 0.0).all()
    assert (df["potencia_rx_media_dbm"] > -40.0).all()

    # Active subscribers must not exceed installed CTO ports
    assert (df["assinantes_ativos"] <= df["portas_cto_instaladas"]).all()
    assert (df["assinantes_ativos"] > 0).all()

    # Churn rate must be positive and bounded within realistic bounds
    assert (df["churn_mensal_pct"] >= 0.5).all()
    assert (df["churn_mensal_pct"] <= 10.0).all()

    # ARPU must be strictly positive
    assert (df["arpu_mensal_rs"] >= 50.0).all()


# ==============================================================================
# 5. TEST FINANCIAL FORMULAS
# ==============================================================================
def test_telecom_financial_formulas(telecom_df, telecom_config):
    """Verify truck roll and churn loss mathematical calculations."""
    df = telecom_df

    # Truck roll annual cost = truck_rolls_mes * 12 * cost_per_roll
    expected_truck = (
        df["truck_rolls_mes"] * 12.0 * telecom_config.cost_per_truck_roll_rs
    ).round(2)
    np.testing.assert_allclose(df["custo_truck_roll_anual_rs"], expected_truck, rtol=1e-4)

    # Churn annual revenue loss = assinantes * (churn_pct / 100) * 12 * arpu
    expected_churn_loss = (
        df["assinantes_ativos"] * (df["churn_mensal_pct"] / 100.0) * 12.0 * df["arpu_mensal_rs"]
    ).round(2)
    np.testing.assert_allclose(df["receita_perdida_churn_anual_rs"], expected_churn_loss, rtol=1e-4)

    # Total loss = truck roll + churn loss
    expected_total_loss = (
        df["custo_truck_roll_anual_rs"] + df["receita_perdida_churn_anual_rs"]
    ).round(2)
    np.testing.assert_allclose(df["perda_total_anual_rs"], expected_total_loss, rtol=1e-4)


# ==============================================================================
# 6. TEST EXECUTIVE KPIS CALCULATION
# ==============================================================================
def test_compute_executive_kpis(telecom_df):
    """Verify consolidated executive KPIs for FTTH operations."""
    kpis = compute_executive_kpis(telecom_df)

    assert isinstance(kpis, dict)
    assert kpis["total_clusters"] == 500.0
    assert kpis["total_assinantes"] > 50000.0
    assert 90.0 < kpis["arpu_medio_rs"] < 160.0
    assert 1.0 < kpis["churn_medio_pct"] < 5.0
    assert kpis["custo_truck_roll_anual_rs"] > 0
    assert kpis["perda_churn_anual_rs"] > 0
    assert kpis["perda_total_anual_rs"] == round(
        kpis["custo_truck_roll_anual_rs"] + kpis["perda_churn_anual_rs"], 2
    )


# ==============================================================================
# 7. TEST BUSINESS QUESTIONS RESOLUTION
# ==============================================================================
def test_answer_business_questions_q1_health(telecom_df):
    """Verify Q1: Optical health impact on churn, truck rolls, and losses."""
    q1_optica, _, _ = answer_business_questions(telecom_df)

    assert isinstance(q1_optica, pd.DataFrame)
    assert len(q1_optica) == 3
    assert "share_perda_pct" in q1_optica.columns
    assert "churn_medio_pct" in q1_optica.columns

    # First row must be the highest churn rate
    assert q1_optica["churn_medio_pct"].iloc[0] == q1_optica["churn_medio_pct"].max()

    # Sum of shares must equal 100%
    assert pytest.approx(q1_optica["share_perda_pct"].sum(), rel=1e-3) == 100.0


def test_answer_business_questions_q2_cto(telecom_df):
    """Verify Q2: Regional CTO port occupancy and idle ports."""
    _, q2_cto, _ = answer_business_questions(telecom_df)

    assert isinstance(q2_cto, pd.DataFrame)
    assert len(q2_cto) == 5
    assert "portas_livres" in q2_cto.columns
    assert "share_portas_livres_pct" in q2_cto.columns

    # Available ports = total ports - active subscribers
    expected_livres = q2_cto["portas_totais"] - q2_cto["assinantes"]
    assert (q2_cto["portas_livres"] == expected_livres).all()

    # Sum of share portas livres must equal 100%
    assert pytest.approx(q2_cto["share_portas_livres_pct"].sum(), rel=1e-3) == 100.0


def test_answer_business_questions_q3_roi(telecom_df):
    """Verify Q3: Telecom modernization business case (ROI, Payback)."""
    _, _, q3_roi = answer_business_questions(telecom_df)

    assert isinstance(q3_roi, dict)
    assert q3_roi["investimento_total_rs"] > 0
    assert q3_roi["beneficio_anual_rs"] > q3_roi["investimento_total_rs"]
    assert q3_roi["economia_truck_roll_rs"] > 0
    assert q3_roi["receita_preservada_churn_rs"] > 0
    assert q3_roi["uplift_arpu_wifi6_rs"] > 0
    # Payback must be under 12 months for this project
    assert 0 < q3_roi["payback_meses"] < 12.0
    assert q3_roi["roi_multiplicador"] > 1.5
