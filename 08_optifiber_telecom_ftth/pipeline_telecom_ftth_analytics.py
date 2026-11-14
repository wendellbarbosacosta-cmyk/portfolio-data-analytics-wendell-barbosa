"""OptiFiber Analytics: Pipeline de Qualidade Óptica FTTH, Churn e ROI de Rede.

Autor: Wendell Barbosa Costa
Segmento: Telecomunicações, Conectividade FTTH (GPON/XGS-PON) & 5G FWA
Padrão de Código: PEP 8, Type Hints estritos e Docstrings Google Style.

Regras de Negócio Aplicadas:
    1. Saúde Óptica do Enlace (Potência RX ONT):
       - Nominal (>= -23.0 dBm)
       - Degradado (-23.1 a -27.0 dBm)
       - Crítico (< -27.0 dBm)
    2. Ocupação de Portas CTO (Caixa de Terminação Óptica):
       - Alta Densidade (>= 75.0%)
       - Maturação (45.0% - 74.9%)
       - Ociosa (< 45.0%)
    3. Custo de Truck Roll de Campo = Visitas Técnicas * R$ 240,00 * 12 meses.
    4. Perda de Receita por Churn = Assinantes * (Churn Mensal % / 100) * 12 meses * ARPU.
    5. Business Case de Transformação FTTH: Saneamento Óptico + Triagem OLT + Expansão Wi-Fi 6 Mesh.
"""

from __future__ import annotations

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

# Configuração de encoding UTF-8 no stdout para compatibilidade com consoles Windows
if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

warnings.filterwarnings("ignore")

# Configuração estética global para gráficos corporativos
sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams["figure.dpi"] = 300
plt.rcParams["axes.titlesize"] = 13
plt.rcParams["axes.labelsize"] = 11


@dataclass(frozen=True)
class TelecomConfig:
    """Parâmetros corporativos, regulatórios e benchmarks do setor de Telecom."""

    total_clusters: int = 500
    random_seed: int = 42
    cost_per_truck_roll_rs: float = 240.0
    benchmark_churn_ftth_pct: float = 1.60
    rx_critico_dbm: float = -27.0
    rx_degradado_dbm: float = -23.0
    limiar_ociosidade_cto_pct: float = 45.0
    limiar_alta_densidade_cto_pct: float = 75.0
    output_dir: str = "relatorios_telecom_ftth"


# Constantes para compatibilidade com scripts existentes
RANDOM_SEED: int = 42
TOTAL_CLUSTERS: int = 500
COST_PER_TRUCK_ROLL_RS: float = 240.0
BENCHMARK_CHURN_FTTH_PCT: float = 1.60
RX_CRITICO_DBM: float = -27.0
RX_DEGRADADO_DBM: float = -23.0
OUTPUT_DIR: str = "relatorios_telecom_ftth"


def classify_optical_health(rx_dbm: float) -> str:
    """Classifica saúde óptica do enlace FTTH de forma escalar."""
    if rx_dbm < RX_CRITICO_DBM:
        return "Crítico (< -27.0 dBm)"
    if rx_dbm < RX_DEGRADADO_DBM:
        return "Degradado (-23.1 a -27.0 dBm)"
    return "Nominal (>= -23.0 dBm)"


def classify_cto_occupancy(ocupacao_pct: float) -> str:
    """Categoriza a ocupação de portas da CTO de forma escalar."""
    if ocupacao_pct >= 75.0:
        return "Alta Densidade (>= 75%)"
    if ocupacao_pct >= 45.0:
        return "Maturação (45% - 74.9%)"
    return "Ociosa (< 45%)"


def classify_optical_health_vectorized(s_rx: pd.Series) -> pd.Series:
    """Classificação vetorizada de atenuação óptica RX de alta performance via np.select."""
    condicoes = [
        s_rx < RX_CRITICO_DBM,
        s_rx < RX_DEGRADADO_DBM,
    ]
    escolhas = [
        "Crítico (< -27.0 dBm)",
        "Degradado (-23.1 a -27.0 dBm)",
    ]
    return pd.Series(
        np.select(condicoes, escolhas, default="Nominal (>= -23.0 dBm)"),
        index=s_rx.index,
    )


def classify_cto_occupancy_vectorized(s_ocupacao: pd.Series) -> pd.Series:
    """Classificação vetorizada de ocupação de portas CTO via np.select."""
    condicoes = [
        s_ocupacao >= 75.0,
        s_ocupacao >= 45.0,
    ]
    escolhas = [
        "Alta Densidade (>= 75%)",
        "Maturação (45% - 74.9%)",
    ]
    return pd.Series(
        np.select(condicoes, escolhas, default="Ociosa (< 45%)"),
        index=s_ocupacao.index,
    )


def generate_telecom_dataset(
    n_clusters: int = TOTAL_CLUSTERS,
    seed: int = RANDOM_SEED,
) -> pd.DataFrame:
    """Gera base analítica realista de 500 clusters FTTH em 5 regionais."""
    rng = np.random.default_rng(seed)

    regionais = [
        ("Grande São Paulo (SP)", 0.28, 0.14, 18.0),
        ("Rio & Baixada (RJ)", 0.20, 0.18, 10.0),
        ("Minas Gerais (MG)", 0.18, 0.24, 4.0),
        ("Sul Integrado (PR/SC)", 0.18, 0.21, 8.0),
        ("Nordeste Litoral (BA/PE)", 0.16, 0.34, -6.0),
    ]
    reg_names = [r[0] for r in regionais]
    reg_probs = [r[1] for r in regionais]
    reg_map = {r[0]: (r[2], r[3]) for r in regionais}

    rows: List[Dict[str, object]] = []
    for idx in range(n_clusters):
        cluster_id = f"CTO-{3001 + idx}"
        regional = str(rng.choice(reg_names, p=reg_probs))
        base_ocioso, arpu_bias = reg_map[regional]

        tech = str(
            rng.choice(
                ["FTTH XGS-PON", "FTTH GPON", "FWA 5G"],
                p=[0.26, 0.62, 0.12],
            )
        )
        wifi6 = bool(
            rng.random() < (0.78 if tech == "FTTH XGS-PON" else 0.24)
        )

        if wifi6 and rng.random() < 0.72:
            plano = "Fibra 1 Gbps + Wi-Fi 6"
            arpu_base = 144.9
        elif rng.random() < 0.56:
            plano = "Fibra 600 Mbps"
            arpu_base = 114.9
        else:
            plano = "Fibra 300 Mbps"
            arpu_base = 92.9

        portas = 128 if tech == "FWA 5G" else int(rng.choice([192, 256]))
        if rng.random() < base_ocioso:
            ocupacao_pct = round(float(rng.uniform(22.0, 44.0)), 1)
        else:
            ocupacao_pct = round(float(rng.uniform(46.0, 90.0)), 1)

        assinantes = max(18, int(round((ocupacao_pct / 100.0) * portas)))

        if tech == "FTTH XGS-PON":
            rx_dbm = round(float(-18.5 - rng.uniform(0.0, 5.2)), 2)
        else:
            p_opt = rng.random()
            if p_opt < 0.23:
                rx_dbm = round(float(-27.2 - rng.uniform(0.0, 3.1)), 2)
            elif p_opt < 0.54:
                rx_dbm = round(float(-23.3 - rng.uniform(0.0, 3.6)), 2)
            else:
                rx_dbm = round(float(-19.2 - rng.uniform(0.0, 3.6)), 2)

        arpu_rs = round(
            max(79.9, arpu_base + arpu_bias + float(rng.uniform(-7.0, 7.0))),
            2,
        )

        fator_optico = (
            2.85
            if rx_dbm < RX_CRITICO_DBM
            else 1.65 if rx_dbm < RX_DEGRADADO_DBM else 0.72
        )
        fator_wifi = 0.65 if wifi6 else 1.25
        chamados_mes = max(
            4,
            int(
                round(
                    assinantes * 0.08 * fator_optico * fator_wifi
                    + rng.uniform(0.0, 8.0)
                )
            ),
        )
        prop_visita = 0.44 if rx_dbm < RX_CRITICO_DBM else 0.28
        truck_rolls_mes = max(1, int(round(chamados_mes * prop_visita)))
        custo_truck_anual = round(
            truck_rolls_mes * 12 * COST_PER_TRUCK_ROLL_RS,
            2,
        )

        if rx_dbm < RX_CRITICO_DBM:
            churn_base = float(rng.uniform(4.15, 5.60))
        elif rx_dbm < RX_DEGRADADO_DBM:
            churn_base = float(rng.uniform(2.35, 3.20))
        else:
            churn_base = float(rng.uniform(1.02, 1.60))

        if wifi6:
            churn_base *= 0.74
        if ocupacao_pct < 45.0:
            churn_base += 0.25

        churn_pct = round(min(6.8, max(0.75, churn_base)), 2)
        perda_churn_anual = round(
            assinantes * (churn_pct / 100.0) * 12.0 * arpu_rs,
            2,
        )

        nps_base = (
            float(rng.uniform(22, 38))
            if rx_dbm < RX_CRITICO_DBM
            else float(rng.uniform(46, 60))
            if rx_dbm < RX_DEGRADADO_DBM
            else float(rng.uniform(68, 86))
        )
        nps_rede = min(92, max(10, int(round(nps_base + (7 if wifi6 else 0)))))

        rows.append(
            {
                "cluster_id": cluster_id,
                "regional_uf": regional,
                "tecnologia_acesso": tech,
                "plano_predominante": plano,
                "assinantes_ativos": assinantes,
                "portas_cto_instaladas": portas,
                "ocupacao_cto_pct": ocupacao_pct,
                "potencia_rx_media_dbm": rx_dbm,
                "possui_wifi6_mesh": int(wifi6),
                "chamados_suporte_mes": chamados_mes,
                "truck_rolls_mes": truck_rolls_mes,
                "custo_truck_roll_anual_rs": custo_truck_anual,
                "arpu_mensal_rs": arpu_rs,
                "churn_mensal_pct": churn_pct,
                "receita_perdida_churn_anual_rs": perda_churn_anual,
                "nps_rede": nps_rede,
            }
        )

    df = pd.DataFrame(rows)
    # Classificações vetorizadas de alta performance via np.select
    df["saude_optica"] = classify_optical_health_vectorized(
        df["potencia_rx_media_dbm"]
    )
    df["faixa_ocupacao_cto"] = classify_cto_occupancy_vectorized(
        df["ocupacao_cto_pct"]
    )
    df["perda_total_anual_rs"] = (
        df["custo_truck_roll_anual_rs"]
        + df["receita_perdida_churn_anual_rs"]
    ).round(2)
    return df


def compute_executive_kpis(df: pd.DataFrame) -> Dict[str, float]:
    """Calcula os KPIs executivos consolidados da operação FTTH."""
    return {
        "total_clusters": float(len(df)),
        "total_assinantes": float(df["assinantes_ativos"].sum()),
        "arpu_medio_rs": round(float(df["arpu_mensal_rs"].mean()), 2),
        "churn_medio_pct": round(float(df["churn_mensal_pct"].mean()), 2),
        "ocupacao_cto_pct": round(float(df["ocupacao_cto_pct"].mean()), 1),
        "rx_medio_dbm": round(float(df["potencia_rx_media_dbm"].mean()), 2),
        "nps_medio": round(float(df["nps_rede"].mean()), 1),
        "custo_truck_roll_anual_rs": round(
            float(df["custo_truck_roll_anual_rs"].sum()), 2
        ),
        "perda_churn_anual_rs": round(
            float(df["receita_perdida_churn_anual_rs"].sum()), 2
        ),
        "perda_total_anual_rs": round(
            float(
                df["custo_truck_roll_anual_rs"].sum()
                + df["receita_perdida_churn_anual_rs"].sum()
            ),
            2,
        ),
        "adocao_wifi6_pct": round(
            float(df["possui_wifi6_mesh"].mean() * 100.0), 1
        ),
    }


def answer_business_questions(
    df: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, float]]:
    """Responde às 3 perguntas críticas de negócio para a diretoria Telecom."""
    # Q1: Saúde Óptica vs Churn, Truck Roll e Perdas
    perda_total_global = df["perda_total_anual_rs"].sum()
    q1_optica = (
        df.groupby("saude_optica", as_index=False)
        .agg(
            clusters=("cluster_id", "count"),
            churn_medio_pct=("churn_mensal_pct", "mean"),
            truck_rolls_mes=("truck_rolls_mes", "sum"),
            nps_medio=("nps_rede", "mean"),
            perda_total_rs=("perda_total_anual_rs", "sum"),
        )
        .sort_values("churn_medio_pct", ascending=False)
    )
    q1_optica["share_perda_pct"] = (
        (q1_optica["perda_total_rs"] / perda_total_global) * 100.0
    ).round(2)
    q1_optica["churn_medio_pct"] = q1_optica["churn_medio_pct"].round(2)
    q1_optica["nps_medio"] = q1_optica["nps_medio"].round(1)
    q1_optica["perda_total_rs"] = q1_optica["perda_total_rs"].round(2)

    # Q2: Ociosidade de Portas CTO por Regional
    total_portas_livres = (
        df["portas_cto_instaladas"].sum() - df["assinantes_ativos"].sum()
    )
    q2_cto = (
        df.groupby("regional_uf", as_index=False)
        .agg(
            clusters=("cluster_id", "count"),
            ocupacao_media_pct=("ocupacao_cto_pct", "mean"),
            portas_totais=("portas_cto_instaladas", "sum"),
            assinantes=("assinantes_ativos", "sum"),
            arpu_medio_rs=("arpu_mensal_rs", "mean"),
        )
        .sort_values("ocupacao_media_pct", ascending=True)
    )
    q2_cto["portas_livres"] = q2_cto["portas_totais"] - q2_cto["assinantes"]
    q2_cto["share_portas_livres_pct"] = (
        (q2_cto["portas_livres"] / total_portas_livres) * 100.0
    ).round(2)
    q2_cto["ocupacao_media_pct"] = q2_cto["ocupacao_media_pct"].round(1)
    q2_cto["arpu_medio_rs"] = q2_cto["arpu_medio_rs"].round(2)

    # Q3: Business Case & ROI do Programa de Modernização FTTH
    elegiveis_optica = df[df["potencia_rx_media_dbm"] < RX_DEGRADADO_DBM]
    elegiveis_wifi6 = df[df["possui_wifi6_mesh"] == 0]

    capex_saneamento = len(elegiveis_optica) * 4800.0
    capex_triagem_olt = len(df) * 1650.0
    capex_wifi6 = len(elegiveis_wifi6) * 6200.0
    investimento_total = float(capex_saneamento + capex_triagem_olt + capex_wifi6)

    economia_truck = float(
        elegiveis_optica["custo_truck_roll_anual_rs"].sum() * 0.34
        + df["custo_truck_roll_anual_rs"].sum() * 0.25
    )
    preservacao_churn = float(
        elegiveis_optica["receita_perdida_churn_anual_rs"].sum() * 0.46
        + df["receita_perdida_churn_anual_rs"].sum() * 0.16
    )
    uplift_arpu = float(
        elegiveis_wifi6["assinantes_ativos"].sum() * 0.42 * 14.5 * 12.0
    )

    beneficio_total = float(economia_truck + preservacao_churn + uplift_arpu)
    payback_meses = float((investimento_total / max(1.0, beneficio_total)) * 12.0)
    payback_dias = float(payback_meses * 30.0)
    roi_12m = float(beneficio_total / max(1.0, investimento_total))

    q3_roi = {
        "investimento_total_rs": round(investimento_total, 2),
        "beneficio_anual_rs": round(beneficio_total, 2),
        "economia_truck_roll_rs": round(economia_truck, 2),
        "receita_preservada_churn_rs": round(preservacao_churn, 2),
        "uplift_arpu_wifi6_rs": round(uplift_arpu, 2),
        "payback_meses": round(payback_meses, 2),
        "payback_dias": round(payback_dias, 1),
        "roi_multiplicador": round(roi_12m, 2),
    }

    return q1_optica, q2_cto, q3_roi


def export_visual_artifacts(df: pd.DataFrame, output_dir: str = OUTPUT_DIR) -> None:
    """Gera gráficos Seaborn em 300 DPI e painel interativo Plotly HTML."""
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", palette="viridis")

    # 1. Boxplot: Saúde Óptica vs Churn Mensal
    plt.figure(figsize=(10, 6))
    sns.boxplot(
        data=df,
        x="saude_optica",
        y="churn_mensal_pct",
        hue="possui_wifi6_mesh",
        palette="Set2",
    )
    plt.axhline(
        BENCHMARK_CHURN_FTTH_PCT,
        color="crimson",
        linestyle="--",
        label=f"Meta Churn FTTH ({BENCHMARK_CHURN_FTTH_PCT:.2f}%)",
    )
    plt.title(
        "OptiFiber: Impacto da Atenuação Óptica (RX dBm) e Wi-Fi 6 no Churn",
        fontsize=13,
        fontweight="bold",
    )
    plt.xlabel("Faixa de Saúde Óptica (OLT -> ONT)")
    plt.ylabel("Churn Mensal (%)")
    plt.legend(title="Wi-Fi 6 Mesh (0=Não, 1=Sim)")
    plt.tight_layout()
    plt.savefig(out_path / "01_churn_vs_saude_optica.png", dpi=300)
    plt.close()

    # 2. Barplot: Ocupação CTO por Regional
    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=df,
        x="ocupacao_cto_pct",
        y="regional_uf",
        estimator="mean",
        errorbar=None,
        color="#7c3aed",
    )
    plt.axvline(
        45.0,
        color="darkorange",
        linestyle="--",
        label="Limite Ociosidade (45%)",
    )
    plt.title(
        "Taxa Média de Ocupação de Portas CTO por Regional",
        fontsize=13,
        fontweight="bold",
    )
    plt.xlabel("Ocupação de Portas CTO (%)")
    plt.ylabel("Regional")
    plt.legend()
    plt.tight_layout()
    plt.savefig(out_path / "02_ocupacao_cto_por_regional.png", dpi=300)
    plt.close()

    # 3. Painel Interativo Plotly
    fig = px.scatter(
        df,
        x="potencia_rx_media_dbm",
        y="churn_mensal_pct",
        size="assinantes_ativos",
        color="regional_uf",
        hover_data=["cluster_id", "ocupacao_cto_pct", "arpu_mensal_rs"],
        title="OptiFiber — Mapa Interativo de Atenuação Óptica vs. Churn",
        labels={
            "potencia_rx_media_dbm": "Potência RX Média (dBm)",
            "churn_mensal_pct": "Churn Mensal (%)",
            "regional_uf": "Regional",
        },
        template="plotly_dark",
    )
    fig.write_html(str(out_path / "painel_ftth_interativo.html"))


def main() -> None:
    """Executa o fluxo completo do pipeline analítico OptiFiber."""
    print("=" * 80)
    print("📡 OPTIFIBER ANALYTICS: TELECOM FTTH, CHURN ÓPTICO & ROI CAPEX")
    print("=" * 80)

    df = generate_telecom_dataset()
    kpis = compute_executive_kpis(df)
    q1, q2, q3 = answer_business_questions(df)

    print(
        f"Base: {int(kpis['total_clusters'])} clusters | "
        f"{int(kpis['total_assinantes']):,} assinantes | "
        f"ARPU: R$ {kpis['arpu_medio_rs']:.2f} | "
        f"Churn: {kpis['churn_medio_pct']:.2f}% | "
        f"NPS: {kpis['nps_medio']:.1f}"
    )
    print(f"Perda Total Anual (Truck Roll + Churn): R$ {kpis['perda_total_anual_rs']:,.2f}")
    print("\n[Q1] Saúde Óptica vs Churn:")
    print(q1.to_string(index=False))
    print("\n[Q2] Ocupação CTO por Regional:")
    print(q2.to_string(index=False))
    print(
        f"\n[Q3] Business Case Transformação FTTH:\n"
        f"  • Investimento Total (Capex):      R$ {q3['investimento_total_rs']:,.2f}\n"
        f"  • Economia Anual Truck Roll:       R$ {q3['economia_truck_roll_rs']:,.2f}\n"
        f"  • Receita Preservada de Churn:     R$ {q3['receita_preservada_churn_rs']:,.2f}\n"
        f"  • Uplift Receita Wi-Fi 6:          R$ {q3['uplift_arpu_wifi6_rs']:,.2f}\n"
        f"  • Benefício Operacional Anual:     R$ {q3['beneficio_anual_rs']:,.2f}\n"
        f"  • Payback Simples:                 {q3['payback_meses']:.2f} meses ({q3['payback_dias']:.1f} dias)\n"
        f"  • ROI Multiplicador (12 Meses):    {q3['roi_multiplicador']:.2f}x"
    )

    export_visual_artifacts(df)
    df.to_csv("dataset_telecom_ftth_clusters.csv", index=False)
    print("\n✓ Artefatos gerados com sucesso e salvos em disco!")
    print("=" * 80)


if __name__ == "__main__":
    main()
