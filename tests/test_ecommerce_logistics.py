#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testes automatizados do módulo OmniLog (Logística, OTIF & SLA E-Commerce)."""

import os
import sys
import pytest
import pandas as pd
import numpy as np

# Adiciona o diretório do módulo ao path de execução
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "02_omnilog_ecommerce_logistics")))

from pipeline_ecommerce_logistics import (
    gerar_dataset_logistica_ecommerce,
    aplicar_feature_engineering_logistica,
    responder_pergunta_1,
    responder_pergunta_2,
    responder_pergunta_3,
    REGRAS_LOGISTICA,
)


def test_gerar_dataset_logistica_ecommerce_schema():
    """Valida formato, schema e restrições de valores na geração de despachos."""
    df = gerar_dataset_logistica_ecommerce(n_pedidos=150, random_seed=42)
    assert len(df) == 150
    assert not df.isnull().values.any()
    colunas_obrigatorias = [
        "id_pedido", "regiao_destino", "categoria", "transportadora",
        "valor_pedido", "frete_cobrado", "custo_frete_real",
        "prazo_prometido_dias", "prazo_real_dias", "extraviado",
        "recomprou_60d", "nps"
    ]
    for col in colunas_obrigatorias:
        assert col in df.columns
    assert (df["valor_pedido"] > 0).all()
    assert (df["prazo_real_dias"] >= 1).all()


def test_aplicar_feature_engineering_logistica_regras():
    """Testa conformidade de regras de negócio de SLA, OTIF, subsídios e indenizações."""
    df_teste = pd.DataFrame({
        "id_pedido": ["PED-1", "PED-2", "PED-3", "PED-4", "PED-5"],
        "regiao_destino": ["Sudeste"] * 5,
        "categoria": ["Eletrônicos"] * 5,
        "transportadora": ["Loggi Express"] * 5,
        "valor_pedido": [200.0, 100.0, 100.0, 100.0, 500.0],
        "frete_cobrado": [0.0, 20.0, 20.0, 20.0, 30.0],
        "custo_frete_real": [25.0, 20.0, 25.0, 25.0, 35.0],
        "prazo_prometido_dias": [3, 3, 3, 3, 5],
        "prazo_real_dias": [3, 5, 7, 10, 10], # atraso: 0, 2, 4, 7
        "extraviado": [False, False, False, False, True],
        "recomprou_60d": [True, True, False, False, False],
        "nps": [10, 7, 4, 2, 1],
    })

    df_res = aplicar_feature_engineering_logistica(df_teste)

    # PED-1: No prazo, sem extravio -> OTIF=1, subsídio = 25 - 0 = 25, indenização = 0
    assert df_res.loc[0, "flag_otif"] == 1
    assert df_res.loc[0, "status_entrega"] == "No Prazo (SLA OK)"
    assert df_res.loc[0, "subsidio_frete"] == 25.0
    assert df_res.loc[0, "custo_indenizacao"] == 0.0

    # PED-2: Atraso 2d -> Atraso Leve, indenização = 30% do frete = 6.0
    assert df_res.loc[1, "flag_otif"] == 0
    assert df_res.loc[1, "status_entrega"] == "Atraso Leve (1-2d)"
    assert df_res.loc[1, "custo_indenizacao"] == 6.0

    # PED-3: Atraso 4d -> Atraso Crítico, indenização = frete total = 20.0
    assert df_res.loc[2, "status_entrega"] == "Atraso Crítico (3-5d)"
    assert df_res.loc[2, "custo_indenizacao"] == 20.0

    # PED-4: Atraso 7d -> Falha Grave, indenização = frete + 15% do valor = 20 + 15 = 35.0
    assert df_res.loc[3, "status_entrega"] == "Falha Grave (>5d)"
    assert df_res.loc[3, "custo_indenizacao"] == 35.0

    # PED-5: Extraviado -> Status Extraviado, indenização = valor + frete = 500 + 30 = 530.0
    assert df_res.loc[4, "status_entrega"] == "Extraviado/Avaria"
    assert df_res.loc[4, "custo_indenizacao"] == 530.0


def test_perguntas_negocio_logistica():
    """Valida perguntas executivas do OmniLog."""
    df_bruto = gerar_dataset_logistica_ecommerce(n_pedidos=200, random_seed=42)
    df_feat = aplicar_feature_engineering_logistica(df_bruto)

    p1 = responder_pergunta_1(df_feat)
    assert isinstance(p1, pd.DataFrame)
    assert "taxa_otif_pct" in p1.columns

    p2 = responder_pergunta_2(df_feat)
    assert isinstance(p2, pd.DataFrame)
    assert "taxa_recompra_60d_pct" in p2.columns

    p3 = responder_pergunta_3(df_feat)
    assert isinstance(p3, dict)
    assert "roi_multiplicador" in p3
    assert p3["roi_multiplicador"] > 0
