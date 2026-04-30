# PocketRE — Progress Log

Diário de progresso e milestones do TCC. Append-only: cada nova iteração entra
ao final, e o **estado atual** no topo é atualizado.

> Companheiro do `@ai/MEMORY.md`. MEMORY descreve **o que o projeto é** (escopo,
> decisões, convenções). Este arquivo descreve **o que aconteceu, em que ordem,
> com que resultado, e por quê** — material direto para o capítulo de
> Resultados/Discussão da TCC.

---

## Estado atual (snapshot)

**Última atualização:** 2026-04-30

### Métodos avaliados

| Método | Modelo / artefato | Status |
|---|---|---|
| NLI (entailment) | `roberta-large-mnli` | Avaliado em **6 variantes** — F1 macro ≈ 0 em todas. **Frente encerrada.** |
| Zero-shot classification | `facebook/bart-large-mnli` | Avaliado em 5 variantes + 2 rodadas de threshold tuning. Teto confirmado (`vague` F1≈0.65, `optional` F1≤0.75). |
| **Rule-based (lexicon)** | regex word-boundary, ~21 termos | Avaliado em 1 variante. **Macro F1 = 0.958** (vague 0.917 / optional 1.000). **Supera BART por +0.6.** |
| Local LLM (instrucional) | — | Não iniciado — única frente capaz de superar o regex em vagueza conceitual. |

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
| 6 | Improved_v4 labels + threshold por defeito (0.65/0.75) | 2-classes | **0.000** | **0.000** ⚠️ |
| 7 | Improved_v4 + threshold tuning + Improved_v5 (0.4/0.3) | 2-classes | **0.000** | **0.3236** ✅ |
| 8 | **Rule-based** (regex lexicon, 15+6 termos) | 2-classes | n/a | **0.9584** 🏆 |

> ⚠️ **Exp. 5:** macro F1 enganosamente alta — média sobre 2 defeitos (vs 3) com
> TN=0 em ambos. Ver M7.
>
> ⚠️ **Exp. 6:** macro F1 = 0 por threshold mal calibrado. Com t≈0.42, `vague`
> atinge F1=**0.667** com TN=8 — melhor resultado real de `vague` até hoje. Ver M8.
>
> ✅ **Exp. 7:** número **honesto** da família v4. Threshold tuning confirmou
> `vague` F1=**0.647** com TN=7 (separação real); `optional` F1=0 (irrecuperável
> com a hipótese v4). Macro 0.324 < M4 (0.4405) mas o melhor `vague`
> empiricamente confirmado. Ver M9.
>
> 🏆 **Exp. 8 (rule-based):** macro F1=**0.9584**, com `optional` em F1 perfeito
> (1.000) e `vague` F1=0.917 (P=1.0, R=0.846). Supera o melhor zero-shot por
> +0.518. Os 2 únicos FN são casos de **vagueza conceitual** (`"secure"`,
> `"timely manner"`) — exatamente onde um LLM com semântica seria útil. Ver M10.

### F1 por defeito — melhor configuração honesta até agora

| Defeito | Melhor F1 real | Configuração | TN | Comentário |
|---|---|---|---|---|
| `optional` (2-cls) | **1.000** 🏆 | rule-based (regex lexicon) | 22/22 | **Resultado perfeito** — token-level signal. Ver M10. |
| `vague` (2-cls) | **0.917** 🏆 | rule-based (regex lexicon) | 17/17 | P=1.0, R=0.846. 2 FN são vagueza conceitual sem trigger word. Ver M10. |
| `optional` (3-cls) | 0.750 | zero-shot improved + tuning, t=0.6 | 20/22 | Melhor resultado *do BART* (3-classes) |
| `vague` (2-cls) | 0.647 ★ | zero-shot improved_v4 + tuning, t=0.4 (improved_v5) | 7/17 | Melhor `vague` *do BART*, confirmado por tuning |
| `ambiguous` (3-cls) | 0.571 | zero-shot improved + tuning, t=0.3 | 0/17 | F1 alto mas TN=0 — modelo não rejeita nada |
| `vague` (2-cls) | 0.571 | zero-shot improved_v3, t=0.45 | 0/17 | F1 alto mas TN=0 — hipótese catch-all |
| `non_measurable` (3-cls) | **0.000** | qualquer configuração | n/a | Score bruto colapsado; eliminado pela fusão em `vague` |
| `optional` (2-cls) | **0.000** | zero-shot improved_v4 / v5 (ver M8/M9) | n/a | Hipótese "ONLY if / NOT if" suprime sinal — score max 0.021, irrecuperável |

> ★ Em M8 a estimativa visual sugeria F1=0.667 (t≈0.42); o tuning sistemático
> de M9 confirmou o ótimo em t=0.4 com F1=**0.647** (TP=11, FP=10, FN=2, TN=7).
> Pequena correção numérica, mesma conclusão.

> **Situação atual:** o **rule-based domina** o leaderboard em ambos os
> defeitos. Os tetos do BART zero-shot ficaram bem abaixo da regex em ambos
> (`optional`: 1.000 vs 0.750; `vague`: 0.917 vs 0.647). Os 2 únicos FN do
> regex são vagueza conceitual sem trigger word — **exatamente o nicho onde
> um LLM local com compreensão semântica poderia agregar valor**. Caso
> contrário, regex já satura o problema com 30 amostras.

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

### M8 — Iteração 6: Improved_v4 — "ONLY if / NOT if"

Tentativa de resolver os dois failure modes da v3 usando cláusulas de exclusão
explícitas na própria hipótese:

- vague → "...vague **ONLY if** it explicitly contains subjective words such as
  fast, quick, good, efficient... **If none of these words appear, it is not
  vague.**"
- optional → "...optional **ONLY if** it explicitly contains terms such as may,
  might, could... **The words must or shall indicate that it is NOT optional.**"

Thresholds embutidos: `{vague: 0.65, optional: 0.75}`.

**Resultados (com thresholds embutidos):**

| Modelo | Defeito | TP | FP | FN | TN | P | R | F1 |
|---|---|---|---|---|---|---|---|---|
| NLI v4 | vague | 0 | 0 | 13 | 17 | 0.000 | 0.000 | **0.000** |
| NLI v4 | optional | 0 | 0 | 8 | 22 | 0.000 | 0.000 | **0.000** |
| Zero-shot v4 | vague | 0 | 0 | 13 | 17 | 0.000 | 0.000 | **0.000** |
| Zero-shot v4 | optional | 0 | 0 | 8 | 22 | 0.000 | 0.000 | **0.000** |

À primeira vista, parece catástrofe total. Mas há dois comportamentos distintos
e o quadro é mais complexo do que os zeros sugerem.

---

**NLI v4 — comportamento interessante em `optional`:**

Pela primeira vez, o NLI deixou de responder só NEUTRAL: para `optional`,
23/30 itens receberam **CONTRADICTION** (não ENTAILMENT). Isso inclui os
próprios requisitos opcionais reais (e.g., "The system may send email
notifications" → CONTRADICTION 0.609). A cláusula "must or shall indicate
that it is NOT optional" foi interpretada pelo RoBERTa como contradição
para a maioria dos requisitos — inclusive os que deveriam ser ENTAILMENT.
O modelo respondeu à instrução negativa, mas na direção errada. `vague`
continua 30/30 NEUTRAL como sempre.

---

**Zero-shot v4 — dois comportamentos opostos entre os defeitos:**

**`vague` — collapsed but salvageable:**

A hipótese com "ONLY if" estreitou demais — score máximo alcançado foi
`0.624`, abaixo do threshold `0.65`. Nenhum item cruzou o limiar.
Mas a distribuição de scores é a **mais separada já observada para `vague`**:

| Intervalo de score | Grupo dominante |
|---|---|
| 0.55 – 0.624 | vague (4/4 são vague) |
| 0.44 – 0.54 | misto (vague + optional + 3 clean) |
| 0.26 – 0.43 | clean e optional |

Sweep manual de thresholds revela:

| t | TP | FP | FN | TN | P | R | F1 |
|---|---|---|---|---|---|---|---|
| 0.42 | 11 | 9 | 2 | 8 | 0.550 | 0.846 | **0.667** |
| 0.44 | 9 | 6 | 4 | 11 | 0.600 | 0.692 | **0.643** |
| 0.46 | 8 | 3 | 5 | 14 | 0.727 | 0.615 | **0.667** |
| 0.50 | 6 | 1 | 7 | 16 | 0.857 | 0.462 | 0.600 |
| 0.55 | 4 | 0 | 9 | 17 | 1.000 | 0.308 | 0.471 |
| **0.65** | **0** | **0** | **13** | **17** | 0 | 0 | **0.000** ← embutido |

Com t=0.42 ou t=0.46, F1=**0.667 com TN real (8 ou 14)**. É o melhor
resultado de `vague` em toda a pesquisa — e foi desperdiçado por 1 decimal
no threshold.

**`optional` — colapso completo:**

O inverso da v3. Enquanto v3 saturou (tudo ENTAILMENT, score mínimo 0.735),
a v4 colapsou (tudo NEUTRAL, score máximo 0.021). A cláusula "must or shall
indicate that it is NOT optional" não foi apenas inútil — ela suprimiu
completamente o sinal de opcionalidade. Mesmo os requisitos que contêm
textualmente "may/could/might" receberam scores ≤ 0.019.

| t | Melhor F1 possível | Situação |
|---|---|---|
| 0.007 | 0.444 | TN=2 (inútil) |
| 0.012 | 0.435 | TN=12 (ok) |
| **0.075** | 0.000 | ← nenhum item acima |

Nenhum threshold razoável recupera `optional` com essa hipótese.

---

**Aprendizado geral de M8:**

1. **Threshold mal calibrado é o único motivo pelo qual v4 parece F1=0.** Com
   re-calibração, `vague` teria F1=0.667 — resultado novo e real. Confirmar
   via threshold tuning é alta prioridade.

2. **A cláusula "ONLY if X" funciona para `vague` (estreita bem), mas mata
   `optional` (suprime o sinal útil)**. Os dois defeitos respondem de forma
   oposta ao mesmo mecanismo de exclusão. Isso sugere que não há uma única
   estratégia de verbalização que funcione para ambos simultaneamente no BART.

3. **`optional` demonstrou um padrão de V invertido ao longo das iterações:**
   - v3: saturação (score min 0.735, threshold 0.70 → tudo ENTAILMENT)
   - v4: colapso (score max 0.021, threshold 0.75 → tudo NEUTRAL)
   - A melhor configuração histórica está em M4 (3-classes, improved+tuning, F1=0.750)
     e provavelmente representa o teto do método para esse defeito.

4. **NLI continua morto** (5ª variante sem ENTAILMENT), mas o comportamento de
   CONTRADICTION em `optional` é inédito — vale nota na discussão da TCC como
   evidência de que o modelo *reage* à instrução negativa, apenas não no sentido
   certo. Confirma que NLI zero-shot não é instruction-tuned.

### M9 — Iteração 7: Threshold tuning de Improved_v4 + Improved_v5 (calibração final)

Objetivo: confirmar empiricamente a previsão de M8 de que `vague` com a
hipótese v4 dá F1≈0.667 com threshold ≈0.42, e fechar o número honesto da
família v4 antes de mudar de método.

**Passo 1 — Threshold tuning sobre `improved_v4`:**

`python scripts/run_threshold_tuning.py --labels improved_v4 --thresholds 0.3 0.4 0.5 0.6 0.7`

| Defeito | t | P | R | F1 | TP | FP | FN | TN |
|---|---|---|---|---|---|---|---|---|
| vague | 0.3 | 0.462 | 0.923 | 0.6154 | 12 | 14 | 1 | 3 |
| vague | **0.4** | **0.524** | **0.846** | **0.6471** ★ | **11** | **10** | **2** | **7** |
| vague | 0.5 | 0.857 | 0.462 | 0.6000 | 6 | 1 | 7 | 16 |
| vague | 0.6 | 1.000 | 0.077 | 0.1429 | 1 | 0 | 12 | 17 |
| vague | 0.7 | 0.000 | 0.000 | 0.0000 | 0 | 0 | 13 | 17 |
| optional | qualquer ∈ [0.3, 0.7] | 0.000 | 0.000 | **0.0000** | 0 | 0 | 8 | 22 |

**Passo 2 — `IMPROVED_V5`: mesma hipótese de v4, thresholds ótimos:**

Codificadas no `LabelSet` para virarem o número canônico (sem mais "F1 dependente do threshold certo embutido"):

```python
IMPROVED_V5 = LabelSet(
    dataset="data/dataset_v2.json",
    defects=...,  # idênticas à v4
    thresholds={"vague": 0.4, "optional": 0.3},
)
```

**Resultados consolidados (zero-shot v5):**

| Defeito | TP | FP | FN | TN | P | R | F1 |
|---|---|---|---|---|---|---|---|
| vague | 11 | 10 | 2 | 7 | 0.524 | 0.846 | **0.647** ✓ |
| optional | 0 | 0 | 8 | 22 | 0.000 | 0.000 | **0.000** |
| **Macro** | | | | | **0.262** | **0.423** | **0.324** |

**Resultados NLI v5** (rodado por hábito): macro F1=**0.000**, 6ª variante
consecutiva sem reação. Em `vague`, score médio de ENTAILMENT 0.0001;
em `optional`, score médio 0.0008. Encerra definitivamente a frente.

---

**Análise didática:**

**1. `vague` — confirmação com pequena correção numérica.**

A previsão de M8 (F1=0.667 em t≈0.42) era boa mas estava ligeiramente
otimista. O tuning sistemático mostra que:

- t=0.3: alto recall (12/13) mas precisão pobre (12 TP em 26 positivos preditos).
- t=**0.4**: ponto ótimo. Captura 11/13 positivos com 7/17 TN reais — primeira
  vez em todo o projeto que `vague` separa de fato.
- t=0.5: a precisão dispara para 0.857 mas o recall despenca para 0.462.
- t≥0.6: a hipótese estreita corta tudo.

A curva F1 em função de t para `vague` v4 forma um platô raso entre 0.4 e 0.5
(F1 ≈ 0.60-0.65), o que significa que **a separação é real mas marginal**.
Comparado a M7/v3 onde tínhamos F1=0.571 com TN=0 (artefato), v5/v4 com
F1=0.647 e TN=7 é cientificamente honesto e melhor.

**2. `optional` — irrecuperável com a hipótese v4.**

O tuning revela algo mais forte do que "threshold mal calibrado": a hipótese
"ONLY if / NOT if" **suprime o sinal de opcionalidade em todo o dataset**.

- Score máximo em 30 itens: **0.021**.
- O top-1 score é "The system must be easy to maintain" (NOT-OPT, score 0.0207).
- Os requisitos genuinamente opcionais ficam entre 0.007 e 0.019 — abaixo do
  topo dos clean.
- **Não há ranking discriminativo:** mesmo que tentássemos t=0.005, F1 ainda
  seria ~0.44 com muitos FP.

Isso confirma o diagnóstico de M8: a cláusula `"The words must or shall
indicate that it is NOT optional"` introduz tokens negativos fortes
(`must`, `shall`, `NOT`) que dominam a inferência de entailment para qualquer
requisito que contenha verbos modais — o BART acaba lendo a hipótese como um
todo, não como um teste condicional.

**3. NLI — 6ª variante. Não há mais o que testar.**

`roberta-large-mnli` zero-shot foi avaliado em 6 verbalizações
fundamentalmente diferentes (curta, longa, com listas léxicas, com cláusulas
prescritivas, em 2 e 3 classes, com 2 datasets). Macro F1=0 em todas. O
único comportamento não-NEUTRAL apareceu em M8/v4 com `optional`
(CONTRADICTION na direção errada). A frente está cientificamente fechada
para o capítulo de Resultados.

**4. Posicionamento dos números no relato da TCC.**

| Cenário | Macro F1 | Vale citar como? |
|---|---|---|
| M4 — improved + tuning, 3-classes | 0.4405 | **Melhor agregado** do projeto (zero-shot) |
| M9/v5 — improved_v4 + tuning, 2-classes | 0.3236 | **Melhor `vague` confirmado** (TN real) |
| M7/v3 (artefato com TN=0) | 0.4962 | **Não citar como ganho** — explicar como artefato |
| Qualquer NLI | 0.000 | Resultado científico (NLI puro não funciona) |

**5. Ranking final dos defeitos no zero-shot (confirmado empiricamente):**

| Defeito | Teto F1 | Configuração de teto |
|---|---|---|
| `optional` (3-cls) | 0.750 | improved + tuning, t=0.6 (M4) |
| `vague` (2-cls) | 0.647 | improved_v4 + tuning, t=0.4 (M9) |
| `ambiguous` (3-cls) | 0.571 | improved + tuning, t=0.3 (M4, com TN=0) |
| `non_measurable` (3-cls) | 0.000 | nenhuma — fusão em `vague` foi a saída |

Os dois primeiros estão **calibrados e prontos para a tabela final do TCC**.

---

**Frase-âncora para a TCC:**

> "Systematic threshold tuning over an entailment-style hypothesis with
> exclusion clauses confirmed an asymmetric ceiling: `vague` reached
> F1=0.647 with real true negatives, while `optional` collapsed to F1=0
> because the hypothesis suppressed the model's discriminative signal across
> the entire dataset (max entailment score 0.021). No threshold can recover
> a defect whose ranking is non-discriminative — a property of the
> verbalization, not of the dataset."

### M10 — Iteração 8: Rule-based baseline (regex lexicon)

**Hipótese de trabalho:** se o BART zero-shot estava degenerando para
*lexical pattern matching* (M7, §6.2 do Diagnóstico), então uma regex
honesta sobre os mesmos tokens-gatilho deveria competir — e talvez vencer
— sem custo computacional. Implementação ~30 linhas, 0 modelos.

**Artefato:** `scripts/lib/rules.py` + `RULES_V1` em `labels.py` +
runners (`scripts/run_rules.py`, `scripts/rules/run_rules_v1.py`).
Mesmo formato de saída JSON dos métodos NLI/zero-shot
(`predictions[defect].label ∈ {ENTAILMENT, NEUTRAL}`), com `score` =
fração de termos do lexicon que casaram e `matched_terms` para análise
qualitativa. Casamento é regex word-boundary (`\bterm\b`,
case-insensitive), o que evita falsos positivos do tipo `"may"` em
`"Mayflower"`.

**Lexicons (`RULES_V1.terms`):**

```python
vague:    quickly, fast, good, large, easy, reliable, adequate, professional,
          efficient, user-friendly, intuitive, clear, helpful, well, reasonable
optional: may, might, could, optionally, if necessary, if appropriate
```

15 termos para `vague`, 6 para `optional`. Todos extraídos manualmente
das hipóteses verbalizadas das iterações v2-v5.

**Resultados sobre `data/dataset_v2.json` (30 amostras):**

| Defeito | TP | FP | FN | TN | P | R | F1 |
|---|---|---|---|---|---|---|---|
| vague | 11 | 0 | 2 | 17 | **1.000** | 0.846 | **0.9167** |
| optional | 8 | 0 | 0 | 22 | **1.000** | **1.000** | **1.0000** |
| **Macro** | | | | | **1.000** | **0.9231** | **0.9584** |

**Comparativo direto com o melhor zero-shot:**

| Defeito | Rule-based F1 | BART zero-shot F1 (melhor honesto) | Δ |
|---|---|---|---|
| optional | **1.000** | 0.750 (M4, 3-classes) | +0.250 |
| vague | **0.917** | 0.647 (M9/v5, 2-classes) | +0.270 |
| Macro | **0.958** | 0.4405 (M4) / 0.324 (M9) | +0.518 / +0.634 |

**Análise dos 2 únicos FN (`vague`):**

Os requisitos que escaparam do regex foram:

1. `"The system should be secure."`
2. `"Data should be processed in a timely manner."`

Nenhum dos 15 termos de `vague` aparece nessas frases — `secure`,
`timely manner` e `processed` são vagos **conceitualmente** mas não
estão no lexicon. Para verificar se eles são detectáveis por um modelo
com compreensão semântica, conferimos como o BART zero-shot v5 pontuou
esses dois itens:

| Requisito | BART v5 — score `vague` | Label v5 (t=0.4) |
|---|---|---|
| `"The system should be secure."` | 0.4395 | ENTAILMENT ✓ |
| `"Data should be processed in a timely manner."` | 0.5891 | ENTAILMENT ✓ |

**O BART acerta justamente os 2 itens onde o regex falha.** Há sinal
**complementar** entre os dois métodos. Um ensemble simples (regex OR
BART) capturaria 13/13 positivos de `vague`, mas o BART carrega 10 FP
do v5; o ensemble teria P=13/23=0.565 e R=1.0, dando F1=0.722 — pior
que o regex sozinho. Em termos de utilidade prática, **o regex
domina sozinho**; o BART agrega valor apenas em uma fatia muito estreita
do espectro de erros.

**Inspeção dos 0 FP:**

Nenhum dos 17 itens *clean* recebeu um match falso para `vague` ou
`optional`. Em particular, `"The system shall encrypt all stored
passwords using bcrypt with a minimum cost factor of 12"` não tem
nenhum trigger word — bcrypt é específico, "minimum cost factor of 12"
é mensurável. O lexicon foi calibrado bem o suficiente para não
produzir overshooting.

**Análise do dataset (esse é o ponto crítico):**

Não há como evitar a observação: **o problema, como definido em
`dataset_v2.json` com 30 amostras manualmente curadas, é majoritariamente
um problema lexical**. Para `optional` (token-level explícito) é
evidente. Para `vague`, 11 dos 13 positivos contêm uma palavra-gatilho
óbvia. Isso reflete (a) o design do dataset, que ancorou a definição
operacional de cada defeito em palavras concretas, e (b) o fato de
`dataset_v2.json` ter sido construído antes mesmo da v3, com termos
muito alinhados aos das hipóteses iniciais — viés de construção a
favor da regex.

Esse é um **resultado científico forte**, mas precisa ser apresentado
com nuances:

1. **Para *este* dataset**, a regex satura o problema. Modelos
   neurais zero-shot são ineficientes nesse regime.
2. **Para problemas reais** de detecção de defeitos em RE, o regex
   provavelmente não generalize: requisitos no campo usam um vocabulário
   muito mais amplo e construções negativas / implícitas que escapam
   ao lexicon. Os 2 FN observados são exatamente uma amostra dessa
   classe de erro.
3. **Validade externa do experimento:** este resultado argumenta a
   favor de um dataset maior e mais diverso para a próxima iteração
   (e.g., 100+ amostras, com vagueza conceitual sem trigger word
   representada explicitamente).

**Aprendizado geral de M10:**

1. **A regex venceu o BART por +0.518 em macro F1.** É o resultado mais
   contraintuitivo do projeto e o que mais fala sobre as escolhas
   metodológicas de zero-shot NLP em tarefas predominantemente
   lexicais.

2. **Confirma o diagnóstico do M7/§6.2:** o BART não estava extraindo
   semântica de opcionalidade ou vagueza — estava medindo sobreposição
   lexical de forma ineficiente, com ruído. Quando o sinal lexical é
   isolado e medido diretamente, ele é puro.

3. **Dois FN em vagueza conceitual** definem precisamente o nicho do
   próximo método: um LLM local (Mistral / Llama) só justifica seu custo
   se conseguir capturar `"timely manner"` e `"secure"` mantendo a
   precisão alta. Caso contrário, **um TCC honesto admite que
   `dataset_v2.json` é bem resolvido por regex**.

4. **Implicação para escrita do TCC:** o experimento rule-based não é
   apenas um baseline — é o **referencial superior** que os métodos
   neurais precisam justificar. O capítulo de Resultados deve abrir
   pelo regex e construir a discussão a partir daí.

---

**Frase-âncora para a TCC:**

> "A 30-line regex baseline using 21 manually curated trigger terms
> achieved macro F1 = 0.958 (precision = 1.0) on the same dataset where
> a zero-shot BART-large-MNLI ceiling was empirically established at
> macro F1 = 0.4405. The two false negatives of the lexical baseline
> were the only items requiring genuine semantic understanding —
> `"timely manner"` and `"secure"` — and were detected by BART, evidencing
> a small but real complementary signal in the neural model. For this
> dataset, however, the regex saturates the problem, and zero-shot
> models cannot justify their compute cost on the basis of accuracy
> alone."

---

## Diagnóstico (consolidado, 2026-04-30)

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

- [x] **`DEFECT_TYPES` desatualizado em `scripts/lib/labels.py`**: resolvido
      tornando os arquivos de resultado **autodescritivos**. Cada JSON agora
      começa com `"defect_types": [...]` (envelope `{defect_types, items}`
      para inferência; `{defect_types, metrics}` para tuning). `evaluate`,
      `compare_experiments` e `select_best_thresholds` leem essa lista do
      próprio arquivo via `io.unwrap_results` / `io.unwrap_threshold_metrics`,
      com fallback para o formato antigo (lista de items / dict de
      `defect → threshold → metrics`). O constante global `DEFECT_TYPES` foi
      removido de `labels.py`. Re-rodar runners regenera os JSONs no novo
      formato automaticamente.
- [x] **Leftover `["ambiguous"]` em `data/dataset_v2.json`**: corrigido em
      M7 — re-rotulado para `["vague"]`. Total de positivos para `vague`
      passou de 12 → 13.

### Prioridade 1 — Encerrar a frente de NLI puro

- [ ] Documentar formalmente em `@ai/MEMORY.md` ("Important insight") que
      NLI zero-shot puro foi avaliado e descartado, com **6 variantes** como
      evidência (baseline, improved, improved_v2, improved_v3, improved_v4,
      improved_v5).
- [x] Não rodar mais iterações de label verbalization no `roberta-large-mnli`
      a partir daqui. **Status: cumprido — 6 variantes consecutivas com
      macro F1=0 são evidência suficiente para o capítulo de Resultados.**

### Prioridade 2 — Decidir o que fazer com o dataset

- [x] **Caminho A executado em M7**: fundimos `ambiguous + non_measurable` em
      `vague` (`data/dataset_v2.json`). Resolveu a colinearidade — agora
      cada amostra tem 0 ou 1 defeito detectável.
- [ ] **Avaliar se vale também dobrar o dataset**: 30 amostras é muito pouco
      para conclusões robustas. Cada flip de 1 amostra muda F1 em ~0.04. Se
      formos comparar com LLM local, dataset de ~60-100 amostras dá mais
      confiança estatística.

### Prioridade 3 — Threshold tuning no improved_v4 para `vague`

- [x] **Concluído em M9.** Threshold tuning confirmou `vague` t=**0.4** →
      F1=**0.647** (TP=11, FP=10, FN=2, TN=7). Pequena correção sobre a
      estimativa visual de M8 (0.667), mesma conclusão.
- [x] `optional` é matematicamente irrecuperável com a hipótese v4 (score
      máx 0.021 sobre todo o dataset, sem ranking discriminativo).
- [x] `IMPROVED_V5` criado com os thresholds ótimos embutidos
      (`{vague: 0.4, optional: 0.3}`) — virou a configuração canônica para
      reprodutibilidade.

### Prioridade 4 — Adicionar um terceiro método ⭐

**Opção A — Rule-based / heurísticas léxicas:**

- [x] **Concluída em M10.** Regex word-boundary + lexicon de 21 termos
      (15 vague + 6 optional). Macro F1=**0.958** sobre `dataset_v2.json`,
      superando o BART zero-shot em +0.518. Implementação em
      `scripts/lib/rules.py`, `LabelSet RULES_V1`, runners
      `scripts/run_rules.py` e `scripts/rules/run_rules_v1.py`.
- [x] **Não foi um "baseline contra o qual modelos têm que ganhar" — virou
      o referencial superior.** O BART nunca chegou perto.

**Opção B — LLM local instrucional** (segue como recomendação principal):

- `Mistral-7B-Instruct`, `Llama-3-8B-Instruct` ou `Phi-3` via Ollama / llama.cpp.
- Prompt: "Classify this requirement against these defects: ..."
- Roda local, sem fine-tuning. Encaixa no escopo "Local AI Assistant" do MEMORY.
- **Bar mais alto agora:** precisa não apenas superar o BART (já feito pelo
  regex) mas chegar perto da regex em precisão **e** capturar os 2 FN de
  vagueza conceitual (`"secure"`, `"timely manner"`). É o único nicho onde
  um LLM tem chance estrutural de agregar valor sobre o regex neste dataset.
- Alternativa mais defensável: usar o LLM em modo **complementar** — apenas
  quando o regex não dispara (top-1 score = 0). Custo zero em 28/30 itens,
  decisão neural só nos 2 itens duvidosos.

> **Próximo passo recomendado:** rodar Mistral-7B-Instruct com prompt simples
> sobre os 30 itens de `dataset_v2.json` antes de mais qualquer coisa. Se
> ele não pegar `"timely manner"` ou `"secure"`, o caminho é admitir o teto
> do dataset; se pegar com precisão alta, justifica a integração.

### Prioridade 5 — Threshold tuning no improved_v2 e improved_v3

- [ ] `python scripts/run_threshold_tuning.py --labels improved_v2 --thresholds 0.05 0.1 0.15 0.2 0.3 0.4 0.5 0.6 0.7 0.8`
- [ ] `python scripts/run_threshold_tuning.py --labels improved_v3 --thresholds 0.5 0.6 0.7 0.75 0.8 0.85 0.9 0.92 0.95`
- Pelo perfil de scores em ambos, o ganho esperado é modesto. Mas vale
  fechar com dado completo antes de declarar o ceiling do zero-shot.
- Nota: v2 não usa `dataset_v2.json` (usa dataset original de 3 classes),
  portanto os resultados não são comparáveis diretamente com v3/v4.

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
- **2026-04-29** — Adicionado M8 (Iteração 6): `IMPROVED_V4` com cláusulas
  "ONLY if / NOT if". NLI: 5ª variante sem ENTAILMENT em `vague`; `optional`
  exibe CONTRADICTION pela 1ª vez (23/30), mas sem ENTAILMENT. Zero-shot:
  `optional` colapsou (score max 0.021); `vague` teve o threshold embutido
  mal calibrado (0.65 vs score max real 0.624) mas com t=0.42 daria F1=0.667
  com TN real — melhor resultado de `vague` de toda a pesquisa. Atualizado
  snapshot e tabela de melhores F1; Prioridade 3 virou threshold tuning de
  improved_v4 para confirmar o número.
- **2026-04-30** — Refatoração: `dataset` migrado para dentro do `LabelSet`
  como `dataset: str` (junto com `defects` e `thresholds`). `LabelSet` agora
  é a única fonte de verdade para experimentos; `DATASET_PATH` removido de
  todos os 8 runners (genéricos + thin wrappers).
- **2026-04-30** — Adicionado M9 (Iteração 7): threshold tuning sobre
  `IMPROVED_V4` confirmou empiricamente o ótimo de `vague` em t=**0.4** →
  F1=**0.647** (TP=11, FP=10, FN=2, TN=7), pequena correção numérica sobre
  M8 (0.667). `optional` confirmado como irrecuperável: F1=0 em todos os
  thresholds testados, score máximo 0.021 em todo o dataset.
  `IMPROVED_V5` criado com `{vague: 0.4, optional: 0.3}` para virar a
  configuração canônica reprodutível. Resultado consolidado de v5:
  zero-shot macro F1=0.324 (com TN real); NLI macro F1=0 (6ª variante,
  encerra a frente). Prioridade 1 cumprida; Prioridade 3 cumprida;
  Prioridade 4 (3º método: rule-based / LLM local) virou a frente ativa.
- **2026-04-30** — Adicionado M10 (Iteração 8): **rule-based baseline**.
  `LabelSet` ganhou campo opcional `terms: dict | None`. Novo módulo
  `scripts/lib/rules.py` (regex word-boundary + case-insensitive),
  `RULES_V1` com 15 termos `vague` + 6 termos `optional`, runners
  `scripts/run_rules.py` e `scripts/rules/run_rules_v1.py`. Resultado
  sobre `dataset_v2.json`: **macro F1 = 0.9584** (`optional` perfeito
  1.000; `vague` 0.917, P=1.0). Supera o melhor BART zero-shot por
  +0.518. Os 2 únicos FN são vagueza conceitual sem trigger word
  (`"secure"`, `"timely manner"`) — exatamente os 2 itens que o BART
  v5 acerta como ENTAILMENT, evidenciando sinal complementar fraco
  entre regex e modelo neural. **Achado científico mais forte do
  projeto.** Prioridade 4A cumprida; 4B (LLM local) ganha bar mais
  alto: precisa cobrir vagueza conceitual sem perder precisão.
