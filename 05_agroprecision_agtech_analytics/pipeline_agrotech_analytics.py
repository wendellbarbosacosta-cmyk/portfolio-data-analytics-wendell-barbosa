"""
Pipeline de Análise de Produtividade Agrícola, Eficiência de Insumos e Risco Climático.
Módulo executivo de Engenharia e Análise de Dados para o setor de AgroTech & Agronegócio de Precisão.

Padrão de Código: PEP 8 estrito com type hints e documentação Google-style.
Autor: Wendell Barbosa Costa
Projeto: AgroPrecision Analytics — AgTech & Agricultura de Precisão
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


@dataclass
class AgroConfig:
    """Parâmetros operacionais e agronômicos de simulação de safra."""

    seed: int = 42
    n_talhoes: int = 550
    output_dir: str = "relatorios_agro"
    preco_saca_soja_rs: float = 135.00
    preco_saca_milho_rs: float = 62.00
    meta_produtividade_soja_scha: float = 72.00
    meta_produtividade_milho_scha: float = 115.00


class AgroAnalyticsPipeline:
    """Pipeline executivo para diagnóstico de lavoura, insumos e margem operacional por hectare."""

    def __init__(self, config: Optional[AgroConfig] = None) -> None:
        self.config = config or AgroConfig()
        np.random.seed(self.config.seed)
        os.makedirs(self.config.output_dir, exist_ok=True)
        self.df: pd.DataFrame = pd.DataFrame()

    def gerar_dados_sinteticos(self) -> pd.DataFrame:
        """Gera dataset calibrado com distribuições de lavouras do Cerrado e Sul brasileiro."""
        n = self.config.n_talhoes

        regioes = ["Cerrado / Mato Grosso", "Matopiba / Bahia", "Paraná / Campos Gerais", "Goiás / Sudoeste", "Mato Grosso do Sul"]
        prob_regioes = [0.35, 0.20, 0.20, 0.15, 0.10]

        culturas = ["Soja Safra Principal", "Milho 2ª Safra (Safrinha)"]
        prob_culturas = [0.65, 0.35]

        texturas_solo = ["Argiloso (>35% argila)", "Médio / Franco-Argiloso", "Arenoso (<15% argila)"]
        prob_texturas = [0.45, 0.40, 0.15]

        tipos_manejo = ["Manejo em Taxa Variável (VRT)", "Aplicação Convencional (Taxa Fixa)"]
        prob_manejo = [0.42, 0.58]

        talhoes_id = [f"TAL-{1000 + i}" for i in range(n)]
        regioes_alocadas = np.random.choice(regioes, size=n, p=prob_regioes)
        culturas_alocadas = np.random.choice(culturas, size=n, p=prob_culturas)
        texturas_alocadas = np.random.choice(texturas_solo, size=n, p=prob_texturas)
        manejos_alocados = np.random.choice(tipos_manejo, size=n, p=prob_manejo)

        areas_ha = np.random.uniform(40.0, 220.0, size=n).round(1)

        v_bases_pct = []
        ph_solo = []
        doses_npk_kgha = []
        custo_insumos_ha = []
        ndvi_medio = []
        precipitacao_mm = []
        produtividade_scha = []

        for i in range(n):
            cultura = culturas_alocadas[i]
            textura = texturas_alocadas[i]
            manejo = manejos_alocados[i]

            if manejo == "Manejo em Taxa Variável (VRT)":
                v_bases = float(np.random.normal(66.0, 5.0))
                ph = float(np.random.normal(5.8, 0.25))
                dose_npk = float(np.random.normal(320.0, 35.0))
                custo_insumo = float(np.random.normal(2450.0, 220.0))
            else:
                v_bases = float(np.random.normal(51.0, 10.0))
                ph = float(np.random.normal(5.2, 0.45))
                dose_npk = float(np.random.normal(410.0, 55.0))
                custo_insumo = float(np.random.normal(3180.0, 310.0))

            v_bases = float(np.clip(v_bases, 30.0, 85.0).round(1))
            ph = float(np.clip(ph, 4.2, 6.8).round(2))
            dose_npk = max(round(dose_npk, 1), 180.0)
            custo_insumo = max(round(custo_insumo, 2), 1500.0)

            chuva = float(np.random.normal(680.0, 120.0))
            if "Bahia" in regioes_alocadas[i] or "Mato Grosso do Sul" in regioes_alocadas[i]:
                chuva -= float(np.random.uniform(80.0, 160.0))
            chuva = max(round(chuva, 1), 320.0)

            ndvi = 0.45 + (v_bases / 100.0) * 0.30 + (min(chuva, 750.0) / 1000.0) * 0.15
            if textura == "Arenoso (<15% argila)":
                ndvi -= 0.08
            ndvi = float(np.clip(ndvi + np.random.normal(0, 0.03), 0.38, 0.92).round(3))

            if cultura == "Soja Safra Principal":
                base_prod = 58.0
                fator_solo = (v_bases - 50.0) * 0.45
                fator_chuva = (min(chuva, 800.0) - 500.0) * 0.03
                fator_manejo = 6.5 if manejo == "Manejo em Taxa Variável (VRT)" else -2.5
                prod = float(np.clip(base_prod + fator_solo + fator_chuva + fator_manejo + np.random.normal(0, 3.2), 32.0, 84.0).round(1))
            else:
                base_prod = 95.0
                fator_solo = (v_bases - 50.0) * 0.70
                fator_chuva = (min(chuva, 700.0) - 450.0) * 0.06
                fator_manejo = 11.0 if manejo == "Manejo em Taxa Variável (VRT)" else -4.0
                prod = float(np.clip(base_prod + fator_solo + fator_chuva + fator_manejo + np.random.normal(0, 5.5), 55.0, 138.0).round(1))

            v_bases_pct.append(v_bases)
            ph_solo.append(ph)
            doses_npk_kgha.append(dose_npk)
            custo_insumos_ha.append(custo_insumo)
            ndvi_medio.append(ndvi)
            precipitacao_mm.append(chuva)
            produtividade_scha.append(prod)

        df = pd.DataFrame({
            "talhao_id": talhoes_id,
            "regiao": regioes_alocadas,
            "cultura": culturas_alocadas,
            "area_ha": areas_ha,
            "textura_solo": texturas_alocadas,
            "tipo_manejo": manejos_alocados,
            "saturacao_bases_v_pct": v_bases_pct,
            "ph_solo_cacl2": ph_solo,
            "dose_npk_kgha": doses_npk_kgha,
            "custo_insumos_rs_ha": custo_insumos_ha,
            "precipitacao_ciclo_mm": precipitacao_mm,
            "ndvi_medio_vegetativo": ndvi_medio,
            "produtividade_scha": produtividade_scha,
        })
        self.df = df
        return df

    def engenharia_features_e_kpis(self) -> pd.DataFrame:
        """Enriquece a base com métricas financeiras, breakeven e classificações agronômicas de forma vetorizada."""
        df = self.df.copy()
        df["preco_saca_rs"] = np.where(df["cultura"].str.contains("Soja"), 135.00, 62.00)
        df["receita_bruta_rs_ha"] = (df["produtividade_scha"] * df["preco_saca_rs"]).round(2)
        df["receita_total_talhao_rs"] = (df["receita_bruta_rs_ha"] * df["area_ha"]).round(2)
        df["custo_total_talhao_rs"] = (df["custo_insumos_rs_ha"] * df["area_ha"]).round(2)
        df["margem_liquida_rs_ha"] = (df["receita_bruta_rs_ha"] - df["custo_insumos_rs_ha"]).round(2)
        df["lucro_total_talhao_rs"] = (df["receita_total_talhao_rs"] - df["custo_total_talhao_rs"]).round(2)

        condicoes_fertilidade = [
            df["saturacao_bases_v_pct"] < 50.0,
            df["saturacao_bases_v_pct"] <= 65.0,
        ]
        rotulos_fertilidade = [
            "Crítica / Ácida (V < 50%)",
            "Média / Regular (V 50-65%)",
        ]
        df["faixa_fertilidade_solo"] = np.select(condicoes_fertilidade, rotulos_fertilidade, default="Excelente / Corrigida (V > 65%)")
        self.df = df
        return df

    def calcular_kpis_executivos(self) -> Dict[str, float]:
        """Calcula os indicadores-chave agronômicos e financeiros da safra consolidada."""
        df = self.df
        area_total_ha = df["area_ha"].sum()
        soja_df = df[df["cultura"].str.contains("Soja")]
        milho_df = df[df["cultura"].str.contains("Milho")]
        prod_soja = (soja_df["produtividade_scha"] * soja_df["area_ha"]).sum() / soja_df["area_ha"].sum()
        prod_milho = (milho_df["produtividade_scha"] * milho_df["area_ha"]).sum() / milho_df["area_ha"].sum()

        return {
            "total_talhoes": len(df),
            "area_total_ha": round(area_total_ha, 1),
            "produtividade_media_soja_scha": round(prod_soja, 1),
            "produtividade_media_milho_scha": round(prod_milho, 1),
            "margem_liquida_media_rs_ha": round(df["lucro_total_talhao_rs"].sum() / area_total_ha, 2),
            "custo_medio_insumos_rs_ha": round(df["custo_total_talhao_rs"].sum() / area_total_ha, 2),
            "lucro_total_safra_rs": round(df["lucro_total_talhao_rs"].sum(), 2),
            "ndvi_medio_vegetativo": round((df["ndvi_medio_vegetativo"] * df["area_ha"]).sum() / area_total_ha, 3),
        }


# =============================================================================
# 4. STORYTELLING & RESPOSTA ÀS 3 PERGUNTAS CRÍTICAS DE NEGÓCIO
# =============================================================================

def responder_pergunta_1(df: pd.DataFrame) -> pd.DataFrame:
    """Pergunta 1: Impacto da acidez e saturação por bases (V%) na produtividade real da lavoura."""
    resumo = (
        df.groupby(["faixa_fertilidade_solo", "cultura"])
        .agg(
            total_talhoes=("talhao_id", "count"),
            area_total_ha=("area_ha", "sum"),
            produtividade_media_scha=("produtividade_scha", "mean"),
            custo_medio_insumos_ha=("custo_insumos_rs_ha", "mean"),
            margem_liquida_media_ha=("margem_liquida_rs_ha", "mean"),
            ndvi_medio=("ndvi_medio_vegetativo", "mean"),
        )
        .reset_index()
    )
    resumo["area_total_ha"] = resumo["area_total_ha"].round(1)
    resumo["produtividade_media_scha"] = resumo["produtividade_media_scha"].round(1)
    resumo["custo_medio_insumos_ha"] = resumo["custo_medio_insumos_ha"].round(2)
    resumo["margem_liquida_media_ha"] = resumo["margem_liquida_media_ha"].round(2)
    resumo["ndvi_medio"] = resumo["ndvi_medio"].round(3)
    return resumo.sort_values(by="produtividade_media_scha", ascending=False)


def responder_pergunta_2(df: pd.DataFrame) -> pd.DataFrame:
    """Pergunta 2: Eficiência agronômica e econômica do Manejo VRT vs Taxa Fixa Convencional."""
    resumo = (
        df.groupby(["tipo_manejo", "cultura"])
        .agg(
            total_talhoes=("talhao_id", "count"),
            area_total_ha=("area_ha", "sum"),
            produtividade_media_scha=("produtividade_scha", "mean"),
            dose_media_npk_kgha=("dose_npk_kgha", "mean"),
            custo_medio_insumos_ha=("custo_insumos_rs_ha", "mean"),
            margem_liquida_media_ha=("margem_liquida_rs_ha", "mean"),
        )
        .reset_index()
    )
    resumo["area_total_ha"] = resumo["area_total_ha"].round(1)
    resumo["produtividade_media_scha"] = resumo["produtividade_media_scha"].round(1)
    resumo["dose_media_npk_kgha"] = resumo["dose_media_npk_kgha"].round(1)
    resumo["custo_medio_insumos_ha"] = resumo["custo_medio_insumos_ha"].round(2)
    resumo["margem_liquida_media_ha"] = resumo["margem_liquida_media_ha"].round(2)
    return resumo.sort_values(by="margem_liquida_media_ha", ascending=False)


def responder_pergunta_3(df: pd.DataFrame) -> Dict[str, float]:
    """Pergunta 3: Modelagem de ROI de converter 100% da lavoura para Agricultura de Precisão (VRT)."""
    talhoes_fixos = df[df["tipo_manejo"] == "Aplicação Convencional (Taxa Fixa)"]
    area_fixa_ha = talhoes_fixos["area_ha"].sum()

    # Diferencial médio de custo de insumos (Taxa Fixa - VRT)
    custo_medio_fixa = df[df["tipo_manejo"] == "Aplicação Convencional (Taxa Fixa)"]["custo_insumos_rs_ha"].mean()
    custo_medio_vrt = df[df["tipo_manejo"] == "Manejo em Taxa Variável (VRT)"]["custo_insumos_rs_ha"].mean()
    economia_insumo_ha = max(0.0, custo_medio_fixa - custo_medio_vrt)

    # Diferencial de produtividade e receita incremental na soja
    soja_fixa = df[(df["tipo_manejo"] == "Aplicação Convencional (Taxa Fixa)") & (df["cultura"].str.contains("Soja"))]
    soja_vrt = df[(df["tipo_manejo"] == "Manejo em Taxa Variável (VRT)") & (df["cultura"].str.contains("Soja"))]
    prod_soja_fixa = soja_fixa["produtividade_scha"].mean() if len(soja_fixa) > 0 else 55.0
    prod_soja_vrt = soja_vrt["produtividade_scha"].mean() if len(soja_vrt) > 0 else 65.0
    delta_prod_soja = max(0.0, prod_soja_vrt - prod_soja_fixa)
    receita_incremental_soja_ha = delta_prod_soja * 135.00

    beneficio_ha = economia_insumo_ha + receita_incremental_soja_ha
    beneficio_total_anual = beneficio_ha * area_fixa_ha

    custo_conversao_ha = 125.00  # Amostragem em grade georreferenciada + telemetria
    investimento_total = custo_conversao_ha * area_fixa_ha
    roi_multiplicador = round(beneficio_total_anual / max(1.0, investimento_total), 2)

    return {
        "area_convencional_ha": round(area_fixa_ha, 1),
        "economia_insumos_ha_rs": round(economia_insumo_ha, 2),
        "ganho_produtividade_soja_scha": round(delta_prod_soja, 1),
        "receita_incremental_soja_ha_rs": round(receita_incremental_soja_ha, 2),
        "beneficio_total_ha_rs": round(beneficio_ha, 2),
        "beneficio_total_safra_rs": round(beneficio_total_anual, 2),
        "investimento_conversao_rs": round(investimento_total, 2),
        "roi_multiplicador": roi_multiplicador,
    }


def main() -> None:
    import sys
    if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 80)
    print("🌾 AGROPRECISION: PIPELINE EXECUTIVO DE PRODUTIVIDADE & MANEJO VRT")
    print("=" * 80)

    pipeline = AgroAnalyticsPipeline()
    pipeline.gerar_dados_sinteticos()
    df_final = pipeline.engenharia_features_e_kpis()
    kpis = pipeline.calcular_kpis_executivos()

    print(f"✓ Base gerada e processada com {kpis['total_talhoes']} talhões comerciais ({kpis['area_total_ha']:,.1f} ha).")
    print(f"✓ Produtividade Média Soja: {kpis['produtividade_media_soja_scha']} sc/ha (Meta: 72.0 sc/ha)")
    print(f"✓ Produtividade Média Milho: {kpis['produtividade_media_milho_scha']} sc/ha (Meta: 115.0 sc/ha)")
    print(f"✓ Margem Líquida Média: R$ {kpis['margem_liquida_media_rs_ha']:,.2f} / ha")
    print(f"✓ Lucro Total da Safra: R$ {kpis['lucro_total_safra_rs']:,.2f}")

    print("\n--- PERGUNTA 1: Produtividade e Margem por Faixa de Fertilidade do Solo (Top 5) ---")
    p1 = responder_pergunta_1(df_final)
    print(p1.head(5).to_string(index=False))

    print("\n--- PERGUNTA 2: Eficiência Econômica: Manejo VRT vs Aplicação Convencional ---")
    p2 = responder_pergunta_2(df_final)
    print(p2.to_string(index=False))

    print("\n--- PERGUNTA 3: ROI de Conversão para Agricultura de Precisão (100% VRT) ---")
    p3 = responder_pergunta_3(df_final)
    for k, v in p3.items():
        print(f"  • {k}: {v:,.2f}" if isinstance(v, float) else f"  • {k}: {v}")

    # Salva dataset processado
    output_path = os.path.join(os.path.dirname(__file__), "dataset_agrotech_talhoes.csv")
    df_final.to_csv(output_path, index=False, encoding="utf-8")
    print(f"\n✓ Dataset exportado com sucesso para: {os.path.basename(output_path)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
