"""
AeroYield Analytics: Pipeline Executivo de Aviação Comercial, Yield RASK/CASK & Pontualidade OTP.

Este script implementa a ingestão, engenharia de atributos vetorizada, regras de negócio da aviação
comercial (padrão ANAC / IATA) e storytelling analítico executivo para responder às 3 perguntas
críticas sobre Load Factor, pontualidade OTP D-15, custos da Resolução ANAC 400 e ROI do pacote
integrado Revenue Management + Turnaround Digital 30min + Eficiência QAV & Ancilares.

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
class AviationConfig:
    """Configurações e parâmetros de negócio para a malha aérea comercial."""

    random_seed: int = 42
    suboccupied_load_factor_threshold: float = 74.0
    high_demand_load_factor_threshold: float = 85.0
    world_class_otp_threshold: float = 85.0
    attention_otp_threshold: float = 75.0
    critical_turnaround_minutes: int = 42
    anac400_reduction_pct: float = 0.58
    qav_reduction_pct: float = 0.45
    idleness_recovery_pct: float = 0.70
    ancillary_boost_per_pax_rs: float = 4.50
    package_investment_rs: float = 12_500_000.0
    output_dir: Path = Path("relatorios_aviacao_yield")
    dataset_filename: str = "dataset_aviacao_yield_rotas.csv"


@dataclass(frozen=True)
class AviationKpiSummary:
    """Estrutura imutável com os KPIs consolidados da malha aérea."""

    total_rotas: int
    total_voos_anuais: int
    total_passageiros_anuais: int
    receita_total_rs: float
    load_factor_medio_pct: float
    otp_d15_medio_pct: float
    rask_medio_centavos: float
    cask_medio_centavos: float
    spread_medio_centavos: float
    custo_anac400_total_rs: float
    custo_excesso_qav_total_rs: float
    perda_ociosidade_total_rs: float
    impacto_financeiro_total_rs: float


def classify_load_factor(load_factor_pct: float) -> str:
    """Classifica a eficiência de ocupação da aeronave (Load Factor) - Versão Escalar.

    Args:
        load_factor_pct: Taxa de ocupação da aeronave em percentual.

    Returns:
        Classificação textual ('Subocupada (< 74%)', 'Equilíbrio (74% - 84.9%)',
        ou 'Alta Demanda (>= 85%)').
    """
    if load_factor_pct < 74.0:
        return "Subocupada (< 74%)"
    if load_factor_pct >= 85.0:
        return "Alta Demanda (>= 85%)"
    return "Equilíbrio (74% - 84.9%)"


def classify_load_factor_vectorized(
    series: pd.Series,
    config: AviationConfig = AviationConfig(),
) -> pd.Series:
    """Classifica vetorizadamente o Load Factor das rotas via NumPy select.

    Args:
        series: Série do Pandas contendo o percentual de ocupação.
        config: Instância de configuração contendo os limiares.

    Returns:
        pd.Series com os tiers de ocupação padronizados.
    """
    conditions = [
        series < config.suboccupied_load_factor_threshold,
        series >= config.high_demand_load_factor_threshold,
    ]
    choices = [
        "Subocupada (< 74%)",
        "Alta Demanda (>= 85%)",
    ]
    return pd.Series(
        np.select(conditions, choices, default="Equilíbrio (74% - 84.9%)"),
        index=series.index,
    )


def classify_otp_performance(otp_d15_pct: float) -> str:
    """Classifica a pontualidade operacional padrão IATA D-15 - Versão Escalar.

    Args:
        otp_d15_pct: Percentual de voos que decolaram/pousaram em até 15 minutos do horário.

    Returns:
        Classificação operacional de pontualidade.
    """
    if otp_d15_pct >= 85.0:
        return "Pontualidade Classe Mundial (>= 85%)"
    if otp_d15_pct >= 75.0:
        return "Atenção Operacional (75% - 84.9%)"
    return "Crítico / Efeito Cascata (< 75%)"


def classify_otp_performance_vectorized(
    series: pd.Series,
    config: AviationConfig = AviationConfig(),
) -> pd.Series:
    """Classifica vetorizadamente o nível de pontualidade OTP D-15 via NumPy select.

    Args:
        series: Série do Pandas contendo os índices de OTP D-15.
        config: Instância de configuração contendo os limites.

    Returns:
        pd.Series com a faixa de pontualidade operacional.
    """
    conditions = [
        series >= config.world_class_otp_threshold,
        series >= config.attention_otp_threshold,
    ]
    choices = [
        "Pontualidade Classe Mundial (>= 85%)",
        "Atenção Operacional (75% - 84.9%)",
    ]
    return pd.Series(
        np.select(conditions, choices, default="Crítico / Efeito Cascata (< 75%)"),
        index=series.index,
    )


def generate_aviation_network_dataset(
    num_routes: int = 500,
    seed: int = 42,
) -> pd.DataFrame:
    """Gera base sintética determinística de 500 rotas comerciais brasileiras.

    Modela rotas com hubs estratégicos, famílias de aeronaves, perfis de voo,
    métricas de assento-quilômetro (ASK), RASK, CASK, pontualidade OTP e perdas financeiras.

    Args:
        num_routes: Quantidade de rotas a serem simuladas.
        seed: Semente do gerador pseudo-aleatório.

    Returns:
        DataFrame com 22 colunas padronizadas.
    """
    rng = np.random.default_rng(seed)
    hubs: List[str] = [
        "GRU — Guarulhos (SP)",
        "CGH — Congonhas (SP)",
        "VCP — Viracopos (SP)",
        "BSB — Brasília (DF)",
        "GIG — Galeão (RJ)",
    ]
    frotas: List[str] = [
        "Airbus A320neo",
        "Boeing 737 MAX 8",
        "Embraer E195-E2",
        "Airbus A320ceo (Legado)",
    ]
    perfis: List[str] = [
        "Ponte Aérea Corporativa",
        "Troncal Nacional",
        "Lazer & Sazonal Nordeste",
    ]
    assentos_map: Dict[str, int] = {
        "Airbus A320neo": 174,
        "Boeing 737 MAX 8": 186,
        "Embraer E195-E2": 136,
        "Airbus A320ceo (Legado)": 168,
    }

    rows: List[Dict[str, Any]] = []
    for idx in range(1, num_routes + 1):
        hub = str(rng.choice(hubs, p=[0.27, 0.22, 0.19, 0.17, 0.15]))
        frota = str(rng.choice(frotas, p=[0.30, 0.26, 0.22, 0.22]))
        perfil = str(rng.choice(perfis, p=[0.34, 0.36, 0.30]))
        digital = bool(
            rng.random() < (0.46 if hub in ("VCP — Viracopos (SP)", "BSB — Brasília (DF)") else 0.30)
        )

        if perfil == "Ponte Aérea Corporativa":
            distancia_km = int(rng.integers(380, 860))
            voos_anuais = int(rng.integers(240, 420))
            load_factor = float(
                rng.choice(
                    [rng.uniform(66.0, 73.8), rng.uniform(75.0, 84.6), rng.uniform(85.4, 93.2)],
                    p=[0.18, 0.44, 0.38],
                )
            )
        elif perfil == "Troncal Nacional":
            distancia_km = int(rng.integers(920, 2070))
            voos_anuais = int(rng.integers(150, 320))
            load_factor = float(
                rng.choice(
                    [rng.uniform(65.0, 73.8), rng.uniform(74.8, 84.6), rng.uniform(85.1, 92.6)],
                    p=[0.24, 0.46, 0.30],
                )
            )
        else:
            distancia_km = int(rng.integers(1750, 3100))
            voos_anuais = int(rng.integers(150, 320))
            load_factor = float(
                rng.choice(
                    [rng.uniform(63.5, 73.7), rng.uniform(74.5, 84.5), rng.uniform(85.2, 93.2)],
                    p=[0.34, 0.38, 0.28],
                )
            )

        turnaround = float(rng.uniform(30.0, 46.0))
        if hub in ("GRU — Guarulhos (SP)", "CGH — Congonhas (SP)"):
            turnaround += 7.5
        if frota == "Airbus A320ceo (Legado)":
            turnaround += 6.0
        if digital:
            turnaround -= 7.5
        turnaround = float(np.clip(turnaround, 24.0, 62.0))

        otp_d15 = 95.0 - (turnaround - 24.0) * 0.68 + float(rng.normal(0.0, 2.2))
        if frota == "Airbus A320ceo (Legado)":
            otp_d15 -= 3.2
        if digital:
            otp_d15 += 3.0
        otp_d15 = float(np.clip(otp_d15, 62.5, 95.2))

        rask_base = (
            float(rng.uniform(45.5, 55.0))
            if perfil == "Ponte Aérea Corporativa"
            else float(rng.uniform(39.5, 47.5))
            if perfil == "Troncal Nacional"
            else float(rng.uniform(35.5, 43.0))
        )
        if load_factor < 74.0:
            rask_base -= 4.8
        elif load_factor >= 85.0:
            rask_base += 3.2
        rask = round(max(30.5, rask_base), 2)

        cask_base = (
            float(rng.uniform(34.5, 39.7))
            if frota in ("Airbus A320neo", "Boeing 737 MAX 8")
            else float(rng.uniform(35.8, 41.3))
            if frota == "Embraer E195-E2"
            else float(rng.uniform(40.8, 47.6))
        )
        if otp_d15 < 75.0:
            cask_base += 3.4
        if perfil == "Ponte Aérea Corporativa":
            cask_base += 2.2
        cask = round(max(31.0, cask_base), 2)
        spread = round(rask - cask, 2)

        assentos = assentos_map[frota]
        ask_anual = voos_anuais * assentos * distancia_km
        passageiros = int(round(voos_anuais * assentos * (load_factor / 100.0)))
        receita_anual = round((ask_anual * (rask / 100.0)) / 10.0, 2)

        taxa_atraso = max(0.04, (100.0 - otp_d15) / 100.0)
        custo_anac400 = round(passageiros * taxa_atraso * (22.5 if otp_d15 < 75.0 else 10.5), 2)
        fator_qav = (0.048 if frota == "Airbus A320ceo (Legado)" else 0.014) + (
            0.012 if turnaround > 42.0 else 0.004
        )
        custo_qav = round(receita_anual * fator_qav, 2)
        perda_ociosidade = round(receita_anual * (max(0.0, 82.0 - load_factor) / 100.0) * 0.42, 2)
        ancilar_pax = round(
            (54.0 if perfil == "Lazer & Sazonal Nordeste" else 36.0)
            + float(rng.uniform(0.0, 34.0))
            + (4.5 if digital else 0.0),
            2,
        )

        rows.append(
            {
                "rota_id": f"ROT-{5000 + idx}",
                "hub_origem": hub,
                "familia_aeronave": frota,
                "perfil_rota": perfil,
                "voos_anuais": voos_anuais,
                "distancia_km": distancia_km,
                "load_factor_pct": round(load_factor, 1),
                "faixa_load_factor": classify_load_factor(load_factor),
                "otp_d15_pct": round(otp_d15, 1),
                "faixa_otp": classify_otp_performance(otp_d15),
                "turnaround_minutos": int(round(turnaround)),
                "rask_centavos": rask,
                "cask_centavos": cask,
                "spread_rask_cask_centavos": spread,
                "receita_ancilar_por_pax_rs": ancilar_pax,
                "passageiros_anuais": passageiros,
                "receita_anual_rs": receita_anual,
                "custo_anac400_anual_rs": custo_anac400,
                "custo_excesso_qav_anual_rs": custo_qav,
                "perda_ociosidade_anual_rs": perda_ociosidade,
                "impacto_financeiro_total_rs": round(
                    custo_anac400 + custo_qav + perda_ociosidade, 2
                ),
                "possui_turnaround_digital": int(digital),
            }
        )

    return pd.DataFrame(rows)


def load_or_generate_dataset(
    csv_path: Optional[Path] = None,
    num_routes: int = 500,
    seed: int = 42,
) -> pd.DataFrame:
    """Carrega o dataset persistido se existente, ou gera deterministicamente.

    Args:
        csv_path: Caminho opcional do arquivo CSV.
        num_routes: Quantidade de rotas caso geração sintética seja necessária.
        seed: Semente pseudo-aleatória.

    Returns:
        DataFrame com colunas e classificações vetorizadas validadas.
    """
    target_path = csv_path or Path("dataset_aviacao_yield_rotas.csv")
    if target_path.exists():
        df = pd.read_csv(target_path)
    else:
        df = generate_aviation_network_dataset(num_routes=num_routes, seed=seed)
        df.to_csv(target_path, index=False)

    # Garante coerência das classificações com operações vetorizadas de alta performance
    df["faixa_load_factor"] = classify_load_factor_vectorized(df["load_factor_pct"])
    df["faixa_otp"] = classify_otp_performance_vectorized(df["otp_d15_pct"])
    return df


def compute_kpis(df: pd.DataFrame) -> AviationKpiSummary:
    """Calcula KPIs executivos consolidados da malha aérea comercial.

    Args:
        df: DataFrame contendo as rotas e métricas da malha.

    Returns:
        AviationKpiSummary com indicadores agregados.
    """
    rask_medio = round(float(df["rask_centavos"].mean()), 2)
    cask_medio = round(float(df["cask_centavos"].mean()), 2)
    return AviationKpiSummary(
        total_rotas=len(df),
        total_voos_anuais=int(df["voos_anuais"].sum()),
        total_passageiros_anuais=int(df["passageiros_anuais"].sum()),
        receita_total_rs=round(float(df["receita_anual_rs"].sum()), 2),
        load_factor_medio_pct=round(float(df["load_factor_pct"].mean()), 1),
        otp_d15_medio_pct=round(float(df["otp_d15_pct"].mean()), 1),
        rask_medio_centavos=rask_medio,
        cask_medio_centavos=cask_medio,
        spread_medio_centavos=round(rask_medio - cask_medio, 2),
        custo_anac400_total_rs=round(float(df["custo_anac400_anual_rs"].sum()), 2),
        custo_excesso_qav_total_rs=round(float(df["custo_excesso_qav_anual_rs"].sum()), 2),
        perda_ociosidade_total_rs=round(float(df["perda_ociosidade_anual_rs"].sum()), 2),
        impacto_financeiro_total_rs=round(float(df["impacto_financeiro_total_rs"].sum()), 2),
    )


def responder_pergunta_1(
    df: pd.DataFrame,
    config: AviationConfig = AviationConfig(),
) -> Dict[str, Any]:
    """Responde à Pergunta 1: Impacto da frota e rotas subocupadas no Spread Unitário.

    Pergunta: Como a frota legada e a subocupação afetam o CASK e o spread unitário?
    """
    resumo_frota = (
        df.groupby("familia_aeronave")
        .agg(
            rotas=("rota_id", "count"),
            rask_medio=("rask_centavos", "mean"),
            cask_medio=("cask_centavos", "mean"),
            spread_medio=("spread_rask_cask_centavos", "mean"),
            load_factor_medio=("load_factor_pct", "mean"),
            receita_total_rs=("receita_anual_rs", "sum"),
        )
        .round(2)
        .to_dict(orient="index")
    )

    mask_sub = df["load_factor_pct"] < config.suboccupied_load_factor_threshold
    qtd_subocupadas = int(mask_sub.sum())
    pct_subocupadas = round((qtd_subocupadas / len(df)) * 100.0, 1)
    perda_ociosidade_sub = round(float(df.loc[mask_sub, "perda_ociosidade_anual_rs"].sum()), 2)
    perda_ociosidade_total = round(float(df["perda_ociosidade_anual_rs"].sum()), 2)

    spread_ceo = resumo_frota.get("Airbus A320ceo (Legado)", {}).get("spread_medio", -1.64)
    spread_neo = resumo_frota.get("Airbus A320neo", {}).get("spread_medio", 6.40)
    spread_max = resumo_frota.get("Boeing 737 MAX 8", {}).get("spread_medio", 6.45)
    gap_spread_centavos = round(spread_neo - spread_ceo, 2)

    return {
        "resumo_por_frota": resumo_frota,
        "spread_a320ceo_centavos": spread_ceo,
        "spread_a320neo_centavos": spread_neo,
        "spread_737max_centavos": spread_max,
        "gap_cask_ceo_vs_neo_centavos": gap_spread_centavos,
        "qtd_rotas_subocupadas": qtd_subocupadas,
        "pct_rotas_subocupadas": pct_subocupadas,
        "perda_ociosidade_total_rs": perda_ociosidade_total,
        "diagnostico": (
            f"O Airbus A320ceo Legado opera com spread unitário negativo ({spread_ceo:+.2f}c/ASK), "
            f"apresentando um CASK até {gap_spread_centavos:.2f}c superior ao A320neo/737 MAX 8. "
            f"Adicionalmente, {qtd_subocupadas} rotas ({pct_subocupadas}% da malha) estão subocupadas (< 74%), "
            f"gerando R$ {perda_ociosidade_total:,.2f} de perda anual por assentos ociosos."
        ),
        "acao_recomendada": (
            "Acelerar o phase-out do A320ceo substituindo-o por A320neo/MAX 8 em rotas de alta densidade "
            "e right-sizing com Embraer E195-E2 em rotas regionais, combinado com motor de Revenue Management "
            "dinâmico para recuperar +3,4 p.p. de Load Factor."
        ),
    }


def responder_pergunta_2(
    df: pd.DataFrame,
    config: AviationConfig = AviationConfig(),
) -> Dict[str, Any]:
    """Responde à Pergunta 2: Gargalos de Turnaround em solo e custos da Resolução ANAC 400.

    Pergunta: Onde estão os gargalos de turnaround em solo e como eles disparam as despesas da ANAC 400?
    """
    mask_critico = df["turnaround_minutos"] > config.critical_turnaround_minutes
    df_critico = df[mask_critico]
    df_controlado = df[~mask_critico]

    qtd_rotas_criticas = int(mask_critico.sum())
    pct_rotas_criticas = round((qtd_rotas_criticas / len(df)) * 100.0, 1)

    custo_anac400_critico = round(float(df_critico["custo_anac400_anual_rs"].sum()), 2)
    custo_anac400_total = round(float(df["custo_anac400_anual_rs"].sum()), 2)
    pct_anac400_concentrado = round((custo_anac400_critico / custo_anac400_total) * 100.0, 1)

    otp_critico = round(float(df_critico["otp_d15_pct"].mean()), 1)
    otp_controlado = round(float(df_controlado["otp_d15_pct"].mean()), 1)
    gap_otp = round(otp_controlado - otp_critico, 1)

    # Detalhamento por Hub
    resumo_hubs = (
        df.groupby("hub_origem")
        .agg(
            rotas=("rota_id", "count"),
            turnaround_medio=("turnaround_minutos", "mean"),
            otp_medio=("otp_d15_pct", "mean"),
            custo_anac400_total=("custo_anac400_anual_rs", "sum"),
            custo_anac400_medio=("custo_anac400_anual_rs", "mean"),
        )
        .round(2)
        .sort_values("custo_anac400_total", ascending=False)
        .to_dict(orient="index")
    )

    custo_gru = resumo_hubs.get("GRU — Guarulhos (SP)", {}).get("custo_anac400_total", 0.0)
    custo_cgh = resumo_hubs.get("CGH — Congonhas (SP)", {}).get("custo_anac400_total", 0.0)
    pct_gru_cgh = round(((custo_gru + custo_cgh) / custo_anac400_total) * 100.0, 1)

    return {
        "qtd_rotas_turnaround_critico": qtd_rotas_criticas,
        "pct_rotas_turnaround_critico": pct_rotas_criticas,
        "custo_anac400_critico_rs": custo_anac400_critico,
        "custo_anac400_total_rs": custo_anac400_total,
        "pct_anac400_concentrado_em_turnaround_critico": pct_anac400_concentrado,
        "otp_medio_critico_pct": otp_critico,
        "otp_medio_controlado_pct": otp_controlado,
        "gap_otp_pontos": gap_otp,
        "resumo_por_hub": resumo_hubs,
        "pct_anac400_gru_cgh": pct_gru_cgh,
        "diagnostico": (
            f"Rotas com turnaround em solo superior a 42 minutos representam {qtd_rotas_criticas} rotas "
            f"({pct_rotas_criticas}% da malha), mas concentram {pct_anac400_concentrado}% de todas as "
            f"despesas da Resolução ANAC 400 da companhia (R$ {custo_anac400_critico:,.2f}). "
            f"O OTP D-15 colapsa para {otp_critico}% (gap de -{gap_otp} p.p.). Os hubs GRU e CGH respondem "
            f"por {pct_gru_cgh}% do total de multas e custos assistenciais aos passageiros."
        ),
        "acao_recomendada": (
            "Implantar o programa 'Turnaround Digital 30 min' integrando telemetria de rampa, "
            "despacho automatizado e biometria de embarque para reduzir o tempo médio de solo em 8 minutos "
            "e cortar 58% das despesas de assistência ao passageiro."
        ),
    }


def responder_pergunta_3(
    df: pd.DataFrame,
    config: AviationConfig = AviationConfig(),
) -> Dict[str, Any]:
    """Responde à Pergunta 3: Retorno financeiro e ROI do pacote integrado AeroYield.

    Pergunta: Qual o retorno financeiro do pacote integrado (Revenue Management + Turnaround Digital + Eficiência QAV & Ancilares)?
    """
    total_anac400 = float(df["custo_anac400_anual_rs"].sum())
    total_qav = float(df["custo_excesso_qav_anual_rs"].sum())
    total_ociosidade = float(df["perda_ociosidade_anual_rs"].sum())
    total_pax = int(df["passageiros_anuais"].sum())

    # 1. Revenue Management: recupera 70% da perda de ociosidade
    recuperacao_ociosidade = total_ociosidade * config.idleness_recovery_pct

    # 2. Turnaround Digital: corta 58% das despesas ANAC 400
    economia_anac400 = total_anac400 * config.anac400_reduction_pct

    # 3. Eficiência de QAV: corta 45% do excesso de consumo de combustível
    economia_qav = total_qav * config.qav_reduction_pct

    # 4. Monetização Ancilar: expansão de R$ 4.50 por passageiro embarcado
    ganho_ancilar = total_pax * config.ancillary_boost_per_pax_rs

    # Ganhos consolidados
    ganho_operacional_anual = recuperacao_ociosidade + economia_anac400 + economia_qav
    ganho_total_com_ancilares = ganho_operacional_anual + ganho_ancilar
    investimento_total = config.package_investment_rs
    retorno_liquido_ano1 = ganho_total_com_ancilares - investimento_total

    payback_meses = round((investimento_total / ganho_total_com_ancilares) * 12.0, 2)
    payback_operacional_meses = round((investimento_total / ganho_operacional_anual) * 12.0, 2)
    roi_ano1_multiplicador = round(ganho_total_com_ancilares / investimento_total, 2)
    roi_operacional_ano1 = round(ganho_operacional_anual / investimento_total, 2)

    return {
        "recuperacao_ociosidade_rs": round(recuperacao_ociosidade, 2),
        "economia_anac400_rs": round(economia_anac400, 2),
        "economia_qav_rs": round(economia_qav, 2),
        "ganho_ancilar_rs": round(ganho_ancilar, 2),
        "ganho_operacional_anual_rs": round(ganho_operacional_anual, 2),
        "ganho_total_anual_rs": round(ganho_total_com_ancilares, 2),
        "investimento_total_rs": round(investimento_total, 2),
        "retorno_liquido_ano1_rs": round(retorno_liquido_ano1, 2),
        "payback_meses": payback_meses,
        "payback_operacional_meses": payback_operacional_meses,
        "roi_ano1_multiplicador": roi_ano1_multiplicador,
        "roi_operacional_ano1": roi_operacional_ano1,
        "diagnostico": (
            f"O pacote integrado gera R$ {ganho_total_com_ancilares:,.2f}/ano em valor corporativo recorrente "
            f"(R$ {ganho_operacional_anual:,.2f} em eficiência operacional direta + "
            f"R$ {ganho_ancilar:,.2f} em expansão de receitas ancilares). Com Capex/Opex de implantação de "
            f"R$ {investimento_total:,.2f}, o payback total é atingido em apenas {payback_meses} meses "
            f"({payback_operacional_meses} meses considerando apenas eficiências operacionais puras), "
            f"com ROI de {roi_ano1_multiplicador}x no primeiro ano."
        ),
        "acao_recomendada": (
            "Aprovar imediatamente a esteira de implantação em duas fases: Fase 1 (primeiros 60 dias) "
            "com Turnaround Digital nos hubs de Congonhas e Guarulhos; Fase 2 (dias 61-120) com roll-out "
            "do motor de Revenue Management e otimização de queima de QAV em toda a malha."
        ),
    }


def answer_business_questions(
    df: pd.DataFrame,
    config: AviationConfig = AviationConfig(),
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
        df: DataFrame com dados da aviação comercial.
        output_dir: Diretório de destino para exportação.
    """
    target_dir = output_dir or Path("relatorios_aviacao_yield")
    target_dir.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", palette="crest")

    # Gráfico 1: Spread RASK - CASK por Frota
    fig, ax = plt.subplots(figsize=(10, 6))
    order = [
        "Airbus A320neo",
        "Boeing 737 MAX 8",
        "Embraer E195-E2",
        "Airbus A320ceo (Legado)",
    ]
    sns.boxplot(
        data=df,
        x="familia_aeronave",
        y="spread_rask_cask_centavos",
        order=order,
        hue="familia_aeronave",
        legend=False,
        palette=["#10b981", "#059669", "#3b82f6", "#ef4444"],
        ax=ax,
    )
    ax.axhline(0.0, color="#dc2626", linestyle="--", linewidth=1.4, label="Break-Even Spread (0c/ASK)")
    ax.set_title("AeroYield: Spread Unitário (RASK − CASK) por Família de Aeronave", fontsize=13, fontweight="bold")
    ax.set_xlabel("Família de Aeronave", fontsize=11)
    ax.set_ylabel("Spread Unitário (R$ centavos / ASK)", fontsize=11)
    ax.legend(loc="upper right")
    plt.xticks(rotation=15)
    plt.tight_layout()
    fig.savefig(target_dir / "01_spread_rask_cask_por_frota.png", dpi=300)
    plt.close(fig)

    # Gráfico 2: Custo ANAC 400 por Hub de Origem
    hub_anac = (
        df.groupby("hub_origem", as_index=False)["custo_anac400_anual_rs"]
        .sum()
        .sort_values("custo_anac400_anual_rs", ascending=False)
    )
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(
        data=hub_anac,
        x="custo_anac400_anual_rs",
        y="hub_origem",
        hue="hub_origem",
        legend=False,
        palette="rocket",
        ax=ax,
    )
    ax.set_title("AeroYield: Custo Anual com Resolução ANAC 400 por Hub de Origem (R$)", fontsize=13, fontweight="bold")
    ax.set_xlabel("Custo Anual Total com Assistência a Passageiros (R$)", fontsize=11)
    ax.set_ylabel("Hub Aeroportuário de Origem", fontsize=11)
    plt.tight_layout()
    fig.savefig(target_dir / "02_custo_anac400_por_hub.png", dpi=300)
    plt.close(fig)

    # Gráfico 3: Painel Interativo Plotly HTML
    fig_plotly = px.scatter(
        df,
        x="turnaround_minutos",
        y="otp_d15_pct",
        size="impacto_financeiro_total_rs",
        color="faixa_load_factor",
        hover_data=[
            "rota_id",
            "hub_origem",
            "familia_aeronave",
            "load_factor_pct",
            "spread_rask_cask_centavos",
            "custo_anac400_anual_rs",
        ],
        title="AeroYield Analytics: Turnaround em Solo vs. Pontualidade OTP D-15 & Impacto Financeiro",
        labels={
            "turnaround_minutos": "Tempo de Turnaround em Solo (min)",
            "otp_d15_pct": "Pontualidade OTP D-15 (%)",
            "impacto_financeiro_total_rs": "Impacto Financeiro (R$)",
            "faixa_load_factor": "Faixa de Ocupação",
        },
        template="plotly_dark",
    )
    fig_plotly.write_html(str(target_dir / "painel_aviacao_yield.html"))


def run_pipeline(
    csv_path: Optional[Path] = None,
    output_dir: Optional[Path] = None,
) -> Tuple[pd.DataFrame, AviationKpiSummary, Dict[str, Dict[str, Any]]]:
    """Executa o pipeline completo AeroYield ponta a ponta.

    Args:
        csv_path: Caminho opcional do arquivo CSV.
        output_dir: Diretório de destino dos relatórios.

    Returns:
        Tupla com (DataFrame processado, AviationKpiSummary, Dicionário com respostas das 3 perguntas).
    """
    config = AviationConfig()
    print("=" * 80)
    print("AEROYIELD ANALYTICS: MALHA AÉREA COMERCIAL, YIELD RASK/CASK & PONTUALIDADE OTP")
    print("=" * 80)

    df = load_or_generate_dataset(csv_path=csv_path, num_routes=500, seed=config.random_seed)
    kpis = compute_kpis(df)
    respostas = answer_business_questions(df, config=config)

    print(f"Rotas Analisadas: {kpis.total_rotas:,} | Voos Totais Anuais: {kpis.total_voos_anuais:,}")
    print(f"Passageiros Anuais: {kpis.total_passageiros_anuais:,} | Receita Anual: R$ {kpis.receita_total_rs:,.2f}")
    print(f"Load Factor Médio: {kpis.load_factor_medio_pct}% | Pontualidade OTP D-15 Média: {kpis.otp_d15_medio_pct}%")
    print(f"RASK Médio: {kpis.rask_medio_centavos}c/ASK | CASK Médio: {kpis.cask_medio_centavos}c/ASK")
    print(f"Spread Médio Unitário: {kpis.spread_medio_centavos:+.2f}c/ASK")
    print(f"Custo ANAC 400 Total: R$ {kpis.custo_anac400_total_rs:,.2f}")
    print(f"Custo Excesso QAV: R$ {kpis.custo_excesso_qav_total_rs:,.2f}")
    print(f"Perda por Ociosidade: R$ {kpis.perda_ociosidade_total_rs:,.2f}")
    print(f"Impacto Financeiro Oportunidade: R$ {kpis.impacto_financeiro_total_rs:,.2f}")
    print("-" * 80)
    print("DIAGNÓSTICO E STORYTELLING EXECUTIVO:")
    print(f"[Q1 - Frota & Spread]: {respostas['pergunta_1']['diagnostico']}")
    print(f"[Q2 - Turnaround & ANAC 400]: {respostas['pergunta_2']['diagnostico']}")
    print(f"[Q3 - Business Case Integrado]: {respostas['pergunta_3']['diagnostico']}")
    print("-" * 80)

    export_visual_reports(df, output_dir=output_dir)
    print("Pipeline executado com sucesso e relatórios exportados.")
    print("=" * 80)

    return df, kpis, respostas


def main() -> None:
    """Função principal para execução CLI."""
    run_pipeline()


if __name__ == "__main__":
    main()
