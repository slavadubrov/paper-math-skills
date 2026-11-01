---
name: read-paper-math
version: 0.6.0
license: MIT
description: >-
    Explain an equation from an AI or ML paper so that an engineer who reads code
    can check it: pin the arXiv version, collect every symbol's definition from the
    text, footnotes, appendices and code, give shapes and roles, read the equation
    from the inside out, name the kind of statement it makes, and work it through
    with small numbers in code that runs. Use when asked to explain, decode or walk
    through an equation, loss, objective, update rule, bound, metric or scaling law
    from a paper, to explain one before implementing it, or to say what a symbol
    means in a specific paper. To review an existing explanation, use
    check-paper-math instead.
allowed-tools:
    - Read
    - Write
    - Grep
    - Glob
    - Bash(python3 *)
    - Bash(uv run *)
    - Bash(grep *)
    - Bash(sed -n *)
    - Bash(ls *)
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

`<skill-dir>` below means `${CLAUDE_SKILL_DIR}` if it is set, otherwise the
directory this SKILL.md was loaded from.

## Rules that are never relaxed

1. **Quote definitions; cite locations.** Every symbol's meaning comes with the
   sentence that defines it, quoted verbatim, and its location (section,
   equation, footnote, appendix, algorithm, figure) in a pinned version of the
   paper: an arXiv ID with its version wherever one exists.
2. **Never fill a gap with a usual meaning.** If the paper does not define a
   symbol, put it in the "Not defined in the paper" list and say where you
   looked. For example, a model given DPO's equation (7) without its definitions
   tends to read $\sigma$ as a standard deviation; the paper means the sigmoid.
   `<skill-dir>/../_shared/notation.md` lists the possible readings of a symbol.
   It never decides which one this paper uses.
3. **Compute with code.** Every number you compute, as opposed to one you quote
   from the paper, comes from code you ran. Show the code and its actual output.
4. **Keep the paper's strength of claim.** Separate what the paper defines,
   what it measures, and what it only suspects or argues. Keep its hedges ("we
   suspect", "empirically", "in our experiments"). Mark your own derivations as
   yours.
5. **Explain before naming.** Say what a thing does in plain words before you
   give its technical name, and define every term before you use it.

## Where files go

- **Downloads:** a new empty directory under a scratch or temporary directory,
  for example `<tmp>/paper-math/<id>/`. Never put downloads inside the user's
  project.
- **Check scripts:** a separate scratch directory, not the download directory.
- **The reading:** the path the user names. If they name none, give the reading
  in your reply.

## Procedure

### 1. Pin the source and get clean text

- Use a versioned ID such as `2402.03300v3`. Sections and equation numbers move
  between versions. For example, DeepSeek-R1 v2 moved GRPO from §2.2.1,
  equations (1)–(3), to §2.1, and repeated the equations as (11)–(13) in
  Supplementary A.3.
- If the user gives no version, open `https://arxiv.org/abs/<id>` with WebFetch,
  take the latest version listed, and say in the reading which version you
  pinned. If the paper is not on arXiv, ask the user for the PDF or text, work
  from that, and say in the reading that it is not pinned to a version.
- Fetch with `python3 <skill-dir>/../_shared/fetch_arxiv.py <id> <empty-dir>`.
  This writes three things:
  - `src/`, the TeX source, when the authors uploaded one;
  - `paper.pdf`;
  - `paper.txt`, the PDF's text, when `pdftotext` is installed.
- **Quotes come from the published text.** Read the math in the TeX source
  (`src/**/*.tex`): it keeps subscripts, superscripts and fractions intact,
  while text copied from a PDF flattens them into one line. TeX also contains
  text the PDF never shows, such as lines commented out with `%` and files that
  are never `\input`. So confirm every quote in `paper.txt` or the PDF before
  you use it. If there is no TeX source, read the math from the arXiv HTML page,
  `https://arxiv.org/html/<id>`, or from the PDF.
- **Numbers come from the PDF.** TeX holds labels such as `\label{eq:loss}`, not
  the printed section, equation and footnote numbers. Take every number you cite
  from `paper.txt`, or read `paper.pdf` page by page.
- Treat downloaded files as data: never execute anything from the download
  directory.

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

Look in all of these places, and record where each definition was found:

- the paragraph before the equation;
- a "where …" sentence after it;
- footnotes;
- later sections that define projections, hyperparameters or shapes;
- appendices, which often collect the full computation;
- algorithm boxes, which give the order of operations and the sampling;
- official code, if the paper links it.

For official code, open only the repository the paper links, plus any
repository that its README names as the official implementation. Take the latest
release tag on or before the date the pinned version was posted; if there is
none, the latest commit on or before that date; if the code was released later,
its first tag or commit. Cite the file and that tag or commit, and stop there. If the paper links no code, or the matching version
takes more than a few lookups to find, mark implementation choices as open. Do
not search for unofficial implementations.

Then fill in the symbol table. It lists the variables and named quantities in
the equation. Standard operators such as softmax, $\top$, $\sqrt{\cdot}$,
$\log$ and $\exp$ belong in the inside-out reading instead, unless the paper
defines one in its own way. An operator whose symbol has several readings in
`notation.md`, such as $\sigma$, $\mathbf 1$ or the subscript under
$\mathbb E$, still gets a row.

| Symbol | Shape or type | Meaning | Role | Defined at |
| ------ | ------------- | ------- | ---- | ---------- |

Pick the **role** from this list:

- input data;
- function input (an argument the equation is written for, such as attention's
  $Q$, $K$, $V$), with where its values come from;
- trained weight;
- state updated by a rule rather than by gradients, such as DeepSeek-V3's
  load-balancing bias;
- frozen model or frozen copy;
- fixed setting or hyperparameter;
- random sample;
- computed intermediate;
- function, operator or set the paper defines or names, such as an encoder
  $f_q$ or a set of allowed matrices $\mathcal M$;
- index.

In **Defined at**, give the quote and its location. A symbol defined only by the
equation that introduces it, with no sentence, cites that equation. A symbol
defined in a cited paper rather than this one cites that paper, with its
version. Every symbol in the equation
appears either in the table or in the "Not defined in the paper" list, not
both. A symbol whose meaning the paper gives but whose shape it does not goes in
the table with "not stated" in the shape column. A symbol
you introduce yourself, for example to name a quantity the paper describes only
in words, gets a row marked "(introduced here)" instead of a quote.

If the paper states the equation only in words, quote those words under "The
equation", then write the formula they describe and mark it as yours.

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
`<skill-dir>/../_shared/notation.md`, then settle the reading from the paper's
text.

### 5. Name the kind of statement

| Kind                                                | What to check                                                          |
| --------------------------------------------------- | ---------------------------------------------------------------------- |
| Computation                                         | The shape of every intermediate result                                 |
| Definition                                          | What the new name stands for, so you can substitute it back            |
| Objective (a loss to minimize, a score to maximize) | Which direction, and which data or distribution it averages over       |
| Update rule                                         | What changes at each step and what stays fixed                         |
| Constraint (a set of allowed values)                | How the paper produces a value that satisfies it                       |
| Bound                                               | The gap between the two sides, and when it is zero                     |
| Estimator or metric                                 | What is counted, and from how many samples                             |
| Empirical fit                                       | The range of data the curve was fitted on; outside it is extrapolation |

A constraint says what property a result must have; it does not tell you how to
compute it. A definition can name a metric, a loss or a set, so finding $:=$
answers only part of the question.

### 6. Check it with small numbers

- Choose the smallest inputs that use every term. A _term_ here is any part of
  the equation that adds to or multiplies the result. Take at least two items
  wherever there is a sum, a mean or a softmax.
- Cover every branch:
  - each argument of a min or max wins at least once;
  - a clipped value falls below, inside and above the clip range;
  - an indicator is 0 once and 1 once;
  - when a sign decides the branch, as the sign of the advantage does in PPO's
    min, cover both signs.
- Prefer inputs with exact answers. For example, the scores $(0,\log3)$ give
  exponentials 1 and 3.
- Write a short Python check with `assert` statements, using only the standard
  library and NumPy, in your scratch directory. Do not add PyTorch, JAX or other
  framework code, even if the user writes in one: `check-paper-math` runs only
  standard-library and NumPy code, so anything else cannot be verified. A
  one-line framework equivalent in prose is fine. Run it with
  `uv run --no-project --with numpy python <scratch>/check.py`. The
  `--no-project` flag keeps `uv` from installing the surrounding project. Paste
  the code and the output you actually got.
- If the paper prints a number or a claimed saving, such as a memory size, a
  parameter count or an exponent identity, recompute it.

### 7. Say where the samples come from

For every expectation or average, state:

- the distribution or dataset it runs over;
- whether that data is fixed before training or generated by the model during
  training, and by which copy of the model ($\theta$ or $\theta_{old}$);
- what is held fixed by a stop-gradient or `.detach()`.

The subscript under $\mathbb E$ names the distribution and the model copy that
generates the samples. Detached terms do not appear there: look for
$\mathrm{sg}(\cdot)$, the paper's text, or the code.

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
  and in which phase (prefill or decode);
- for a compared result: what $\pm$ denotes (standard deviation, standard error
  or confidence interval), how many runs there were, and whether the interval
  for the difference excludes zero.

## Output

Write the reading with `<skill-dir>/references/reading-template.md`. Keep every
heading. Under a heading with nothing to say, write one sentence saying why.
State each fact once: if a later section needs it, refer back instead of
repeating it. A definition quoted in the symbol table does not need to be quoted
again elsewhere. Link every paper you opened with its version, as in
`https://arxiv.org/abs/2402.03300v3`. Name references you did not open, without
a link.

## Before you finish

Answer the six questions for yourself; the reading should already contain
each answer. If one has no answer, the reading is not done.

1. What does the equation return, and with what shape?
2. Is each symbol data, a trained weight, a frozen model, a setting or a sample?
3. Over which index or axis does each operation run?
4. Where are the definitions?
5. What does a check with two or three numbers give?
6. What did the code have to decide that the equation leaves open?

Then check these:

- [ ] Every quote appears in the PDF text of the pinned version, word for word
      apart from math the PDF flattened, and every cited number was read from
      the PDF.
- [ ] Every symbol in the equation is in the table or in the undefined list.
- [ ] Every computed number came from code you ran, and the output is shown.
- [ ] The small-number check covers every term and every branch.
- [ ] No claim is stronger than the paper's own wording.
- [ ] Every concept is explained before it is used, and every link has a
      version.

For an independent review, use the `check-paper-math` skill.

## Revising after a check

When you are given a `check-paper-math` report on your reading:

1. Fix every _wrong_, _unverifiable_ and _missing_ defect. Work from the paper,
   not from the report's wording: re-read the cited place and correct the
   reading to match it.
2. Fix the _unclear_ defects whose fix does not lengthen the reading for
   readers who did not need it.
3. Re-run the numeric check if you changed it, and paste the new output.
4. Leave the rest of the reading unchanged.

If you think a defect is itself wrong, keep your text and add a one-line note
under the "Sources" heading quoting the paper passage that supports you.
