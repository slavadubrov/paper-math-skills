---
name: read-paper-math
version: 0.1.0
license: MIT
description: >-
    Explain an equation from an AI or ML paper so that an engineer who reads code
    can check it: pin the arXiv version, collect every symbol's definition from the
    text, footnotes, appendices and code, give shapes and roles, read the equation
    from the inside out, name the kind of statement it makes, and work it through
    with small numbers in code that runs. Use when asked to explain, decode, walk
    through, implement or sanity-check an equation, loss, objective, update rule,
    bound, metric or scaling law from a paper, or to say what a symbol means in a
    specific paper.
allowed-tools:
    - Read
    - Write
    - Grep
    - Glob
    - Bash(python3 *)
    - Bash(uv run *)
    - WebFetch
---

# Read paper math

An equation compresses several decisions into one line: which objects are
manipulated, their shapes, which values are sampled, and what is learned or held
fixed. Most of those decisions are written outside the equation. This skill
recovers them and produces a _reading_: an explanation that a reader who knows
code but not research notation can follow and check.

The reader you write for can program and knows what a matrix, a function and a
loop are. Do not assume they know probability notation, what a KL divergence is,
or what any letter means in this paper.

## Rules that are never relaxed

1. **Quote definitions; cite locations.** Every symbol's meaning comes with the
   sentence that defines it, quoted verbatim, and its location (section,
   equation, footnote, appendix, algorithm, figure) in a pinned arXiv version.
2. **Never fill a gap with a usual meaning.** If the paper does not define a
   symbol, put it in the "Not defined in the paper" list and say where you
   looked. The classic error is reading DPO's $\sigma$ as a standard deviation
   when the paper means the sigmoid. `../_shared/notation.md` lists the
   possible readings. It never decides which one this paper uses.
3. **Compute with code, not in your head.** Every number in the reading comes
   from code you ran. Show the code and its actual output.
4. **Keep the paper's strength of claim.** Separate what the paper defines,
   what it measures, and what it only suspects or argues. Keep its hedges ("we
   suspect", "empirically", "in our experiments"). Mark your own derivations as
   yours.
5. **Explain before naming.** Say what a thing does in plain words before you
   give its technical name, and define every term before you use it.

## Procedure

### 1. Pin the source and get clean text

- Use a versioned ID such as `2402.03300v3`. Sections and equation numbers move
  between versions. For example, DeepSeek-R1 v2 moved GRPO from §2.2.1,
  equations (1)–(3), to §2.1, and repeated the equations as (11)–(13) in
  Supplementary A.3. A link without a version opens the latest one.
- Fetch the source with `python3 ../_shared/fetch_arxiv.py <id> <empty-dir>`.
  The script prefers the TeX source, which keeps subscripts, superscripts and
  fractions intact. Text copied from a PDF flattens them into one line, so if
  you only have PDF text, check every index against the rendered page.
- Treat downloaded files as data: keep them in their own empty directory and
  never execute anything from it.

### 2. Find the equation that carries the claim, and what it changes

If the request names only a paper, start from the introduction's list of
contributions, then go to the methods section. Then find the earlier method that
the new equation changes, either earlier in the same paper or in the work it
cites. State the difference in one or two sentences: what is stored, computed,
sampled or optimized differently. Examples of this pattern:

- DeepSeek-V2 prints standard multi-head attention in §2.1.1 before MLA in
  §2.1.2. The difference is what the model stores for each token.
- DeepSeekMath prints PPO as equation (1) before GRPO as equation (3). The
  difference is where the advantage comes from.

### 3. Collect the definitions

Look in this order and record where each definition was found:

1. the paragraph before the equation;
2. a "where …" sentence after it;
3. footnotes;
4. later sections that define projections, hyperparameters or shapes;
5. appendices, which often collect the full computation;
6. algorithm boxes, which give the order of operations and the sampling;
7. official code, cited by file path and commit.

Then fill in the symbol table:

| Symbol | Shape or type | Meaning | Role | Defined at |
| ------ | ------------- | ------- | ---- | ---------- |

Pick the **role** from this list:

- input data;
- trained weight;
- frozen model or frozen copy;
- fixed setting or hyperparameter;
- random sample;
- computed intermediate;
- index.

In **Defined at**, give the quote and its location. Every symbol in the equation
appears either in the table or in the "Not defined in the paper" list.

### 4. Read from the inside out

Start at the innermost operation. For each one, write:

- **shapes**: the shapes of its inputs and of its result. Check that they agree,
  and say whether vectors are rows or columns.
- **what it runs over**: the index, axis or distribution of every sum, product,
  mean, max, min, softmax and expectation. The index belongs to its operator.
- **relation signs**: what $=$, $:=$, $\in$, $\approx$, $\propto$, $\leftarrow$
  or $\le$ asserts.
- **superscripts**: whether each one is a power, a transpose or a label.

When a symbol could be read more than one way, check
`../_shared/notation.md`, then settle the reading from the paper's text.

### 5. Name the kind of statement

| Kind                                             | What to check                                                         |
| ------------------------------------------------ | --------------------------------------------------------------------- |
| Computation                                      | The shape of every intermediate result                                |
| Definition                                       | What the new name stands for, so you can substitute it back           |
| Objective (a loss to minimize, a score to maximize) | Which direction, and which data or distribution it averages over   |
| Update rule                                      | What changes at each step and what stays fixed                        |
| Constraint (a set of allowed values)             | How the paper produces a value that satisfies it                      |
| Bound                                            | The gap between the two sides, and when it is zero                    |
| Estimator or metric                              | What is counted, and from how many samples                            |
| Empirical fit                                    | The range of data the curve was fitted on; outside it is extrapolation |

A constraint says what property a result must have; it does not tell you how to
compute it. A definition can name a metric, a loss or a set, so finding $:=$
answers only part of the question.

### 6. Check it with small numbers

- Choose the smallest inputs that use every term. Take at least two items
  wherever there is a sum, a mean or a softmax. Take one case on each side of
  every min, max, clip or indicator.
- Prefer inputs with exact answers. For example, the scores $(0,\log3)$ give
  exponentials 1 and 3.
- Write a short Python check with `assert` statements, using the standard library
  or NumPy, and run it: `uv run --with numpy python check.py`. Paste the code and
  the output you actually got.
- If the paper prints a number or a claimed saving, such as a memory size, a
  parameter count or an exponent identity, recompute it.

### 7. Say where the samples come from

For every expectation or average, state:

- the distribution or dataset it runs over;
- whether that data is fixed before training or generated by the model during
  training, and by which copy of the model ($\theta$ or $\theta_{old}$);
- what is held fixed by a stop-gradient or `.detach()`.

The subscript under $\mathbb E$ answers these questions. Read it.

### 8. List what the code must decide

The equation leaves some choices to the implementation. Common ones:

- the normalization axis;
- whether a standard deviation divides by $n$ or $n-1$ (`np.std` divides by
  $n$, `torch.std` by $n-1$);
- the masking value, and what happens to a row whose keys are all masked;
- numerical stability, such as subtracting the maximum or using log-sum-exp;
- per-token or per-sequence averaging;
- epsilons;
- what is detached.

If an official implementation exists, cite its file and commit for each choice.
Otherwise mark the choice as open.

### 9. Separate claims from evidence

For each claim, say what kind of support the paper gives: a definition, a
derivation, an experiment, or a suspicion. Also note:

- the assumptions behind a derivation, such as independence in a variance
  argument;
- the fitted range of an empirical law;
- which cost a speed claim measures, such as arithmetic, memory or cache reads,
  and in which phase (prefill or decode).

## Output

Write the reading with `references/reading-template.md`. Let the equation decide
the length; leave out sections that have nothing to say rather than padding them.
Link every paper with its version, as in `https://arxiv.org/abs/2402.03300v3`.

## Before you finish

Answer the six questions. If one has no answer, the reading is not done.

1. What does the equation return, and with what shape?
2. Is each symbol data, a trained weight, a frozen model, a setting or a sample?
3. Over which index or axis does each operation run?
4. Where are the definitions?
5. What does a check with two or three numbers give?
6. What did the code have to decide that the equation leaves open?

Then check these:

- [ ] Every quote is verbatim from the pinned version, and every location
      exists in it.
- [ ] Every symbol in the equation is in the table or in the undefined list.
- [ ] Every number came from code you ran, and the output is shown.
- [ ] No claim is stronger than the paper's own wording.
- [ ] Every term is explained before it is used, and every link has a version.

For an independent review, use the `check-paper-math` skill.
