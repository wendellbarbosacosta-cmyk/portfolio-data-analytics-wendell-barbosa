"""
Test Suite: AeroYield Aviation Analytics Pipeline.

Valida a integridade matemática, regras de negócio da aviação comercial (padrão ANAC / IATA),
funções de classificação vetorizadas, consistência estatística e respostas executivas.
"""

import os
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import pytest

# Adiciona o diretório do módulo 10 e a raiz do portfólio ao sys.path
MODULE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "10_aeroyield_aviation_analytics"))
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from pipeline_aviation_yield_analytics import (
    AviationConfig,
    AviationKpiSummary,
    classify_load_factor,
    classify_load_factor_vectorized,
    classify_otp_performance,
    classify_otp_performance_vectorized,
    generate_aviation_network_dataset,
    load_or_generate_dataset,
    compute_kpis,
    responder_pergunta_1,
    responder_pergunta_2,
    responder_pergunta_3,
    answer_business_questions,
    export_visual_reports,
)


@pytest.fixture(scope="module")
def sample_dataset() -> pd.DataFrame:
    """Fixture que fornece um dataset sintético determinístico com 50 rotas."""
    return generate_aviation_network_dataset(num_routes=50, seed=42)


@pytest.fixture(scope="module")
def real_dataset() -> pd.DataFrame:
    """Fixture que carrega o dataset do projeto (500 rotas)."""
    csv_file = Path(MODULE_DIR) / "dataset_aviacao_yield_rotas.csv"
    return load_or_generate_dataset(csv_path=csv_file)


def test_aviation_config_defaults():
    """Valida que a configuração padrão mantém os parâmetros de negócio exigidos."""
    config = AviationConfig()
    assert config.random_seed == 42
    assert config.suboccupied_load_factor_threshold == 74.0
    assert config.high_demand_load_factor_threshold == 85.0
    assert config.world_class_otp_threshold == 85.0
    assert config.attention_otp_threshold == 75.0
    assert config.critical_turnaround_minutes == 42
    assert config.anac400_reduction_pct == 0.58
    assert config.qav_reduction_pct == 0.45
    assert config.idleness_recovery_pct == 0.70
    assert config.ancillary_boost_per_pax_rs == 4.50
    assert config.package_investment_rs == 12_500_000.0


def test_classify_load_factor_scalar_and_vectorized():
    """Testa consistência entre funções escalar e vetorizada de ocupação (Load Factor)."""
    # Teste Escalar
    assert classify_load_factor(73.9) == "Subocupada (< 74%)"
    assert classify_load_factor(74.0) == "Equilíbrio (74% - 84.9%)"
    assert classify_load_factor(84.9) == "Equilíbrio (74% - 84.9%)"
    assert classify_load_factor(85.0) == "Alta Demanda (>= 85%)"

    # Teste Vetorizado
    series = pd.Series([65.0, 73.9, 74.0, 80.5, 84.9, 85.0, 92.0])
    expected = [
        "Subocupada (< 74%)",
        "Subocupada (< 74%)",
        "Equilíbrio (74% - 84.9%)",
        "Equilíbrio (74% - 84.9%)",
        "Equilíbrio (74% - 84.9%)",
        "Alta Demanda (>= 85%)",
        "Alta Demanda (>= 85%)",
    ]
    result = classify_load_factor_vectorized(series).tolist()
    assert result == expected


def test_classify_otp_performance_scalar_and_vectorized():
    """Testa consistência entre funções escalar e vetorizada de pontualidade OTP D-15."""
    # Teste Escalar
    assert classify_otp_performance(85.0) == "Pontualidade Classe Mundial (>= 85%)"
    assert classify_otp_performance(84.9) == "Atenção Operacional (75% - 84.9%)"
    assert classify_otp_performance(75.0) == "Atenção Operacional (75% - 84.9%)"
    assert classify_otp_performance(74.9) == "Crítico / Efeito Cascata (< 75%)"

    # Teste Vetorizado
    series = pd.Series([68.0, 74.9, 75.0, 80.0, 84.9, 85.0, 95.0])
    expected = [
        "Crítico / Efeito Cascata (< 75%)",
        "Crítico / Efeito Cascata (< 75%)",
        "Atenção Operacional (75% - 84.9%)",
        "Atenção Operacional (75% - 84.9%)",
        "Atenção Operacional (75% - 84.9%)",
        "Pontualidade Classe Mundial (>= 85%)",
        "Pontualidade Classe Mundial (>= 85%)",
    ]
    result = classify_otp_performance_vectorized(series).tolist()
    assert result == expected


def test_dataset_generation_shape_and_columns(sample_dataset: pd.DataFrame):
    """Verifica se o gerador sintético produz a quantidade correta de linhas e colunas."""
    assert len(sample_dataset) == 50
    expected_cols = [
        "rota_id",
        "hub_origem",
        "familia_aeronave",
        "perfil_rota",
        "voos_anuais",
        "distancia_km",
        "load_factor_pct",
        "faixa_load_factor",
        "otp_d15_pct",
        "faixa_otp",
        "turnaround_minutos",
        "rask_centavos",
        "cask_centavos",
        "spread_rask_cask_centavos",
        "receita_ancilar_por_pax_rs",
        "passageiros_anuais",
        "receita_anual_rs",
        "custo_anac400_anual_rs",
        "custo_excesso_qav_anual_rs",
        "perda_ociosidade_anual_rs",
        "impacto_financeiro_total_rs",
        "possui_turnaround_digital",
    ]
    for col in expected_cols:
        assert col in sample_dataset.columns
    assert sample_dataset.isna().sum().sum() == 0


def test_dataset_business_rules_integrity(real_dataset: pd.DataFrame):
    """Valida integridade lógica e financeira das variáveis da malha aérea."""
    # 1. Spread RASK - CASK deve ser consistente
    spread_calculado = real_dataset["rask_centavos"] - real_dataset["cask_centavos"]
    assert np.all(np.isclose(real_dataset["spread_rask_cask_centavos"], spread_calculado, atol=0.02))

    # 2. Impacto financeiro total deve ser a soma das 3 perdas
    impacto_calculado = (
        real_dataset["custo_anac400_anual_rs"]
        + real_dataset["custo_excesso_qav_anual_rs"]
        + real_dataset["perda_ociosidade_anual_rs"]
    )
    assert np.all(np.isclose(real_dataset["impacto_financeiro_total_rs"], impacto_calculado, atol=1.0))

    # 3. Voos, passageiros e receita devem ser positivos
    assert (real_dataset["voos_anuais"] > 0).all()
    assert (real_dataset["passageiros_anuais"] > 0).all()
    assert (real_dataset["receita_anual_rs"] > 0).all()


def test_compute_kpis_accuracy(real_dataset: pd.DataFrame):
    """Garante que a agregação de KPIs reflete com exatidão a base de dados."""
    kpis = compute_kpis(real_dataset)
    assert isinstance(kpis, AviationKpiSummary)
    assert kpis.total_rotas == len(real_dataset)
    assert kpis.total_voos_anuais == int(real_dataset["voos_anuais"].sum())
    assert kpis.total_passageiros_anuais == int(real_dataset["passageiros_anuais"].sum())
    assert np.isclose(kpis.receita_total_rs, real_dataset["receita_anual_rs"].sum(), atol=1.0)
    assert np.isclose(kpis.impacto_financeiro_total_rs, real_dataset["impacto_financeiro_total_rs"].sum(), atol=1.0)
    assert 75.0 <= kpis.load_factor_medio_pct <= 85.0
    assert 80.0 <= kpis.otp_d15_medio_pct <= 90.0
    assert 3.0 <= kpis.spread_medio_centavos <= 6.0


def test_pergunta_1_fleet_and_suboccupied_routes(real_dataset: pd.DataFrame):
    """Valida a Pergunta 1: spread deficitário do A320ceo e rotas subocupadas."""
    p1 = responder_pergunta_1(real_dataset)
    assert p1["spread_a320ceo_centavos"] < 0.0  # Spread negativo do legado
    assert p1["spread_a320neo_centavos"] > 5.0  # Spread positivo da nova geração
    assert p1["gap_cask_ceo_vs_neo_centavos"] > 5.0  # Gap expressivo
    assert p1["qtd_rotas_subocupadas"] > 0
    assert p1["perda_ociosidade_total_rs"] > 15_000_000.0
    assert "Revenue Management" in p1["acao_recomendada"]


def test_pergunta_2_turnaround_and_anac400_metrics(real_dataset: pd.DataFrame):
    """Valida a Pergunta 2: concentração de custos ANAC 400 em turnaround > 42 min."""
    p2 = responder_pergunta_2(real_dataset)
    assert p2["qtd_rotas_turnaround_critico"] > 0
    assert p2["pct_anac400_concentrado_em_turnaround_critico"] > 50.0  # Mais de 50% concentrado
    assert p2["otp_medio_critico_pct"] < p2["otp_medio_controlado_pct"]
    assert p2["gap_otp_pontos"] > 8.0
    assert "GRU — Guarulhos (SP)" in p2["resumo_por_hub"]
    assert "CGH — Congonhas (SP)" in p2["resumo_por_hub"]
    assert p2["pct_anac400_gru_cgh"] > 55.0  # GRU + CGH concentram mais de 55%
    assert "Turnaround Digital 30 min" in p2["acao_recomendada"]


def test_pergunta_3_integrated_package_roi(real_dataset: pd.DataFrame):
    """Valida a Pergunta 3: viabilidade econômico-financeira, payback e ROI do pacote."""
    p3 = responder_pergunta_3(real_dataset)
    assert p3["ganho_operacional_anual_rs"] > 40_000_000.0
    assert p3["ganho_ancilar_rs"] > 60_000_000.0
    assert p3["ganho_total_anual_rs"] > 100_000_000.0
    assert p3["investimento_total_rs"] == 12_500_000.0
    assert p3["payback_meses"] < 4.0  # Payback total inferior a 4 meses
    assert p3["payback_operacional_meses"] < 4.0  # Payback puramente operacional também < 4 meses
    assert p3["roi_ano1_multiplicador"] >= 3.0  # ROI total superior a 3.0x
    assert p3["roi_operacional_ano1"] >= 3.0  # ROI puramente operacional também >= 3.0x


def test_export_visual_reports(tmp_path: Path, sample_dataset: pd.DataFrame):
    """Garante que a rotina de exportação gera os 3 artefatos visuais sem erros."""
    export_visual_reports(sample_dataset, output_dir=tmp_path)
    assert (tmp_path / "01_spread_rask_cask_por_frota.png").exists()
    assert (tmp_path / "02_custo_anac400_por_hub.png").exists()
    assert (tmp_path / "painel_aviacao_yield.html").exists()
    assert (tmp_path / "01_spread_rask_cask_por_frota.png").stat().st_size > 10_000
