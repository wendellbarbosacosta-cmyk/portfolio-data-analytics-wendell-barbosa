# 💳 NexusRisk: Otimização de Carteira de Crédito PF & Mitigação de Inadimplência D90+

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Pandas](https://img.shields.io/badge/Pandas-2.1+-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![Seaborn](https://img.shields.io/badge/Seaborn-0.13+-4C72B0?style=for-the-badge)](https://seaborn.pydata.org)
[![Plotly](https://img.shields.io/badge/Plotly-5.18+-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)
[![PEP 8](https://img.shields.io/badge/Code%20Style-PEP%208-blueviolet?style=for-the-badge)](https://pep8.org)
[![Regulatory](https://img.shields.io/badge/Compliance-BACEN%20CMN%202.682-008080?style=for-the-badge)](https://www.bcb.gov.br)

> **Projeto de Análise de Dados e Inteligência de Negócio para o Setor Financeiro / Fintechs.**  
> Foco executivo na identificação de perdas por inadimplência crônica (D90+), calibração de limites por comprometimento de renda (DTI) e modelagem de provisão regulatória (PCLD).

---

## 📌 1. Contexto do Problema & Desafio de Negócio

Uma fintech brasileira de serviços financeiros digitais e cartões de crédito expandiu sua base ativa de clientes em **+600% nos últimos 18 meses**, impulsionada por campanhas massivas de tráfego pago e parcerias com canais de afiliados. 

Contudo, essa expansão acelerada gerou um efeito colateral crítico na saúde da carteira de crédito:
* A taxa de inadimplência superior a 90 dias (**NPL 90+ / D90+**) saltou de **4,2% para 9,8%**, superando a média prudencial de mercado (6,5%).
* A **Provisão para Créditos de Liquidação Duvidosa (PCLD)** escalou exponencialmente, consumindo **42% do lucro operacional bruto** da instituição.
* O Comitê Executivo e de Risco precisava de uma resposta rápida e fundamentada em dados para **três dilemas estratégicos**:
  1. *Onde exatamente está o vazamento de inadimplência e qual canal é o vilão da rentabilidade?*
  2. *Estamos concedendo limites desproporcionais ou recusando bons pagadores por falta de calibração fina?*
  3. *Qual intervenção preventiva gera o maior retorno financeiro (ROI) para reverter a carteira antes do default irreversible?*

---

## 🎯 2. Regras de Negócio e Arcabouço Regulatório

Para garantir aderência estrita às práticas do mercado bancário brasileiro, foram implementadas as seguintes diretrizes:

1. **Classificação da Régua de Atraso e Default:**
   * `Em Dia (D0)`: Sem histórico de atraso na fatura atual.
   * `Atraso Leve (D1 - D15)`: Atraso pontual operacional ou esquecimento; probabilidade de autocura > 85%.
   * `Alerta (D16 - D60)`: Deterioração de liquidez; momento ideal para repactuação preventiva.
   * `Crítico (D61 - D90)`: Risco iminente de perda integral; roll-rate para D90+ atinge 65%.
   * `Inadimplente (D90+)`: Considerado default/NPL para fins de balanço e provisão.

2. **Cálculo de PCLD segundo a Resolução CMN/BACEN nº 2.682:**
   O provisionamento obrigatório segue as alíquotas oficiais vinculadas ao rating de risco do cliente:
   PCLD (R$) = Saldo Devedor * Alíquota do Rating
   * `AA (0,0%)` | `A (0,5%)` | `B (1,0%)` | `C (3,0%)` | `D (10,0%)` | `E (30,0%)` | `F (50,0%)` | `G (70,0%)` | `H (100,0%)`

3. **Índice DTI (Debt-to-Income / Alavancagem):**
   DTI = Limite Concedido / Renda Mensal Comprovada
   * Limite prudencial: DTI <= 0,40 (40%). Valores superiores a 0,70 com Score < 600 foram classificados como **Alavancagem Tóxica**.

---

## 📊 3. KPIs Principais Analisados

| Métrica / KPI | Valor Atual da Carteira | Benchmark Saudável | Variação / Diagnóstico |
| :--- | :---: | :---: | :--- |
| **Volume Total sob Gestão (AUM)** | **R$ 48.720.000** | — | Carteira com 350.000 contas ativas |
| **Taxa de Inadimplência D90+** | **9,82%** | <= 6,00% | +3,82 p.p. acima do teto de tolerância |
| **Provisão PCLD Acumulada** | **R$ 3.840.500** | R$ 1.950.000 | Sobrecarga de R$ 1,89M no balanço trimestral |
| **Net Interest Margin (NIM)** | **6,10% a.a.** | 12,0% - 15,0% | Margem comprimida pelo custo do risco |
| **Score Médio da Carteira** | **638 pontos** | >= 680 pontos | Distribuição bimodal com cauda de risco em afiliados |
| **Alavancagem Média (DTI)** | **0,64x renda** | <= 0,35x renda | Concessão inicial de limite desproporcional |

---

## 💡 4. Storytelling Executivo: Respostas às 3 Perguntas Críticas

### 🔍 Pergunta 1: Qual canal de aquisição e perfil de renda concentra a maior taxa de inadimplência e perda financeira?
* **Constatação dos Dados:** O canal **"Parcerias & Afiliados"** apresentou uma taxa de default D90+ de **21,8%**, seguido pelo **"Tráfego Pago Agressivo" (12,4%)**. Em contrapartida, o canal **"Orgânico"** teve apenas **3,4%** e o **"Member-get-Member"** teve **2,1%**.
* **Causa Raiz:** Afiliados monetizavam por aprovação (CPA), incentivando a atração de perfis inadimplentes com renda até R$ 2.500.
* **Ação Executiva Recomendada:** Migração para modelo de comissionamento atrelado à adimplência após 90 dias (Chargeback por Default). **Impacto: Redução de R$ 1,4M/ano em novo PCLD.**

### 🔍 Pergunta 2: A esteira de concessão de limite está calibrada ou geramos alavancagem tóxica em clientes intermediários?
* **Constatação dos Dados:** Clientes com **Score Médio (550 a 699)** receberam limite médio de **R$ 4.850** para renda média de **R$ 3.100** (DTI = 1,56x), respondendo por **48% do volume de default**.
* **Ação Executiva Recomendada:** Trava algorítmica de DTI máximo em **0,40x da renda** no onboarding para scores abaixo de 700. **Impacto: Redução do default da faixa de 14,2% para 5,3%.**

### 🔍 Pergunta 3: Qual o ROI de adotar uma régua preventiva de renegociação digital no estágio de Alerta (D16 - D60)?
* **Constatação dos Dados:** Carteira possuía **R$ 6,2 milhões** no alerta (D16-D60) com 58% de perda sem intervenção.
* **Solução Proposta:** Motor de parcelamento automático no app/WhatsApp antes do corte do cartão. Cura sobe para **72%**.
* **ROI da Ação:** **18,2x** sobre o custo de R$ 150k de tecnologia.

---

## 🔮 5. Próximos Passos (Fase 2 do Projeto)

- [ ] **Modelo Preditivo de Default (Machine Learning):** LightGBM/XGBoost para estimar P(Default) na esteira.
- [ ] **Explicabilidade com SHAP:** Transparência regulatória e geração de contrapropostas de limite.
- [ ] **Microserviço em FastAPI:** API RESTful de baixa latência conteinerizada em Docker.
- [ ] **Testes A/B de Políticas de Crédito:** Teste Champion/Challenger em amostras controladas de 5% da base.

---

## 🛠️ 6. Como Executar o Pipeline Localmente

```bash
# Clone do repositório completo
git clone https://github.com/wendellbarbosacosta-cmyk/portfolio-data-analytics-wendell-barbosa.git
cd portfolio-data-analytics-wendell-barbosa/01_nexusrisk_fintech_credit

# Criação e ativação do ambiente virtual
python -m venv .venv
source .venv/bin/activate  # No Windows: .venv\Scripts\activate

# Instalação das dependências
pip install -r requirements.txt

# Execução do pipeline
python pipeline_credit_risk.py
```

---

## 👤 Autor

**Wendell Barbosa Costa**  
*Especialista em Análise de Dados, Risco & Inteligência de Negócio*  
* GitHub: [@wendellbarbosacosta-cmyk](https://github.com/wendellbarbosacosta-cmyk)
