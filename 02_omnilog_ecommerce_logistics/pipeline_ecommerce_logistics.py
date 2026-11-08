#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Projeto: OmniLog - Otimização Logística, SLA de Entregas & Mitigação de Churn no E-Commerce
Segmento: Varejo Omnichannel & Supply Chain (E-Commerce Nacional)
Autor: Wendell Barbosa Costa (Portfólio de Data Analytics)
Norma: PEP 8 Compliant, Type Annotations e Docstrings Executivas
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import seaborn as sns

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["font.sans-serif"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = "#cccccc"
plt.rcParams["axes.linewidth"] = 0.8


@dataclass(frozen=True)
class RegrasNegocioLogistica:
    """Parâmetros e metas operacionais de SLA e custos de logística."""

    META_OTIF_PCT: float = 95.0
    TETO_SUBSIDIO_FRETE_REAIS: float = 15.00
    TAXA_DESCONTO_INDENIZACAO_LEVE: float = 0.30
    MULTIPLICADOR_LTV_ANUAL: float = 1.50


REGRAS_LOGISTICA = RegrasNegocioLogistica()


def gerar_dataset_logistica_ecommerce(
    n_pedidos: int = 1200, random_seed: int = 42
) -> pd.DataFrame:
    """Gera um conjunto simulado e representativo de despachos logísticos no Brasil."""
    np.random.seed(random_seed)

    transportadoras = [
        "Loggi Express",
        "Jadlog Standard",
        "Total Express",
        "Correios Sedex",
        "Mandaê Flex",
    ]
    prob_transportadoras = [0.28, 0.24, 0.22, 0.16, 0.10]
    regioes = ["Sudeste", "Sul", "Nordeste", "Centro-Oeste", "Norte"]
    prob_regioes = [0.48, 0.20, 0.18, 0.09, 0.05]
    categorias = [
        "Eletrônicos",
        "Moda & Vestuário",
        "Casa & Decoração",
        "Beleza & Saúde",
        "Alimentos & Bebidas",
    ]
    prob_categorias = [0.32, 0.28, 0.18, 0.14, 0.08]

    pedidos_ids = [f"PED-{str(i).zfill(6)}" for i in range(1, n_pedidos + 1)]
    transp_atribuidas = np.random.choice(transportadoras, size=n_pedidos, p=prob_transportadoras)
    regioes_atribuidas = np.random.choice(regioes, size=n_pedidos, p=prob_regioes)
    cat_atribuidas = np.random.choice(categorias, size=n_pedidos, p=prob_categorias)

    valores_pedidos = []
    for cat in cat_atribuidas:
        if cat == "Eletrônicos":
            val = np.random.normal(loc=650, scale=220)
        elif cat == "Casa & Decoração":
            val = np.random.normal(loc=340, scale=110)
        elif cat == "Moda & Vestuário":
            val = np.random.normal(loc=190, scale=60)
        else:
            val = np.random.normal(loc=140, scale=45)
        valores_pedidos.append(round(max(49.90, val), 2))

    valores_arr = np.array(valores_pedidos)

    prazos_prometidos = []
    custos_reais = []
    fretes_cobrados = []

    for regiao, transp, val in zip(regioes_atribuidas, transp_atribuidas, valores_arr):
        if regiao == "Sudeste":
            prazo = np.random.choice([2, 3, 4], p=[0.4, 0.45, 0.15])
            custo_base = np.random.uniform(14.0, 26.0)
        elif regiao == "Sul":
            prazo = np.random.choice([4, 5, 6], p=[0.3, 0.5, 0.2])
            custo_base = np.random.uniform(22.0, 38.0)
        elif regiao == "Centro-Oeste":
            prazo = np.random.choice([5, 6, 7], p=[0.25, 0.5, 0.25])
            custo_base = np.random.uniform(26.0, 44.0)
        elif regiao == "Nordeste":
            prazo = np.random.choice([6, 7, 8, 9], p=[0.2, 0.4, 0.3, 0.1])
            custo_base = np.random.uniform(34.0, 62.0)
        else:
            prazo = np.random.choice([8, 10, 12], p=[0.3, 0.4, 0.3])
            custo_base = np.random.uniform(55.0, 95.0)

        if val >= 199.0 and np.random.rand() < 0.70:
            frete_cliente = 0.0
        else:
            frete_cliente = round(custo_base * np.random.uniform(0.65, 0.95), 2)

        prazos_prometidos.append(int(prazo))
        custos_reais.append(round(custo_base, 2))
        fretes_cobrados.append(frete_cliente)

    prazos_prometidos_arr = np.array(prazos_prometidos)
    custos_reais_arr = np.array(custos_reais)
    fretes_cobrados_arr = np.array(fretes_cobrados)

    prazos_reais = []
    extravios = []

    for regiao, transp, prometido in zip(regioes_atribuidas, transp_atribuidas, prazos_prometidos_arr):
        prob_atraso = 0.06
        if regiao in ["Norte", "Nordeste"]:
            prob_atraso += 0.16
        if transp == "Jadlog Standard" and regiao == "Nordeste":
            prob_atraso += 0.28
        if transp == "Correios Sedex":
            prob_atraso -= 0.03

        prob_atraso = min(0.75, max(0.02, prob_atraso))
        is_extravio = np.random.rand() < 0.008
        extravios.append(is_extravio)

        if is_extravio:
            prazo_real = prometido + 14
        elif np.random.rand() < prob_atraso:
            atraso_adicional = np.random.choice([1, 2, 3, 4, 6, 8], p=[0.35, 0.25, 0.18, 0.10, 0.08, 0.04])
            prazo_real = prometido + atraso_adicional
        else:
            prazo_real = max(1, prometido - int(np.random.choice([0, 1], p=[0.7, 0.3])))

        prazos_reais.append(int(prazo_real))

    recompras = []
    nps_scores = []

    for prometido, real, is_ext in zip(prazos_prometidos_arr, prazos_reais, extravios):
        atraso = max(0, real - prometido)
        if is_ext:
            recompra_prob = 0.03
            nps = 1
        elif atraso == 0:
            recompra_prob = 0.45
            nps = 10
        elif atraso <= 2:
            recompra_prob = 0.26
            nps = 7
        elif atraso <= 5:
            recompra_prob = 0.14
            nps = 4
        else:
            recompra_prob = 0.06
            nps = 2

        recompras.append(bool(np.random.rand() < recompra_prob))
        nps_scores.append(int(nps))

    df = pd.DataFrame(
        {
            "id_pedido": pedidos_ids,
            "regiao_destino": regioes_atribuidas,
            "categoria": cat_atribuidas,
            "transportadora": transp_atribuidas,
            "valor_pedido": valores_arr,
            "frete_cobrado": fretes_cobrados_arr,
            "custo_frete_real": custos_reais_arr,
            "prazo_prometido_dias": prazos_prometidos_arr,
            "prazo_real_dias": prazos_reais,
            "extraviado": extravios,
            "recomprou_60d": recompras,
            "nps": nps_scores,
        }
    )
    return df


def aplicar_feature_engineering_logistica(df: pd.DataFrame) -> pd.DataFrame:
    """Enriquece o DataFrame com métricas de SLA, subsídio e indenizações."""
    df_feat = df.copy()
    df_feat["dias_atraso"] = np.maximum(0, df_feat["prazo_real_dias"] - df_feat["prazo_prometido_dias"])
    df_feat["flag_otif"] = ((df_feat["dias_atraso"] == 0) & (~df_feat["extraviado"])).astype(int)

    condicoes_status = [
        df_feat["extraviado"],
        df_feat["dias_atraso"] == 0,
        df_feat["dias_atraso"] <= 2,
        df_feat["dias_atraso"] <= 5,
    ]
    rotulos_status = [
        "Extraviado/Avaria",
        "No Prazo (SLA OK)",
        "Atraso Leve (1-2d)",
        "Atraso Crítico (3-5d)",
    ]
    df_feat["status_entrega"] = np.select(condicoes_status, rotulos_status, default="Falha Grave (>5d)")
    df_feat["subsidio_frete"] = np.maximum(0.0, df_feat["custo_frete_real"] - df_feat["frete_cobrado"]).round(2)

    condicoes_indenizacao = [
        df_feat["status_entrega"] == "No Prazo (SLA OK)",
        df_feat["status_entrega"] == "Atraso Leve (1-2d)",
        df_feat["status_entrega"] == "Atraso Crítico (3-5d)",
        df_feat["status_entrega"] == "Falha Grave (>5d)",
        df_feat["status_entrega"] == "Extraviado/Avaria",
    ]
    valores_indenizacao = [
        0.0,
        (df_feat["frete_cobrado"] * REGRAS_LOGISTICA.TAXA_DESCONTO_INDENIZACAO_LEVE).round(2),
        df_feat["frete_cobrado"].round(2),
        (df_feat["frete_cobrado"] + (df_feat["valor_pedido"] * 0.15)).round(2),
        (df_feat["valor_pedido"] + df_feat["frete_cobrado"]).round(2),
    ]
    df_feat["custo_indenizacao"] = np.select(condicoes_indenizacao, valores_indenizacao, default=0.0)
    return df_feat


# =============================================================================
# 4. STORYTELLING & RESPOSTA ÀS 3 PERGUNTAS CRÍTICAS DE NEGÓCIO
# =============================================================================

def responder_pergunta_1(df: pd.DataFrame) -> pd.DataFrame:
    """Pergunta 1: Transportadora e rota interestadual com maiores falhas de SLA e indenizações."""
    resumo_rotas = (
        df.groupby(["transportadora", "regiao_destino"])
        .agg(
            total_pedidos=("id_pedido", "count"),
            pedidos_otif=("flag_otif", "sum"),
            prazo_medio_real=("prazo_real_dias", "mean"),
            prazo_medio_prometido=("prazo_prometido_dias", "mean"),
            total_indenizacoes=("custo_indenizacao", "sum"),
            total_subsidio=("subsidio_frete", "sum"),
        )
        .reset_index()
    )
    resumo_rotas["taxa_otif_pct"] = ((resumo_rotas["pedidos_otif"] / resumo_rotas["total_pedidos"]) * 100).round(2)
    resumo_rotas["taxa_atraso_pct"] = (100.0 - resumo_rotas["taxa_otif_pct"]).round(2)
    resumo_rotas["lead_time_gap"] = (resumo_rotas["prazo_medio_real"] - resumo_rotas["prazo_medio_prometido"]).round(1)
    return resumo_rotas.sort_values(by="taxa_atraso_pct", ascending=False)


def responder_pergunta_2(df: pd.DataFrame) -> pd.DataFrame:
    """Pergunta 2: Impacto real do atraso logístico na destruição de LTV e churn de recompra."""
    resumo_churn = (
        df.groupby("status_entrega")
        .agg(
            pedidos=("id_pedido", "count"),
            recompras=("recomprou_60d", "sum"),
            nps_medio=("nps", "mean"),
            ticket_medio=("valor_pedido", "mean"),
            indenizacao_total=("custo_indenizacao", "sum"),
        )
        .reset_index()
    )
    resumo_churn["taxa_recompra_60d_pct"] = ((resumo_churn["recompras"] / resumo_churn["pedidos"]) * 100).round(2)
    resumo_churn["nps_medio"] = resumo_churn["nps_medio"].round(1)
    resumo_churn["ticket_medio"] = resumo_churn["ticket_medio"].round(2)
    return resumo_churn.sort_values(by="taxa_recompra_60d_pct", ascending=False)


def responder_pergunta_3(df: pd.DataFrame) -> Dict[str, float]:
    """Pergunta 3: ROI de Smart Carrier Allocation e teto de subsídio a R$ 15,00."""
    subsidio_excedente = df[df["subsidio_frete"] > REGRAS_LOGISTICA.TETO_SUBSIDIO_FRETE_REAIS]["subsidio_frete"].sum()
    economia_subsidio_anual = subsidio_excedente * 12

    # Eliminação de 70% das indenizações de rotas críticas via alocação inteligente
    indenizacoes_atuais = df["custo_indenizacao"].sum()
    economia_indenizacoes_anual = (indenizacoes_atuais * 0.70) * 12

    # LTV recuperado: clientes que deixaram de recomprar por atraso
    pedidos_com_atraso = df[df["dias_atraso"] > 0]
    taxa_recompra_prazo = df[df["dias_atraso"] == 0]["recomprou_60d"].mean()
    taxa_recompra_atraso = pedidos_com_atraso["recomprou_60d"].mean()
    delta_recompra = max(0.0, taxa_recompra_prazo - taxa_recompra_atraso)

    ltv_medio = df["valor_pedido"].mean() * REGRAS_LOGISTICA.MULTIPLICADOR_LTV_ANUAL
    clientes_recuperados_anual = len(pedidos_com_atraso) * delta_recompra * 12
    ganho_ltv_anual = clientes_recuperados_anual * ltv_medio

    custo_implementacao_tech = 85000.0
    beneficio_total_anual = economia_subsidio_anual + economia_indenizacoes_anual + ganho_ltv_anual
    roi_multiplicador = round(beneficio_total_anual / custo_implementacao_tech, 2)

    return {
        "economia_subsidio_frete_anual": round(economia_subsidio_anual, 2),
        "economia_indenizacoes_anual": round(economia_indenizacoes_anual, 2),
        "ltv_preservado_anual": round(ganho_ltv_anual, 2),
        "beneficio_total_anual": round(beneficio_total_anual, 2),
        "custo_implementacao": custo_implementacao_tech,
        "roi_multiplicador": roi_multiplicador,
    }


def main() -> None:
    if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 80)
    print("🚚 OMNILOG: PIPELINE EXECUTIVO DE ANÁLISE LOGÍSTICA & SLA NO E-COMMERCE")
    print("=" * 80)
    df_bruto = gerar_dataset_logistica_ecommerce(n_pedidos=1200, random_seed=42)
    df_final = aplicar_feature_engineering_logistica(df_bruto)

    taxa_otif_global = (df_final["flag_otif"].mean() * 100).round(2)
    print(f"✓ Base gerada e processada com {len(df_final)} despachos logísticos.")
    print(f"✓ OTIF Global da Operação: {taxa_otif_global}% (Meta: >={REGRAS_LOGISTICA.META_OTIF_PCT}%)")
    print(f"✓ Total Subsídios de Frete: R$ {df_final['subsidio_frete'].sum():,.2f}")
    print(f"✓ Total Indenizações SAC: R$ {df_final['custo_indenizacao'].sum():,.2f}")

    print("\n--- PERGUNTA 1: Piores Rotas por Taxa de Atraso e Indenização (Top 5) ---")
    p1 = responder_pergunta_1(df_final)
    print(p1.head(5).to_string(index=False))

    print("\n--- PERGUNTA 2: Destruição de LTV e Churn de Recompra por Status de Entrega ---")
    p2 = responder_pergunta_2(df_final)
    print(p2.to_string(index=False))

    print("\n--- PERGUNTA 3: ROI de Smart Carrier Allocation e Teto de Subsídio ---")
    p3 = responder_pergunta_3(df_final)
    for k, v in p3.items():
        print(f"  • {k}: {v:,.2f}" if isinstance(v, float) else f"  • {k}: {v}")

    # Salva dataset processado
    output_path = os.path.join(os.path.dirname(__file__), "dataset_logistica_ecommerce.csv")
    df_final.to_csv(output_path, index=False, encoding="utf-8")
    print(f"\n✓ Dataset exportado com sucesso para: {os.path.basename(output_path)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
