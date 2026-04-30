# PocketRE — Progress Log

Diário de progresso e milestones do TCC. Append-only: cada nova iteração entra
ao final, e o **estado atual** no topo é atualizado.

> Companheiro do `@ai/MEMORY.md`. MEMORY descreve **o que o projeto é** (escopo,
> decisões, convenções). Este arquivo descreve **o que aconteceu, em que ordem,
> com que resultado, e por quê** — material direto para o capítulo de
> Resultados/Discussão da TCC.

---

## Estado atual (snapshot)

**Última atualização:** 2026-04-29

### Métodos avaliados

| Método | Modelo | Status |
|---|---|---|
| NLI (entailment) | `roberta-large-mnli` | Avaliado em 3 variantes — saturado, F1 ≈ 0 |
| Zero-shot classification | `facebook/bart-large-mnli` | Avaliado em 3 variantes + threshold tuning — único caminho com sinal |
| Local LLM (instrucional) | — | Não iniciado / próximo grande passo |

### Macro F1 por experimento (consolidado)

| # | Experimento | NLI macro F1 | Zero-shot macro F1 |
|---|---|---|---|
| 1 | Baseline labels (threshold 0.5 fixo) | **0.074** | **0.286** |
| 2 | Improved labels (threshold 0.5 fixo) | **0.000** | **0.322** |
| 3 | Improved labels + threshold tuning per-defeito | n/a | **0.4405** |
| 4 | Improved_v2 labels + threshold por defeito (0.75/0.30/0.70) | **0.000** | **0.190** |

### F1 por defeito — melhor configuração até agora

| Defeito | Melhor F1 | Configuração | Comentário |
|---|---|---|---|
| `optional` | **0.75** | zero-shot improved + tuning, t=0.6 | Pistas lexicais explícitas (may, could, might) — método funciona |
| `ambiguous` | **0.571** | zero-shot improved + tuning, t=0.3 | Recall alto (0.92), mas precision baixa (0.41) — muitos FP |
| `non_measurable` | **0.000** | em todas as configurações | Score bruto colapsado, não cruza nenhum threshold realista |

---

## Timeline (milestones)

### M0 — Setup do projeto

- Definição da pesquisa em torno de **DSR**: construir artefato local + avaliar.
- Escopo travado em **3 defeitos** (`ambiguous`, `non_measurable`, `optional`)
  e métodos zero-shot (sem treino do zero), tudo local.
- Stack: Python 3.10, `transformers`, `torch`. Sem GPU obrigatória.

Documentos: `@ai/MEMORY.md`, `README.md`.

### M1 — Dataset manual (30 amostras)

- Construído manualmente em `data/dataset.json`.
- Composição (de propósito enviesada para cobrir todos os defeitos):
  - 12 com `ambiguous + non_measurable`
  - 8 com `optional`
  - 1 com `ambiguous` apenas
  - 9 sem defeito (well-written)
- Decisão consciente: dataset pequeno, é prova de conceito.

> ⚠️ Esse desenho do dataset gerou um problema sério detectado depois — ver
> seção **Diagnóstico**.

### M2 — Iteração 1: Baseline NLI + Zero-shot

Hipóteses curtas e genéricas (`scripts/lib/labels.py` → `BASELINE`):

- ambiguous → "This requirement contains vague or unclear terms..."
- non_measurable → "This requirement cannot be objectively measured or tested."
- optional → "This requirement includes optional or non-mandatory behavior."

Resultados:

- **NLI baseline** — macro F1 = **0.074**
  - Tudo NEUTRAL exceto 1 acerto sortudo em `optional`.
- **Zero-shot baseline** (threshold 0.5) — macro F1 = **0.286**
  - `optional` recall = 1.0 mas precision = 0.33 (muitos FP).
  - `non_measurable` zero — scores brutos no chão (max 0.007).

Aprendizado: NLI puro com hipóteses genéricas não acende. Zero-shot tem sinal,
mas threshold único 0.5 é ruim.

### M3 — Iteração 2: Improved labels

Hipóteses mais específicas, listando palavras-gatilho concretas
(`labels.py` → `IMPROVED`):

- ambiguous → "...vague or subjective words such as clear, intuitive, fast,
  good, or efficient..."
- non_measurable → "...does not define measurable acceptance criteria such as
  time limits, quantities, percentages, thresholds..."
- optional → "...uses optional language such as may, might, could, optionally..."

Resultados:

- **NLI improved** — macro F1 = **0.000**. Piorou em relação ao baseline (perdeu
  o único acerto de `optional`).
- **Zero-shot improved** (threshold 0.5) — macro F1 = **0.322**.
  - `ambiguous` F1 0.36 → 0.44 (melhorou).
  - `optional` F1 0.50 → 0.52 (estável).
  - `non_measurable` continua 0.

Aprendizado: melhor verbalização ajuda zero-shot mas **não destrava** NLI nem
`non_measurable`.

### M4 — Iteração 3: Threshold tuning (BART improved)

Sweep de `t ∈ {0.3, 0.4, 0.5, 0.6, 0.7}` por defeito, mantendo as hipóteses
`IMPROVED`. Threshold ótimo escolhido por F1 individual:

| Defeito | t* | P | R | F1 |
|---|---|---|---|---|
| ambiguous | 0.3 | 0.41 | 0.92 | 0.571 |
| non_measurable | qualquer | 0 | 0 | 0.000 |
| optional | 0.6 | 0.75 | 0.75 | 0.750 |

**Macro F1 combinado = 0.4405** — melhor configuração obtida no projeto até hoje.

Aprendizado: thresholds específicos por defeito **resolvem o `optional`** e
melhoram `ambiguous` (às custas de precision). `non_measurable` continua sendo
um buraco — não é problema de threshold, é de score bruto.

### M5 — Refatoração de código (suporte a múltiplas variantes)

Antes desta iteração, cada experimento era um script copiado-e-colado com 100+
linhas. Refatoração para deixar a evolução experimental barata:

- Lib em `scripts/lib/` (`labels`, `io`, `inference`, `metrics`).
- Runners genéricos via CLI (`scripts/run_nli.py --labels <name>`, etc.).
- Cada variante de label vira um `LabelSet(defects, thresholds)` no
  `labels.py` — sem duplicar runner.
- Wrappers finos preservados em `baseline/`, `improved/`, `threshold_tuning/`
  para rastreabilidade da iteração.

Não alterou resultados; apenas reduziu fricção para as próximas iterações.

### M6 — Iteração 4: Improved_v2 labels + thresholds embutidos

Tentativa de afiar as hipóteses ainda mais (`labels.py` → `IMPROVED_V2`):

- ambiguous → "...is ambiguous because it can be interpreted in multiple ways,
  has unclear references, or does not clearly specify what the system must do."
- non_measurable → "...contains vague quality terms such as quickly, fast,
  good, large, easy, reliable, adequate, professional, efficient,
  user-friendly, or intuitive, **without objective measurable criteria**."
- optional → "...is optional only if it uses explicit optional terms such as
  may, might, could, optionally, if necessary, or if appropriate. **The word
  should alone is not enough.**"

Thresholds embutidos: `{ambiguous: 0.75, non_measurable: 0.30, optional: 0.70}`.

Resultados:

- **NLI v2** — macro F1 = **0.000** (terceira variante consecutiva sem reação).
- **Zero-shot v2** — macro F1 = **0.190** (regressão vs improved).
  - `ambiguous`: F1 = 0 — verbalização mais abstrata derrubou os scores
    (média 0.62 → 0.50) **e** o threshold subiu (0.5 → 0.75). Penalidade dupla.
  - `non_measurable`: F1 = 0 — score máximo de todos os 30 itens é 0.337;
    todos os positivos verdadeiros ficam abaixo de 0.20. Hipótese em forma
    negada ("does not define...", "without objective...") parece confundir o
    BART-MNLI.
  - `optional`: F1 = **0.571** (de 0.522). Pequeno ganho, dirigido pela
    cláusula "should alone is not enough".

Aprendizado: confirmou-se que NLI saturou e que reformular hipótese
**sozinho** não é suficiente. Resultado científico válido, não fracasso.

---

## Diagnóstico (consolidado, 2026-04-29)

Síntese das análises feitas em sessões com Claude e GPT após a iteração v2.
Material direto para o capítulo de Discussão.

### 1. NLI puro (sem fine-tuning) não funciona neste problema

Três iterações consecutivas com `roberta-large-mnli`:

- baseline → macro F1 0.074
- improved → macro F1 0.000
- improved_v2 → macro F1 0.000

Em todas, o modelo prediz NEUTRAL para 28-30 dos 30 itens, com confiança média
≥ 0.94. Não é variância; o modelo simplesmente não está tratando a tarefa
como entailment.

Nuance importante para a TCC: o paper de referência usa NLI **fine-tunado**;
estamos usando NLI **zero-shot puro**. Conclusão honesta:

> "Zero-shot NLI with `roberta-large-mnli` failed to detect requirement
> defects across three label verbalization variants, suggesting that
> task-specific adaptation (fine-tuning) is required for this method to be
> viable."

Isso já é resultado de tese.

### 2. Zero-shot (BART) tem sinal, mas é desigual entre defeitos

Hierarquia clara de dificuldade:

| Defeito | Tipo de sinal | Dificuldade | Melhor F1 |
|---|---|---|---|
| `optional` | Lexical explícito (may, could, might) | Fácil | 0.75 |
| `ambiguous` | Interpretativo / palavras vagas | Média | 0.57 |
| `non_measurable` | Conceitual abstrato (ausência de métrica) | Alta | 0.00 |

Insight para a discussão da TCC:

> "Detecting **optional** requirements relies on explicit lexical cues, while
> detecting **ambiguity** and **non-measurability** requires deeper semantic
> understanding that zero-shot NLI models fail to capture without
> task-specific adaptation."

### 3. Verbalização sozinha não destrava

Comparando improved vs improved_v2 (zero-shot):

- `optional` melhorou +0.05 (clarificação "should alone is not enough" ajudou).
- `ambiguous` regrediu para 0 (verbalização mais abstrata + threshold 0.75 alto demais).
- `non_measurable` continuou 0 (hipótese negada não acende o BART).

Reformular o texto da hipótese tem efeito limitado — a barreira é o que o
modelo consegue extrair, não o que pedimos.

### 4. ⚠️ Problema do dataset: `ambiguous` ↔ `non_measurable` colapsados

Esse é o achado mais importante da iteração v2.

Composição do `data/dataset.json` (30 amostras):

| Combinação de rótulos | Quantidade |
|---|---|
| `ambiguous + non_measurable` | **12** |
| `optional` apenas | 8 |
| `ambiguous` apenas | 1 |
| `non_measurable` apenas | **0** |
| Sem defeito (clean) | 9 |

Conclusões:

- Os dois rótulos são **quase perfeitamente correlacionados** no dataset.
- Para qualquer modelo, isso vira "essas duas classes são a mesma coisa".
- A métrica fica enviesada: não dá para o modelo aprender a separá-las, e
  também não dá para nós avaliarmos justamente se ele as separa.

Esse é um achado científico forte: **o problema não é só o modelo, é o
desenho do dataset**.

### 5. Por que `non_measurable` é o caso mais difícil

Três hipóteses (não excludentes) para o colapso desse defeito:

1. **Verbalização negada**: hipóteses no formato "does not / without" são
   conhecidamente difíceis para modelos MNLI, treinados majoritariamente em
   pares afirmativos.
2. **Sobreposição semântica com `ambiguous`**: como o dataset não separa os
   dois, o modelo não tem incentivo a aprender a distinção.
3. **Conceito de ausência**: `non_measurable` é "falta de algo" (números,
   limites, percentuais). NLI/zero-shot extraem evidência **presente** no
   texto, não ausência.

---

## Próximos passos (em ordem de prioridade)

### Prioridade 1 — Encerrar a frente de NLI puro

- [ ] Documentar formalmente em `@ai/MEMORY.md` ("Important insight") que
      NLI zero-shot puro foi avaliado e descartado, com 3 variantes como
      evidência.
- [ ] Não rodar mais iterações de label verbalization no `roberta-large-mnli`.

### Prioridade 2 — Decidir o que fazer com o dataset

Duas alternativas, ambas defensáveis:

**Caminho A — Fundir `ambiguous + non_measurable` em `vague`** (mais simples):
- Vira esquema de 3 classes: `vague`, `optional`, `clean`.
- Resolve a colinearidade de uma só vez.
- Justificativa acadêmica: non-measurability **é** uma forma de vagueza
  quantitativa.
- Retrofit: re-rotular `data/dataset.json` e re-rodar todos os experimentos
  com `LABEL_SETS` adaptados.

**Caminho B — Manter separado, mas reparar o dataset** (mais trabalho, mais
acadêmico):
- Adicionar exemplos com `ambiguous` sem `non_measurable` (ex: "the report
  must be generated **in 5 minutes** but **look professional**" — tem métrica,
  tem palavra vaga).
- Adicionar exemplos com `non_measurable` sem `ambiguous` (ex: "the system
  shall be **easy to use**" — vago mas sem sobreposição forte? difícil
  separar de fato).
- Honestamente, separar de verdade é difícil porque os dois conceitos se
  encavalam.

> **Recomendação atual:** Caminho A. É mais limpo, é mais defensável e libera
> tempo para a Prioridade 3.

### Prioridade 3 — Adicionar um terceiro método

Aqui é onde o TCC ganha diferencial:

**Opção A — Rule-based / heurísticas léxicas** (mais simples):
- Regex de palavras-gatilho por defeito.
- Vira o "baseline simples" contra o qual modelos têm que ganhar.
- Útil para mostrar que NLI/zero-shot ganha (ou não ganha) de uma abordagem
  trivial.

**Opção B — LLM local instrucional** (mais interessante):
- `Mistral-7B-Instruct`, `Llama-3-8B-Instruct` ou `Phi-3` via Ollama / llama.cpp.
- Prompt: "Classify this requirement against these defects: ..."
- Roda local, sem fine-tuning. Encaixa no escopo "Local AI Assistant" do MEMORY.
- Provavelmente supera zero-shot puro em tarefas semânticas.

> **Recomendação atual:** B. É o que diferencia o TCC e está alinhado com o
> título do trabalho ("Local AI Assistant").

### Prioridade 4 — Threshold tuning no improved_v2

- [ ] `python scripts/run_threshold_tuning.py --labels improved_v2 --thresholds 0.05 0.1 0.15 0.2 0.3 0.4 0.5 0.6 0.7 0.8`
- Pelo perfil de scores brutos analisado (`non_measurable` max 0.337), o
  ganho esperado é pequeno — mas vale fechar a iteração com dado completo
  antes de descartar.

### Prioridade 5 — Análise qualitativa de erros

Para a TCC ficar mais rica:

- [ ] Listar manualmente os 5-10 piores FP e FN do zero-shot improved + tuning.
- [ ] Categorizar: erro do modelo? erro do rótulo? requisito ambíguo de fato?
- [ ] Material direto para a seção de Discussão.

---

## Como atualizar este arquivo

Quando uma iteração terminar:

1. Atualizar a tabela **Estado atual** no topo.
2. Adicionar uma nova entrada **M_n_** em **Timeline**, com:
   - O que mudou (variável)
   - Resultados numéricos (P/R/F1 ou macro F1)
   - O que aprendemos (1-2 frases)
3. Se um achado for forte, mover para **Diagnóstico**.
4. Riscar/marcar `[x]` os itens em **Próximos passos** que foram concluídos.
5. Datar a entrada e commitar.

---

## Changelog

- **2026-04-29** — Criado arquivo. Cobertura retroativa de M0–M6
  (setup → dataset → baseline → improved → threshold tuning → refactor →
  improved_v2). Diagnóstico consolidado pós-v2.
