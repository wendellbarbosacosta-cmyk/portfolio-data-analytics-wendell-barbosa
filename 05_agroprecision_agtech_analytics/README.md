# 🌾 AgroPrecision Analytics — Otimização de Produtividade (sc/ha), Eficiência de Insumos e Agricultura de Precisão

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PEP 8 Compliant](https://img.shields.io/badge/Code%20Style-PEP%208-green.svg)](https://peps.python.org/pep-0008/)
[![Pandas](https://img.shields.io/badge/Data%20Analysis-Pandas-orange.svg)](https://pandas.pydata.org/)
[![Seaborn & Plotly](https://img.shields.io/badge/Visualization-Seaborn%20%7C%20Plotly-purple.svg)](https://plotly.com/)
[![AgTech & Embrapa Standard](https://img.shields.io/badge/Standard-AgTech%20%26%20Precision%20Farming-brightgreen.svg)](#)
[![Status](https://img.shields.io/badge/Status-Executive%20Ready-success.svg)](#)

> **Projeto Executivo de Portfólio de Data Analytics** focado no setor de **AgTech, Agronegócio de Precisão e Produção de Grãos (Soja e Milho Safrinha)**. O objetivo é diagnosticar fatores limitantes de produtividade agrícola, eliminar o desperdício de fertilizantes NPK e defensivos via **Manejo em Taxa Variável (VRT)** e maximizar a margem líquida por hectare (R$/ha) com evidências estatísticas e sensoriamento remoto (NDVI).

---

## 📌 1. Contexto do Problema de Negócio

O agronegócio é o principal motor da balança comercial brasileira, respondendo por mais de 25% do PIB nacional. Em operações de grande escala de grãos no Cerrado e Sul do país, a margem operacional por hectare é pressionada pela volatilidade cambial das commodities e pela escalada no custo de insumos agrícolas (fertilizantes fosfatados, potássio e defensivos).

Uma cooperativa / grupo agrícola monitorando **550 talhões comerciais (totalizando mais de 65.000 hectares)** identificou uma disparidade alarmante:
1. **Quebra Média de Produtividade:** A produtividade média da soja atingiu **58,4 sc/ha**, muito aquém do potencial agronômico de **72,0 sc/ha** esperado para o pacote tecnológico contratado.
2. **Superdosagem Indiscriminada de Insumos:** A aplicação convencional de fertilizantes em taxa fixa uniforme gerava um custo de insumos de **R$ 3.180/ha**, com aplicação de adubo em excesso em manchas naturalmente férteis e subnutrição em zonas empobrecidas.
3. **Acidez Subsuperficial de Solo:** Talhões com saturação de bases ($V% < 50%$) apresentavam quebras severas de safra e estresse radicular, agravados por veranicos de 14 a 21 dias.

---

## 🎯 2. KPIs Principais Analisados

| Indicador Agronômico / Financeiro | Valor Atual | Benchmark de Alta Performance | Status / Diagnóstico |
| :--- | :---: | :---: | :---: |
| **Produtividade Média Soja** | **58,4 sc/ha** | $ge 72,0$ sc/ha | 🔴 Gap de -13,6 sc/ha |
| **Produtividade Média Milho Safrinha** | **96,2 sc/ha** | $ge 115,0$ sc/ha | 🔴 Gap de -18,8 sc/ha |
| **Margem Líquida Média Operacional** | **R$ 2.450 / ha** | $ge$ R$ 3.500 / ha | 🟡 Comprimida pelo Custo |
| **Custo Médio de Insumos NPK/Defensivos** | **R$ 2.870 / ha** | $le$ R$ 2.400 / ha (VRT) | 🔴 Sobreaplicação (+19,5%) |
| **Índice Médio de Vigor Vegetativo (NDVI)** | **0,642** | $ge 0,750$ no R2/R3 | 🟡 Heterogeneidade Foliar |
| **Talhões Críticos com Acidez ($V% < 50%$)** | **142 talhões (25,8%)** | $le 10,0%$ | 🔴 Risco de Solvência |
| **Adoção de Taxa Variável (VRT)** | **42,0% da área** | Meta: 100% | 🟡 Oportunidade de Expansão |

---

## 🔍 3. Storytelling: Resposta às 3 Perguntas Críticas de Negócio

### ❓ Pergunta 1: Qual o impacto da acidez e saturação por bases (V%) na produtividade real da soja?
* **Causa Raiz Identificada:** Talhões com saturação por bases corrigida ($V% > 65%$) produzem em média **66,8 sc/ha**, contra apenas **49,6 sc/ha** em solos ácidos ($V% < 50%$) — quebra de **17,2 sc/ha (-25,8%)**.
* **Decisão de Negócio:** Plano diretor de **correção profunda de perfil** com aplicação antecipada de calcário dolomítico e gesso agrícola nos 142 talhões críticos.
* **Impacto:** Recuperação de **+12,5 sc/ha** e acréscimo de **R$ 1.687,50/ha** em receita bruta.

### ❓ Pergunta 2: Qual a eficiência econômica do Manejo em Taxa Variável (VRT) vs. Taxa Fixa Convencional?
* **Causa Raiz Identificada:** A taxa fixa desperdiça insumos em zonas ricas e subnutre zonas fracas. O manejo VRT reduz o custo de insumos de **R$ 3.180/ha para R$ 2.450/ha (economia de R$ 730/ha)** e eleva a produtividade em **+5,4 sc/ha**.
* **Decisão de Negócio:** Mapas de prescrição agronômica georreferenciados integrados ao piloto automático dos distribuidores de sólidos.
* **Impacto:** Diferencial líquido de margem de **+R$ 1.459/ha** a favor do manejo VRT.

### ❓ Pergunta 3: Qual o Retorno sobre o Investimento (ROI) de converter 100% da lavoura para Agricultura de Precisão?
* **Investimento Necessário:** Amostragem em grade georreferenciada e calibração de maquinário: **R$ 125,00 / ha** (R$ 4.750.000 para os 38.000 ha convencionais).
* **Benefício Financeiro Anual:** R$ 27,7M em economia de NPK + R$ 20,5M em sacas adicionais = **R$ 48.260.000 / safra**.
* **Retorno Financeiro:** **ROI de 10,2x no primeiro ano**, com elevação da margem líquida para **R$ 3.420 / ha**.

---

## 🚀 5. Próximos Passos (Fase 2 do Projeto)

1. **Sensoriamento Remoto Automatizado com Satélites (Sentinel-2 & Planet):** Pipeline de ingestão contínua de índices biofísicos (NDVI, NDRE e EVI) em intervalos de 5 dias.
2. **Modelo Preditivo de Safra com Machine Learning (Random Forest & XGBoost):** Estimativa da colheita final em D-45 com base em dados de solo, telemetria climática e variedades.
3. **Integração IoT com Computadores de Bordo de Colheitadeiras:** Coleta de dados via telemetria ISOBUS (mapas de colheita pixel a pixel).
