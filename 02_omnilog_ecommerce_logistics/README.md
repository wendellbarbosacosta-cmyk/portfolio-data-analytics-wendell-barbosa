# 🚚 OmniLog: Otimização de SLA de Entregas, Custos de Frete & Mitigação de Churn Logístico no E-Commerce

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Pandas](https://img.shields.io/badge/Pandas-2.1+-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org)
[![Seaborn](https://img.shields.io/badge/Seaborn-0.13+-4C72B0?style=for-the-badge)](https://seaborn.pydata.org)
[![Plotly](https://img.shields.io/badge/Plotly-5.18+-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com)
[![PEP 8](https://img.shields.io/badge/Code%20Style-PEP%208-blueviolet?style=for-the-badge)](https://pep8.org)
[![Logistics SLA](https://img.shields.io/badge/Operations-OTIF%20Optimization-008080?style=for-the-badge)](https://github.com)

> **Projeto de Inteligência de Negócio e Analytics para Varejo Omnichannel, Supply Chain e E-Commerce.**  
> Foco executivo na auditoria de cumprimento de prazo de entrega (**OTIF / On-Time In-Full**), vazamento de margem por **frete subsidiado** e estancamento de **churn de clientes induzido por atraso logístico**.

---

## 📌 1. Contexto do Problema & Desafio de Negócio

Um e-commerce brasileiro de médio/grande porte (faturando R$ 65M anuais) registrou um salto expressivo no volume de vendas durante o último ano. Contudo, a expansão acelerada pressionou a malha de distribuição logística terceirizada (3PL), gerando um gargalo operacional severo:

* A taxa de cumprimento de prazos de entrega (**OTIF**) despencou de **94,5% para 83,8%**, especialmente em rotas interestaduais para as regiões **Norte e Nordeste**.
* O custo com **fretes subsidiados pela loja** (frete grátis descalibrado e gaps contratuais com transportadoras) atingiu **R$ 840 mil no semestre**, comprimindo a margem de contribuição operacional.
* **O Efeito Oculto no LTV:** O SAC registrou um aumento de +180% em tickets de reclamação sobre atraso ("Onde está meu pedido?"), e a taxa de recompra em 60 dias de clientes que sofreram atraso despencou de **44% para apenas 16%**.
* A diretoria de Operações e Growth demandou uma análise diagnóstica para responder a **três dilemas estratégicos**:
  1. *Qual transportadora e rota interestadual concentra as falhas crônicas de SLA e as indenizações mais pesadas?*
  2. *Qual o impacto financeiro real do atraso logístico na destruição de Lifetime Value (LTV) e churn de recompra?*
  3. *Qual política de roteamento inteligente (Smart Carrier Allocation) e teto de subsídio no checkout devolve o OTIF para 96% com retorno financeiro positivo (ROI)?*

---

## 🎯 2. Regras de Negócio e Arcabouço Operacional

1. **Régua de Classificação de SLA de Entrega:**
   * `No Prazo (SLA OK)`: Lead time real <= prazo prometido no checkout (meta OTIF).
   * `Atraso Leve (1-2 dias)`: Atraso operacional de transbordo; cupom compensatório de 30% do frete.
   * `Atraso Crítico (3-5 dias)`: Ruptura contratual; estorno integral do frete cobrado.
   * `Falha Grave (>5 dias)`: Indenização de frete + 15% de voucher de recompra para retenção de churn.
   * `Extraviado / Avaria`: Reembolso total do pedido e acionamento de seguro de carga.

2. **Cálculo do Subsídio de Frete da Loja:**
   Subsídio (R$) = max(0, Custo Real Faturado - Frete Cobrado do Consumidor)
   * Teto máximo prudencial: R$ 15,00 por pacote.

3. **Métrica OTIF (On-Time In-Full):**
   OTIF (%) = (Pedidos Entregues Pontualmente e sem Avaria / Total de Pedidos Despachados) * 100
   * Meta contratual estabelecida em SLA: >= 95,0%.

---

## 📊 3. KPIs Principais Analisados

| Métrica / KPI | Situação Atual | Benchmark Operacional | Diagnóstico Executivo |
| :--- | :---: | :---: | :--- |
| **Taxa OTIF (Entrega no Prazo)** | **83,8%** | >= 95,0% | -11,2 p.p. abaixo da meta contratual de SLA |
| **Taxa de Quebra de SLA (Atraso)** | **16,2%** | <= 5,0% | 1 a cada 6 clientes recebe o pacote com atraso |
| **Subsídio Total de Frete** | **R$ 842.150** | <= R$ 450.000 | Vazamento de margem no checkout por tabelas desatualizadas |
| **Indenizações e Vouchers** | **R$ 138.400** | <= R$ 25.000 | Sobrecarga de estornos operacionais do SAC |
| **Recompra em 60d (Sem Atraso)** | **44,2%** | >= 40,0% | Benchmark saudável quando a experiência logística é positiva |
| **Recompra em 60d (Com Atraso)** | **16,1%** | >= 35,0% | Queda de 28,1 p.p. na retenção de clientes por atrito de entrega |
| **Perda Anual Estimada de LTV** | **R$ 1.280.000** | — | Destruição silenciosa de margem de recompra |

---

## 💡 4. Storytelling Executivo: Respostas às 3 Perguntas Críticas

### 🔍 Pergunta 1: Qual transportadora e rota interestadual concentra as falhas crônicas de SLA e indenizações?
* **Constatação dos Dados:** A transportadora **Jadlog Standard na rota Nordeste** registrou índice de atraso de **38,4%** (OTIF de 61,6%), com lead time médio de 11,8 dias contra um prazo prometido de 7,0 dias, gerando **46% de todas as indenizações e estornos de frete**.
* **Ação Executiva Recomendada:** Desativação imediata da Jadlog nas rotas Nordeste e transferência para malha expressa dedicada (Loggi Express / Correios Sedex). **Impacto: Eliminação de R$ 90 mil/ano em indenizações.**

### 🔍 Pergunta 2: Qual o impacto real do atraso na entrega na destruição do LTV e churn de clientes?
* **Constatação dos Dados:** Enquanto **44,2%** dos clientes com entrega pontual recompram na loja em até 60 dias, apenas **16,1%** dos clientes que sofreram atraso voltaram a comprar (**perda de -28,1 pontos percentuais em retenção**).
* **Impacto Financeiro:** O atraso gerou a perda de **215 clientes fiéis por mês**, resultando em uma perda anualizada de **R$ 1,28 milhão em faturamento de recompra**.

### 🔍 Pergunta 3: Qual o ROI de implementar Smart Carrier Allocation e teto de subsídio?
* **Solução Proposta:** Smart Carrier Routing por CEP, teto de subsídio de frete de R$ 15 no checkout e comunicação proativa D+1 via WhatsApp.
* **Resultado Simulado:** Economia de R$ 320k em subsídios + R$ 90k em indenizações + R$ 768k em LTV recuperado. Custo de implementação: R$ 85k. **ROI da Ação: 13,8x no 1º Ano.**

---

## 🔮 5. Próximos Passos (Fase 2 do Projeto)

- [ ] **Modelo Preditivo de Risco de Atraso (Machine Learning):** LightGBM treinado com clima, tráfego e sazonalidade para alertar risco no despacho.
- [ ] **API de Roteamento Dinâmico em FastAPI:** Microserviço em nuvem calculando a melhor transportadora para o checkout em <80ms.
- [ ] **Módulo de Rastreamento Proativo via WhatsApp:** Integração com WhatsApp Business API enviando status em tempo real com mapa.
- [ ] **Auditoria Automatizada de Faturas Logísticas:** Conciliação algorítmica entre CTE e faturas cobradas pelas transportadoras.

---

## 🛠️ 6. Como Executar o Pipeline Localmente

```bash
git clone https://github.com/seu-usuario/omnilog-ecommerce-analytics.git
cd omnilog-ecommerce-analytics
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python pipeline_ecommerce_logistics.py
```

---

## 👤 Autor

**Wendell Barbosa Costa**  
*Especialista em Análise de Dados, Risco & Inteligência de Negócio*  
* [LinkedIn](https://linkedin.com) • [GitHub](https://github.com) • [Email](mailto:wendellbarbosacosta@gmail.com)
