"""
Pipeline de Análise de Sinistralidade, Readmissão Hospitalar e Eficiência Assistencial.
Módulo executivo de Engenharia e Análise de Dados para o setor de Saúde Suplementar (HealthTech & Hospitais).

Padrão de Código: PEP 8 estrito com type hints e documentação Google-style.
Autor: Wendell Barbosa Costa
Projeto: CarePulse Analytics — HealthTech & Saúde Suplementar
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
class HealthTechConfig:
    """Configurações e hiperparâmetros de negócio do pipeline de saúde."""

    seed: int = 42
    n_registros: int = 600
    output_dir: str = "relatorios_saude"
    meta_sinistralidade_max: float = 0.78  # Benchmark ANS: 75% a 78%
    custo_medio_diaria_uti: float = 4500.00
    custo_medio_diaria_enfermaria: float = 1200.00


class HealthcareAnalyticsPipeline:
    """Pipeline executivo de extração, tratamento, modelagem e geração de insights em Saúde."""

    def __init__(self, config: Optional[HealthTechConfig] = None) -> None:
        self.config = config or HealthTechConfig()
        np.random.seed(self.config.seed)
        os.makedirs(self.config.output_dir, exist_ok=True)
        self.df: pd.DataFrame = pd.DataFrame()

    def gerar_dados_sinteticos(self) -> pd.DataFrame:
        """Gera dataset sintético calibrado com distribuições do setor de Saúde Suplementar brasileiro."""
        n = self.config.n_registros

        tipos_internacao = ["Clínica Geral", "Cirúrgica Eletiva", "Cirúrgica Emergência", "Cardiológica", "Oncológica"]
        prob_internacao = [0.35, 0.25, 0.15, 0.15, 0.10]

        faixas_etarias = ["18-35 anos", "36-50 anos", "51-65 anos", "Acima de 65 anos"]
        prob_etarias = [0.18, 0.22, 0.32, 0.28]

        hospitais = ["Hospital Samaritano Central", "Rede D'Or Barra", "Hospital Sírio Metropolitano", "Hospital Santa Cruz", "Clínica Vida & Saúde"]
        planos = ["Plano Básico Individual", "Plano Especial Corporativo", "Plano Executivo Premium"]

        pacientes_id = [f"PAC-{1000 + i}" for i in range(n)]
        internacoes_tipo = np.random.choice(tipos_internacao, size=n, p=prob_internacao)
        etarias = np.random.choice(faixas_etarias, size=n, p=prob_etarias)
        hospitais_alocados = np.random.choice(hospitais, size=n)
        planos_alocados = np.random.choice(planos, size=n, p=[0.45, 0.40, 0.15])

        comorbidades_count = np.clip(np.random.poisson(lam=1.4, size=n), 0, 4)

        dias_internacao = []
        dias_uti = []
        custo_total_sinistro = []
        valor_mensalidade_ano = []

        for i in range(n):
            tipo = internacoes_tipo[i]
            idade = etarias[i]
            comorb = comorbidades_count[i]

            if tipo in ["Cirúrgica Emergência", "Cardiológica", "Oncológica"] or idade == "Acima de 65 anos":
                dias = int(np.random.gamma(shape=3.5, scale=2.5)) + 2
                uti = int(np.random.binomial(n=min(dias, 10), p=0.45))
            else:
                dias = int(np.random.gamma(shape=2.0, scale=1.5)) + 1
                uti = int(np.random.binomial(n=min(dias, 5), p=0.15))

            dias = max(dias, 1)
            uti = min(uti, dias)

            custo_base = (dias - uti) * self.config.custo_medio_diaria_enfermaria + uti * self.config.custo_medio_diaria_uti
            custo_opme = float(np.random.uniform(2000, 18000)) if tipo.startswith("Cirúrgica") else float(np.random.uniform(800, 6000))
            custo_total = max(round(custo_base + custo_opme + float(np.random.normal(1500, 400)), 2), 1200.0)

            if planos_alocados[i] == "Plano Executivo Premium":
                mensalidade_ano = float(np.random.uniform(24000, 36000))
            elif planos_alocados[i] == "Plano Especial Corporativo":
                mensalidade_ano = float(np.random.uniform(14000, 22000))
            else:
                mensalidade_ano = float(np.random.uniform(8000, 13000))

            dias_internacao.append(dias)
            dias_uti.append(uti)
            custo_total_sinistro.append(custo_total)
            valor_mensalidade_ano.append(round(mensalidade_ano, 2))

        lace_scores = []
        readmissao_30d = []
        taxa_glosa_prestador = []

        for i in range(n):
            dias = dias_internacao[i]
            tipo = internacoes_tipo[i]
            comorb = comorbidades_count[i]

            pts_l = min(dias, 7)
            pts_a = 3 if "Emergência" in tipo or tipo in ["Cardiológica"] else 0
            pts_c = min(comorb * 2, 5)
            pts_e = int(np.random.choice([0, 1, 2, 3], p=[0.50, 0.30, 0.15, 0.05]))
            score_lace = pts_l + pts_a + pts_c + pts_e
            lace_scores.append(score_lace)

            prob_readm = min(0.04 + (score_lace / 20.0) * 0.40 + (0.12 if dias_uti[i] > 2 else 0), 0.85)
            readmissao_30d.append(bool(np.random.rand() < prob_readm))

            taxa_glosa = float(np.random.beta(a=2, b=15) * 100)
            if tipo == "Cirúrgica Emergência":
                taxa_glosa += 4.5
            taxa_glosa_prestador.append(round(min(taxa_glosa, 30.0), 2))

        df = pd.DataFrame({
            "paciente_id": pacientes_id,
            "plano_saude": planos_alocados,
            "faixa_etaria": etarias,
            "hospital_prestador": hospitais_alocados,
            "tipo_internacao": internacoes_tipo,
            "num_comorbidades": comorbidades_count,
            "dias_internacao": dias_internacao,
            "dias_uti": dias_uti,
            "custo_sinistro_rs": custo_total_sinistro,
            "receita_anual_rs": valor_mensalidade_ano,
            "lace_index": lace_scores,
            "readmissao_30_dias": readmissao_30d,
            "taxa_glosa_pct": taxa_glosa_prestador,
        })

        self.df = df
        return df

    def engenharia_features_e_kpis(self) -> pd.DataFrame:
        """Enriquece o DataFrame com métricas atuariais da ANS e segmentações clínicas."""
        df = self.df.copy()
        df["sinistralidade_pct"] = ((df["custo_sinistro_rs"] / df["receita_anual_rs"]) * 100).round(2)
        condicoes_lace = [
            df["lace_index"] <= 4,
            df["lace_index"] <= 9,
        ]
        rotulos_lace = [
            "Baixo Risco (LACE 0-4)",
            "Médio Risco (LACE 5-9)",
        ]
        df["faixa_risco_lace"] = np.select(condicoes_lace, rotulos_lace, default="Alto Risco (LACE 10+)")
        df["valor_glosa_rs"] = (df["custo_sinistro_rs"] * (df["taxa_glosa_pct"] / 100)).round(2)
        df["flag_custo_catastrofico"] = df["custo_sinistro_rs"] >= 25000.0
        self.df = df
        return df

    def calcular_kpis_executivos(self) -> Dict[str, float]:
        """Calcula os indicadores-chave de desempenho atuarial e assistencial."""
        df = self.df
        total_sinistros = df["custo_sinistro_rs"].sum()
        total_receita = df["receita_anual_rs"].sum()
        sinistralidade_global = (total_sinistros / total_receita) * 100
        taxa_readmissao = (df["readmissao_30_dias"].sum() / len(df)) * 100
        total_glosas = df["valor_glosa_rs"].sum()

        return {
            "total_pacientes": len(df),
            "sinistralidade_global_pct": round(sinistralidade_global, 2),
            "taxa_readmissao_30d_pct": round(taxa_readmissao, 2),
            "custo_total_sinistros_rs": round(total_sinistros, 2),
            "custo_medio_internacao_rs": round(df["custo_sinistro_rs"].mean(), 2),
            "tempo_medio_permanencia_dias": round(df["dias_internacao"].mean(), 1),
            "taxa_ocupacao_uti_pct": round((df["dias_uti"].sum() / df["dias_internacao"].sum()) * 100, 2),
            "total_glosas_auditadas_rs": round(total_glosas, 2),
        }


# =============================================================================
# 4. STORYTELLING & RESPOSTA ÀS 3 PERGUNTAS CRÍTICAS DE NEGÓCIO
# =============================================================================

def responder_pergunta_1(df: pd.DataFrame) -> pd.DataFrame:
    """Pergunta 1: Perfis e faixas de risco LACE que concentram as readmissões hospitalares."""
    resumo = (
        df.groupby(["faixa_risco_lace", "faixa_etaria"])
        .agg(
            total_pacientes=("paciente_id", "count"),
            readmissoes_30d=("readmissao_30_dias", "sum"),
            media_comorbidades=("num_comorbidades", "mean"),
            media_permanencia_dias=("dias_internacao", "mean"),
            custo_medio_rs=("custo_sinistro_rs", "mean"),
        )
        .reset_index()
    )
    resumo["taxa_readmissao_pct"] = ((resumo["readmissoes_30d"] / resumo["total_pacientes"]) * 100).round(2)
    resumo["media_comorbidades"] = resumo["media_comorbidades"].round(1)
    resumo["media_permanencia_dias"] = resumo["media_permanencia_dias"].round(1)
    resumo["custo_medio_rs"] = resumo["custo_medio_rs"].round(2)
    return resumo.sort_values(by="taxa_readmissao_pct", ascending=False)


def responder_pergunta_2(df: pd.DataFrame) -> pd.DataFrame:
    """Pergunta 2: Custos catastróficos e prestadores com distorções de faturamento e glosas."""
    resumo = (
        df.groupby(["hospital_prestador", "tipo_internacao"])
        .agg(
            internacoes=("paciente_id", "count"),
            custo_total_rs=("custo_sinistro_rs", "sum"),
            custo_medio_rs=("custo_sinistro_rs", "mean"),
            taxa_glosa_media_pct=("taxa_glosa_pct", "mean"),
            total_glosas_rs=("valor_glosa_rs", "sum"),
            casos_catastroficos=("flag_custo_catastrofico", "sum"),
        )
        .reset_index()
    )
    resumo["custo_medio_rs"] = resumo["custo_medio_rs"].round(2)
    resumo["taxa_glosa_media_pct"] = resumo["taxa_glosa_media_pct"].round(2)
    resumo["total_glosas_rs"] = resumo["total_glosas_rs"].round(2)
    return resumo.sort_values(by="custo_total_rs", ascending=False)


def responder_pergunta_3(df: pd.DataFrame) -> Dict[str, float]:
    """Pergunta 3: Modelagem de ROI de Navegação Pós-Alta e Auditoria Concorrente."""
    total_sinistros = df["custo_sinistro_rs"].sum()
    total_receita = df["receita_anual_rs"].sum()
    mlr_atual_pct = (total_sinistros / total_receita) * 100

    # Internações de Alto Risco LACE
    alto_risco = df[df["faixa_risco_lace"] == "Alto Risco (LACE 10+)"]
    custo_readmissoes_alto_risco = alto_risco[alto_risco["readmissao_30_dias"]]["custo_sinistro_rs"].sum()
    economia_readmissoes = custo_readmissoes_alto_risco * 0.45  # Redução de 45%

    # Auditoria Concorrente (recuperação de 30% das glosas controversas)
    total_glosas = df["valor_glosa_rs"].sum()
    economia_glosas = total_glosas * 0.30

    beneficio_total = economia_readmissoes + economia_glosas
    custo_programa = 180000.0  # Equipe multidisciplinar + telemonitoramento
    roi_multiplicador = round(beneficio_total / custo_programa, 2)

    novo_sinistro_projetado = total_sinistros - beneficio_total
    mlr_projetado_pct = (novo_sinistro_projetado / total_receita) * 100

    return {
        "sinistralidade_mlr_atual_pct": round(mlr_atual_pct, 2),
        "economia_readmissoes_evitadas_rs": round(economia_readmissoes, 2),
        "economia_auditoria_glosas_rs": round(economia_glosas, 2),
        "beneficio_total_anual_rs": round(beneficio_total, 2),
        "custo_programa_gestao_rs": custo_programa,
        "roi_multiplicador": roi_multiplicador,
        "sinistralidade_mlr_projetada_pct": round(mlr_projetado_pct, 2),
    }


def main() -> None:
    import sys
    if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 80)
    print("🏥 CAREPULSE: PIPELINE EXECUTIVO DE SINISTRALIDADE (MLR) & READMISSÃO LACE")
    print("=" * 80)

    pipeline = HealthcareAnalyticsPipeline()
    pipeline.gerar_dados_sinteticos()
    df_final = pipeline.engenharia_features_e_kpis()
    kpis = pipeline.calcular_kpis_executivos()

    print(f"✓ Base gerada e processada com {kpis['total_pacientes']} internações hospitalares.")
    print(f"✓ Sinistralidade Global (MLR): {kpis['sinistralidade_global_pct']}% (Meta ANS: <=78.0%)")
    print(f"✓ Taxa de Readmissão 30d: {kpis['taxa_readmissao_30d_pct']}% (Meta: <=10.0%)")
    print(f"✓ Total Sinistros Assistenciais: R$ {kpis['custo_total_sinistros_rs']:,.2f}")
    print(f"✓ Total Glosas Auditadas: R$ {kpis['total_glosas_auditadas_rs']:,.2f}")

    print("\n--- PERGUNTA 1: Readmissão 30d por Risco LACE e Faixa Etária (Top 5) ---")
    p1 = responder_pergunta_1(df_final)
    print(p1.head(5).to_string(index=False))

    print("\n--- PERGUNTA 2: Prestadores e Tipos de Internação de Maior Custo e Glosa (Top 5) ---")
    p2 = responder_pergunta_2(df_final)
    print(p2.head(5).to_string(index=False))

    print("\n--- PERGUNTA 3: ROI de Saúde Populacional e Recuperação de MLR ---")
    p3 = responder_pergunta_3(df_final)
    for k, v in p3.items():
        print(f"  • {k}: {v:,.2f}" if isinstance(v, float) else f"  • {k}: {v}")

    # Salva dataset processado
    output_path = os.path.join(os.path.dirname(__file__), "dataset_healthcare_sinistralidade.csv")
    df_final.to_csv(output_path, index=False, encoding="utf-8")
    print(f"\n✓ Dataset exportado com sucesso para: {os.path.basename(output_path)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
