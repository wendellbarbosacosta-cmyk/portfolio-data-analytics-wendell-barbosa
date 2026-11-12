"""Pipeline de Análise de Dados e Inteligência de Negócio em Energia Renovável.

Projeto: VoltGrid Analytics
Segmento: EnergyTech, Geração de Energia Renovável (Solar & Eólica) & Utilities
Autor: Wendell Barbosa Costa
Padrão de Código: PEP 8 (Google Style Docstrings, Typed, Production-Ready)
"""

from dataclasses import dataclass
import os
from typing import Dict, List, Optional, Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns


@dataclass(frozen=True)
class EnergyConfig:
    """Configurações paramétricas de mercado e custos de energia elétrica."""
    preco_medio_ppa_mwh: float = 185.00
    pld_medio_horario_ponta_mwh: float = 380.00
    custo_lavagem_painel_por_mw: float = 1450.00
    capex_bess_por_mwh: float = 850000.00
    eficiencia_roundtrip_bess: float = 0.88
    random_seed: int = 42


def generate_energy_plant_dataset(num_plants: int = 480, seed: int = 42) -> pd.DataFrame:
    """Gera base sintética fidedigna de usinas geradoras solares e eólicas."""
    np.random.seed(seed)
    plant_ids = [f"VOLT-{1000 + i}" for i in range(num_plants)]
    fontes = np.random.choice(["Solar Fotovoltaica (UFV)", "Eólica Onshore (EOL)"], size=num_plants, p=[0.60, 0.40])
    regioes = np.random.choice(
        ["Nordeste / Bahia", "Nordeste / Rio Grande do Norte", "Sudeste / Minas Gerais", "Centro-Oeste / Goiás", "Sul / Rio Grande do Sul"],
        size=num_plants, p=[0.35, 0.25, 0.20, 0.10, 0.10]
    )

    tecnologias_rastreamento, capacidades_mw, fatores_capacidade_base, irradiacao_ou_vento = [], [], [], []
    for fonte, regiao in zip(fontes, regioes):
        if fonte == "Solar Fotovoltaica (UFV)":
            cap = float(np.round(np.random.uniform(5.0, 75.0), 1))
            capacidades_mw.append(cap)
            tec = np.random.choice(["Tracker 1-Eixo (Single Axis)", "Fixo Tilt Otimizado"], p=[0.75, 0.25])
            tecnologias_rastreamento.append(tec)
            ghi = np.random.uniform(5.1, 6.4) if "Nordeste" in regiao else np.random.uniform(4.5, 5.7)
            irradiacao_ou_vento.append(round(ghi, 2))
            cf = np.random.normal(27.5, 3.2) + (3.5 if tec == "Tracker 1-Eixo (Single Axis)" else 0)
            fatores_capacidade_base.append(float(np.clip(cf, 18.0, 34.5)))
        else:
            cap = float(np.round(np.random.uniform(15.0, 120.0), 1))
            capacidades_mw.append(cap)
            tecnologias_rastreamento.append("Aerogerador Rotor Grande (Class S)")
            wind = np.random.uniform(7.8, 10.2) if "Nordeste" in regiao or "Sul" in regiao else np.random.uniform(6.0, 8.2)
            irradiacao_ou_vento.append(round(wind, 2))
            cf = np.random.normal(46.0, 5.5)
            fatores_capacidade_base.append(float(np.clip(cf, 30.0, 62.0)))

    curtailment_pct = [round(float(np.random.beta(2, 6) * 22.0), 1) if "Nordeste" in r else round(float(np.random.beta(1.5, 8) * 9.0), 1) for r in regioes]
    soiling_pct = [round(float(np.random.uniform(1.8, 9.5)), 1) if f == "Solar Fotovoltaica (UFV)" else 0.0 for f in fontes]

    return pd.DataFrame({
        "id_usina": plant_ids, "fonte_energia": fontes, "regiao": regioes, "capacidade_instalada_mw": capacidades_mw,
        "tecnologia_seguimento": tecnologias_rastreamento, "recurso_natural_medio": irradiacao_ou_vento,
        "fator_capacidade_base_pct": fatores_capacidade_base, "taxa_curtailment_pct": curtailment_pct,
        "taxa_soiling_loss_pct": soiling_pct, "possui_bess_bateria": np.random.choice([True, False], size=num_plants, p=[0.18, 0.82]),
        "status_operacional": np.random.choice(["Operação Normal", "Restrição de Despacho ONS", "Alerta de Sujidade Elevada", "Manutenção Preventiva"], size=num_plants, p=[0.60, 0.22, 0.12, 0.06])
    })

def engineer_energy_features(df: pd.DataFrame, config: EnergyConfig = EnergyConfig()) -> pd.DataFrame:
    """Aplica regras de negócio, modelagem de perdas e cálculo de receita líquida."""
    df = df.copy()
    horas_ano = 8760.0
    df["geracao_teorica_mwh_ano"] = (df["capacidade_instalada_mw"] * (df["fator_capacidade_base_pct"] / 100.0) * horas_ano).round(1)
    df["perda_total_pct"] = (df["taxa_curtailment_pct"] + df["taxa_soiling_loss_pct"]).clip(upper=35.0).round(1)
    df["geracao_liquida_mwh_ano"] = (df["geracao_teorica_mwh_ano"] * (1.0 - (df["perda_total_pct"] / 100.0))).round(1)
    df["fator_capacidade_real_pct"] = ((df["geracao_liquida_mwh_ano"] / (df["capacidade_instalada_mw"] * horas_ano)) * 100.0).round(1)
    df["energia_cortada_curtailment_mwh"] = (df["geracao_teorica_mwh_ano"] * (df["taxa_curtailment_pct"] / 100.0)).round(1)
    df["energia_perdida_soiling_mwh"] = (df["geracao_teorica_mwh_ano"] * (df["taxa_soiling_loss_pct"] / 100.0)).round(1)
    df["receita_bruta_realizada_rs"] = (df["geracao_liquida_mwh_ano"] * config.preco_medio_ppa_mwh).round(2)
    df["perda_financeira_curtailment_rs"] = (df["energia_cortada_curtailment_mwh"] * config.preco_medio_ppa_mwh).round(2)
    df["perda_financeira_soiling_rs"] = (df["energia_perdida_soiling_mwh"] * config.preco_medio_ppa_mwh).round(2)
    df["custo_om_anual_rs"] = (df["capacidade_instalada_mw"] * 48000.0).round(2)
    df["ebitda_operacional_rs"] = (df["receita_bruta_realizada_rs"] - df["custo_om_anual_rs"]).round(2)
    df["margem_ebitda_pct"] = np.where(df["receita_bruta_realizada_rs"] > 0, ((df["ebitda_operacional_rs"] / df["receita_bruta_realizada_rs"]) * 100.0).round(1), 0.0)

    condicoes_curtailment = [
        df["taxa_curtailment_pct"] >= 10.0,
        df["taxa_curtailment_pct"] >= 4.0,
    ]
    rotulos_curtailment = [
        "Crítica (Corte ≥ 10%)",
        "Moderada (Corte 4% a 10%)",
    ]
    df["faixa_severidade_curtailment"] = np.select(condicoes_curtailment, rotulos_curtailment, default="Baixa / Tolerável (< 4%)")
    return df


# =============================================================================
# 3. CÁLCULO DE KPIS EXECUTIVOS
# =============================================================================

def calculate_executive_kpis(df: pd.DataFrame) -> Dict[str, float]:
    """Calcula os indicadores-chave operacionais e financeiros da carteira de geração."""
    capacidade_total_mw = df["capacidade_instalada_mw"].sum()
    geracao_teorica_total = df["geracao_teorica_mwh_ano"].sum()
    geracao_liquida_total = df["geracao_liquida_mwh_ano"].sum()
    curtailment_total_mwh = df["energia_cortada_curtailment_mwh"].sum()
    soiling_total_mwh = df["energia_perdida_soiling_mwh"].sum()
    perda_curtailment_total_rs = df["perda_financeira_curtailment_rs"].sum()
    perda_soiling_total_rs = df["perda_financeira_soiling_rs"].sum()
    receita_total_rs = df["receita_bruta_realizada_rs"].sum()
    ebitda_total_rs = df["ebitda_operacional_rs"].sum()

    fator_capacidade_medio = (geracao_liquida_total / (capacidade_total_mw * 8760.0)) * 100.0
    taxa_media_curtailment = (curtailment_total_mwh / geracao_teorica_total) * 100.0
    margem_ebitda_media = (ebitda_total_rs / receita_total_rs) * 100.0 if receita_total_rs > 0 else 0.0

    return {
        "total_usinas": len(df),
        "capacidade_instalada_total_mw": round(capacidade_total_mw, 1),
        "geracao_teorica_total_mwh": round(geracao_teorica_total, 1),
        "geracao_liquida_total_mwh": round(geracao_liquida_total, 1),
        "fator_capacidade_real_ponderado_pct": round(fator_capacidade_medio, 2),
        "taxa_media_curtailment_pct": round(taxa_media_curtailment, 2),
        "perda_total_curtailment_rs": round(perda_curtailment_total_rs, 2),
        "perda_total_soiling_rs": round(perda_soiling_total_rs, 2),
        "receita_bruta_anual_rs": round(receita_total_rs, 2),
        "ebitda_total_anual_rs": round(ebitda_total_rs, 2),
        "margem_ebitda_consolidada_pct": round(margem_ebitda_media, 2),
    }


# =============================================================================
# 4. STORYTELLING & RESPOSTA ÀS 3 PERGUNTAS CRÍTICAS DE NEGÓCIO
# =============================================================================

def responder_pergunta_1(df: pd.DataFrame) -> pd.DataFrame:
    """Pergunta 1: Região e fonte geradora que concentram as perdas por Curtailment ONS."""
    perda_global_curtailment = df["perda_financeira_curtailment_rs"].sum()
    resumo = (
        df.groupby(["regiao", "fonte_energia"])
        .agg(
            total_usinas=("id_usina", "count"),
            capacidade_total_mw=("capacidade_instalada_mw", "sum"),
            energia_cortada_mwh=("energia_cortada_curtailment_mwh", "sum"),
            perda_financeira_rs=("perda_financeira_curtailment_rs", "sum"),
            taxa_media_curtailment_pct=("taxa_curtailment_pct", "mean"),
        )
        .reset_index()
    )
    resumo["capacidade_total_mw"] = resumo["capacidade_total_mw"].round(1)
    resumo["energia_cortada_mwh"] = resumo["energia_cortada_mwh"].round(1)
    resumo["perda_financeira_rs"] = resumo["perda_financeira_rs"].round(2)
    resumo["taxa_media_curtailment_pct"] = resumo["taxa_media_curtailment_pct"].round(2)
    resumo["share_perda_curtailment_pct"] = ((resumo["perda_financeira_rs"] / max(1.0, perda_global_curtailment)) * 100.0).round(2)
    return resumo.sort_values(by="perda_financeira_rs", ascending=False)


def responder_pergunta_2(df: pd.DataFrame, config: EnergyConfig = EnergyConfig()) -> Dict[str, float]:
    """Pergunta 2: Eficiência econômica e ROI de ciclos de lavagem robotizada anti-soiling."""
    df_solar = df[df["fonte_energia"].str.contains("Solar")]
    capacidade_solar_mw = df_solar["capacidade_instalada_mw"].sum()
    perda_soiling_atual_rs = df_solar["perda_financeira_soiling_rs"].sum()

    # 2 ciclos de lavagem robotizada seca por ano a R$ 1.450 / MW / lavagem
    custo_lavagens_anual = capacidade_solar_mw * config.custo_lavagem_painel_por_mw * 2.0

    # A lavagem robotizada periódica recupera 70% das perdas por sujidade (soiling)
    receita_recuperada_anual = perda_soiling_atual_rs * 0.70
    beneficio_liquido_anual = receita_recuperada_anual - custo_lavagens_anual

    roi_multiplicador = round(receita_recuperada_anual / max(1.0, custo_lavagens_anual), 2)
    payback_meses = round((custo_lavagens_anual / max(1.0, receita_recuperada_anual)) * 12.0, 1)

    return {
        "capacidade_solar_total_mw": round(capacidade_solar_mw, 1),
        "perda_soiling_atual_rs": round(perda_soiling_atual_rs, 2),
        "custo_lavagem_anual_rs": round(custo_lavagens_anual, 2),
        "receita_recuperada_anual_rs": round(receita_recuperada_anual, 2),
        "beneficio_liquido_anual_rs": round(beneficio_liquido_anual, 2),
        "payback_simples_meses": payback_meses,
        "roi_multiplicador": roi_multiplicador,
    }


def responder_pergunta_3(df: pd.DataFrame, config: EnergyConfig = EnergyConfig()) -> Dict[str, float]:
    """Pergunta 3: Arbitragem de energia cortada (Curtailment) com Sistemas BESS de Baterias."""
    energia_cortada_total_mwh = df["energia_cortada_curtailment_mwh"].sum()

    # Armazenamento de 40% do curtailment nas usinas críticas
    energia_capturada_mwh = energia_cortada_total_mwh * 0.40
    # Eficiência round-trip de 88%
    energia_despachada_pico_mwh = energia_capturada_mwh * config.eficiencia_roundtrip_bess

    # Receita adicional despachada no horário de ponta ao PLD médio de R$ 380,00/MWh
    receita_adicional_bess_rs = energia_despachada_pico_mwh * config.pld_medio_horario_ponta_mwh

    # Dimensionamento: capacidade diária de armazenamento requerida (4 horas de autonomia no pico)
    capacidade_bess_mwh = (energia_capturada_mwh / 365.0)
    capex_total_bess_rs = capacidade_bess_mwh * config.capex_bess_por_mwh

    payback_anos = round(capex_total_bess_rs / max(1.0, receita_adicional_bess_rs), 1)
    roi_10_anos = round((receita_adicional_bess_rs * 10.0) / max(1.0, capex_total_bess_rs), 2)

    return {
        "energia_cortada_total_mwh": round(energia_cortada_total_mwh, 1),
        "energia_capturada_bess_mwh": round(energia_capturada_mwh, 1),
        "energia_despachada_pico_mwh": round(energia_despachada_pico_mwh, 1),
        "receita_adicional_anual_rs": round(receita_adicional_bess_rs, 2),
        "capacidade_bess_dimensionada_mwh": round(capacidade_bess_mwh, 1),
        "investimento_capex_bess_rs": round(capex_total_bess_rs, 2),
        "payback_simples_anos": payback_anos,
        "roi_multiplicador_10_anos": roi_10_anos,
    }


def main() -> None:
    import sys
    if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 80)
    print("⚡ VOLTGRID: PIPELINE EXECUTIVO DE ANÁLISE DE ENERGIA RENOVÁVEL & CURTAILMENT")
    print("=" * 80)

    config = EnergyConfig()
    df_raw = generate_energy_plant_dataset(num_plants=480, seed=config.random_seed)
    df_final = engineer_energy_features(df_raw, config=config)
    kpis = calculate_executive_kpis(df_final)

    print(f"✓ Base gerada e processada com {kpis['total_usinas']} usinas ({kpis['capacidade_instalada_total_mw']:,.1f} MW).")
    print(f"✓ Geração Líquida Anual: {kpis['geracao_liquida_total_mwh']:,.1f} MWh/ano")
    print(f"✓ Fator de Capacidade Médio Real: {kpis['fator_capacidade_real_ponderado_pct']}%")
    print(f"✓ Taxa Média de Curtailment: {kpis['taxa_media_curtailment_pct']}% (Meta ONS: <= 3.0%)")
    print(f"✓ Perda Financeira Anual por Curtailment: R$ {kpis['perda_total_curtailment_rs']:,.2f}")
    print(f"✓ Perda Financeira Anual por Sujidade (Soiling): R$ {kpis['perda_total_soiling_rs']:,.2f}")
    print(f"✓ Receita Bruta Realizada: R$ {kpis['receita_bruta_anual_rs']:,.2f}")
    print(f"✓ EBITDA Operacional Consolidado: R$ {kpis['ebitda_total_anual_rs']:,.2f} (Margem: {kpis['margem_ebitda_consolidada_pct']}%)")

    print("\n--- PERGUNTA 1: Região e Fonte com Maior Impacto de Curtailment ONS (Top 5) ---")
    p1 = responder_pergunta_1(df_final)
    print(p1.head(5).to_string(index=False))

    print("\n--- PERGUNTA 2: Eficiência Econômica da Limpeza Robotizada Anti-Soiling ---")
    p2 = responder_pergunta_2(df_final, config=config)
    for k, v in p2.items():
        print(f"  • {k}: {v:,.2f}" if isinstance(v, float) else f"  • {k}: {v}")

    print("\n--- PERGUNTA 3: Arbitragem de Energia Cortada com Baterias BESS ---")
    p3 = responder_pergunta_3(df_final, config=config)
    for k, v in p3.items():
        print(f"  • {k}: {v:,.2f}" if isinstance(v, float) else f"  • {k}: {v}")

    # Salva dataset processado
    output_path = os.path.join(os.path.dirname(__file__), "dataset_energytech_usinas.csv")
    df_final.to_csv(output_path, index=False, encoding="utf-8")
    print(f"\n✓ Dataset exportado com sucesso para: {os.path.basename(output_path)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
