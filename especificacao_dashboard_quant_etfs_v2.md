# Especificação Técnica de Dashboard Quantitativo para Alocação em ETFs
## Alinhado às Regras Oficiais do 11º Desafio JGP (2026)

**Período da Competição:** 28/08/2026 a 18/12/2026 (16 semanas / ~80 pregões úteis)  
**Taxa Livre de Risco (Risk-Free / Hurdle Rate):** 5.0% ao ano (Fed Funds - remuneração do caixa)  
**Restrição de Capital:** Não alavancado ($\sum |w_i| \le 100\%$)  
**Custo de Posição Vendida (Short):** 0.4% ao mês ($1/20$ ao dia sobre o financeiro short)  
**Universo Elegível (18 ETFs):**
- **Benchmark / Core:** `SPY` (S&P 500)
- **Setoriais EUA (10):** `XLB` (Materiais), `XLE` (Energia), `XLF` (Financeiro), `XLI` (Industrial), `XLK` (Tecnologia), `XLP` (Consumo Não-Cíclico), `XLU` (Utilities), `XLV` (Saúde), `XLY` (Consumo Cíclico), `XTN` (Transportes)
- **Internacionais (4):** `EWJ` (Japão), `EWG` (Alemanha), `EEM` (Emergentes Amplo), `EWZ` (Brasil)
- **Macro / Safe-Havens / Renda Fixa / Câmbio (3):** `TLT` (Treasuries 20+ anos), `GLD` (Ouro), `FXE` (Euro/USD)
- **Universo de Ações Subjacentes (Deep-Dive Brasil - Eleições):** Top 10 holdings do `EWZ` (`VALE3`, `PETR4`, `ITUB4`, `BBDC4`, `BBAS3`, `B3SA3`, `WEGE3`, `ABEV3`, `RENT3`, `PRIO3` / `ELET3`).

---

## 1. Módulo 1: Performance vs. Hurdle Rate (5% a.a. Caixa) & Sazonalidade Q4

### 1.1 Objetivo
Identificar ativos com alfa real sobre o custo de oportunidade do caixa (que rende 5.0% a.a. automaticamente em Fed Funds segundo a regra da JGP) e mapear a distribuição estatística de retornos dos últimos 4 anos no mesmo período tático de 16 semanas (28 de agosto a 18 de dezembro).

### 1.2 Métricas e Fórmulas
- **Retorno Acumulado Tático:**
  $$R_{cum, t} = \prod_{k=1}^t (1 + r_k) - 1$$
- **Hurdle Rate do Caixa JGP (Pro Rata 16 Semanas / 80 dias úteis):**
  $$R_{hurdle} = (1 + 0.05)^{rac{80}{252}} - 1 pprox +1.56\%$$
- **Retorno Líquido em Estratégias Short (quando aplicável):**
  $$r_{short, t} = -r_{t} - rac{0.004}{20}$$
- **Sazonalidade Histórica Q4 ($N-1, N-2, N-3, N-4$):**
  - Retorno médio e mediano verificado na mesma janela temporal.
  - **Win Rate Sazonal (%):** Proporção de anos em que o ETF superou o retorno do caixa (+1.56%).

### 1.3 Componentes Visuais
1. **Gráfico 1A - Curva de Retorno Acumulado Multi-Ativos:**
   - **Tipo:** Multi-line chart normalizado em base 100 ou percentual.
   - **Eixo X:** Tempo (Semana 1 a Semana 16 / 80 pregões).
   - **Eixo Y:** Retorno percentual acumulado ($R_{cum}$).
   - **Linha de Referência:** Linha tracejada horizontal em $+1.56\%$ (Rendimento do Caixa).
   - **Interatividade:** Toggle para isolar categorias (Setoriais, Mercados Globais, Macro/Hedge).
2. **Gráfico 1B - Painel de Sazonalidade Q4 (Últimos 4 Anos):**
   - **Tipo:** Bar Chart Agrupado + Boxplot de dispersão por ETF.
   - **Eixo X:** Lista dos 18 ETFs ordenados pelo retorno médio histórico do período.
   - **Eixo Y:** Retorno percentual verificado em cada ano.
   - **Badge de Informação:** Indicador de *Win Rate* (% de anos acima do hurdle rate).

---

## 2. Módulo 2: Matriz Interativa de Correlação & Heatmap Clustered

### 2.1 Objetivo
Mapear a estrutura de dependência estatística e risco de contágio entre os 18 ETFs, identificando instrumentos descorrelacionados para compor hedges e carteiras eficientes.

### 2.2 Métricas e Fórmulas
- **Retornos Logarítmicos Diários:**
  $$r_{i, t} = \ln\left(rac{P_{i, t}}{P_{i, t-1}}ight)$$
- **Matriz de Correlação de Pearson ($18 	imes 18$):**
  $$ho_{i,j} = rac{	ext{Cov}(r_i, r_j)}{\sigma_i \sigma_j}$$
- **Clusterização Hierárquica:** Algoritmo de enlace de Ward (*Ward's Linkage*) sobre a distância euclidiana $d_{i,j} = \sqrt{2(1 - ho_{i,j})}$.

### 2.3 Componentes Visuais
1. **Heatmap Matriz $18 	imes 18$:**
   - **Escala de Cores:** Bipolar divergente contínua (Azul $[-1.0]$ $ightarrow$ Neutro $[0.0]$ $ightarrow$ Vermelho $[+1.0]$).
   - **Labels Numéricos:** Valor exato de $ho$ em cada célula com 2 casas decimais.
   - **Filtro de Janela Temporal (Lookback):** Dropdown dinâmico com opções de 1 Mês (20d - padrão JGP), 3 Meses (60d), 6 Meses (120d) e 1 Ano (252d).
2. **Gráfico de Correlação Rolante (Rolling Correlation 20d & 60d):**
   - **Tipo:** Line chart de correlação móvel de qualquer ETF selecionado contra o `SPY` ou `TLT`.

---

## 3. Módulo 3: Decomposição dos Top 10 Holdings & Risco de Concentração

### 3.1 Objetivo
Diagnosticar o grau de concentração de cada ETF elegível, separando risco idiossincrático (poucas ações dominantes) de exposição beta setorial ampla.

### 3.2 Métricas e Fórmulas
- **Taxa de Concentração dos 10 Principais Ativos ($CR_{10}$):**
  $$CR_{10} = \sum_{i=1}^{10} w_i$$
- **Índice Herfindahl-Hirschman (HHI):**
  $$HHI = \sum_{i=1}^{N} (w_i 	imes 100)^2$$
  - *Faixas:* $HHI < 1000$ (Diversificado); $1000 \le HHI \le 1800$ (Moderado); $HHI > 1800$ (Altamente Concentrado).

### 3.3 Componentes Visuais
1. **Bar Chart Horizontal / Treemap Dinâmico por ETF Selecionado:**
   - **Barras:** 10 maiores componentes com ticker, nome da empresa e peso percentual ($w_i$).
   - **Barra de Fechamento:** "Demais Ativos da Carteira" representando $100\% - CR_{10}$.
2. **Cards de Diagnóstico de Risco:**
   - Score $CR_{10}$, Score HHI e alerta visual de sensibilidade a balanços corporativos individuais.
3. **Gráfico Comparativo de Concentração ($CR_{10}$ Ranking):**
   - Gráfico de colunas comparando a concentração dos 18 ETFs lado a lado.

---

## 4. Módulo 4: Análise Técnica Individual, Regime e Volatilidade (20d Padrão JGP)

### 4.1 Objetivo
Fornecer painel individual para calibração de pontos de entrada/saída tática, monitoramento da volatilidade móvel oficial de 20 dias (critério avaliado pela banca JGP) e detecção de exaustão de tendência.

### 4.2 Métricas e Fórmulas
- **Volatilidade Realizada Anualizada (Janela Móvel Oficial de 20 dias da JGP):**
  $$\sigma_{ann, 20d} = \sqrt{252} 	imes \sqrt{rac{1}{19} \sum_{t=1}^{20} (r_t - ar{r})^2}$$
- **Médias Móveis Simples:** $	ext{SMA}_{50}(P)$ e $	ext{SMA}_{200}(P)$.
- **Bandas de Bollinger ($20, 2\sigma$):**
  $$	ext{Superior/Inferior} = 	ext{SMA}_{20}(P) \pm 2 	imes \sigma_{20}(P)$$
- **Z-Score de Distância da Média (Mean-Reversion Score):**
  $$Z_t = rac{P_t - 	ext{SMA}_{200}(P)}{\sigma_{200}(P)}$$

### 4.3 Componentes Visuais
1. **Painel 1 (Preço & Tendência):**
   - Gráfico de Candlestick / Linha diária.
   - Sobreposições: $	ext{SMA}_{50}$, $	ext{SMA}_{200}$ e Bandas de Bollinger ($20, 2\sigma$).
2. **Painel 2 (Regime de Volatilidade 20d vs 60d):**
   - Curva de Volatilidade Realizada de 20 dias (laranja, métrica da banca JGP) vs 60 dias (cinza, tendência de volatilidade).
3. **Painel 3 (Oscilador Z-Score):**
   - Indicador de desvio padrão em relação à média com bandas de Sobrecompra ($Z > +2.0\sigma$) e Sobrevenda ($Z < -2.0\sigma$).

---

## 5. Módulo 5: Rotação Setorial, Força Relativa, Drawdown & Fronteira de Eficiência

### 5.1 Objetivo
Mapear a liderança de momentum setorial relativo ao S&P 500 (`SPY`), quantificar o Worst Drawdown e posicionar os ativos na **Fronteira de Eficiência** (critério explícito do Desafio JGP).

### 5.2 Métricas e Fórmulas
- **Força Relativa (Relative Strength Ratio):**
  $$RS_t = rac{P_{ETF, t}}{P_{SPY, t}}$$
- **Worst Drawdown Histórico / Período:**
  $$DD_t = rac{P_t - \max_{0 \le s \le t}(P_s)}{\max_{0 \le s \le t}(P_s)}, \quad 	ext{Worst DD} = \min_{t}(DD_t)$$
- **Índice de Sharpe Oficial da JGP:**
  $$	ext{Sharpe} = rac{R_{	ext{acumulado}} - R_{f}}{	ext{Volatilidade Média (20d)}}, \quad R_f = 5.0\% 	ext{ a.a.}$$
- **Otimização Média-Variância (Markowitz):**
  $$\min \mathbf{w}^T \mathbf{\Sigma} \mathbf{w} \quad 	ext{sujeito a} \quad \mathbf{w}^T \mathbf{\mu} = \mu_p, \quad \sum |w_i| \le 1.0$$

### 5.3 Componentes Visuais
1. **Gráfico 5A - Ratio de Força Relativa com Médias (vs. SPY):**
   - Curva $P_{ETF}/P_{SPY}$ com $	ext{SMA}_{50}$ e $	ext{SMA}_{200}$ calculadas sobre a razão.
2. **Gráfico 5B - Quadrantes RRG (Relative Rotation Graph):**
   - Gráfico de dispersão 2D com 4 quadrantes (*Leading, Weakening, Lagging, Improving*).
3. **Gráfico 5C - Painel de Drawdown (Underwater Chart):**
   - Área sombreada em vermelho ilustrando a magnitude e tempo de recuperação dos drawdowns.
4. **Gráfico 5D - Fronteira de Eficiência & Dispersão Risco x Retorno:**
   - **Eixo X:** Volatilidade Realizada (20d anualizada).
   - **Eixo Y:** Retorno Esperado / Retorno Histórico.
   - **Curva:** Fronteira Eficiente gerada pelos 18 ETFs sob a restrição de não-alavancagem ($\sum |w_i| \le 1.0$).
   - **Pontos:** Localização individual de cada ETF e da carteira teórica proposta.

---

## 6. Módulo 6: Ciclos Eleitorais no Brasil (2010, 2014, 2018, 2022) - Reação dos Top Holdings do EWZ

### 6.1 Objetivo
Avaliar quantitativamente o comportamento das **principais ações subjacentes do ETF Brasil (`EWZ`)** e seus agrupamentos setoriais durante o período eleitoral presidencial de **setembro a dezembro (16 semanas)**.

### 6.2 Grupos de Ações Subjacentes do EWZ Analisadas
- **Estatais (Risco Político / Governança):** `PETR4` (Petrobras), `BBAS3` (Banco do Brasil), `ELET3` (Eletrobras - ciclo pré-privatização).
- **Setor Financeiro Privado (Resiliência Institucional):** `ITUB4` (Itaú Unibanco), `BBDC4` (Bradesco), `B3SA3` (B3).
- **Commodities Globais / Exportadoras (Hedge Cambial):** `VALE3` (Vale), `PRIO3` (PetroRio), `SUZB3` (Suzano).
- **Consumo Doméstico / Indústria:** `WEGE3` (WEG), `ABEV3` (Ambev), `RENT3` (Localiza).

### 6.3 Métricas e Fórmulas
- **Decomposição Temporal do Q4 Eleitoral:**
  - **Fase 1 (Pré-1º Turno):** 1º de Setembro até a véspera da votação de Outubro.
  - **Fase 2 (Entre-Turnos):** 1º Turno até o 2º Turno (fase de maior reprecificação e volatilidade).
  - **Fase 3 (Pós-Eleição / Transição):** Fim de Outubro até 31 de Dezembro.
- **Spread de Risco Político (Estatais vs. Privadas):**
  $$\Delta_{pol, t} = rac{R_{	ext{PETR4}, t} + R_{	ext{BBAS3}, t}}{2} - rac{R_{	ext{ITUB4}, t} + R_{	ext{BBDC4}, t}}{2}$$
- **Compressão de Volatilidade Pós-Eleitoral (20d):**
  $$\Delta\sigma_{eleitoral} = \sigma_{20d}(	ext{Pós-2º Turno}) - \sigma_{20d}(	ext{Pré-1º Turno})$$

### 6.4 Componentes Visuais
1. **Gráfico 6A - Matriz de Retorno dos Top Holdings em Anos Eleitorais (Set-Dez):**
   - **Tipo:** Heatmap / Tabela comparativa de retorno por ativo individual em 2010, 2014, 2018, 2022.
   - **Ativos no Eixo Y:** VALE3, PETR4, ITUB4, BBDC4, BBAS3, B3SA3, WEGE3, ABEV3, RENT3.
   - **Colunas:** Retorno Q4 2010, Q4 2014, Q4 2018, Q4 2022, Retorno Médio Eleitoral, Volatilidade 20d Média.
2. **Gráfico 6B - Curva de Performance Acumulada Média por Cesta (Base 100):**
   - Comparação diária acumulada ao longo das 16 semanas para as 4 cestas (Estatais, Privadas, Exportadoras e EWZ consolidado) com linhas verticais demarcando 1º e 2º turnos.
3. **Gráfico 6C - Volatilidade Realizada de 20 Dias (Pré vs. Pós-Eleição):**
   - Bar chart comparando o choque e a subsequente compressão da volatilidade de 20 dias após a definição do pleito para cada ação.

---

## 7. Tabela Resumo de Parâmetros de Implementação

| Parâmetro | Valor de Calibração Regulamentar | Justificativa no Desafio JGP |
| :--- | :--- | :--- |
| **Janela Tática da Competição** | 16 Semanas (28/08/2026 a 18/12/2026 / ~80 dias úteis) | Duração exata estipulada pelo regulamento |
| **Hurdle Rate / Risk-Free** | 5.0% a.a. (Fed Funds / $+1.56\%$ no período de 16 semanas) | Taxa automática de rendimento do caixa não alocado |
| **Volatilidade Padrão** | Janela móvel de **20 dias de negociação** | Métrica oficial exigida no cálculo de performance e Sharpe pela JGP |
| **Restrição de Alavancagem** | Exposição Bruta Máxima $\sum \|w_i\| \le 1.0$ | Proibição expressa de alavancagem no regulamento |
| **Custo de Posições Short** | $0.4\%$ ao mês ($1/20$ ao dia sobre o financeiro vendido) | Custo regulamentar debitado pela JGP em posições vendidas |
| **Tratamento de Preços** | Preços de fechamento ajustados (*Total Return*) | Incorpora dividendos e proventos dos ETFs |
| **Anos Eleitorais BR** | 2010, 2014, 2018, 2022 (Setembro a Dezembro) | Ciclos presidenciais com histórico completo dos top holdings |
