"""ForgeIQ Analytics: Pipeline de OEE Industrial, Downtime, Scrap e Manutenção Preditiva.

Autor: Wendell Barbosa Costa
Segmento: IndustryTech & Manufatura Inteligente (Indústria 4.0 / ISO 10816-3)
Padrão de Código: PEP 8, Type Hints estritos e Docstrings Google Style.

Regras de Negócio Aplicadas:
    1. OEE (Overall Equipment Effectiveness) = Disponibilidade * Performance * Qualidade.
       Benchmark World-Class: >= 85.0% | Competitiva: 72-84.9% | Atenção: 65-71.9% | Crítico: < 65.0%.
    2. Zona de Vibração ISO 10816-3 (mm/s RMS):
       - Normal / Zona A/B (<= 2.8 mm/s)
       - Alerta / Zona C (2.8 a 6.0 mm/s)
       - Crítica / Risco de Falha / Zona D (> 6.0 mm/s)
    3. Custo de Downtime Não Planejado = Horas Paradas * Custo Hora Linha (R$/h) * 12 meses.
    4. Custo de Refugo (Scrap Loss) = Peças Refugadas * Custo Unitário MP/Conversão * 12 meses.
    5. Viabilidade de Capex em Manutenção Preditiva IoT (CBM): Redução de 58% em downtime e 45% em refugo.
"""

from dataclasses import dataclass
import os
from pathlib import Path
import sys
from typing import Dict, List, Tuple
import warnings

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns

# Configuração de encoding UTF-8 no stdout para compatibilidade com console Windows
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

warnings.filterwarnings("ignore")

# Configuração estética global para gráficos corporativos
sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams["figure.dpi"] = 300
plt.rcParams["axes.titlesize"] = 13
plt.rcParams["axes.labelsize"] = 11


@dataclass(frozen=True)
class IndustryConfig:
    """Parâmetros corporativos e benchmarks industriais da planta."""

    n_maquinas: int = 500
    random_seed: int = 42
    horas_programadas_mes: float = 520.0
    oee_world_class_pct: float = 85.0
    oee_critico_pct: float = 65.0
    vibracao_critica_mm_s: float = 6.0
    custo_sensor_iot_maquina_rs: float = 18500.0
    reducao_downtime_cbm: float = 0.58
    reducao_scrap_cbm: float = 0.45
    output_dir: str = "relatorios_industrytech"


def classificar_faixa_oee(oee_pct: float) -> str:
    """Classifica a eficiência global do equipamento (OEE) de forma escalar."""
    if oee_pct >= 85.0:
        return "World-Class (>= 85%)"
    if oee_pct >= 72.0:
        return "Competitiva (72% - 84.9%)"
    if oee_pct >= 65.0:
        return "Atenção (65% - 71.9%)"
    return "Crítica (< 65%)"


def classificar_zona_iso_vibracao(vibracao_mm_s: float) -> str:
    """Classifica severidade mecânica conforme norma ISO 10816-3 de forma escalar."""
    if vibracao_mm_s > 6.0:
        return "Zona D: Crítica (> 6.0 mm/s)"
    if vibracao_mm_s > 2.8:
        return "Zona C: Alerta (2.8 - 6.0 mm/s)"
    return "Zona A/B: Normal (<= 2.8 mm/s)"


def classificar_faixa_oee_vetorizado(s_oee: pd.Series) -> pd.Series:
    """Classificação vetorizada de OEE de alta performance via np.select."""
    condicoes = [
        s_oee >= 85.0,
        s_oee >= 72.0,
        s_oee >= 65.0,
    ]
    escolhas = [
        "World-Class (>= 85%)",
        "Competitiva (72% - 84.9%)",
        "Atenção (65% - 71.9%)",
    ]
    return pd.Series(
        np.select(condicoes, escolhas, default="Crítica (< 65%)"),
        index=s_oee.index,
    )


def classificar_zona_iso_vibracao_vetorizado(s_vibracao: pd.Series) -> pd.Series:
    """Classificação vetorizada de vibração mecânica ISO 10816-3 via np.select."""
    condicoes = [
        s_vibracao > 6.0,
        s_vibracao > 2.8,
    ]
    escolhas = [
        "Zona D: Crítica (> 6.0 mm/s)",
        "Zona C: Alerta (2.8 - 6.0 mm/s)",
    ]
    return pd.Series(
        np.select(condicoes, escolhas, default="Zona A/B: Normal (<= 2.8 mm/s)"),
        index=s_vibracao.index,
    )


def gerar_dataset_industrial(config: IndustryConfig = IndustryConfig()) -> pd.DataFrame:
    """Gera base sintética realista de ativos fabris distribuídos em plantas brasileiras."""
    rng = np.random.default_rng(config.random_seed)

    plantas: List[str] = [
        "ABC Paulista (SP)",
        "Betim (MG)",
        "Joinville (SC)",
        "Curitiba (PR)",
        "Camaçari (BA)",
    ]
    pesos_plantas: List[float] = [0.30, 0.24, 0.20, 0.14, 0.12]

    setores: List[str] = [
        "Usinagem CNC",
        "Estamparia Pesada",
        "Injeção Termoplástica",
        "Solda Robotizada",
        "Montagem & Acabamento",
    ]
    pesos_setores: List[float] = [0.28, 0.22, 0.22, 0.16, 0.12]

    estrategias_manutencao: List[str] = [
        "Corretiva (Run-to-Failure)",
        "Preventiva Calendário",
        "Preditiva IoT (CBM)",
    ]

    registros: List[Dict[str, object]] = []

    for idx in range(1, config.n_maquinas + 1):
        planta = str(rng.choice(plantas, p=pesos_plantas))
        setor = str(rng.choice(setores, p=pesos_setores))

        # Mix de maturidade de manutenção por planta
        if planta in ("Joinville (SC)", "Curitiba (PR)"):
            probs_est = [0.25, 0.40, 0.35]
        elif planta == "ABC Paulista (SP)":
            probs_est = [0.38, 0.38, 0.24]
        else:
            probs_est = [0.52, 0.33, 0.15]

        estrategia = str(rng.choice(estrategias_manutencao, p=probs_est))

        # Custo hora de linha parada e custo unitário de refugo por setor
        custo_hora_map = {
            "Estamparia Pesada": (14500.0, 21000.0, 185.0),
            "Usinagem CNC": (11000.0, 16500.0, 140.0),
            "Solda Robotizada": (13000.0, 19500.0, 160.0),
            "Injeção Termoplástica": (8500.0, 13000.0, 75.0),
            "Montagem & Acabamento": (7500.0, 11500.0, 95.0),
        }
        min_ch, max_ch, custo_peca = custo_hora_map[setor]
        custo_hora_parada = float(np.round(rng.uniform(min_ch, max_ch), 2))

        # Telemetria física conforme estratégia de manutenção
        if estrategia == "Preditiva IoT (CBM)":
            vibracao = float(np.round(rng.normal(2.1, 0.55), 2))
            temp_rolamento = float(np.round(rng.normal(56.0, 5.5), 1))
            horas_parada_nao_plan = float(np.round(rng.uniform(4.0, 18.0), 1))
            falhas_mes = int(rng.integers(1, 3))
            performance_pct = float(np.round(rng.uniform(86.0, 96.5), 1))
            scrap_rate_pct = float(np.round(rng.uniform(0.8, 2.4), 2))
        elif estrategia == "Preventiva Calendário":
            vibracao = float(np.round(rng.normal(3.9, 1.15), 2))
            temp_rolamento = float(np.round(rng.normal(66.5, 8.0), 1))
            horas_parada_nao_plan = float(np.round(rng.uniform(16.0, 44.0), 1))
            falhas_mes = int(rng.integers(2, 6))
            performance_pct = float(np.round(rng.uniform(78.0, 90.0), 1))
            scrap_rate_pct = float(np.round(rng.uniform(1.8, 4.5), 2))
        else:  # Corretiva (Run-to-Failure)
            vibracao = float(np.round(rng.normal(6.4, 1.65), 2))
            temp_rolamento = float(np.round(rng.normal(79.0, 10.5), 1))
            horas_parada_nao_plan = float(np.round(rng.uniform(38.0, 98.0), 1))
            falhas_mes = int(rng.integers(4, 11))
            performance_pct = float(np.round(rng.uniform(68.0, 84.0), 1))
            scrap_rate_pct = float(np.round(rng.uniform(3.4, 8.8), 2))

        vibracao = max(0.8, min(11.5, vibracao))
        temp_rolamento = max(38.0, min(108.0, temp_rolamento))

        # Disponibilidade líquida (%)
        horas_disponiveis = max(
            100.0, config.horas_programadas_mes - horas_parada_nao_plan
        )
        disponibilidade_pct = float(
            np.round((horas_disponiveis / config.horas_programadas_mes) * 100.0, 1)
        )
        qualidade_pct = float(np.round(100.0 - scrap_rate_pct, 2))

        # Cálculo clássico de OEE
        oee_pct = float(
            np.round(
                (disponibilidade_pct / 100.0)
                * (performance_pct / 100.0)
                * (qualidade_pct / 100.0)
                * 100.0,
                1,
            )
        )

        # Volume de produção e custos financeiros (anualizados x 12)
        cadencia_pecas_hora = float(rng.integers(110, 260))
        pecas_produzidas_mes = int(
            horas_disponiveis * cadencia_pecas_hora * (performance_pct / 100.0)
        )
        pecas_refugadas_mes = int(pecas_produzidas_mes * (scrap_rate_pct / 100.0))

        custo_downtime_anual = float(
            np.round(horas_parada_nao_plan * custo_hora_parada * 12.0, 2)
        )
        custo_scrap_anual = float(
            np.round(pecas_refugadas_mes * custo_peca * 12.0, 2)
        )
        custo_manutencao_anual = float(
            np.round(
                (
                    falhas_mes * 8200.0
                    if estrategia == "Corretiva (Run-to-Failure)"
                    else falhas_mes * 3800.0
                )
                * 12.0,
                2,
            )
        )

        mtbf_horas = float(np.round(horas_disponiveis / max(1, falhas_mes), 1))
        mttr_horas = float(np.round(horas_parada_nao_plan / max(1, falhas_mes), 1))

        registros.append(
            {
                "ativo_id": f"MAQ-{2000 + idx}",
                "planta_industrial": planta,
                "setor_produtivo": setor,
                "estrategia_manutencao": estrategia,
                "sensores_iot_instalados": estrategia == "Preditiva IoT (CBM)",
                "disponibilidade_pct": disponibilidade_pct,
                "performance_pct": performance_pct,
                "qualidade_pct": qualidade_pct,
                "oee_pct": oee_pct,
                "scrap_rate_pct": scrap_rate_pct,
                "vibracao_rms_mm_s": vibracao,
                "temperatura_mancal_c": temp_rolamento,
                "horas_parada_mes": horas_parada_nao_plan,
                "mtbf_horas": mtbf_horas,
                "mttr_horas": mttr_horas,
                "custo_downtime_anual_rs": custo_downtime_anual,
                "custo_scrap_anual_rs": custo_scrap_anual,
                "custo_manutencao_anual_rs": custo_manutencao_anual,
                "custo_hora_parada_rs": custo_hora_parada,
            }
        )

    df = pd.DataFrame(registros)
    # Classificações vetorizadas com np.select
    df["faixa_oee"] = classificar_faixa_oee_vetorizado(df["oee_pct"])
    df["zona_iso_vibracao"] = classificar_zona_iso_vibracao_vetorizado(
        df["vibracao_rms_mm_s"]
    )
    df["perda_total_anual_rs"] = (
        df["custo_downtime_anual_rs"] + df["custo_scrap_anual_rs"]
    ).round(2)
    return df


def calcular_kpis_executivos(df: pd.DataFrame) -> Dict[str, float]:
    """Consolida KPIs corporativos de desempenho fabril e perdas financeiras."""
    return {
        "total_ativos": float(len(df)),
        "oee_medio_pct": round(float(df["oee_pct"].mean()), 2),
        "disponibilidade_media_pct": round(float(df["disponibilidade_pct"].mean()), 2),
        "performance_media_pct": round(float(df["performance_pct"].mean()), 2),
        "qualidade_media_pct": round(float(df["qualidade_pct"].mean()), 2),
        "scrap_rate_medio_pct": round(float(df["scrap_rate_pct"].mean()), 2),
        "mtbf_medio_horas": round(float(df["mtbf_horas"].mean()), 1),
        "mttr_medio_horas": round(float(df["mttr_horas"].mean()), 1),
        "custo_downtime_total_rs": round(float(df["custo_downtime_anual_rs"].sum()), 2),
        "custo_scrap_total_rs": round(float(df["custo_scrap_anual_rs"].sum()), 2),
        "perda_total_operacional_rs": round(
            float(df["custo_downtime_anual_rs"].sum() + df["custo_scrap_anual_rs"].sum()), 2
        ),
        "ativos_criticos_oee": float((df["oee_pct"] < 65.0).sum()),
        "adocao_iot_pct": round(float(df["sensores_iot_instalados"].mean() * 100.0), 2),
    }


def responder_perguntas_negocio(
    df: pd.DataFrame, config: IndustryConfig = IndustryConfig()
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, float]]:
    """Executa o Storytelling analítico corporativo focado nas 3 perguntas críticas."""
    # Q1: Concentração de Downtime por Planta
    custo_total_downtime = df["custo_downtime_anual_rs"].sum()
    q1_planta = (
        df.groupby("planta_industrial", as_index=False)
        .agg(
            ativos=("ativo_id", "count"),
            oee_medio=("oee_pct", "mean"),
            horas_parada_mes=("horas_parada_mes", "sum"),
            custo_downtime_anual=("custo_downtime_anual_rs", "sum"),
        )
        .sort_values("custo_downtime_anual", ascending=False)
    )
    q1_planta["share_downtime_pct"] = (
        (q1_planta["custo_downtime_anual"] / custo_total_downtime) * 100.0
    ).round(2)
    q1_planta["oee_medio"] = q1_planta["oee_medio"].round(2)
    q1_planta["horas_parada_mes"] = q1_planta["horas_parada_mes"].round(1)
    q1_planta["custo_downtime_anual"] = q1_planta["custo_downtime_anual"].round(2)

    # Q2: Relação entre Vibração ISO 10816 e Scrap Rate
    custo_total_scrap = df["custo_scrap_anual_rs"].sum()
    q2_vibracao = (
        df.groupby("zona_iso_vibracao", as_index=False)
        .agg(
            ativos=("ativo_id", "count"),
            scrap_medio_pct=("scrap_rate_pct", "mean"),
            custo_scrap_anual=("custo_scrap_anual_rs", "sum"),
            oee_medio=("oee_pct", "mean"),
        )
        .sort_values("scrap_medio_pct", ascending=False)
    )
    q2_vibracao["share_scrap_pct"] = (
        (q2_vibracao["custo_scrap_anual"] / custo_total_scrap) * 100.0
    ).round(2)
    q2_vibracao["scrap_medio_pct"] = q2_vibracao["scrap_medio_pct"].round(2)
    q2_vibracao["custo_scrap_anual"] = q2_vibracao["custo_scrap_anual"].round(2)
    q2_vibracao["oee_medio"] = q2_vibracao["oee_medio"].round(2)

    # Q3: Viabilidade Financeira do Retrofit de Preditiva IoT (CBM)
    ativos_sem_iot = df[~df["sensores_iot_instalados"]]
    capex_iot = len(ativos_sem_iot) * config.custo_sensor_iot_maquina_rs
    economia_downtime = (
        ativos_sem_iot["custo_downtime_anual_rs"].sum()
        * config.reducao_downtime_cbm
    )
    economia_scrap = (
        ativos_sem_iot["custo_scrap_anual_rs"].sum() * config.reducao_scrap_cbm
    )
    beneficio_anual_total = float(economia_downtime + economia_scrap)
    payback_meses = float((capex_iot / max(1.0, beneficio_anual_total)) * 12.0)
    payback_dias = payback_meses * 30.0
    roi_12m = float(beneficio_anual_total / max(1.0, capex_iot))

    q3_business_case = {
        "ativos_elegiveis": float(len(ativos_sem_iot)),
        "capex_iot_rs": round(float(capex_iot), 2),
        "economia_downtime_rs": round(float(economia_downtime), 2),
        "economia_scrap_rs": round(float(economia_scrap), 2),
        "beneficio_anual_total_rs": round(beneficio_anual_total, 2),
        "payback_meses": round(payback_meses, 3),
        "payback_dias": round(payback_dias, 1),
        "roi_12m_x": round(roi_12m, 2),
    }

    return q1_planta, q2_vibracao, q3_business_case


def gerar_visualizacoes(df: pd.DataFrame, config: IndustryConfig = IndustryConfig()) -> None:
    """Gera gráficos estáticos Seaborn (300 DPI) e painel interativo Plotly."""
    out_path = Path(config.output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # 1. Gráfico de Barras: OEE por Planta e Estratégia
    plt.figure(figsize=(10, 5))
    ordem = (
        df.groupby("planta_industrial")["custo_downtime_anual_rs"]
        .sum()
        .sort_values(ascending=False)
        .index
    )
    sns.barplot(
        data=df,
        x="planta_industrial",
        y="oee_pct",
        hue="estrategia_manutencao",
        order=ordem,
        palette="viridis",
    )
    plt.axhline(
        config.oee_world_class_pct,
        color="green",
        linestyle="--",
        linewidth=1.5,
        label=f"Benchmark World-Class ({config.oee_world_class_pct:.0f}%)",
    )
    plt.title("OEE Médio por Planta Industrial e Estratégia de Manutenção")
    plt.ylabel("OEE (%)")
    plt.xlabel("Planta Industrial")
    plt.xticks(rotation=15)
    plt.legend(loc="lower right", fontsize=8)
    plt.tight_layout()
    plt.savefig(out_path / "01_oee_por_planta_e_estrategia.png")
    plt.close()

    # 2. Scatter Plot: Vibração ISO 10816 vs Scrap Rate
    plt.figure(figsize=(9, 5))
    sns.scatterplot(
        data=df,
        x="vibracao_rms_mm_s",
        y="scrap_rate_pct",
        hue="zona_iso_vibracao",
        size="custo_scrap_anual_rs",
        sizes=(30, 260),
        alpha=0.75,
        palette={
            "Zona A/B: Normal (<= 2.8 mm/s)": "#10b981",
            "Zona C: Alerta (2.8 - 6.0 mm/s)": "#f59e0b",
            "Zona D: Crítica (> 6.0 mm/s)": "#ef4444",
        },
    )
    plt.axvline(
        config.vibracao_critica_mm_s,
        color="#ef4444",
        linestyle="--",
        label=f"Limite Crítico ISO 10816 ({config.vibracao_critica_mm_s:.1f} mm/s)",
    )
    plt.title("Impacto da Vibração Mecânica no Desperdício por Refugo (Scrap %)")
    plt.xlabel("Vibração RMS (mm/s)")
    plt.ylabel("Taxa de Refugo / Scrap (%)")
    plt.legend(fontsize=8)
    plt.tight_layout()
    plt.savefig(out_path / "02_vibracao_iso10816_vs_scrap.png")
    plt.close()

    # 3. Painel Interativo Plotly
    fig = px.scatter(
        df,
        x="oee_pct",
        y="perda_total_anual_rs",
        color="estrategia_manutencao",
        size="horas_parada_mes",
        hover_data=["ativo_id", "planta_industrial", "setor_produtivo", "mtbf_horas"],
        title="ForgeIQ — Mapa de Criticidade OEE vs. Perda Financeira Anual (R$)",
        labels={
            "oee_pct": "OEE (%)",
            "perda_total_anual_rs": "Perda Anual (Downtime + Scrap em R$)",
            "estrategia_manutencao": "Estratégia Atual",
        },
        template="plotly_dark",
    )
    fig.write_html(str(out_path / "painel_industrial_interativo.html"))


def main() -> None:
    """Executa o fluxo completo de engenharia e análise industrial."""
    config = IndustryConfig()
    df = gerar_dataset_industrial(config)
    kpis = calcular_kpis_executivos(df)
    q1_planta, q2_vibracao, q3_roi = responder_perguntas_negocio(df, config)

    gerar_visualizacoes(df, config)
    df.to_csv("dataset_industrytech_oee.csv", index=False)

    print("=" * 78)
    print("FORGEIQ ANALYTICS: DIAGNÓSTICO DE OEE, SCRAP E MANUTENÇÃO PREDITIVA IoT")
    print("=" * 78)
    print(f"Ativos Monitorados:            {int(kpis['total_ativos'])} máquinas")
    print(f"OEE Médio Global:              {kpis['oee_medio_pct']:.1f}% (Benchmark World-Class: 85.0%)")
    print(f"Disponibilidade Média:         {kpis['disponibilidade_media_pct']:.1f}%")
    print(f"Performance Operacional Média: {kpis['performance_media_pct']:.1f}%")
    print(f"Qualidade Média:               {kpis['qualidade_media_pct']:.1f}%")
    print(f"Scrap Rate Médio:              {kpis['scrap_rate_medio_pct']:.2f}%")
    print(f"Perda Anual por Downtime:      R$ {kpis['custo_downtime_total_rs']:,.2f}")
    print(f"Perda Anual por Scrap/Refugo:  R$ {kpis['custo_scrap_total_rs']:,.2f}")
    print(f"Perda Operacional Total:       R$ {kpis['perda_total_operacional_rs']:,.2f}")
    print("-" * 78)
    print("Q1 - Concentração de Downtime por Planta:\n", q1_planta.to_string(index=False))
    print("\nQ2 - Correlação Vibração ISO 10816 x Scrap:\n", q2_vibracao.to_string(index=False))
    print(
        f"\nQ3 - Business Case Retrofit IoT Preditivo:\n"
        f"  • Máquinas Elegíveis:          {int(q3_roi['ativos_elegiveis'])}\n"
        f"  • Capex Estimado em Sensores:  R$ {q3_roi['capex_iot_rs']:,.2f}\n"
        f"  • Economia Anual Downtime:     R$ {q3_roi['economia_downtime_rs']:,.2f}\n"
        f"  • Economia Anual Scrap:        R$ {q3_roi['economia_scrap_rs']:,.2f}\n"
        f"  • Benefício Líquido Anual:     R$ {q3_roi['beneficio_anual_total_rs']:,.2f}\n"
        f"  • Payback do Investimento:     {q3_roi['payback_dias']:.1f} dias ({q3_roi['payback_meses']:.2f} meses)\n"
        f"  • ROI Multiplicador (12m):     {q3_roi['roi_12m_x']:.1f}x"
    )
    print("=" * 78)


if __name__ == "__main__":
    main()
