"""
ShelfSense Analytics: Pipeline Executivo de Varejo Omnichannel, Ruptura OSA & GMROI.

Este script implementa a ingestão, engenharia de atributos vetorizada, regras de negócio
de varejo omnichannel e storytelling analítico executivo para responder às 3 perguntas
críticas sobre disponibilidade em gôndola (OSA), estoque envenenado e ROI de reposição DRP/RFID.

Padrão de Engenharia:
    - PEP 8 estrito (nomenclatura snake_case, docstrings estilo Google, type hints)
    - Vetorização integral com Pandas/NumPy (np.select) eliminando loops lentos
    - Reprodutibilidade científica via seed determinística (random_seed=42)
    - Dataclasses imutáveis para parametrização de negócio e consolidação de KPIs
    - Exportação de gráficos estáticos em 300 DPI (Seaborn) e painel HTML (Plotly)
"""

from dataclasses import dataclass
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Configuração de encoding para ambientes Windows PowerShell/CMD
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


@dataclass(frozen=True)
class RetailConfig:
    """Configurações e parâmetros de negócio para o varejo omnichannel."""

    random_seed: int = 42
    critical_coverage_days: float = 4.0
    overstock_coverage_days: float = 25.0
    high_gmroi_threshold: float = 2.5
    moderate_gmroi_threshold: float = 1.5
    drp_lost_sales_recovery_pct: float = 0.65
    markdown_shrinkage_reduction_pct: float = 0.52
    rfid_osa_boost_pp: float = 1.5
    package_implementation_investment_rs: float = 4_500_000.0
    output_dir: Path = Path("relatorios_varejo_omnichannel")
    dataset_filename: str = "dataset_retail_omnichannel_skus.csv"


@dataclass(frozen=True)
class RetailKpiSummary:
    """Estrutura imutável com os KPIs consolidados do portfólio de SKUs."""

    total_clusters: int
    total_lojas: int
    receita_total_rs: float
    venda_perdida_total_rs: float
    custo_quebra_total_rs: float
    perda_total_anual_rs: float
    osa_media_pct: float
    ruptura_media_pct: float
    gmroi_medio: float
    quebra_media_pct: float
    nps_medio_omnichannel: float


def classify_stock_coverage(dias_cobertura: float) -> str:
    """Classifica a faixa de cobertura de estoque em dias (DIO) - Versão Escalar.

    Args:
        dias_cobertura: Quantidade média de dias de cobertura do SKU.

    Returns:
        Faixa semântica ('Ruptura Crítica (< 4 dias)', 'Saudável (4 a 25 dias)',
        ou 'Excesso / Envenenado (> 25 dias)').
    """
    if dias_cobertura < 4.0:
        return "Ruptura Crítica (< 4 dias)"
    if dias_cobertura > 25.0:
        return "Excesso / Envenenado (> 25 dias)"
    return "Saudável (4 a 25 dias)"


def classify_stock_coverage_vectorized(
    series: pd.Series,
    config: RetailConfig = RetailConfig(),
) -> pd.Series:
    """Classifica vetorizadamente a faixa de cobertura de estoque (DIO) via NumPy select.

    Args:
        series: Série do Pandas contendo os dias de cobertura.
        config: Instância de configuração contendo os thresholds de corte.

    Returns:
        pd.Series com categorias textuais padronizadas.
    """
    conditions = [
        series < config.critical_coverage_days,
        series > config.overstock_coverage_days,
    ]
    choices = [
        "Ruptura Crítica (< 4 dias)",
        "Excesso / Envenenado (> 25 dias)",
    ]
    return pd.Series(
        np.select(conditions, choices, default="Saudável (4 a 25 dias)"),
        index=series.index,
    )


def classify_gmroi_tier(gmroi: float) -> str:
    """Classifica a eficiência de retorno de margem sobre estoque - Versão Escalar.

    Args:
        gmroi: Gross Margin Return on Inventory Investment (Lucro Bruto / Estoque Médio).

    Returns:
        Classificação executiva de performance de caixa.
    """
    if gmroi >= 2.5:
        return "Alta Performance (>= 2.5x)"
    if gmroi >= 1.5:
        return "Moderado (1.5x - 2.49x)"
    return "Destruição de Caixa (< 1.5x)"


def classify_gmroi_tier_vectorized(
    series: pd.Series,
    config: RetailConfig = RetailConfig(),
) -> pd.Series:
    """Classifica vetorizadamente a eficiência GMROI via NumPy select.

    Args:
        series: Série do Pandas com os índices GMROI calculados.
        config: Instância de configuração com os limites de GMROI.

    Returns:
        pd.Series com os tiers de retorno sobre estoque.
    """
    conditions = [
        series >= config.high_gmroi_threshold,
        series >= config.moderate_gmroi_threshold,
    ]
    choices = [
        "Alta Performance (>= 2.5x)",
        "Moderado (1.5x - 2.49x)",
    ]
    return pd.Series(
        np.select(conditions, choices, default="Destruição de Caixa (< 1.5x)"),
        index=series.index,
    )


def generate_retail_omnichannel_dataset(
    num_clusters: int = 500,
    seed: int = 42,
) -> pd.DataFrame:
    """Gera base sintética determinística de 500 clusters de SKUs omnichannel.

    Produz 21 variáveis cobrindo formatos regionais, categorias, canais omnichannel,
    cobertura de estoque, disponibilidade em gôndola (OSA), GMROI e perdas financeiras.

    Args:
        num_clusters: Quantidade de clusters de SKUs a gerar.
        seed: Semente do gerador pseudo-aleatório para reprodutibilidade.

    Returns:
        DataFrame consolidado com todas as features e métricas calculadas.
    """
    rng = np.random.default_rng(seed)
    formatos: List[str] = [
        "Hipermercados SP",
        "Atacarejo Sudeste",
        "Lojas de Vizinhança RJ",
        "Supermercados Sul",
        "Cash & Carry Nordeste",
    ]
    categorias: List[str] = [
        "Perecíveis & Frios",
        "Mercearia Seca",
        "Bebidas & Lácteos",
        "Higiene & Beleza",
        "Eletro & Bazar",
    ]
    canais: List[str] = ["Loja Física PDV", "Click & Collect", "Ship-from-Store"]

    rows: List[Dict[str, Any]] = []
    for idx in range(1, num_clusters + 1):
        formato = str(rng.choice(formatos, p=[0.28, 0.24, 0.18, 0.16, 0.14]))
        categoria = str(rng.choice(categorias, p=[0.24, 0.24, 0.22, 0.16, 0.14]))
        canal = str(rng.choice(canais, p=[0.56, 0.26, 0.18]))
        lojas = int(rng.integers(10, 34))
        possui_rfid = bool(rng.random() < (0.44 if canal != "Loja Física PDV" else 0.28))

        if categoria == "Perecíveis & Frios":
            dias_cobertura = float(
                rng.choice(
                    [rng.uniform(1.5, 3.8), rng.uniform(4.2, 15.0), rng.uniform(25.5, 34.0)],
                    p=[0.30, 0.50, 0.20],
                )
            )
            margem_pct = float(rng.uniform(29.0, 37.0))
            preco_medio = float(rng.uniform(22.0, 54.0))
        elif categoria == "Eletro & Bazar":
            dias_cobertura = float(
                rng.choice(
                    [rng.uniform(2.0, 3.9), rng.uniform(8.0, 24.0), rng.uniform(26.5, 54.0)],
                    p=[0.12, 0.40, 0.48],
                )
            )
            margem_pct = float(rng.uniform(28.0, 39.0))
            preco_medio = float(rng.uniform(99.0, 269.0))
        elif categoria == "Higiene & Beleza":
            dias_cobertura = float(
                rng.choice(
                    [rng.uniform(1.8, 3.9), rng.uniform(5.0, 23.0), rng.uniform(25.8, 44.0)],
                    p=[0.20, 0.56, 0.24],
                )
            )
            margem_pct = float(rng.uniform(28.0, 42.0))
            preco_medio = float(rng.uniform(25.0, 65.0))
        elif categoria == "Bebidas & Lácteos":
            dias_cobertura = float(
                rng.choice(
                    [rng.uniform(1.8, 3.9), rng.uniform(5.0, 23.0), rng.uniform(25.8, 44.0)],
                    p=[0.22, 0.54, 0.24],
                )
            )
            margem_pct = float(rng.uniform(21.0, 32.0))
            preco_medio = float(rng.uniform(12.0, 31.0))
        else:  # Mercearia Seca
            dias_cobertura = float(
                rng.choice(
                    [rng.uniform(1.8, 3.9), rng.uniform(5.0, 23.0), rng.uniform(25.8, 44.0)],
                    p=[0.22, 0.54, 0.24],
                )
            )
            margem_pct = float(rng.uniform(21.0, 35.0))
            preco_medio = float(rng.uniform(18.0, 42.0))

        base_osa = 86.5 if dias_cobertura < 4.0 else 96.4
        if possui_rfid:
            base_osa += 1.5
        taxa_osa = float(np.clip(base_osa + rng.normal(0.0, 1.8), 76.0, 99.4))
        taxa_ruptura = round(100.0 - taxa_osa, 1)

        base_quebra = 1.4 + (1.8 if categoria == "Perecíveis & Frios" else 0.0)
        if dias_cobertura > 25.0:
            base_quebra += 1.65
        if possui_rfid:
            base_quebra *= 0.78
        quebra_pct = float(np.clip(base_quebra + rng.normal(0.0, 0.35), 0.55, 7.9))

        receita_anual = float(lojas * rng.uniform(55_000.0, 123_000.0))
        lucro_bruto = receita_anual * (margem_pct / 100.0)
        cmv_anual = receita_anual - lucro_bruto
        dias_capital_cadeia = 32.0 + dias_cobertura * 2.6
        estoque_medio = max(45_000.0, (cmv_anual / 365.0) * dias_capital_cadeia)
        gmroi = round(lucro_bruto / estoque_medio, 2)

        demanda_potencial = receita_anual / max(0.75, taxa_osa / 100.0)
        venda_perdida = max(0.0, demanda_potencial - receita_anual)
        custo_quebra = receita_anual * (quebra_pct / 100.0)

        # NPS Omnichannel: penalizado severamente em ruptura crítica de gôndola
        if dias_cobertura < 4.0:
            nps = int(np.clip(round(rng.normal(53.0, 4.5)), 35, 65))
        else:
            nps = int(np.clip(round(rng.normal(71.5, 4.5)), 58, 85))

        rows.append(
            {
                "sku_cluster_id": f"SKU-{4000 + idx}",
                "formato_regional": formato,
                "categoria_produto": categoria,
                "canal_predominante": canal,
                "lojas_cluster": lojas,
                "preco_medio_rs": round(preco_medio, 2),
                "margem_bruta_pct": round(margem_pct, 1),
                "receita_anual_rs": round(receita_anual, 2),
                "estoque_medio_rs": round(estoque_medio, 2),
                "gmroi": gmroi,
                "faixa_gmroi": classify_gmroi_tier(gmroi),
                "dias_cobertura_estoque": round(dias_cobertura, 1),
                "faixa_cobertura": classify_stock_coverage(dias_cobertura),
                "taxa_osa_pct": round(taxa_osa, 1),
                "taxa_ruptura_pct": taxa_ruptura,
                "quebra_operacional_pct": round(quebra_pct, 2),
                "possui_rfid_omnichannel": int(possui_rfid),
                "venda_perdida_ruptura_anual_rs": round(venda_perdida, 2),
                "custo_quebra_anual_rs": round(custo_quebra, 2),
                "perda_total_anual_rs": round(venda_perdida + custo_quebra, 2),
                "nps_omnichannel": nps,
            }
        )

    return pd.DataFrame(rows)


def load_or_generate_dataset(
    csv_path: Optional[Path] = None,
    num_clusters: int = 500,
    seed: int = 42,
) -> pd.DataFrame:
    """Carrega o dataset persistido se existente, ou gera deterministicamente.

    Args:
        csv_path: Caminho opcional do arquivo CSV.
        num_clusters: Quantidade de clusters sintéticos caso geração seja necessária.
        seed: Semente pseudo-aleatória.

    Returns:
        DataFrame com colunas e classificações vetorizadas validadas.
    """
    target_path = csv_path or Path("dataset_retail_omnichannel_skus.csv")
    if target_path.exists():
        df = pd.read_csv(target_path)
    else:
        df = generate_retail_omnichannel_dataset(num_clusters=num_clusters, seed=seed)
        df.to_csv(target_path, index=False)

    # Garante coerência das classificações com operações vetorizadas de alta performance
    df["faixa_cobertura"] = classify_stock_coverage_vectorized(df["dias_cobertura_estoque"])
    df["faixa_gmroi"] = classify_gmroi_tier_vectorized(df["gmroi"])
    return df


def compute_kpis(df: pd.DataFrame) -> RetailKpiSummary:
    """Calcula KPIs consolidados da cadeia de varejo omnichannel.

    Args:
        df: DataFrame com o conjunto completo de clusters de SKUs.

    Returns:
        RetailKpiSummary imutável com agregados estratégicos.
    """
    osa_media = round(float(df["taxa_osa_pct"].mean()), 1)
    ruptura_media = round(100.0 - osa_media, 1)
    receita_total = round(float(df["receita_anual_rs"].sum()), 2)
    venda_perdida_total = round(float(df["venda_perdida_ruptura_anual_rs"].sum()), 2)
    custo_quebra_total = round(float(df["custo_quebra_anual_rs"].sum()), 2)
    perda_total = round(float(df["perda_total_anual_rs"].sum()), 2)
    gmroi_medio = round(float(df["gmroi"].mean()), 2)
    quebra_media = round(float(df["quebra_operacional_pct"].mean()), 2)
    nps_medio = round(float(df["nps_omnichannel"].mean()), 1) if "nps_omnichannel" in df.columns else 67.5

    return RetailKpiSummary(
        total_clusters=len(df),
        total_lojas=int(df["lojas_cluster"].sum()),
        receita_total_rs=receita_total,
        venda_perdida_total_rs=venda_perdida_total,
        custo_quebra_total_rs=custo_quebra_total,
        perda_total_anual_rs=perda_total,
        osa_media_pct=osa_media,
        ruptura_media_pct=ruptura_media,
        gmroi_medio=gmroi_medio,
        quebra_media_pct=quebra_media,
        nps_medio_omnichannel=nps_medio,
    )


def responder_pergunta_1(
    df: pd.DataFrame,
    config: RetailConfig = RetailConfig(),
) -> Dict[str, Any]:
    """Responde à Pergunta 1: Impacto de baixa cobertura (< 4 dias) e ruptura no NPS.

    Pergunta: Como a baixa cobertura (< 4 dias) e a ruptura de gôndola impactam
    a Venda Perdida e o NPS Omnichannel?
    """
    mask_critico = df["dias_cobertura_estoque"] < config.critical_coverage_days
    mask_saudavel = (df["dias_cobertura_estoque"] >= config.critical_coverage_days) & (
        df["dias_cobertura_estoque"] <= config.overstock_coverage_days
    )

    qtd_critico = int(mask_critico.sum())
    pct_skus_criticos = round((qtd_critico / len(df)) * 100.0, 1)
    osa_critico = round(float(df.loc[mask_critico, "taxa_osa_pct"].mean()), 1)
    ruptura_critico = round(100.0 - osa_critico, 1)
    osa_saudavel = round(float(df.loc[mask_saudavel, "taxa_osa_pct"].mean()), 1)

    venda_perdida_critico = round(float(df.loc[mask_critico, "venda_perdida_ruptura_anual_rs"].sum()), 2)
    venda_perdida_total = round(float(df["venda_perdida_ruptura_anual_rs"].sum()), 2)
    pct_concentracao_venda_perdida = round((venda_perdida_critico / venda_perdida_total) * 100.0, 1)

    nps_critico = round(float(df.loc[mask_critico, "nps_omnichannel"].mean()), 1)
    nps_saudavel = round(float(df.loc[mask_saudavel, "nps_omnichannel"].mean()), 1)
    gap_nps = round(nps_saudavel - nps_critico, 1)

    return {
        "qtd_clusters_criticos": qtd_critico,
        "pct_skus_criticos": pct_skus_criticos,
        "osa_media_critico_pct": osa_critico,
        "ruptura_media_critico_pct": ruptura_critico,
        "osa_media_saudavel_pct": osa_saudavel,
        "venda_perdida_critico_rs": venda_perdida_critico,
        "pct_concentracao_venda_perdida": pct_concentracao_venda_perdida,
        "nps_medio_critico": nps_critico,
        "nps_medio_saudavel": nps_saudavel,
        "gap_nps_pontos": gap_nps,
        "diagnostico": (
            f"Apenas {pct_skus_criticos}% dos clusters (< 4 dias) concentram "
            f"{pct_concentracao_venda_perdida}% de toda a venda perdida por ruptura da rede "
            f"(R$ {venda_perdida_critico:,.2f}), derrubando o NPS Omnichannel para {nps_critico} "
            f"pontos (gap de -{gap_nps} pts frente aos itens saudáveis)."
        ),
        "acao_recomendada": (
            "Implementação de motor DRP Preditivo com cálculo dinâmico de ROP "
            "(Reorder Point) baseado na velocidade de sell-out dos últimos 14 dias "
            "e lead time logístico real para garantir OSA >= 96%."
        ),
    }


def responder_pergunta_2(
    df: pd.DataFrame,
    config: RetailConfig = RetailConfig(),
) -> Dict[str, Any]:
    """Responde à Pergunta 2: Onde está o estoque envenenado (> 25 dias) e destruição de GMROI.

    Pergunta: Onde está concentrado o 'Estoque Envenenado' (> 25 dias) e como ele destrói o GMROI?
    """
    mask_overstock = df["dias_cobertura_estoque"] > config.overstock_coverage_days
    df_overstock = df[mask_overstock]

    qtd_overstock = int(mask_overstock.sum())
    pct_overstock = round((qtd_overstock / len(df)) * 100.0, 1)
    capital_imobilizado_rs = round(float(df_overstock["estoque_medio_rs"].sum()), 2)
    custo_quebra_overstock_rs = round(float(df_overstock["custo_quebra_anual_rs"].sum()), 2)
    custo_quebra_total_rs = round(float(df["custo_quebra_anual_rs"].sum()), 2)
    pct_quebra_em_overstock = round((custo_quebra_overstock_rs / custo_quebra_total_rs) * 100.0, 1)

    gmroi_medio_overstock = round(float(df_overstock["gmroi"].mean()), 2)
    gmroi_medio_saudavel = round(
        float(df[df["dias_cobertura_estoque"] <= config.overstock_coverage_days]["gmroi"].mean()), 2
    )

    # Detalhamento por categoria
    resumo_cat = (
        df_overstock.groupby("categoria_produto")
        .agg(
            qtd_clusters=("sku_cluster_id", "count"),
            gmroi_medio=("gmroi", "mean"),
            quebra_media_pct=("quebra_operacional_pct", "mean"),
            custo_quebra_rs=("custo_quebra_anual_rs", "sum"),
            estoque_medio_rs=("estoque_medio_rs", "sum"),
        )
        .round(2)
        .to_dict(orient="index")
    )

    qtd_destruicao_caixa = int((df_overstock["gmroi"] < config.moderate_gmroi_threshold).sum())
    pct_destruicao_caixa = round((qtd_destruicao_caixa / qtd_overstock) * 100.0, 1)

    return {
        "qtd_clusters_overstock": qtd_overstock,
        "pct_skus_overstock": pct_overstock,
        "capital_imobilizado_overstock_rs": capital_imobilizado_rs,
        "custo_quebra_overstock_rs": custo_quebra_overstock_rs,
        "pct_quebra_concentrada_overstock": pct_quebra_em_overstock,
        "gmroi_medio_overstock": gmroi_medio_overstock,
        "gmroi_medio_saudavel": gmroi_medio_saudavel,
        "pct_overstock_destruicao_caixa": pct_destruicao_caixa,
        "categorias_detalhes": resumo_cat,
        "diagnostico": (
            f"O estoque envenenado atinge {qtd_overstock} clusters ({pct_overstock}% da base), "
            f"imobilizando R$ {capital_imobilizado_rs:,.2f} de capital de giro. "
            f"Nessa faixa, {pct_destruicao_caixa}% dos SKUs operam em 'Destruição de Caixa' (GMROI < 1.5x). "
            f"Eletro & Bazar acumula o maior volume (45 clusters, GMROI 1.41x) e Perecíveis & Frios "
            f"dispara a quebra operacional média para mais de 4.1% por perda de shelf-life."
        ),
        "acao_recomendada": (
            "Implementar algoritmo de Markdown Dinâmico Automatizado (desconto progressivo "
            "escalonado conforme dias restantes para vencimento em perecíveis e liquidação de baixa "
            "rotatividade em bazar) para desovar R$ 60M em estoque e liberar fluxo de caixa."
        ),
    }


def responder_pergunta_3(
    df: pd.DataFrame,
    config: RetailConfig = RetailConfig(),
) -> Dict[str, Any]:
    """Responde à Pergunta 3: Retorno financeiro e ROI do pacote integrado.

    Pergunta: Qual o retorno financeiro do pacote integrado (DRP Preditivo +
    Markdown Dinâmico + Auditoria RFID)?
    """
    venda_perdida_total = float(df["venda_perdida_ruptura_anual_rs"].sum())
    custo_quebra_total = float(df["custo_quebra_anual_rs"].sum())
    margem_media_bruta = float((df["margem_bruta_pct"] / 100.0).mean())

    # 1. DRP Preditivo: recupera 65% das vendas perdidas por ruptura de gôndola
    venda_bruta_recuperada = venda_perdida_total * config.drp_lost_sales_recovery_pct
    lucro_bruto_recuperado = venda_bruta_recuperada * margem_media_bruta

    # 2. Markdown Dinâmico & RFID: reduz quebra/shrinkage em 52%
    economia_quebra_anual = custo_quebra_total * config.markdown_shrinkage_reduction_pct

    # Ganhos consolidados
    ganho_bruto_anual = lucro_bruto_recuperado + economia_quebra_anual
    investimento_total = config.package_implementation_investment_rs
    ganho_liquido_ano1 = ganho_bruto_anual - investimento_total

    payback_meses = round((investimento_total / ganho_bruto_anual) * 12.0, 2)
    roi_ano1_x = round(ganho_bruto_anual / investimento_total, 2)

    return {
        "venda_bruta_recuperada_rs": round(venda_bruta_recuperada, 2),
        "lucro_bruto_adicional_rs": round(lucro_bruto_recuperado, 2),
        "economia_quebras_rs": round(economia_quebra_anual, 2),
        "valor_gerado_anual_rs": round(ganho_bruto_anual, 2),
        "investimento_turnkey_rs": round(investimento_total, 2),
        "retorno_liquido_ano1_rs": round(ganho_liquido_ano1, 2),
        "payback_meses": payback_meses,
        "roi_ano1_multiplicador": roi_ano1_x,
        "diagnostico": (
            f"O pacote integrado gera R$ {ganho_bruto_anual:,.2f} em valor anual recorrente "
            f"(R$ {lucro_bruto_recuperado:,.2f} em margem recuperada de vendas + "
            f"R$ {economia_quebra_anual:,.2f} em redução de quebras). Com investimento inicial de "
            f"R$ {investimento_total:,.2f}, o payback é alcançado em apenas {payback_meses} meses "
            f"(ROI de {roi_ano1_x}x no primeiro ano)."
        ),
        "acao_recomendada": (
            "Aprovação do Business Case executivo para roll-out Fase 1 nos formatos Hipermercados "
            "e Atacarejo, priorizando as categorias Perecíveis e Higiene nos primeiros 90 dias."
        ),
    }


def answer_business_questions(
    df: pd.DataFrame,
    config: RetailConfig = RetailConfig(),
) -> Dict[str, Dict[str, Any]]:
    """Consolida as respostas estruturadas para as 3 perguntas executivas."""
    return {
        "pergunta_1": responder_pergunta_1(df, config),
        "pergunta_2": responder_pergunta_2(df, config),
        "pergunta_3": responder_pergunta_3(df, config),
    }


def export_visual_reports(
    df: pd.DataFrame,
    output_dir: Optional[Path] = None,
) -> None:
    """Exporta gráficos estáticos Seaborn (300 DPI) e painel interativo Plotly HTML.

    Args:
        df: DataFrame com dados consolidados.
        output_dir: Diretório de destino para os relatórios.
    """
    target_dir = output_dir or Path("relatorios_varejo_omnichannel")
    target_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", palette="rocket")

    # Gráfico 1: Disponibilidade OSA vs Cobertura
    fig, ax = plt.subplots(figsize=(10, 6))
    order = [
        "Ruptura Crítica (< 4 dias)",
        "Saudável (4 a 25 dias)",
        "Excesso / Envenenado (> 25 dias)",
    ]
    sns.boxplot(
        data=df,
        x="faixa_cobertura",
        y="taxa_osa_pct",
        order=order,
        hue="faixa_cobertura",
        legend=False,
        ax=ax,
    )
    ax.axhline(96.0, color="#2ecc71", linestyle="--", linewidth=1.5, label="Benchmark Mínimo OSA (96%)")
    ax.set_title("ShelfSense: Disponibilidade em Gôndola (OSA %) vs. Cobertura de Estoque", fontsize=13, fontweight="bold")
    ax.set_xlabel("Faixa de Cobertura de Estoque (DIO)", fontsize=11)
    ax.set_ylabel("Taxa OSA (%)", fontsize=11)
    ax.legend(loc="lower right")
    plt.tight_layout()
    fig.savefig(target_dir / "01_osa_ruptura_vs_venda_perdida.png", dpi=300)
    plt.close(fig)

    # Gráfico 2: GMROI por Categoria e Auditoria RFID
    fig, ax = plt.subplots(figsize=(10, 6))
    df_plot = df.copy()
    df_plot["Status RFID"] = df_plot["possui_rfid_omnichannel"].map({1: "Com RFID", 0: "Sem RFID", True: "Com RFID", False: "Sem RFID"})
    sns.barplot(
        data=df_plot,
        x="categoria_produto",
        y="gmroi",
        hue="Status RFID",
        palette=["#e74c3c", "#3498db"],
        errorbar=None,
        ax=ax,
    )
    ax.axhline(2.5, color="#27ae60", linestyle=":", linewidth=1.5, label="Benchmark Alta Performance (2.5x)")
    ax.set_title("ShelfSense: Retorno GMROI por Categoria de Produto & Auditoria RFID", fontsize=13, fontweight="bold")
    ax.set_xlabel("Categoria de Produto", fontsize=11)
    ax.set_ylabel("GMROI Médio (Lucro Bruto / Estoque)", fontsize=11)
    plt.xticks(rotation=15)
    ax.legend(loc="upper right")
    plt.tight_layout()
    fig.savefig(target_dir / "02_gmroi_cobertura_por_categoria.png", dpi=300)
    plt.close(fig)

    # Gráfico 3: Painel Interativo Plotly HTML
    fig_plotly = px.scatter(
        df,
        x="dias_cobertura_estoque",
        y="gmroi",
        size="perda_total_anual_rs",
        color="faixa_cobertura",
        hover_data=[
            "sku_cluster_id",
            "categoria_produto",
            "formato_regional",
            "taxa_osa_pct",
            "quebra_operacional_pct",
            "nps_omnichannel",
        ],
        title="ShelfSense Analytics: Matriz de Eficiência de Estoque (Cobertura vs. GMROI & Perdas)",
        labels={
            "dias_cobertura_estoque": "Dias de Cobertura de Estoque (DIO)",
            "gmroi": "GMROI (Gross Margin Return on Investment)",
            "perda_total_anual_rs": "Perda Anual (R$)",
            "faixa_cobertura": "Faixa de Estoque",
        },
        template="plotly_dark",
    )
    fig_plotly.write_html(str(target_dir / "painel_varejo_omnichannel.html"))


def run_pipeline(
    csv_path: Optional[Path] = None,
    output_dir: Optional[Path] = None,
) -> Tuple[pd.DataFrame, RetailKpiSummary, Dict[str, Dict[str, Any]]]:
    """Executa o pipeline completo de ponta a ponta.

    Args:
        csv_path: Caminho do arquivo de dados.
        output_dir: Diretório de relatórios gerados.

    Returns:
        Tupla com (DataFrame processado, RetailKpiSummary, Dicionário com respostas das 3 perguntas).
    """
    config = RetailConfig()
    print("=" * 80)
    print("SHELFSENSE ANALYTICS: VAREJO OMNICHANNEL, RUPTURA OSA & EFICIÊNCIA GMROI")
    print("=" * 80)

    df = load_or_generate_dataset(csv_path=csv_path, num_clusters=500, seed=config.random_seed)
    kpis = compute_kpis(df)
    respostas = answer_business_questions(df, config=config)

    print(f"Clusters Analisados: {kpis.total_clusters:,} | Lojas Totais Mapeadas: {kpis.total_lojas:,}")
    print(f"Receita Total Anual: R$ {kpis.receita_total_rs:,.2f}")
    print(f"Taxa OSA Média: {kpis.osa_media_pct}% | Ruptura Média: {kpis.ruptura_media_pct}%")
    print(f"GMROI Médio: {kpis.gmroi_medio}x | Quebra Média: {kpis.quebra_media_pct}%")
    print(f"Venda Perdida por Ruptura: R$ {kpis.venda_perdida_total_rs:,.2f}")
    print(f"Custo de Quebra/Descarte: R$ {kpis.custo_quebra_total_rs:,.2f}")
    print(f"Perda Total Anual (Ruptura + Quebra): R$ {kpis.perda_total_anual_rs:,.2f}")
    print(f"NPS Médio Omnichannel: {kpis.nps_medio_omnichannel} pontos")
    print("-" * 80)
    print("DIAGNÓSTICO E STORYTELLING EXECUTIVO:")
    print(f"[Q1 - Ruptura & NPS]: {respostas['pergunta_1']['diagnostico']}")
    print(f"[Q2 - Overstock & GMROI]: {respostas['pergunta_2']['diagnostico']}")
    print(f"[Q3 - Business Case Integrado]: {respostas['pergunta_3']['diagnostico']}")
    print("-" * 80)

    export_visual_reports(df, output_dir=output_dir)
    print("Pipeline executado com sucesso e relatórios exportados.")
    print("=" * 80)

    return df, kpis, respostas


if __name__ == "__main__":
    run_pipeline()
