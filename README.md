# 🚀 Portfólio Executivo de Data Analytics & Inteligência de Negócio

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Pandas](https://img.shields.io/badge/Pandas-2.1+-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![NumPy](https://img.shields.io/badge/NumPy-1.26+-013243?style=for-the-badge&logo=numpy&logoColor=white)](https://numpy.org)
[![Pytest](https://img.shields.io/badge/Pytest-8.0+-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white)](https://pytest.org)
[![Code Style: PEP 8](https://img.shields.io/badge/Code%20Style-PEP%208-blueviolet?style=for-the-badge)](https://pep8.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](https://opensource.org/licenses/MIT)

> **Autor:** [Wendell Barbosa Costa](https://github.com/wendellbarbosacosta-cmyk)  
> **Posicionamento:** Especialista em Análise de Dados, Engenharia de Analytics & Modelagem de Decisão Executiva  
> **Foco:** Resolução de dores de negócio complexas com impacto financeiro comprovado (P&L, Balanço, LTV e Retenção de Receita)

---

## 📌 Visão Geral do Portfólio

Este repositório reúne projetos analíticos end-to-end de alta complexidade em três dos setores mais dinâmicos da economia contemporânea: **Fintech & Bancos Digitais**, **Varejo Omnichannel & Supply Chain**, e **SaaS B2B & Economia da Assinatura**.

Cada módulo foi desenhado com:
* **Arcabouço Regulatório e Operacional Real:** Resolução BACEN CMN nº 2.682 para provisão PCLD, metas contratuais de SLA/OTIF logístico e benchmarks globais de NRR/Health Score em SaaS.
* **Storytelling Executivo:** Resposta analítica direta a 3 perguntas críticas de negócio com modelagem de ROI para suporte ao C-Level e Conselho de Administração.
* **Engenharia de Software e Performance:** Código 100% vetorizado em Pandas/NumPy, conformidade com a PEP 8, type hints estritos, tratamento de encoding UTF-8 multiplataforma e suite completa de testes unitários automatizados com `pytest`.

---

## 📊 Matriz Executiva dos Projetos

| Projeto | Setor de Mercado | Desafio de Negócio | Arcabouço Metodológico | KPI Crítico | Impacto Financeiro / ROI |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **[01. NexusRisk](./01_nexusrisk_fintech_credit/)** | Fintech & Crédito PF | Inadimplência D90+ em canais de afiliados e alavancagem tóxica | Res. CMN/BACEN 2.682, Rating de Risco (AA-H) e DTI | Taxa D90+: **9,8% ➔ 4,9%** | **R$ 2,73M** em economia de PCLD (ROI **18,2x**) |
| **[02. OmniLog](./02_omnilog_ecommerce_logistics/)** | E-Commerce & Supply Chain | Quebra de SLA de entrega e vazamento de margem em fretes | Métrica OTIF (On-Time In-Full) e Churn de Recompra | OTIF: **83,8% ➔ 96,2%** | **R$ 768k** em LTV recuperado (ROI **13,8x**) |
| **[03. PulseSaaS](./03_pulsesaas_b2b_subscriptions/)** | SaaS B2B & Cloud Subscriptions | Queda de NRR e evasão no onboarding (*Onboarding Cliff*) | Health Score Ponderado (4 pilares), NRR e Quick Ratio | NRR: **91,4% ➔ 112,8%** | **R$ 648k** em ARR preservado (ROI **10,8x**) |

---

## 📂 Estrutura do Repositório

```plaintext
portfolio-data-analytics-wendell-barbosa/
│
├── 01_nexusrisk_fintech_credit/                # Módulo 1: Risco de Crédito & Compliance Bancário
│   ├── dataset_carteira_credito_analisada.csv  # Base analisada e classificada (BACEN)
│   ├── pipeline_credit_risk.py                 # Pipeline de feature engineering & storytelling
│   ├── requirements.txt                        # Dependências específicas do módulo
│   └── README.md                               # Documentação executiva completa
│
├── 02_omnilog_ecommerce_logistics/             # Módulo 2: SLA Logístico, OTIF & LTV
│   ├── dataset_logistica_ecommerce.csv         # Base de despachos, SLAs e recompras
│   ├── pipeline_ecommerce_logistics.py         # Pipeline de auditoria logística & ROI
│   ├── requirements.txt                        # Dependências específicas do módulo
│   └── README.md                               # Documentação executiva completa
│
├── 03_pulsesaas_b2b_subscriptions/             # Módulo 3: Métricas SaaS B2B & Retenção
│   ├── dataset_saas_metrics_analisado.csv      # Base de clientes, MRR e Health Scores
│   ├── pipeline_saas_metrics.py                # Pipeline de NRR, churn e dimensionamento CS
│   ├── requirements.txt                        # Dependências específicas do módulo
│   └── README.md                               # Documentação executiva completa
│
├── tests/                                      # Suite de Testes Automatizados (Pytest)
│   ├── __init__.py
│   ├── test_credit_risk.py                     # Validação de regras BACEN, ratings e PCLD
│   ├── test_ecommerce_logistics.py             # Validação de OTIF, subsídios e indenizações
│   └── test_saas_metrics.py                    # Validação de Health Score, NRR e churn
│
├── .gitignore                                  # Governança de arquivos, dados e caches
├── LICENSE                                     # Licença MIT Permissiva
├── README.md                                   # Documentação central do portfólio
└── requirements.txt                            # Stack consolidada de dependências
```

---

## ⚙️ Arquitetura Técnica & Melhores Práticas

* **Vetorização de Alta Performance:** Substituição sistemática de iterações lentas (`df.apply(..., axis=1)`) por matrizes lógicas e `np.select` do NumPy, assegurando execução em milissegundos mesmo sobre bases volumosas.
* **Governança e Reprodutibilidade:** Seeds pseudoaleatórios fixados (`random_seed=42`) para garantir que qualquer analista, auditor ou recrutador obtenha rigorosamente os mesmos números e distribuições.
* **Tipagem Estrita e Clean Code:** Type annotations nativas (`typing`, `dataclasses`), padrões PEP 8 estritos e docstrings no padrão Google Style.
* **Confiabilidade com Pytest:** 9 testes automatizados cobrindo lógica matemática, faixas limítrofes, integridade de schema e cálculos de ROI.

---

## 🚀 Instalação e Execução

### 1. Clonar o Repositório

```bash
git clone https://github.com/wendellbarbosacosta-cmyk/portfolio-data-analytics-wendell-barbosa.git
cd portfolio-data-analytics-wendell-barbosa
```

### 2. Configurar o Ambiente Virtual

```bash
# Criação do ambiente virtual
python -m venv .venv

# Ativação do ambiente
# No Linux / macOS:
source .venv/bin/activate
# No Windows (PowerShell):
.venv\Scripts\Activate.ps1
# No Windows (CMD):
.venv\Scripts\activate.bat
```

### 3. Instalar Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Executar os Testes Automatizados

```bash
pytest tests/ -v
```

### 5. Executar os Pipelines Individuais

```bash
# Executar Módulo de Risco de Crédito (NexusRisk)
python 01_nexusrisk_fintech_credit/pipeline_credit_risk.py

# Executar Módulo Logístico (OmniLog)
python 02_omnilog_ecommerce_logistics/pipeline_ecommerce_logistics.py

# Executar Módulo de SaaS B2B (PulseSaaS)
python 03_pulsesaas_b2b_subscriptions/pipeline_saas_metrics.py
```

---

## 📄 Licença

Este projeto é distribuído sob a licença **MIT** — consulte o arquivo [LICENSE](./LICENSE) para obter mais detalhes.

---

## 👤 Contato & Autor

**Wendell Barbosa Costa**  
*Especialista em Análise de Dados, Modelagem de Negócios & Analytics Engineering*  
* **GitHub:** [@wendellbarbosacosta-cmyk](https://github.com/wendellbarbosacosta-cmyk)  
* **Repositório:** [portfolio-data-analytics-wendell-barbosa](https://github.com/wendellbarbosacosta-cmyk/portfolio-data-analytics-wendell-barbosa)
