"""
Test Suite: ShelfSense Retail Omnichannel Analytics Pipeline.

Valida a integridade matemática, regras de negócio de inventário e gôndola,
funções vetorizadas, consistência estatística e respostas executivas.
"""

import os
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import pytest

# Adiciona o diretório do módulo 09 e a raiz do portfólio ao sys.path
MODULE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "09_shelfsense_retail_omnichannel"))
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if MODULE_DIR not in sys.path:
    sys.path.insert(0, MODULE_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from pipeline_retail_omnichannel_analytics import (
    RetailConfig,
    RetailKpiSummary,
    classify_stock_coverage,
    classify_stock_coverage_vectorized,
    classify_gmroi_tier,
    classify_gmroi_tier_vectorized,
    generate_retail_omnichannel_dataset,
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
    """Fixture que fornece um dataset sintético determinístico com 50 clusters."""
    return generate_retail_omnichannel_dataset(num_clusters=50, seed=42)


@pytest.fixture(scope="module")
def real_dataset() -> pd.DataFrame:
    """Fixture que carrega o dataset do projeto (500 clusters)."""
    csv_file = Path(MODULE_DIR) / "dataset_retail_omnichannel_skus.csv"
    return load_or_generate_dataset(csv_path=csv_file)


def test_retail_config_defaults():
    """Valida que a configuração padrão mantém os parâmetros de negócio exigidos."""
    config = RetailConfig()
    assert config.random_seed == 42
    assert config.critical_coverage_days == 4.0
    assert config.overstock_coverage_days == 25.0
    assert config.high_gmroi_threshold == 2.5
    assert config.moderate_gmroi_threshold == 1.5
    assert config.drp_lost_sales_recovery_pct == 0.65
    assert config.markdown_shrinkage_reduction_pct == 0.52
    assert config.package_implementation_investment_rs == 4_500_000.0


def test_classify_stock_coverage_scalar_and_vectorized():
    """Testa consistência entre funções escalar e vetorizada de cobertura de estoque."""
    # Teste Escalar
    assert classify_stock_coverage(3.9) == "Ruptura Crítica (< 4 dias)"
    assert classify_stock_coverage(4.0) == "Saudável (4 a 25 dias)"
    assert classify_stock_coverage(25.0) == "Saudável (4 a 25 dias)"
    assert classify_stock_coverage(25.1) == "Excesso / Envenenado (> 25 dias)"

    # Teste Vetorizado
    series = pd.Series([1.5, 4.0, 15.0, 25.0, 32.0])
    expected = [
        "Ruptura Crítica (< 4 dias)",
        "Saudável (4 a 25 dias)",
        "Saudável (4 a 25 dias)",
        "Saudável (4 a 25 dias)",
        "Excesso / Envenenado (> 25 dias)",
    ]
    result = classify_stock_coverage_vectorized(series).tolist()
    assert result == expected


def test_classify_gmroi_tier_scalar_and_vectorized():
    """Testa consistência entre funções escalar e vetorizada de faixas de GMROI."""
    # Teste Escalar
    assert classify_gmroi_tier(3.2) == "Alta Performance (>= 2.5x)"
    assert classify_gmroi_tier(2.5) == "Alta Performance (>= 2.5x)"
    assert classify_gmroi_tier(2.49) == "Moderado (1.5x - 2.49x)"
    assert classify_gmroi_tier(1.5) == "Moderado (1.5x - 2.49x)"
    assert classify_gmroi_tier(1.49) == "Destruição de Caixa (< 1.5x)"

    # Teste Vetorizado
    series = pd.Series([0.95, 1.49, 1.50, 2.49, 2.50, 4.10])
    expected = [
        "Destruição de Caixa (< 1.5x)",
        "Destruição de Caixa (< 1.5x)",
        "Moderado (1.5x - 2.49x)",
        "Moderado (1.5x - 2.49x)",
        "Alta Performance (>= 2.5x)",
        "Alta Performance (>= 2.5x)",
    ]
    result = classify_gmroi_tier_vectorized(series).tolist()
    assert result == expected


def test_dataset_generation_shape_and_columns(sample_dataset: pd.DataFrame):
    """Verifica se o gerador sintético produz a quantidade correta de linhas e colunas."""
    assert len(sample_dataset) == 50
    expected_cols = [
        "sku_cluster_id",
        "formato_regional",
        "categoria_produto",
        "canal_predominante",
        "lojas_cluster",
        "preco_medio_rs",
        "margem_bruta_pct",
        "receita_anual_rs",
        "estoque_medio_rs",
        "gmroi",
        "faixa_gmroi",
        "dias_cobertura_estoque",
        "faixa_cobertura",
        "taxa_osa_pct",
        "taxa_ruptura_pct",
        "quebra_operacional_pct",
        "possui_rfid_omnichannel",
        "venda_perdida_ruptura_anual_rs",
        "custo_quebra_anual_rs",
        "perda_total_anual_rs",
        "nps_omnichannel",
    ]
    for col in expected_cols:
        assert col in sample_dataset.columns
    assert sample_dataset.isna().sum().sum() == 0


def test_dataset_business_rules_integrity(real_dataset: pd.DataFrame):
    """Valida integridade lógica e financeira das variáveis do dataset real."""
    # 1. OSA + Ruptura deve ser aproximadamente 100%
    soma_osa_ruptura = real_dataset["taxa_osa_pct"] + real_dataset["taxa_ruptura_pct"]
    assert np.all(np.isclose(soma_osa_ruptura, 100.0, atol=0.2))

    # 2. Perda total deve ser igual a venda perdida + custo de quebra
    perda_calculada = real_dataset["venda_perdida_ruptura_anual_rs"] + real_dataset["custo_quebra_anual_rs"]
    assert np.all(np.isclose(real_dataset["perda_total_anual_rs"], perda_calculada, atol=1.0))

    # 3. GMROI positivo e estoque positivo
    assert (real_dataset["gmroi"] > 0).all()
    assert (real_dataset["estoque_medio_rs"] > 0).all()
    assert (real_dataset["receita_anual_rs"] > 0).all()


def test_compute_kpis_accuracy(real_dataset: pd.DataFrame):
    """Garante que a agregação de KPIs reflete com exatidão a base de dados."""
    kpis = compute_kpis(real_dataset)
    assert isinstance(kpis, RetailKpiSummary)
    assert kpis.total_clusters == len(real_dataset)
    assert kpis.total_lojas == int(real_dataset["lojas_cluster"].sum())
    assert np.isclose(kpis.receita_total_rs, real_dataset["receita_anual_rs"].sum(), atol=1.0)
    assert np.isclose(kpis.perda_total_anual_rs, real_dataset["perda_total_anual_rs"].sum(), atol=1.0)
    assert 90.0 <= kpis.osa_media_pct <= 98.0
    assert 1.0 <= kpis.quebra_media_pct <= 4.0
    assert 2.0 <= kpis.gmroi_medio <= 3.5


def test_pergunta_1_ruptura_nps_metrics(real_dataset: pd.DataFrame):
    """Valida a Pergunta 1: concentração de venda perdida e queda de NPS na ruptura crítica."""
    p1 = responder_pergunta_1(real_dataset)
    assert p1["qtd_clusters_criticos"] > 0
    assert p1["pct_concentracao_venda_perdida"] > 40.0  # Concentra a maior parte da perda
    assert p1["osa_media_critico_pct"] < p1["osa_media_saudavel_pct"]
    assert p1["nps_medio_critico"] < 60.0  # Deterioração de NPS
    assert p1["gap_nps_pontos"] > 10.0  # Forte distorção de satisfação
    assert "DRP Preditivo" in p1["acao_recomendada"]


def test_pergunta_2_overstock_gmroi_metrics(real_dataset: pd.DataFrame):
    """Valida a Pergunta 2: destruição de GMROI e capital imobilizado em overstock."""
    p2 = responder_pergunta_2(real_dataset)
    assert p2["qtd_clusters_overstock"] > 0
    assert p2["capital_imobilizado_overstock_rs"] > 40_000_000.0
    assert p2["gmroi_medio_overstock"] < p2["gmroi_medio_saudavel"]
    assert p2["pct_overstock_destruicao_caixa"] > 50.0
    assert "Eletro & Bazar" in p2["categorias_detalhes"]
    assert "Perecíveis & Frios" in p2["categorias_detalhes"]
    assert "Markdown Dinâmico" in p2["acao_recomendada"]


def test_pergunta_3_integrated_package_roi(real_dataset: pd.DataFrame):
    """Valida a Pergunta 3: viabilidade econômico-financeira, payback e ROI do pacote."""
    p3 = responder_pergunta_3(real_dataset)
    assert p3["venda_bruta_recuperada_rs"] > 20_000_000.0
    assert p3["lucro_bruto_adicional_rs"] > 8_000_000.0
    assert p3["economia_quebras_rs"] > 8_000_000.0
    assert p3["valor_gerado_anual_rs"] > 18_000_000.0
    assert p3["investimento_turnkey_rs"] == 4_500_000.0
    assert p3["payback_meses"] < 4.0  # Payback deve ser inferior a 4 meses
    assert p3["roi_ano1_multiplicador"] >= 3.0  # ROI superior a 3.0x


def test_export_visual_reports(tmp_path: Path, sample_dataset: pd.DataFrame):
    """Garante que a rotina de exportação gera os 3 artefatos visuais sem erros."""
    export_visual_reports(sample_dataset, output_dir=tmp_path)
    assert (tmp_path / "01_osa_ruptura_vs_venda_perdida.png").exists()
    assert (tmp_path / "02_gmroi_cobertura_por_categoria.png").exists()
    assert (tmp_path / "painel_varejo_omnichannel.html").exists()
    assert (tmp_path / "01_osa_ruptura_vs_venda_perdida.png").stat().st_size > 10_000
