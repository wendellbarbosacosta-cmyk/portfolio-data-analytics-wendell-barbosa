# ⚡ PulseSaaS: Diagnóstico de Churn de MRR, Otimização de Net Revenue Retention (NRR) & Eficiência de CAC em Plataforma B2B

![Python](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python)
![Pandas](https://img.shields.io/badge/Pandas-2.1%2B-150458?logo=pandas)
![Seaborn](https://img.shields.io/badge/Seaborn-0.13%2B-4c72b0)
![Plotly](https://img.shields.io/badge/Plotly-5.18%2B-3f4f75?logo=plotly)
![PEP 8](https://img.shields.io/badge/Code%20Style-PEP%208-green)
![SaaS Metrics](https://img.shields.io/badge/Domain-SaaS%20%26%20Subscription%20Economy-purple)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

> **Projeto de Portfólio de Data Analytics & Inteligência de Negócio**  
> **Segmento:** SaaS B2B, Computação em Nuvem e Economia da Assinatura (*Recurring Revenue*)  
> **Autor:** Wendell Barbosa Costa  
> **Foco Executivo:** Recuperação de Net Revenue Retention (NRR), reversão do *Onboarding Cliff*, modelagem preditiva de Health Score e expansão de Customer Lifetime Value (LTV).

---

## 📌 1. Contexto do Problema & Desafio de Negócio

Uma empresa scale-up brasileira de software B2B (*Software-as-a-Service* de produtividade e gestão corporativa) acelerou expressivamente suas vendas no último exercício fiscal, ultrapassando a marca de **500 clientes ativos** e **R$ 540.000 de MRR** (faturamento anualizado de **R$ 6,48M de ARR**).

Contudo, a pressão por crescimento rápido gerou distorções severas na retenção:
* O indicador fundamental de saúde em SaaS, o **Net Revenue Retention (NRR)**, desabou de **115% para 91,4%** (o benchmark de scale-ups de excelência do Vale do Silício e B3 é $ge 110%$). Valores abaixo de 100% significam que a empresa está encolhendo organicamente, mesmo adquirindo novos clientes.
* O **Gross Churn de MRR atingiu R$ 68.500/mês (12,7% do MRR total)**, concentrado no segmento Starter/PME nos primeiros 90 dias após a assinatura (*Onboarding Cliff*).
* O **CAC Payback dilatou de 8 para 18,5 meses**, forçando a queima de caixa e gerando tensão junto ao Conselho de Administração (*Board of Directors*).

O Comitê Executivo (CEO, CRO e Head de Customer Success) contratou esta consultoria analítica para diagnosticar a causa raiz da evasão, estabelecer um modelo de **Health Score antecipatório** e desenhar um plano de intervenção quantitativo com ROI mensurável.

---

## 🎯 2. Regras de Negócio e Arcabouço Metodológico de SaaS

| Métrica / Conceito | Fórmula & Definição Operacional | Benchmark Saudável | Status Atual |
| :--- | :--- | :--- | :--- |
| **Net Revenue Retention (NRR)** | $rac{	ext{MRR Inicial} + 	ext{Expansão} - 	ext{Contração} - 	ext{Churn}}{	ext{MRR Inicial}} 	imes 100$ | $ge 110,0%$ | **91,4%** (Crítico ⚠️) |
| **Gross Revenue Churn Rate** | $rac{	ext{MRR Cancelado}}{	ext{MRR Inicial}} 	imes 100$ | $le 1,0%$ a.m. | **12,7%** a.m. (Crítico ⚠️) |
| **Quick Ratio de SaaS** | $rac{	ext{Novo MRR} + 	ext{Expansion MRR}}{	ext{Churn MRR} + 	ext{Contraction MRR}}$ | $ge 4,0x$ | **1,62x** (Insuficiente) |
| **LTV / CAC Ratio** | $rac{	ext{LTV}}{	ext{CAC}}$ onde $	ext{LTV} = rac{	ext{ARPU} 	imes 	ext{Margem Bruta}}{	ext{Churn Rate}}$ | $ge 3,0x$ | **1,85x** (Comprimido) |
| **Tempo de Payback do CAC** | $rac{	ext{CAC}}{	ext{ARPU} 	imes 	ext{Margem Bruta (82%)}}$ | $le 12$ meses | **18,5 meses** |

### Algoritmo de Health Score do Cliente (0 a 100 pts)
O Health Score avalia 4 pilares comportamentais com cálculo dinâmico:
1. **Frequência de Login Semanal (35%):** Normalizado de 0 a 7 dias úteis.
2. **Adoção de Features Core (35%):** % de módulos estratégicos habilitados no workspace.
3. **Ocupação de Assentos Licenciados (15%):** $rac{	ext{Assentos Ativos}}{	ext{Assentos Contratados}} 	imes 100$.
4. **Severidade de Chamados de Suporte (15%):** Penalidade progressiva de 12 pts por chamado crítico não resolvido.
* **Classificação:**
  * 🟢 **Verde (Saudável):** Score $ge 70$ (risco de churn $< 5%$)
  * 🟡 **Amarelo (Atenção):** Score $50 - 69$ (risco de churn $15% - 30%$)
  * 🔴 **Vermelho (Crítico):** Score $< 50$ (risco de churn $> 65%$)

---

## 💡 3. Storytelling: Resposta às 3 Perguntas Críticas de Negócio

### 🔍 Pergunta 1: Qual plano e faixa de maturidade concentra mais de 65% das perdas de MRR?
* **Evidência dos Dados:**
  * O plano **Starter (PME)** no estágio de **Onboarding (0 a 3 meses)** concentra **68,2% dos cancelamentos de contas (Logo Churn)** e responde por **R$ 38.400 em MRR perdido por mês**.
  * Em contrapartida, contas **Enterprise** sustentam NRR de **128,4%**, com churn quase nulo (0,8% a.a.) e alta expansão de licenças adicionais.
* **Causa Raiz:** O atrito no processo de migração de planilhas e a ausência de treinamento síncrono nos primeiros 15 dias levam a equipe do cliente a abandonar o software antes de perceber valor (*Time-to-Value dilatado*).
* **Decisão Executiva:** Instituição do programa obrigatório de *Onboarding White-Glove* para planos Starter com valor acima de R$ 600/mês e automação de tour guiado no primeiro acesso.

---

### 🔍 Pergunta 2: Como o desuso de assentos e o Health Score antecipam o cancelamento com 60 dias de antecedência?
* **Evidência dos Dados:**
  * Clientes na faixa **Vermelho (Health Score < 50)** têm uma taxa de churn efetiva de **73,8%**, enquanto contas no **Verde** cancelam apenas **2,1%**.
  * **84% dos cancelados** apresentavam uma taxa de ocupação de assentos **inferior a 40%** já na terceira semana pós-contratação (clientes pagavam por 10 assentos, mas apenas 2 ou 3 colaboradores logavam).
* **Decisão Executiva:** Configuração de gatilho de alerta automatizado no CRM de Customer Success para disparar intervenção humana quando a taxa de assentos ativos cair abaixo de 50% por 14 dias consecutivos.

---

### 🔍 Pergunta 3: Qual o impacto financeiro (ROI) de implantar um playbook de Customer Success proativo para recuperar o NRR para 112%?
* **Modelagem de Cenários:**
  * A redução de 55% no churn do onboarding preserva **R$ 37.675 em MRR mensal**.
  * A identificação precoce de clientes no quadrante Amarelo/Verde permite campanhas de upsell de assentos, gerando **R$ 16.325 em expansão mensal adicional**.
  * **Impacto Anualizado:** **R$ 648.000 em ARR líquido adicional preservado/gerado**.
  * **Custo da Intervenção:** R$ 65.000 (contratação de 1 analista pleno de CS + licença de software de Customer Success).
  * **Retorno sobre o Investimento:** **ROI de 10,8x no primeiro ano**, elevando o NRR consolidado de **91,4% para 112,8%**.

---

## 🔮 5. Próximos Passos (Fase 2 do Projeto)

Para evoluir este projeto em um ciclo avançado de engenharia e data science corporativo:
* [ ] **Machine Learning de Previsão de Churn (Survival Analysis):** Treinar modelo LightGBM e Curvas de Kaplan-Meier para estimar o risco pontual de churn em D-30 e D-60.
* [ ] **Explicabilidade com SHAP Values:** Fornecer ao time de Customer Success o exato motivo pelo qual o score de uma conta caiu (ex: "queda de 40% no envio de relatórios").
* [ ] **Microserviço em FastAPI:** Desenvolver API RESTful que recalcula o Health Score a cada evento de telemetria de produto (*product analytics*).
* [ ] **Integração com Slack e HubSpot via Webhooks:** Envio automático de cards de risco para o canal de CS quando um cliente Enterprise cair para score < 60.
