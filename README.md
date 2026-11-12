# 🚀 Portfólio Executivo de Data Analytics & Inteligência de Negócio (7 Verticais de Mercado)

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Pandas](https://img.shields.io/badge/Pandas-2.1+-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![NumPy](https://img.shields.io/badge/NumPy-1.26+-013243?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org)
[![Pytest](https://img.shields.io/badge/Pytest-8.0+-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org)
[![Code Style: PEP 8](https://img.shields.io/badge/Code%20Style-PEP%208-blueviolet?style=for-the-badge)](https://pep8.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](https://opensource.org/licenses/MIT)

> **Autor:** [Wendell Barbosa Costa](https://github.com/wendellbarbosacosta-cmyk)  
> **Posicionamento:** Tech Lead & Especialista em Análise de Dados, Engenharia de Analytics e Modelagem de Decisão Executiva  
> **Foco Estratégico:** Resolução de dores de negócio complexas com impacto financeiro comprovado no P&L, balanço patrimonial, EBITDA e retorno sobre capital (ROI/Payback).

---

## 📌 Visão Geral do Portfólio

Este repositório consolida 7 projetos analíticos corporativos *end-to-end* em setores estratégicos da economia: **Fintech & Bancos Digitais**, **Varejo Omnichannel & Supply Chain**, **SaaS B2B & Assinaturas**, **HealthTech & Saúde Suplementar**, **AgTech & Agronegócio de Precisão**, **EnergyTech & Geração Renovável (ONS/CCEE)** e **IndustryTech & Manufatura Inteligente (Indústria 4.0 / ISO 10816-3)**.

Cada vertical foi desenhada com:
* **Arcabouço Regulatório e Operacional Real:** Resoluções BACEN CMN nº 2.682 para provisão PCLD, metas contratuais de SLA/OTIF logístico, métricas SaaS B2B (NRR e Onboarding Cliff), diretrizes ANS de sinistralidade (MLR)/LACE Index hospitalar, manejo de fertilidade de solo (Embrapa), regras de *curtailment* ONS/CCEE e padrões mecânicos ISO 10816-3.
* **Storytelling Executivo & C-Level:** Resposta analítica quantitativa a 3 perguntas críticas de negócio por projeto com modelagem de retorno de investimento (ROI & Payback simples).
* **Engenharia de Software e Performance:** Código 100% vetorizado em Pandas/NumPy (eliminando `.apply()` lentos por `np.select`), tipagem estrita com `@dataclass` e `typing`, tratamento de encoding UTF-8 multiplataforma e suite com **34 testes automatizados com `pytest` (100% aprovados)**.

---

## 📊 Matriz Executiva dos 7 Projetos

| Projeto | Setor de Mercado | Desafio de Negócio | Arcabouço Metodológico | KPI Crítico | Impacto Financeiro / ROI | Repositório Dedicado |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| **[01. NexusRisk](./01_nexusrisk_fintech_credit/)** | Fintech & Crédito PF | Inadimplência D90+ em canais de afiliados e alavancagem tóxica | Res. CMN/BACEN 2.682, Rating (AA-H) e DTI | Default D90+: **9,8% ➔ 4,9%** | **R\$ 2,73M** em economia de PCLD (ROI **18,2x**) | [Repo NexusRisk](https://github.com/wendellbarbosacosta-cmyk/nexusrisk-credit-analytics-projeto-completo) |
| **[02. OmniLog](./02_omnilog_ecommerce_logistics/)** | E-Commerce & Logística | Quebra de SLA de entrega e vazamento de margem em fretes | Métrica OTIF (On-Time In-Full) e Churn de Recompra | OTIF: **83,8% ➔ 96,2%** | **R\$ 768k** em LTV recuperado (ROI **13,8x**) | [Repo OmniLog](https://github.com/wendellbarbosacosta-cmyk/omnilog-ecommerce-logistics) |
| **[03. PulseSaaS](./03_pulsesaas_b2b_subscriptions/)** | SaaS B2B & Assinaturas | Queda de NRR e evasão no onboarding (*Onboarding Cliff*) | Health Score Ponderado, NRR e Quick Ratio | NRR: **91,4% ➔ 112,8%** | **R\$ 648k** em ARR preservado (ROI **10,8x**) | [Repo PulseSaaS](https://github.com/wendellbarbosacosta-cmyk/pulsesaas-b2b-subscriptions) |
| **[04. CarePulse](./04_carepulse_healthtech_analytics/)** | HealthTech & Saúde | Sinistralidade (MLR) alta, readmissão 30d e distorção em glosas | LACE Index, Auditoria Concorrente e Padrões ANS | MLR: **88,4% ➔ 76,2%** | **R\$ 1,56M** em internações e glosas evitadas (ROI **8,7x**) | [Repo CarePulse](https://github.com/wendellbarbosacosta-cmyk/carepulse-healthtech-analytics) |
| **[05. AgroPrecision](./05_agroprecision_agtech_analytics/)** | AgTech & Precisão | Acidez de solo (V% < 50%), quebra de safra e sobreaplicação NPK | Manejo em Taxa Variável (VRT), Saturação V% e NDVI | Soja: **+5,4 sc/ha** \| NPK: **-R\$ 730/ha** | **R\$ 48,2M** em benefício anual total (ROI **10,2x**) | [Repo AgroPrecision](https://github.com/wendellbarbosacosta-cmyk/agroprecision-agtech-analytics) |
| **[06. VoltGrid](./06_voltgrid_energytech_analytics/)** | EnergyTech & Utilities | Curtailment ONS no Nordeste, perdas por sujidade e PLD spot | Balanço de Energia (MWh), Robótica Solar e BESS | Curtailment: **4,05%** \| Margem EBITDA: **91,8%** | **R\$ 214,1M** em soiling (Payback **1,8m**) + BESS **R\$ 446M/a** | [Repo VoltGrid](https://github.com/wendellbarbosacosta-cmyk/voltgrid-energytech-analytics-projeto) |
| **[07. ForgeIQ](./07_forgeiq_industrytech_oee/)** | IndustryTech & Manufatura | Paradas não planejadas Run-to-Failure, refugo e OEE deprimido | OEE (Disp × Perf × Qual), ISO 10816-3 e IoT CBM | OEE: **74,1%** \| Parada: **R\$ 3,26B** \| Scrap: **R\$ 2,06B** | **R\$ 2,54B/ano** recuperados via IoT (Payback **1 dia** / ROI **378x**) | [Repo ForgeIQ](https://github.com/wendellbarbosacosta-cmyk/forgeiq-industrytech-oee-projeto) |

---

## 📂 Estrutura do Repositório Integrado

```plaintext
portfolio-data-analytics-wendell-barbosa/
│
├── 01_nexusrisk_fintech_credit/                # Módulo 1: Risco de Crédito & Compliance Bancário
│   ├── dataset_carteira_credito_analisada.csv  # Base analisada e classificada (BACEN 2.682)
│   ├── pipeline_credit_risk.py                 # Pipeline de feature engineering & ratings
│   ├── requirements.txt                        # Dependências específicas do módulo
│   └── README.md                               # Documentação executiva completa
│
├── 02_omnilog_ecommerce_logistics/             # Módulo 2: Logística Omnichannel & Gestão de SLA
│   ├── dataset_logistica_ecommerce.csv         # Base de despachos, transportadoras e OTIF
│   ├── pipeline_ecommerce_logistics.py         # Pipeline de lead time, fretes e churn
│   ├── requirements.txt                        # Dependências específicas do módulo
│   └── README.md                               # Documentação executiva completa
│
├── 03_pulsesaas_b2b_subscriptions/             # Módulo 3: Métricas SaaS B2B, NRR & Health Score
│   ├── dataset_saas_metrics_analisado.csv      # Base de contas, MRR, telemetria de produto
│   ├── pipeline_saas_metrics.py                # Pipeline de NRR, churn e dimensionamento CS
│   ├── requirements.txt                        # Dependências específicas do módulo
│   └── README.md                               # Documentação executiva completa
│
├── 04_carepulse_healthtech_analytics/          # Módulo 4: Sinistralidade Hospitalar & HealthTech
│   ├── dataset_healthcare_sinistralidade.csv   # Base de internações, LACE Index e glosas
│   ├── pipeline_healthcare_analytics.py        # Pipeline de MLR, readmissão e ROI em Saúde
│   ├── requirements.txt                        # Dependências específicas do módulo
│   └── README.md                               # Documentação executiva completa
│
├── 05_agroprecision_agtech_analytics/          # Módulo 5: Agricultura de Precisão & AgTech
│   ├── dataset_agrotech_talhoes.csv            # Base de talhões, fertilidade, V% e NDVI
│   ├── pipeline_agrotech_analytics.py          # Pipeline de produtividade, manejo VRT e ROI
│   ├── requirements.txt                        # Dependências específicas do módulo
│   └── README.md                               # Documentação executiva completa
│
├── 06_voltgrid_energytech_analytics/           # Módulo 6: Geração Renovável & EnergyTech (ONS/CCEE)
│   ├── dataset_energytech_usinas.csv           # Base com 480 usinas geradoras (Solar & Eólica)
│   ├── pipeline_energytech_analytics.py        # Pipeline de curtailment, robótica e baterias BESS
│   ├── requirements.txt                        # Dependências específicas do módulo
│   └── README.md                               # Documentação executiva completa
│
├── 07_forgeiq_industrytech_oee/                # Módulo 7: Manufatura Inteligente & OEE (Indústria 4.0)
│   ├── dataset_industrytech_oee.csv            # Base com 500 máquinas industriais críticas
│   ├── pipeline_industry_oee_analytics.py      # Pipeline de OEE, vibração ISO 10816 e IoT CBM
│   ├── requirements.txt                        # Dependências específicas do módulo
│   └── README.md                               # Documentação executiva completa
│
├── tests/                                      # Suite Completa de Testes Automatizados (34 Testes)
│   ├── __init__.py
│   ├── test_credit_risk.py                     # Validação de regras BACEN, ratings e PCLD
│   ├── test_ecommerce_logistics.py             # Validação de OTIF, subsídios e fretes
│   ├── test_saas_metrics.py                    # Validação de Health Score, NRR e churn
│   ├── test_healthcare_analytics.py            # Validação de LACE Index, MLR e glosas
│   ├── test_agrotech_analytics.py              # Validação de manejo VRT, fertilidade e margens
│   ├── test_energytech_analytics.py            # Validação de balanço energético, curtailment e BESS
│   └── test_industry_oee_analytics.py          # Validação de OEE, ISO 10816 e ROI de IoT Preditiva
│
├── .gitignore                                  # Governança de arquivos, dados e caches
├── LICENSE                                     # Licença MIT Permissiva
├── README.md                                   # Documentação central do portfólio
└── requirements.txt                            # Stack consolidada de dependências
```

---

## ⚙️ Arquitetura Técnica & Melhores Práticas

* **Vetorização de Alta Performance:** Substituição de loops e `.apply(..., axis=1)` por operações matriciais em NumPy (`np.select`, `np.where`), permitindo processamento em milissegundos.
* **Governança e Reprodutibilidade:** Seeds fixados (`random_seed=42`) para garantir rastreabilidade completa e auditabilidade estatística.
* **Tipagem Estrita e Clean Code:** Classes de configuração com `@dataclass(frozen=True)`, tipagem estrita com `typing` e padrões PEP 8.
* **Confiabilidade com Pytest:** **34 testes automatizados** cobrindo integridade de schema, conformidade matemática e cálculos financeiros de ROI com 100% de taxa de aprovação.

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

### 4. Executar os Testes Automatizados (34 Testes)

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
```

---

## 👤 Autor & Contato

**Wendell Barbosa Costa**  
*Tech Lead & Especialista em Análise de Dados, Engenharia de Analytics & Modelagem de Negócios*  
* **GitHub:** [@wendellbarbosacosta-cmyk](https://github.com/wendellbarbosacosta-cmyk)  
* **Repositório:** [portfolio-data-analytics-wendell-barbosa](https://github.com/wendellbarbosacosta-cmyk/portfolio-data-analytics-wendell-barbosa)
