"""
Test Suite: VoltGrid EnergyTech Analytics Pipeline
Author: Wendell Barbosa (Tech Lead / Senior Data Analytics)
Coverage: Data generation integrity, mathematical models, vectorized feature engineering,
executive KPI calculations, and strategic business question resolutions.
"""

import sys
import os
import pytest
import pandas as pd
import numpy as np

# Ensure module directory and root directory are importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "06_voltgrid_energytech_analytics")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pipeline_energytech_analytics import (
    EnergyConfig,
    generate_energy_plant_dataset,
    engineer_energy_features,
    calculate_executive_kpis,
    responder_pergunta_1,
    responder_pergunta_2,
    responder_pergunta_3,
)


@pytest.fixture(scope="module")
def energy_config() -> EnergyConfig:
    return EnergyConfig()


@pytest.fixture(scope="module")
def raw_dataset(energy_config) -> pd.DataFrame:
    return generate_energy_plant_dataset(num_plants=480, seed=energy_config.random_seed)


@pytest.fixture(scope="module")
def processed_dataset(raw_dataset, energy_config) -> pd.DataFrame:
    return engineer_energy_features(raw_dataset, config=energy_config)


# ==============================================================================
# 1. TEST CONFIGURATION & SEED REPRODUCIBILITY
# ==============================================================================
def test_energy_config_defaults(energy_config):
    """Verify regulatory and business parameter defaults."""
    assert energy_config.random_seed == 42
    assert energy_config.preco_medio_ppa_mwh == 185.0
    assert energy_config.pld_medio_horario_ponta_mwh == 380.0
    assert energy_config.custo_lavagem_painel_por_mw == 1450.0
    assert energy_config.capex_bess_por_mwh == 850000.0
    assert energy_config.eficiencia_roundtrip_bess == 0.88


# ==============================================================================
# 2. TEST DATA GENERATION INTEGRITY
# ==============================================================================
def test_generate_energy_plant_dataset_shape_and_nulls(raw_dataset):
    """Ensure generated dataset satisfies enterprise completeness criteria."""
    assert len(raw_dataset) == 480
    assert raw_dataset.isnull().sum().sum() == 0

    expected_cols = [
        "id_usina",
        "fonte_energia",
        "regiao",
        "capacidade_instalada_mw",
        "tecnologia_seguimento",
        "recurso_natural_medio",
        "fator_capacidade_base_pct",
        "taxa_curtailment_pct",
        "taxa_soiling_loss_pct",
        "possui_bess_bateria",
        "status_operacional",
    ]
    for col in expected_cols:
        assert col in raw_dataset.columns, f"Column {col} missing from dataset."


def test_generate_energy_plant_dataset_domain_rules(raw_dataset):
    """Validate physical and regulatory constraints of power plant generation."""
    # Capacity must be strictly positive within realistic commercial plant range
    assert (raw_dataset["capacidade_instalada_mw"] > 0).all()

    # Curtailment rate must be non-negative
    assert (raw_dataset["taxa_curtailment_pct"] >= 0.0).all()

    # Soiling is exclusive to solar PV (0 for wind)
    eol_soiling = raw_dataset.loc[
        raw_dataset["fonte_energia"] == "Eólica Onshore (EOL)", "taxa_soiling_loss_pct"
    ]
    assert (eol_soiling == 0.0).all(), "Wind plants must not incur solar soiling loss."

    ufv_soiling = raw_dataset.loc[
        raw_dataset["fonte_energia"] == "Solar Fotovoltaica (UFV)", "taxa_soiling_loss_pct"
    ]
    assert (ufv_soiling > 0.0).all(), "Solar PV plants must incur positive soiling rate."


# ==============================================================================
# 3. TEST FEATURE ENGINEERING & VECTORIZED CALCULATIONS
# ==============================================================================
def test_engineer_energy_features_calculations(processed_dataset, energy_config):
    """Verify energy balance equations and financial derivations."""
    df = processed_dataset

    # Theoretical generation = capacity * (base_cf / 100) * 8760
    expected_theo = (df["capacidade_instalada_mw"] * (df["fator_capacidade_base_pct"] / 100.0) * 8760.0).round(1)
    np.testing.assert_allclose(df["geracao_teorica_mwh_ano"], expected_theo, rtol=1e-4)

    # Net generation cannot exceed theoretical generation
    assert (df["geracao_liquida_mwh_ano"] <= df["geracao_teorica_mwh_ano"]).all()
    assert (df["geracao_liquida_mwh_ano"] > 0).all()

    # Financial relations
    # Gross revenue = net generation * PPA price
    expected_gross = (df["geracao_liquida_mwh_ano"] * energy_config.preco_medio_ppa_mwh).round(2)
    np.testing.assert_allclose(df["receita_bruta_realizada_rs"], expected_gross, rtol=1e-4)

    # EBITDA = Gross revenue - O&M cost
    expected_ebitda = (df["receita_bruta_realizada_rs"] - df["custo_om_anual_rs"]).round(2)
    np.testing.assert_allclose(df["ebitda_operacional_rs"], expected_ebitda, rtol=1e-4)


def test_curtailment_severity_vectorization(processed_dataset):
    """Verify vectorized np.select categorization for curtailment severity."""
    df = processed_dataset

    valid_categories = {
        "Crítica (Corte ≥ 10%)",
        "Moderada (Corte 4% a 10%)",
        "Baixa / Tolerável (< 4%)",
    }
    assert set(df["faixa_severidade_curtailment"].unique()).issubset(valid_categories)

    # Check boundary consistency
    criticos = df[df["taxa_curtailment_pct"] >= 10.0]
    assert (criticos["faixa_severidade_curtailment"] == "Crítica (Corte ≥ 10%)").all()

    moderados = df[(df["taxa_curtailment_pct"] >= 4.0) & (df["taxa_curtailment_pct"] < 10.0)]
    assert (moderados["faixa_severidade_curtailment"] == "Moderada (Corte 4% a 10%)").all()

    toleraveis = df[df["taxa_curtailment_pct"] < 4.0]
    assert (toleraveis["faixa_severidade_curtailment"] == "Baixa / Tolerável (< 4%)").all()


# ==============================================================================
# 4. TEST EXECUTIVE KPIS CALCULATION
# ==============================================================================
def test_calculate_executive_kpis(processed_dataset):
    """Verify corporate executive KPI outputs and metrics."""
    kpis = calculate_executive_kpis(processed_dataset)

    assert isinstance(kpis, dict)
    assert kpis["total_usinas"] == 480
    assert kpis["capacidade_instalada_total_mw"] > 20000.0
    assert kpis["geracao_liquida_total_mwh"] > 50000000.0
    assert kpis["receita_bruta_anual_rs"] > 10000000000.0
    assert kpis["ebitda_total_anual_rs"] > 0
    assert 0.0 < kpis["margem_ebitda_consolidada_pct"] <= 100.0
    assert kpis["perda_total_curtailment_rs"] > 0
    assert kpis["perda_total_soiling_rs"] > 0


# ==============================================================================
# 5. TEST BUSINESS QUESTIONS RESOLUTION
# ==============================================================================
def test_responder_pergunta_1_curtailment_ranking(processed_dataset):
    """Verify business question 1: ONS curtailment ranking by region and energy source."""
    res_p1 = responder_pergunta_1(processed_dataset)

    assert isinstance(res_p1, pd.DataFrame)
    assert len(res_p1) > 0
    assert "share_perda_curtailment_pct" in res_p1.columns
    assert "perda_financeira_rs" in res_p1.columns

    # First row must be the highest financial loss
    assert res_p1["perda_financeira_rs"].iloc[0] == res_p1["perda_financeira_rs"].max()

    # Share sum must equal 100% (within floating point precision)
    assert pytest.approx(res_p1["share_perda_curtailment_pct"].sum(), rel=1e-3) == 100.0


def test_responder_pergunta_2_robotized_cleaning(processed_dataset, energy_config):
    """Verify business question 2: Economic viability of automated dry robotic cleaning."""
    res_p2 = responder_pergunta_2(processed_dataset, energy_config)

    assert isinstance(res_p2, dict)
    assert res_p2["capacidade_solar_total_mw"] > 0
    assert res_p2["custo_lavagem_anual_rs"] > 0
    assert res_p2["receita_recuperada_anual_rs"] > res_p2["custo_lavagem_anual_rs"]
    assert res_p2["beneficio_liquido_anual_rs"] > 0
    # Payback must be rapid (< 6 months)
    assert 0 < res_p2["payback_simples_meses"] < 6.0
    assert res_p2["roi_multiplicador"] > 2.0


def test_responder_pergunta_3_bess_arbitrage(processed_dataset, energy_config):
    """Verify business question 3: BESS battery storage curtailment capture and arbitrage."""
    res_p3 = responder_pergunta_3(processed_dataset, energy_config)

    assert isinstance(res_p3, dict)
    assert res_p3["energia_cortada_total_mwh"] > 0
    assert res_p3["energia_capturada_bess_mwh"] < res_p3["energia_cortada_total_mwh"]
    # Dispatched energy = captured energy * efficiency
    expected_dispatched = round(res_p3["energia_capturada_bess_mwh"] * energy_config.eficiencia_roundtrip_bess, 1)
    assert pytest.approx(res_p3["energia_despachada_pico_mwh"], rel=1e-3) == expected_dispatched
    assert res_p3["receita_adicional_anual_rs"] > 0
    assert res_p3["investimento_capex_bess_rs"] > 0
    # Payback should be realistic for utility-scale BESS (< 12 years)
    assert 0 < res_p3["payback_simples_anos"] < 12.0
