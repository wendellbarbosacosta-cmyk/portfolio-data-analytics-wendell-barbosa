# 🚀 Portfólio Executivo de Data Analytics & Inteligência de Negócio (10 Verticais de Mercado)

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Pandas](https://img.shields.io/badge/Pandas-2.1+-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![NumPy](https://img.shields.io/badge/NumPy-1.26+-013243?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org)
[![Pytest](https://img.shields.io/badge/Pytest-64%2F64%20Passed%20(100%25)-brightgreen?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org)
[![Code Style: PEP 8](https://img.shields.io/badge/Code%20Style-PEP%208-blueviolet?style=for-the-badge)](https://pep8.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](https://opensource.org/licenses/MIT)

> **Autor:** [Wendell Barbosa Costa](https://github.com/wendellbarbosacosta-cmyk)  
> **Posicionamento:** Tech Lead & Especialista em Análise de Dados, Engenharia de Analytics e Modelagem de Decisão Executiva  
> **Foco Estratégico:** Resolução de dores de negócio complexas com impacto financeiro comprovado no P&L, balanço patrimonial, EBITDA e retorno sobre capital (ROI/Payback).

---

## 📌 Visão Geral do Portfólio

Este repositório consolida 10 projetos analíticos corporativos *end-to-end* em setores estratégicos da economia: **Fintech & Bancos Digitais**, **Varejo Omnichannel & Supply Chain**, **SaaS B2B & Assinaturas**, **HealthTech & Saúde Suplementar**, **AgTech & Agronegócio de Precisão**, **EnergyTech & Geração Renovável (ONS/CCEE)**, **IndustryTech & Manufatura Inteligente (Indústria 4.0 / ISO 10816-3)**, **Telecomunicações & Redes FTTH (Anatel)**, **Varejo Supermercadista & Ruptura OSA (ShelfSense)** e **Aviação Comercial & Yield RASK/CASK (AeroYield / ANAC / IATA)**.

Cada vertical foi desenhada com:
* **Arcabouço Regulatório e Operacional Real:** Resoluções BACEN CMN nº 2.682 para provisão PCLD, metas contratuais de SLA/OTIF logístico, métricas SaaS B2B (NRR e Onboarding Cliff), diretrizes ANS de sinistralidade (MLR)/LACE Index hospitalar, manejo de fertilidade de solo (Embrapa), regras de *curtailment* ONS/CCEE, padrões mecânicos ISO 10816-3, parâmetros ópticos Anatel, benchmarks de disponibilidade em gôndola (OSA >= 96%) e regulação de pontualidade e assistência ao passageiro (ANAC 400 / IATA D-15).
* **Storytelling Executivo & C-Level:** Resposta analítica quantitativa a 3 perguntas críticas de negócio por projeto com modelagem de retorno de investimento (ROI & Payback simples).
* **Engenharia de Software e Performance:** Código 100% vetorizado em Pandas/NumPy (eliminando `.apply()` lentos por `np.select`), tipagem estrita com `@dataclass` e `typing`, tratamento de encoding UTF-8 multiplataforma e suite com **64 testes automatizados com `pytest` (100% aprovados)**.

---

## 📊 Matriz Executiva dos 10 Projetos

| Projeto | Setor de Mercado | Desafio de Negócio | Arcabouço Metodológico | KPI Crítico | Impacto Financeiro / ROI | Repositório Dedicado |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| **[01. NexusRisk](./01_nexusrisk_fintech_credit/)** | Fintech & Crédito PF | Inadimplência D90+ em canais de afiliados e alavancagem tóxica | Res. CMN/BACEN 2.682, Rating (AA-H) e DTI | Default D90+: **9,8% ➔ 4,9%** | **R\$ 2,73M** em economia de PCLD (ROI **18,2x**) | [Repo NexusRisk](https://github.com/wendellbarbosacosta-cmyk/nexusrisk-credit-analytics-projeto-completo) |
| **[02. OmniLog](./02_omnilog_ecommerce_logistics/)** | E-Commerce & Logística | Quebra de SLA de entrega e vazamento de margem em fretes | Métrica OTIF (On-Time In-Full) e Churn de Recompra | OTIF: **83,8% ➔ 96,2%** | **R\$ 768k** em LTV recuperado (ROI **13,8x**) | [Repo OmniLog](https://github.com/wendellbarbosacosta-cmyk/omnilog-ecommerce-logistics) |
| **[03. PulseSaaS](./03_pulsesaas_b2b_subscriptions/)** | SaaS B2B & Assinaturas | Queda de NRR e evasão no onboarding (*Onboarding Cliff*) | Health Score Ponderado, NRR e Quick Ratio | NRR: **91,4% ➔ 112,8%** | **R\$ 648k** em ARR preservado (ROI **10,8x**) | [Repo PulseSaaS](https://github.com/wendellbarbosacosta-cmyk/pulsesaas-b2b-subscriptions) |
| **[04. CarePulse](./04_carepulse_healthtech_analytics/)** | HealthTech & Saúde | Sinistralidade (MLR) alta, readmissão 30d e distorção em glosas | LACE Index, Auditoria Concorrente e Padrões ANS | MLR: **88,4% ➔ 76,2%** | **R\$ 1,56M** em internações e glosas evitadas (ROI **8,7x**) | [Repo CarePulse](https://github.com/wendellbarbosacosta-cmyk/carepulse-healthtech-analytics) |
| **[05. AgroPrecision](./05_agroprecision_agtech_analytics/)** | AgTech & Precisão | Acidez de solo (V% < 50%), quebra de safra e sobreaplicação NPK | Manejo em Taxa Variável (VRT), Saturação V% e NDVI | Soja: **+5,4 sc/ha** \| NPK: **-R\$ 730/ha** | **R\$ 48,2M** em benefício anual total (ROI **10,2x**) | [Repo AgroPrecision](https://github.com/wendellbarbosacosta-cmyk/agroprecision-agtech-analytics) |
| **[06. VoltGrid](./06_voltgrid_energytech_analytics/)** | EnergyTech & Utilities | Curtailment ONS no Nordeste, perdas por sujidade e PLD spot | Balanço de Energia (MWh), Robótica Solar e BESS | Curtailment: **4,05%** \| Margem EBITDA: **91,8%** | **R\$ 214,1M** em soiling (Payback **1,8m**) + BESS **R\$ 446M/a** | [Repo VoltGrid](https://github.com/wendellbarbosacosta-cmyk/voltgrid-energytech-analytics-projeto) |
| **[07. ForgeIQ](./07_forgeiq_industrytech_oee/)** | IndustryTech & Manufatura | Paradas não planejadas Run-to-Failure, refugo e OEE deprimido | OEE (Disp × Perf × Qual), ISO 10816-3 e IoT CBM | OEE: **74,1%** \| Parada: **R\$ 3,26B** \| Scrap: **R\$ 2,06B** | **R\$ 2,54B/ano** recuperados via IoT (Payback **1 dia** / ROI **378x**) | [Repo ForgeIQ](https://github.com/wendellbarbosacosta-cmyk/forgeiq-industrytech-oee-projeto) |
| **[08. OptiFiber](./08_optifiber_telecom_ftth/)** | Telecom & Conectividade | Degradação óptica RX (dBm), visitas técnicas e portas ociosas | Telemetria OLT/ONT, Ocupação CTO e Wi-Fi 6 Mesh | Churn Óptico: **4,64% ➔ 1,23%** \| Ocupação: **59,3%** | **R\$ 7,98M/ano** em economia e receita (Payback **5,8m** / ROI **2,1x**) | [Repo OptiFiber](https://github.com/wendellbarbosacosta-cmyk/optifiber-telecom-ftth-projeto) |
| **[09. ShelfSense](./09_shelfsense_retail_omnichannel/)** | Varejo Omnichannel & Supermercados | Ruptura de gôndola (OSA), estoque envenenado e quebra em perecíveis | DIO (Cobertura), GMROI, DRP Preditivo e Portais RFID | OSA: **94,9%** \| GMROI: **2,61x** \| Quebra: **2,34%** | **R\$ 21,83M/ano** em valor gerado (Payback **2,5m** / ROI **4,85x**) | [Repo ShelfSense](https://github.com/wendellbarbosacosta-cmyk/shelfsense-retail-omnichannel-projeto) |
| **[10. AeroYield](./10_aeroyield_aviation_analytics/)** | Aviação Comercial & Linhas Aéreas | Spread unitário comprimido por frotas legadas, atrasos e ANAC 400 | RASK, CASK, OTP D-15, Turnaround Digital e QAV | Spread: **+4,57c/ASK** \| OTP: **84,4%** \| Load Factor: **80,4%** | **R\$ 130,4M/ano** em valor gerado (Payback **1,2m** / ROI **10,4x**) | [Repo AeroYield](https://github.com/wendellbarbosacosta-cmyk/aeroyield-aviation-analytics-projeto) |

---

## 📂 Estrutura do Repositório Integrado

```plaintext
portfolio-data-analytics-wendell-barbosa/
│
├── 01_nexusrisk_fintech_credit/                # Módulo 1: Risco de Crédito & Compliance Bancário
├── 02_omnilog_ecommerce_logistics/             # Módulo 2: Logística Omnichannel & Gestão de SLA
├── 03_pulsesaas_b2b_subscriptions/             # Módulo 3: Métricas SaaS B2B, NRR & Health Score
├── 04_carepulse_healthtech_analytics/          # Módulo 4: Sinistralidade Hospitalar & HealthTech
├── 05_agroprecision_agtech_analytics/          # Módulo 5: Agricultura de Precisão & AgTech
├── 06_voltgrid_energytech_analytics/           # Módulo 6: Geração Renovável & EnergyTech (ONS/CCEE)
├── 07_forgeiq_industrytech_oee/                # Módulo 7: Manufatura Inteligente & OEE (Indústria 4.0)
├── 08_optifiber_telecom_ftth/                  # Módulo 8: Telecomunicações & Redes Ópticas FTTH
├── 09_shelfsense_retail_omnichannel/           # Módulo 9: Varejo Omnichannel, Ruptura OSA & GMROI
├── 10_aeroyield_aviation_analytics/            # Módulo 10: Aviação Comercial, Yield RASK/CASK & OTP D-15
│   ├── dataset_aviacao_yield_rotas.csv         # Base com 500 rotas comerciais brasileiras
│   ├── pipeline_aviation_yield_analytics.py    # Pipeline analítico de yield, turnaround e ANAC 400
│   ├── requirements.txt                        # Dependências específicas do módulo
│   └── README.md                               # Documentação executiva completa
│
├── tests/                                      # Suite Completa de Testes Automatizados (64 Testes)
│   ├── __init__.py
│   ├── test_credit_risk.py                     # Validação de regras BACEN, ratings e PCLD
│   ├── test_ecommerce_logistics.py             # Validação de OTIF, subsídios e fretes
│   ├── test_saas_metrics.py                    # Validação de Health Score, NRR e churn
│   ├── test_healthcare_analytics.py            # Validação de LACE Index, MLR e glosas
│   ├── test_agrotech_analytics.py              # Validação de manejo VRT, fertilidade e margens
│   ├── test_energytech_analytics.py            # Validação de balanço energético, curtailment e BESS
│   ├── test_industry_oee_analytics.py          # Validação de OEE, ISO 10816 e ROI de IoT Preditiva
│   ├── test_telecom_ftth_analytics.py          # Validação de atenuação RX, portas CTO e ROI Telecom
│   ├── test_retail_omnichannel_analytics.py    # Validação de ruptura OSA, GMROI e ROI Varejo
│   └── test_aviation_yield_analytics.py        # Validação de RASK/CASK, turnaround e ROI Aviação
│
├── .gitignore                                  # Governança de arquivos, dados e caches
├── LICENSE                                     # Licença MIT Permissiva
├── pytest.ini                                  # Configuração padronizada do runner de testes
├── README.md                                   # Documentação central do portfólio
└── requirements.txt                            # Stack consolidada de dependências
```

---

## ⚙️ Arquitetura Técnica & Melhores Práticas

* **Vetorização de Alta Performance:** Substituição de loops e `.apply(..., axis=1)` por operações matriciais em NumPy (`np.select`, `np.where`), permitindo processamento em milissegundos.
* **Governança e Reprodutibilidade:** Seeds fixados (`random_seed=42`) para garantir rastreabilidade completa e auditabilidade estatística.
* **Tipagem Estrita e Clean Code:** Classes de configuração com `@dataclass(frozen=True)`, tipagem estrita com `typing` e padrões PEP 8.
* **Confiabilidade com Pytest:** **64 testes automatizados** cobrindo integridade de schema, conformidade matemática e cálculos financeiros de ROI com 100% de taxa de aprovação.

---

## 🚀 Instalação e Execução

### 1. Clonar o Repositório

```bash
git clone https://github.com/wendellbarbosacosta-cmyk/portfolio-data-analytics-wendell-barbosa.git
cd portfolio-data-analytics-wendell-barbosa
```

### 2. Configurar o Ambiente Virtual

```bash
# Windows (PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4. Executar os Testes Automatizados (64 Testes)

```bash
pytest tests/ -v
```

### 5. Executar os Pipelines Individuais

```bash
python 01_nexusrisk_fintech_credit/pipeline_credit_risk.py
python 02_omnilog_ecommerce_logistics/pipeline_ecommerce_logistics.py
python 03_pulsesaas_b2b_subscriptions/pipeline_saas_metrics.py
python 04_carepulse_healthtech_analytics/pipeline_healthcare_analytics.py
python 05_agroprecision_agtech_analytics/pipeline_agrotech_analytics.py
python 06_voltgrid_energytech_analytics/pipeline_energytech_analytics.py
python 07_forgeiq_industrytech_oee/pipeline_industry_oee_analytics.py
python 08_optifiber_telecom_ftth/pipeline_telecom_ftth_analytics.py
python 09_shelfsense_retail_omnichannel/pipeline_retail_omnichannel_analytics.py
python 10_aeroyield_aviation_analytics/pipeline_aviation_yield_analytics.py
```

---

## 👤 Autor & Contato

**Wendell Barbosa Costa**  
*Tech Lead & Especialista em Análise de Dados, Engenharia de Analytics & Modelagem de Negócios*  
* **GitHub:** [@wendellbarbosacosta-cmyk](https://github.com/wendellbarbosacosta-cmyk)  
* **Repositório:** [portfolio-data-analytics-wendell-barbosa](https://github.com/wendellbarbosacosta-cmyk/portfolio-data-analytics-wendell-barbosa)
