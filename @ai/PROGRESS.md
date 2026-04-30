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
| NLI (entailment) | `roberta-large-mnli` | Avaliado em 4 variantes — **saturado**, F1 ≈ 0 em todas |
| Zero-shot classification | `facebook/bart-large-mnli` | Avaliado em 4 variantes + threshold tuning — único caminho com sinal, mas **com teto** |
| Local LLM (instrucional) | — | Não iniciado / próximo grande passo |

### Esquemas de rótulos avaliados

| Esquema | Defeitos | Dataset | Justificativa |
|---|---|---|---|
| 3-classes | `ambiguous`, `non_measurable`, `optional` | `data/dataset.json` | Esquema original |
| 2-classes (fundido) | `vague`, `optional` | `data/dataset_v2.json` | `ambiguous + non_measurable → vague` para resolver colinearidade do dataset (M7) |

### Macro F1 por experimento (consolidado)

| # | Experimento | Esquema | NLI macro F1 | Zero-shot macro F1 |
|---|---|---|---|---|
| 1 | Baseline labels (threshold 0.5 fixo) | 3-classes | **0.074** | **0.286** |
| 2 | Improved labels (threshold 0.5 fixo) | 3-classes | **0.000** | **0.322** |
| 3 | Improved labels + threshold tuning per-defeito | 3-classes | n/a | **0.4405** |
| 4 | Improved_v2 labels + threshold por defeito (0.75/0.30/0.70) | 3-classes | **0.000** | **0.190** |
| 5 | Improved_v3 labels + threshold por defeito (0.45/0.70) | **2-classes** | **0.000** | **0.4962** ⚠️ |

> ⚠️ A macro F1 do experimento 5 é **enganosamente boa**: subiu vs improved_v2 só
> porque a média agora é sobre 2 defeitos em vez de 3. Olhando counts crus, o
> modelo prediz **ENTAILMENT para tudo** (TN=0 em ambos os defeitos). Ver M7.

### F1 por defeito — melhor configuração honesta até agora

| Defeito | Melhor F1 | Configuração | TN | Comentário |
|---|---|---|---|---|
| `optional` (3-cls) | **0.75** | zero-shot improved + tuning, t=0.6 | 20/22 | **Resultado real** — separa positivo de negativo |
| `ambiguous` (3-cls) | **0.571** | zero-shot improved + tuning, t=0.3 | 0/17 | F1 alto mas TN=0 — modelo não rejeita nada |
| `non_measurable` (3-cls) | **0.000** | qualquer configuração | n/a | Score bruto colapsado, hipótese negada não acende BART |
| `vague` (2-cls) | **0.571** | zero-shot improved_v3, t=0.45 | 0/17 | F1 alto mas TN=0 — hipótese virou catch-all |
| `optional` (2-cls) | **0.421** | zero-shot improved_v3, t=0.70 | 0/22 | F1 caiu vs 3-cls — hipótese listou tokens, virou caça-palavras |

> **Único defeito com sinal real e separação útil até hoje:** `optional` no
> esquema 3-classes com hipótese improved + threshold 0.6. Os demais ou têm
> F1 zero, ou têm F1 numericamente decente mas com TN=0.

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

### M7 — Iteração 5: dataset_v2 (esquema fundido) + Improved_v3 labels

**Mudança de esquema de rótulos (Caminho A do diagnóstico anterior):**
fundimos `ambiguous + non_measurable` em um único rótulo `vague`, atacando o
problema da colinearidade detectado em M6.

Novo dataset `data/dataset_v2.json`:
- 13 com `vague` (12 ex-`ambiguous+non_measurable` + 1 ex-`ambiguous` puro)
- 8 com `optional`
- 9 sem defeito (clean)
- Esquema final: 2 defeitos detectáveis + classe implícita "clean"

> Bug de transição corrigido nesta iteração: havia 1 amostra com leftover
> `["ambiguous"]` no `dataset_v2.json` que nunca seria detectada (não existe
> mais esse rótulo no esquema). Re-rotulada para `["vague"]`, totalizando 13
> positivos para `vague`.

Hipóteses (`labels.py` → `IMPROVED_V3`):

- vague → "...vague because it uses subjective or imprecise language such as
  fast, quick, good, efficient, reliable, user-friendly, intuitive, adequate,
  or large, **and does not clearly define exact behavior or measurable
  criteria**."
- optional → "...optional only if it uses explicit optional terms such as may,
  might, could, optionally, if necessary, or if appropriate. **The word should
  alone is not enough to indicate optionality.**"

Thresholds embutidos: `{vague: 0.45, optional: 0.70}`.

**Resultados:**

| Modelo | Defeito | TP | FP | FN | TN | P | R | F1 |
|---|---|---|---|---|---|---|---|---|
| NLI v3 | vague | 0 | 0 | 13 | 17 | 0.000 | 0.000 | **0.000** |
| NLI v3 | optional | 0 | 0 | 8 | 22 | 0.000 | 0.000 | **0.000** |
| Zero-shot v3 | vague | 12 | 17 | 1 | **0** | 0.414 | 0.923 | **0.571** |
| Zero-shot v3 | optional | 8 | 22 | 0 | **0** | 0.267 | 1.000 | **0.421** |

NLI: 30/30 NEUTRAL em ambos os defeitos (4ª iteração consecutiva sem reação).

Zero-shot: virou um classificador "sim para tudo".
- `vague`: 29/30 ENTAILMENT, score médio 0.824, threshold 0.45 → quase nada cai.
- `optional`: 30/30 ENTAILMENT, score mínimo 0.735, threshold 0.70 → tudo cai.
- **TN = 0 em ambos os defeitos** — o modelo não rejeitou nenhum requisito clean.

Aprendizado: dois failure modes novos do zero-shot, ambos detalhados na
seção **Diagnóstico** abaixo:
1. Hipótese de `vague` virou catch-all semântico.
2. Hipótese de `optional` virou caça-palavras léxico.

A macro F1 (0.4962) parece a melhor de todas, mas isso é artefato de
**média sobre 2 defeitos em vez de 3**. Em termos de utilidade prática, M7
é um regresso vs M4 (threshold tuning, 0.4405 com TN saudável em `optional`).

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

### 6. Failure modes do zero-shot expostos pela v3

A iteração v3 (M7) revelou **dois modos de falha distintos** do zero-shot
NLI que valem ouro pra discussão da TCC:

#### 6.1 Catch-all hypothesis — quando a hipótese é ampla demais

A hipótese de `vague` em v3 termina com:

> "...and does not clearly define exact behavior or measurable criteria."

Esse pedaço final é semanticamente quase universal: praticamente qualquer
requisito em linguagem natural pode ser lido como "não definindo
exatamente o comportamento". Resultado:

- Score médio para `vague` em todos os 30 itens = **0.824**.
- Requisito clean "Each user session shall expire after 30 minutes of
  inactivity." (perfeitamente mensurável) recebeu score 0.710 para `vague`.
- O modelo retorna ENTAILMENT para 29/30 itens (TN = 0/17).

**Insight científico:** hipóteses que terminam em cláusulas semanticamente
amplas viram **catch-all** — o modelo dispara entailment para o pedaço
genérico, não para a condição específica que queremos detectar. A v2 caiu no
extremo oposto (hipótese estreita demais, scores no chão); a v3 atravessou o
ponto ótimo.

#### 6.2 Lexical pattern matching — quando a hipótese lista tokens

A hipótese de `optional` em v3 cita explicitamente:

> "...explicit optional terms such as **may, might, could, optionally, if
> necessary, or if appropriate**."

E inclui uma meta-instrução:

> "**The word should alone is not enough** to indicate optionality."

Resultado: o BART pontuou ENTAILMENT para 30/30 itens, com score mínimo de
0.735 (todos acima do threshold 0.70).

Inspeção dos scores mostra dois padrões:

- Requisitos que contêm tokens "shall", "should", "may", "could" (= todos)
  recebem scores altos (0.83-0.96) **independentemente de serem optional ou
  não**.
- Requisitos genuinamente optional não pontuam mais alto que requisitos
  clean: `"The system may provide an optional two-factor authentication
  mechanism"` = 0.826 vs `"The system shall authenticate users via OAuth
  2.0"` = 0.955.

**Dois insights científicos:**

1. **Listar tokens-gatilho na hipótese induz pattern matching léxico.** O
   BART não está extraindo a semântica de opcionalidade — está medindo a
   sobreposição lexical entre hipótese e premissa. Como toda hipótese da
   forma "...such as X, Y, Z" tem alta sobreposição com qualquer requisito
   contendo verbos modais, o modelo perde a capacidade de discriminar.

2. **NLI zero-shot não segue meta-instruções.** A cláusula "the word should
   alone is not enough" não é executável pelo modelo — ele não é
   instruction-tuned. Para o BART, essa frase é apenas mais texto, e
   provavelmente *piora* o resultado por reforçar o token "should" no
   contexto da hipótese.

#### 6.3 Frase-âncora para a TCC

> "Zero-shot NLI hypotheses live on a Goldilocks zone: too narrow and
> scores collapse to zero (M6/v2); too broad and scores saturate to one
> (M7/v3). Hypothesis verbalization that lists trigger tokens degenerates
> into lexical pattern matching, while meta-instructional clauses are
> ignored entirely. This bounds the achievable performance of zero-shot NLI
> for requirement defect detection regardless of dataset relabeling."

---

## Próximos passos (em ordem de prioridade)

### Prioridade 0 — Higiene técnica antes da próxima rodada

Bugs detectados durante M7 que precisam ser corrigidos para qualquer
experimento futuro com esquemas != 3-classes:

- [ ] **`DEFECT_TYPES` desatualizado em `scripts/lib/labels.py`**: ainda é
      `["ambiguous", "non_measurable", "optional"]`. `print_evaluation()` e
      `print_comparison()` usam ele como default → quebram com `KeyError` em
      cima de resultados v3 (que têm chaves `vague`, `optional`).
      Sugestão: tornar dinâmico (`label_set.defects.keys()`) ou aceitar
      `defect_types` explicitamente em todos os runners.
- [x] **Leftover `["ambiguous"]` em `data/dataset_v2.json`**: corrigido em
      M7 — re-rotulado para `["vague"]`. Total de positivos para `vague`
      passou de 12 → 13.

### Prioridade 1 — Encerrar a frente de NLI puro

- [ ] Documentar formalmente em `@ai/MEMORY.md` ("Important insight") que
      NLI zero-shot puro foi avaliado e descartado, com **4 variantes** como
      evidência (baseline, improved, improved_v2, improved_v3).
- [x] Não rodar mais iterações de label verbalization no `roberta-large-mnli`
      a partir daqui.

### Prioridade 2 — Decidir o que fazer com o dataset

- [x] **Caminho A executado em M7**: fundimos `ambiguous + non_measurable` em
      `vague` (`data/dataset_v2.json`). Resolveu a colinearidade — agora
      cada amostra tem 0 ou 1 defeito detectável.
- [ ] **Avaliar se vale também dobrar o dataset**: 30 amostras é muito pouco
      para conclusões robustas. Cada flip de 1 amostra muda F1 em ~0.04. Se
      formos comparar com LLM local, dataset de ~60-100 amostras dá mais
      confiança estatística.

### Prioridade 3 — Fechar zero-shot com uma v4 cirúrgica

Antes de pular para LLM local, vale **uma última iteração** para
confirmar/refutar os failure modes do M7. Hipóteses curtas, sem listar
tokens, sem catch-all final:

```python
IMPROVED_V4 = LabelSet(
    defects={
        "vague": "This requirement uses subjective wording that different "
                 "readers would interpret differently.",
        "optional": "This requirement describes optional or non-mandatory "
                    "behavior that the system may or may not implement.",
    },
    thresholds={"vague": 0.5, "optional": 0.5},  # depois calibrar via tuning
)
```

- [ ] Rodar `python scripts/run_zeroshot.py --labels improved_v4`.
- [ ] Rodar `python scripts/run_threshold_tuning.py --labels improved_v4
      --thresholds 0.3 0.4 0.5 0.6 0.7 0.8 0.9`.
- [ ] Hipótese a testar: hipóteses **abstratas curtas** evitam tanto o
      collapse (v2) quanto a saturação (v3). Se F1 ficar abaixo de M4
      (0.4405), confirma o teto do método.

### Prioridade 4 — Adicionar um terceiro método

Aqui é onde o TCC ganha diferencial:

**Opção A — Rule-based / heurísticas léxicas** (mais simples):
- Regex de palavras-gatilho por defeito.
- Vira o "baseline simples" contra o qual modelos têm que ganhar.
- Útil para mostrar que NLI/zero-shot ganha (ou não ganha) de uma abordagem
  trivial. Dado o que vimos em M7 sobre `optional` (BART vira pattern
  matching), suspeita-se que regex pode até **empatar** com zero-shot.

**Opção B — LLM local instrucional** (mais interessante):
- `Mistral-7B-Instruct`, `Llama-3-8B-Instruct` ou `Phi-3` via Ollama / llama.cpp.
- Prompt: "Classify this requirement against these defects: ..."
- Roda local, sem fine-tuning. Encaixa no escopo "Local AI Assistant" do MEMORY.
- Provavelmente supera zero-shot puro em tarefas semânticas, **e** consegue
  seguir meta-instruções (limitação clara do BART exposta em M7).

> **Recomendação atual:** ambas, em ordem A → B. O rule-based dá um piso de
> comparação honesto e leva 1-2h para implementar. O LLM local é o
> diferencial real do TCC.

### Prioridade 5 — Threshold tuning no improved_v2 e improved_v3

- [ ] `python scripts/run_threshold_tuning.py --labels improved_v2 --thresholds 0.05 0.1 0.15 0.2 0.3 0.4 0.5 0.6 0.7 0.8`
- [ ] `python scripts/run_threshold_tuning.py --labels improved_v3 --thresholds 0.5 0.6 0.7 0.75 0.8 0.85 0.9 0.92 0.95`
- Pelo perfil de scores em ambos, o ganho esperado é modesto. Mas vale
  fechar com dado completo antes de declarar o ceiling do zero-shot.

### Prioridade 6 — Análise qualitativa de erros

Para a TCC ficar mais rica:

- [ ] Listar manualmente os 5-10 piores FP e FN do zero-shot improved + tuning
      (M4) — a melhor configuração honesta até hoje.
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
- **2026-04-29** — Adicionado M7 (Iteração 5): mudança de esquema para
  `vague + optional` no `dataset_v2.json` e nova `LabelSet` `IMPROVED_V3`.
  NLI segue morto (4ª variante). Zero-shot virou "sim para tudo" (TN=0 em
  ambos os defeitos). Estendido o Diagnóstico com dois novos failure modes:
  catch-all hypothesis e lexical pattern matching. Adicionada Prioridade 0
  (higiene técnica) com bug do `DEFECT_TYPES` e Prioridade 3 com proposta
  de `improved_v4` cirúrgica para fechar a frente de zero-shot.
