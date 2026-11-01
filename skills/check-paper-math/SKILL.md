---
name: check-paper-math
version: 0.1.0
license: MIT
description: >-
    Check a written explanation of a paper's equation against the paper itself.
    Verifies every quote and every section, equation or footnote number in the
    pinned arXiv version, re-runs every numeric check, flags symbols given a
    meaning the paper does not state, and marks claims that are stronger than the
    paper's evidence. Use to review or audit an equation walkthrough, a paper
    summary with math, an LLM's reading of an equation, or a blog post that
    explains a paper's formula. Returns PASS or FAIL with exact defects and fixes.
allowed-tools:
    - Read
    - Grep
    - Glob
    - Bash(python3 *)
    - Bash(uv run *)
    - WebFetch
---

# Check paper math

You review a reading of a paper's equation. A reading is any text that explains
a paper's equation, whether written by a person, an LLM, or the `read-paper-math`
skill. Work from the paper, not from the reading. A reading that sounds right is
not evidence. Assume every unchecked statement may be wrong until you have seen
it in the source or reproduced it.

## Inputs

- The reading, as a file or as pasted text.
- The paper, identified by a versioned arXiv ID. If the reading gives no version,
  record that as a defect, then check against the version its locations fit.
- Optional: reference facts, for example from an earlier verified walkthrough.
  Treat them as claims to check, not as truth. They can be wrong too.

## Procedure

1. **Fetch the same version.** Run
   `python3 ../_shared/fetch_arxiv.py <id> <empty-dir>` and search the TeX source
   (`src/*.tex`). If there is no TeX source, use the PDF text and check
   subscripts against the rendered page. Never execute anything from the
   download directory.
2. **Quotes.** Search the source for every quoted definition. Normalize
   whitespace and line breaks, and allow for TeX markup between the words. A
   quote you cannot find is an _unverifiable_ defect, and the row that relies on
   it counts as a guess.
3. **Locations.** Check that every section, equation, footnote, appendix,
   algorithm and figure number points to the right place in that version.
4. **Symbols.** List every symbol that appears in the equation itself. Each one
   must be either in the reading's table with a meaning sourced from the paper,
   or in its "not defined" list. Flag every meaning taken from convention rather
   than from the paper, such as $\sigma$ read as a standard deviation when the
   paper means the sigmoid. Use `../_shared/notation.md` to see which readings
   are possible.
5. **Shapes and axes.** Re-derive the shape of every intermediate result, and the
   index, axis or distribution of every reduction. Flag mismatches and unstated
   row or column conventions.
6. **Numbers.** Run every code block in a scratch directory, using
   `uv run --with numpy python <file>`. Compare the output with the output
   printed in the reading. Then check what the example covers:
   - it uses every term of the equation;
   - it takes both branches of every min, max, clip and indicator;
   - every figure the reading attributes to the paper has been recomputed.
7. **Claims.** For every statement about what the paper does, shows or argues,
   compare its strength with the paper's own wording. Look for:
   - "shows" or "proves" where the paper says "suspects" or "argues";
   - a fitted law used outside its fitted range;
   - a measured cost that is reported as a different cost;
   - a statement about another paper with no source.
8. **Sampling.** For every expectation or average, check the reading's account of
   the data source, the generating model copy and the detached terms against the
   paper's notation and algorithm box.
9. **Clarity for the target reader.** The reader can code but does not know the
   notation. Flag:
   - a term used before it is explained;
   - a step that skips the reason it holds;
   - a sentence that carries no information;
   - a paragraph whose subject the reader cannot name.
10. **Reference facts, if given.** Mark each one _present_, _missing_ or
    _contradicted_. For a contradiction, decide from the source which side is
    right, and say which.

## Report

```markdown
# Check: <reading file> against <arXiv id with version>

**Verdict:** PASS | FAIL

| # | Severity | Passage (quoted) | Problem | Evidence | Fix |
| - | -------- | ---------------- | ------- | -------- | --- |

**Numbers re-run:** <each code block and whether its output matched>

**Reference facts:** <present / missing / contradicted, one line each>
```

Severity is one of these:

- **wrong**: contradicts the source or the arithmetic;
- **unverifiable**: a quote or location you cannot find;
- **missing**: a symbol, a term or a reference fact that the reading leaves out;
- **unclear**: correct, but the target reader cannot follow it.

Give the verdict PASS only when there is no _wrong_ or _unverifiable_ defect, no
_missing_ symbol, and no missing reference fact that changes how the equation is
read. Back every defect with evidence: a quote and its location, or the output of
code. Without evidence, a defect is only an opinion; leave it out.
