# Reading template

Copy this structure and keep every heading, so readings can be compared.

````markdown
# <Paper short name>: <what the equation does, in plain words>

**Source:** <Authors>, [<Title>](https://arxiv.org/abs/<id>v<N>), v<N>,
§<section>, equation(s) (<numbers>). <Other locations used: footnotes,
appendix, algorithm, code files at a tag or commit>.

## What it computes and what it changes

Two to four sentences. First, what the equation produces and why the paper
needs it, in plain words. Second, the earlier equation it changes (name the
location), and the difference: what is stored, computed, sampled or optimized
differently.

## The equation

$$
<the equation exactly as printed, with its number; when the scope covers
several equations, give each one in its own block, in the paper's order>
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
model-generated; which model copy; what is detached. If the equation has no
expectation or sampling, say so in one sentence.>

## Check with small numbers

<One sentence on the chosen inputs and how they cover every term and branch.>

```python
<runnable check with asserts>
```

Output:

```text
<the actual output>
```

<One or two sentences on what the numbers show.>

## What the code must decide

- <choice the equation leaves open>: <what the official code does, with file,
  line range and tag or commit, or "open">

## What the paper claims and what it shows

- <claim>: <defined, derived, measured (which experiment, table or figure), or
  suspected>. <Assumptions or fitted range.>

## Sources

- <every paper, code file or page you opened, versioned>
````
