# Reading template

Copy this structure. Keep the headings so readings can be compared. Under any
heading with nothing to say, write one sentence explaining why, rather than
filler.

```markdown
# <Paper short name>: <what the equation does, in plain words>

**Source:** <Authors>, [<Title>](https://arxiv.org/abs/<id>v<N>), v<N>,
§<section>, equation(s) (<numbers>). <Other locations used: footnotes,
appendix, algorithm, code at commit>.

## What it computes and what it changes

Two to four sentences. First, what the equation produces and why the paper
needs it, in plain words. Second, the earlier equation it changes (name the
location), and the difference: what is stored, computed, sampled or optimized
differently.

## The equation

$$
<the equation exactly as printed, with its number>
$$

## Symbols

| Symbol | Shape or type | Meaning | Role | Defined at |
| ------ | ------------- | ------- | ---- | ---------- |
| ...    | ...           | ...     | ...  | "<quote>" (§x.y) |

**Not defined in the paper:** <symbols, and where you looked>. If none, say
"none".

## Read from the inside out

1. <innermost operation: inputs and their shapes → result and its shape; the
   index, axis or distribution it runs over>
2. ...

**Kind of statement:** <computation, definition, objective, update rule,
constraint, bound, estimator or metric, or empirical fit>, and what that means
for this equation.

## Where the samples come from

<For each expectation or average: the distribution or dataset; fixed data or
model-generated; which model copy; what is detached. Write "No expectation or
sampling in this equation" when that is true.>

## Check with small numbers

<One sentence on the chosen inputs and why they exercise every term.>

```python
<runnable check with asserts>
```

Output:

```text
<the actual output>
```

<One or two sentences on what the numbers show.>

## What the code must decide

- <choice the equation leaves open>: <what official code does, with file and
  commit, or "open">

## What the paper claims and what it shows

- <claim>: <defined, derived, measured (which experiment, table or figure), or
  suspected>. <Assumptions or fitted range.>

## The six questions

| Question | Answer |
| -------- | ------ |
| What does the equation return, and with what shape? | ... |
| Is each symbol data, a trained weight, a frozen model, a setting or a sample? | ... |
| Over which index or axis does each operation run? | ... |
| Where are the definitions? | ... |
| What does a check with two or three numbers give? | ... |
| What did the code have to decide that the equation leaves open? | ... |

## Sources

- <every paper, code file or page used, versioned>
```
