---
name: check-paper-math
version: 0.7.9
license: MIT
description: >-
    Check a written explanation of a paper's equation against the paper itself.
    Verifies every quote and every section, equation or footnote number in the
    pinned arXiv version, re-runs the numeric checks, flags symbols given a
    meaning the paper does not state, and marks claims that are stronger than the
    paper's evidence. Use to review or audit an equation walkthrough, a paper
    summary with math, or an LLM's reading of an equation. Returns PASS or FAIL
    with exact defects and fixes.
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

# Check paper math

You review a reading of a paper's equation. A reading is any text that explains
a paper's equation, whether written by a person, an LLM, or the `read-paper-math`
skill. Work from the paper, not from the reading. A reading that sounds right is
not evidence. Assume every unchecked statement may be wrong until you have seen
it in the source or reproduced it.

`<skill-dir>` below means `${CLAUDE_SKILL_DIR}` if it is set, otherwise the
directory this SKILL.md was loaded from.

## Inputs

- The reading, as a file or as pasted text.
- The paper, identified by a versioned arXiv ID. If the reading gives no version,
  record a _missing_ defect, then check against the version its locations fit.
  If the paper is not on arXiv, ask the user for the PDF or text and check
  against that.
- Optional: reference facts, for example from an earlier verified walkthrough.
  Treat them as claims to check, not as truth. They can be wrong too.

## Tools

`allowed-tools` lists commands that run without asking for permission; it is
not a limit. Read-only shell commands such as `ls`, `cat`, `grep` and `sed -n`
are fine for reading downloads. To check a figure, render the PDF page, with
`pdftoppm` or by reading `paper.pdf` with page numbers; a figure file from the
TeX source also counts.

## Where files go

Put downloads in a new empty scratch directory, such as
`<tmp>/paper-math/<id>/`, and code you run in a separate scratch directory.
Never write into the user's project except the report, and write the report only
where the user asks.

## Procedure

1. **Fetch the same version.** Run
   `python3 <skill-dir>/../_shared/fetch_arxiv.py <id> <empty-dir>`. Never
   execute anything from the download directory.
2. **Quotes.** Search for every quote in `paper.txt`, which is the
   published text. Before comparing, normalize both sides:
   - collapse whitespace and line breaks;
   - rejoin words split by a line-end hyphen, accepting either form when the
     word may carry a real hyphen, as "pre-trained" does;
   - expand ligatures such as ﬁ and ﬂ;
   - allow for math that the PDF flattened.

   Read the math in `src/**/*.tex`. If there is no TeX source, use
   `https://arxiv.org/html/<id>` or the PDF. TeX contains text the PDF never
   shows, such as `%` comments. If `paper.txt` is missing, read `paper.pdf`
   page by page. A quote found only in a TeX comment, or not at all, is
   _unverifiable_.

   A quote attributed to code is checked against the cited file at the cited
   tag or commit, not against the paper. Code shortened with `…` counts as
   found when each visible part matches; code edited without a mark does not. A quote marked "(figure image)" is
   checked against the rendered page. A quote from another paper is checked
   against that paper, fetched at the version the reading cites.
3. **Numbers in citations.** Check every section, equation, footnote, appendix,
   algorithm and figure number in `paper.txt` or the PDF. The TeX source holds
   labels, not printed numbers, so it cannot confirm them.
4. **Symbols.** List every variable and named quantity in the equation itself.
   Standard operators such as softmax, $\top$ and $\log$ do not need a table row
   unless the paper defines them in its own way. An operator whose symbol has
   several readings in `notation.md`, such as $\sigma$, $\mathbf 1$ or the
   subscript under $\mathbb E$, does need one. Each item must be either in the
   reading's table with a meaning sourced from the paper, or in its "not
   defined" list. Flag every meaning taken from convention rather than from the
   paper, such as $\sigma$ read as a standard deviation when the paper means the
   sigmoid. `<skill-dir>/../_shared/notation.md` shows which readings are
   possible.
5. **Shapes and axes.** Re-derive the shape of every intermediate result, and the
   index, axis or distribution of every reduction. Flag mismatches and unstated
   row or column conventions.
6. **Numbers.** Read each fenced code block before you run it; inline code in
   prose is not a code block. Run a block only if it
   uses nothing but the standard library and NumPy, and touches no files and no
   network; mark any other block _unverifiable_. Copy each runnable block into
   your scratch directory and run it with
   `uv run --no-project --with numpy python <file>`. Compare the output with the
   output printed in the reading. Then check what the example covers:
   - every term: every part of the equation that adds to or multiplies the
     result;
   - every branch the equation itself defines: each argument of a min or max
     wins at least once; a clipped value falls below, inside and above its
     range; an indicator is 0 once and 1 once; when a sign decides the branch,
     both signs appear. A split the paper describes without a rule is not a
     branch;
   - the reading's own code recomputes every number that the reading attributes
     to the paper and that follows from the paper's formulas, such as a
     parameter count or a memory size. Measured results, such as a benchmark
     score, are checked as quotes instead.
7. **Claims.** For every statement about what the paper does, shows or argues,
   compare its strength with the paper's own wording. Look for:
   - "shows" or "proves" where the paper says "suspects" or "argues", and the
     reverse: a hedge the paper does not make;
   - a fitted law used outside its fitted range as if it were a prediction;
   - a measured cost that is reported as a different cost or phase;
   - a compared result whose $\pm$ is read as the wrong quantity (standard
     deviation, standard error or confidence interval), or a difference called
     real when its interval contains zero;
   - a statement about another paper or about a library's behaviour with no
     source;
   - a claim that the paper never mentions or specifies something: search the
     whole paper, footnotes and appendices included, before accepting it.
8. **Sampling.** For every expectation or average, check the reading's account of
   the data source, the generating model copy and the detached terms against the
   paper's notation, text and algorithm box.
9. **Clarity for the target reader.** The reader can code but does not know the
   notation. Flag:
   - a term used before it is explained;
   - a step that skips the reason it holds;
   - a sentence that carries no information;
   - a fact repeated in several sections;
   - a paragraph whose subject the reader cannot name.
10. **Reference facts, if given.** Mark each one _present_, _missing_ or
    _contradicted_. A fact counts as present when the reading establishes the
    same point, even with a different example or different numbers. A fact the
    reading covers only in part is _missing_; say which part is absent. A
    reading that gives the right formula but explains it wrongly
    _contradicts_ the fact. For a contradiction, decide from the source which side is
    right, and say which.

## Severity

Give every defect exactly one severity.

| Severity       | Use it for |
| -------------- | ---------- |
| _wrong_        | contradicts the source, the arithmetic or another part of the reading; a word that misstates a computed number, such as "roughly unchanged" for a 2.6-fold change; output that differs from the printed output; a claim stronger or weaker than the paper's wording; an extrapolated fit presented as a prediction; a misread $\pm$ |
| _unverifiable_ | a quote or cited number you cannot find in the published text; a code block you could not or would not run; a statement about another paper or a library's behaviour with no source |
| _missing_      | a missing paper version; a symbol absent from both the table and the undefined list; a term or branch the numeric check does not cover; a derived number from the paper that was not recomputed; a reference fact the reading omits or covers only in part |
| _unclear_      | correct, but the target reader cannot follow it |

## Verdict

PASS only when all three hold:

- there is no _wrong_ and no _unverifiable_ defect;
- there is no _missing_ version, symbol, term, branch or recomputation;
- no reference fact marked essential is missing or contradicted (unless the
  source shows the reference fact is wrong).

_Unclear_ defects and missing non-essential facts do not block PASS. List them
anyway, so they can be fixed: unclear defects in the table, missing facts in the
"Reference facts" line. If the reading cites page numbers, check them too.

## Report

```markdown
# Check: <reading file> against <arXiv id with version>

**Verdict:** PASS | FAIL

| # | Severity | Passage (quoted) | Problem | Evidence | Fix |
| - | -------- | ---------------- | ------- | -------- | --- |

**Numbers re-run:** <each code block and whether its output matched>

**Reference facts:** <present / missing / contradicted, one line each>
```

Every defect needs evidence:

- for _wrong_, _unverifiable_ and _missing_: a quote and its location in the
  paper, or the output of code;
- for _unclear_: the passage, plus the term or step the reader lacks.

Leave out any defect you cannot support with evidence.
