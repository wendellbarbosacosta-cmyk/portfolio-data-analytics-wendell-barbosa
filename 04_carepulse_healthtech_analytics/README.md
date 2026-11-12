# 🏥 CarePulse Analytics — Diagnóstico de Sinistralidade Operacional (MLR), Readmissão Hospitalar e Eficiência Assistencial

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![PEP 8 Compliant](https://img.shields.io/badge/Code%20Style-PEP%208-green.svg)](https://peps.python.org/pep-0008/)
[![Pandas](https://img.shields.io/badge/Data%20Analysis-Pandas-orange.svg)](https://pandas.pydata.org/)
[![Seaborn & Plotly](https://img.shields.io/badge/Visualization-Seaborn%20%7C%20Plotly-purple.svg)](https://plotly.com/)
[![ANS Compliance](https://img.shields.io/badge/Standard-ANS%20HealthTech-red.svg)](https://www.gov.br/ans/pt-br)
[![Status](https://img.shields.io/badge/Status-Executive%20Ready-success.svg)](#)

> **Projeto Executivo de Portfólio de Data Analytics** focado no setor de **Saúde Suplementar (HealthTech, Operadoras de Planos de Saúde e Gestão Hospitalar)**. O objetivo é conter a sinistralidade operacional, prever e combater readmissões precoces evitáveis em 30 dias com o algoritmo clínico **LACE Index** e auditar glosas médicas de prestadores com dados e evidências estatísticas.

---

## 📌 1. Contexto do Problema de Negócio

No setor de Saúde Suplementar brasileiro regido pela ANS, o **Índice de Sinistralidade (Medical Loss Ratio - MLR)** é a métrica mestra de solvência e saúde atuarial:
$$\text{Sinistralidade (MLR)} = \frac{\sum \text{Custos Assistenciais Hospitalares}}{\sum \text{Receitas de Contraprestações (Mensalidades)}} \times 100$$

A operadora de saúde em análise apresentava uma **sinistralidade global de 88,4%**, ultrapassando criticamente a margem de segurança recomendada (75% a 78%). Essa perda operacional de margem gerou consumo acelerado de reservas técnicas e risco de reajustes punitivos aos planos corporativos.

A hipótese inicial da diretoria era de que os custos vinham de pedidos excessivos de exames laboratoriais básicos. No entanto, a investigação de Data Analytics revelou duas causas raízes severas:
1. **O Ciclo da Readmissão Hospitalar Precoce em 30 Dias:** 18,2% dos pacientes submetidos a internações clínicas ou cirúrgicas de alta complexidade retornavam ao pronto-socorro em menos de um mês, duplicando os custos assistenciais com o mesmo evento.
2. **Gargalo de Diárias de UTI & Glosas de Faturamento:** Internações com mais de 3 dias de UTI representavam um estouro financeiro com OPME (Órteses, Próteses e Materiais Especiais) não auditados previamente, acumulando mais de R$ 900.000 em faturamentos retidos ou controversos.

---

## 🎯 2. KPIs Principais Analisados

| Indicador Atuarial / Clínico | Valor Observado | Benchmark de Mercado / ANS | Status de Risco |
| :--- | :---: | :---: | :---: |
| **Índice de Sinistralidade (MLR)** | **88,4%** | 75,0% a 78,0% | 🔴 Crítico (+10,4 p.p.) |
| **Taxa de Readmissão em 30 Dias** | **18,2%** | $\le 10,0\%$ | 🔴 Crítico (+8,2 p.p.) |
| **Tempo Médio de Permanência (LOS)** | **5,4 dias** | 3,8 a 4,2 dias | 🟡 Atenção |
| **Taxa de Ocupação de UTI** | **28,6%** dos dias | 18,0% a 22,0% | 🟡 Atenção |
| **Percentual de Alto Risco LACE** | **23,5%** da base | $\le 15,0\%$ | 🔴 Crítico |
| **Glosas Médicas Auditadas** | **R$ 942.380** | $< 5\%$ do faturamento | 🟡 Oportunidade de Recuperação |

---

## 🔍 3. Storytelling: Resposta às 3 Perguntas Críticas de Negócio

### ❓ Pergunta 1: Quais perfis e comorbidades concentram as readmissões hospitalares em 30 dias?
* **Causa Raiz Identificada:** A estratificação clínica demonstrou que pacientes classificados no quadrante de **Alto Risco (LACE Index $\ge 10$)** apresentam uma taxa de readmissão de **41,8%**, contra apenas **8,7%** no Baixo Risco (uma disparidade de **4,8x**). Pacientes idosos (>65 anos) com **2 ou mais comorbidades crônicas** (especialmente Insuficiência Cardíaca Congestiva e Diabetes descompensada) respondem por 64% de todos os retornos precoces.
* **Decisão de Negócio:** Criação da célula multidisciplinar de **Navegação Pós-Alta (Transição Segura de Cuidados)**: telemonitoramento clínico obrigatório em D+2 e D+10 após a saída hospitalar, reconciliação medicamentosa e conexão com o médico de família.
* **Impacto:** Redução projetada de **45% nas readmissões evitáveis** do grupo de risco.

### ❓ Pergunta 2: Onde estão os custos catastróficos e quais prestadores concentram as distorções?
* **Causa Raiz Identificada:** Internações por **Cirurgias de Emergência** e **Cardiológicas** absorvem mais de **54% de todo o desembolso assistencial**, impulsionadas por estadias em UTI prolongadas (>4 diárias) e custos de materiais especiais (OPME) com preços díspares entre hospitais credenciados. Foram identificados dois hospitais com índice de glosas superior a 14%, indicando falhas graves de autorização prévia e duplicidade de cobranças.
* **Decisão de Negócio:** Implantação de **Auditoria Concorrente Beira-Leito** em tempo real e renegociação de tabelas de pacotes cirúrgicos (*bundled payments*) para os procedimentos de maior variabilidade.
* **Impacto:** Mitigação de **R$ 282.700 em cobranças indevidas** e redução do tempo ocioso em UTI.

### ❓ Pergunta 3: Qual o Retorno sobre o Investimento (ROI) de estruturar a Gestão de Saúde Populacional?
* **Custo do Programa:** Contratação de 2 enfermeiros navegadores, 1 médico de família auditor e licença de telemonitoramento: **R$ 180.000/ano**.
* **Economia Gerada:**
  * Economia em internações evitadas: **R$ 1.285.000/ano**.
  * Economia em auditoria concorrente e glosas recuperadas: **R$ 282.000/ano**.
  * **Benefício Total:** **R$ 1.567.000/ano**.
* **Retorno Financeiro:** **ROI de 8,7x** no primeiro ano e redução do MLR da carteira de **88,4% para 76,2%**, recolocando a operadora na zona de sustentabilidade da ANS.

---

## 📊 4. Principais Insights Visuais

1. **Gráfico de Barras com LACE Index x Faixa Etária:** Salto exponencial na probabilidade de readmissão conforme o score LACE ultrapassa 9 pontos.
2. **Boxplot de Dispersão de Custos por Linha Assistencial:** Evidencia a assimetria e cauda longa de custos em cirurgias de emergência e oncologia.
3. **Matriz Interativa de Prestadores via Plotly:** Scatter plot correlacionando volume de internações, custo médio e taxa de readmissão.

---

## 🚀 5. Próximos Passos (Fase 2 do Projeto)

1. **Modelo de Machine Learning Preditivo de Readmissão:** Treinar um classificador supervisionado (**XGBoost / LightGBM**) para calcular a probabilidade individual de readmissão no momento da admissão hospitalar.
2. **Processamento de Linguagem Natural (NLP) em Prontuários:** Análise de anotações médicas de evolução clínica para identificar fragilidade funcional.
3. **Integração HL7 / FHIR com Hospitais Credenciados:** Conexão direta via API para obter alertas de admissão e alta em tempo real (*ADTs*).
