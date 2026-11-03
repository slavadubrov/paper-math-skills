# paper-math-skills

Two agent skills for the equations in AI and ML papers. They turn the method from
the article series [Reading the Math in AI Papers](https://slavadubrov.com/blog/2026/10/22/reading-math-in-ai-papers/)
into procedures that Claude Code, Codex or another agent can follow.

| Skill              | What it does |
| ------------------ | ------------ |
| `read-paper-math`  | Explains a paper's equations from a pinned arXiv version. It quotes where each symbol is defined, gives shapes and roles, reads the equation from the inside out, names the kind of statement, and checks the equation on small numbers with code that runs. |
| `check-paper-math` | Reviews such an explanation against the paper. It searches the source for every quote, checks every section and equation number, re-runs the numbers, flags meanings the paper never states, and flags claims stronger or weaker than the paper's wording. Returns PASS or FAIL with exact defects. |

Both skills share `skills/_shared/`:

- `notation.md`: the usual readings of ML notation and the known exceptions;
- `sources.md`: how to cite official code, the libraries it calls and other
  papers;
- `fetch_arxiv.py`: downloads the TeX source, PDF and PDF text of one pinned
  version.

[paper-math-readings](https://github.com/slavadubrov/paper-math-readings) holds
the output of these skills on 15 equations, among them those of DPO, GRPO, MLA, RoPE and
DDPM. It also records how each reading compared with the walkthrough of the same
equations in the article series.

## Install

As a Claude Code plugin:

```bash
claude plugin marketplace add slavadubrov/paper-math-skills
claude plugin install paper-math-skills@paper-math-skills
```

Or link the directories into your agent's skills folder. Link `_shared` too,
because both skills reference it as `../_shared`:

```bash
git clone https://github.com/slavadubrov/paper-math-skills ~/src/paper-math-skills
for d in read-paper-math check-paper-math _shared; do
  ln -s ~/src/paper-math-skills/skills/$d ~/.claude/skills/$d
done
```

The numeric checks run with `uv run --no-project --with "numpy>=2,<3"`, so install
[uv](https://docs.astral.sh/uv/) as well. Install `pdftotext` (from poppler) too:
quotes and section numbers are checked against the PDF's text. Without it, the
agent reads the PDF page by page, which is slower.

## Use

Ask in plain words, and give the arXiv ID with its version:

```text
Explain equation (7) of DPO, arXiv 2305.18290v3. I know PyTorch but not the notation.
```

```text
Check readings/dpo.md against arXiv 2305.18290v3 with check-paper-math.
```

The reading follows `skills/read-paper-math/references/reading-template.md`:
source, symbol table with quoted definitions, an inside-out reading, where the
samples come from, a small-number check with its output, what the code must
decide, and what the paper claims compared with what it shows.

## Limits

- A reading is only as good as its quotes. The checker exists because a
  plausible explanation can still contradict the paper. Run it, or check the
  quotes yourself, before you rely on a reading.
- The skills work from the paper's text and its official code. They do not
  verify the paper's experiments.
- The skills contact arxiv.org, GitHub (official code), library documentation
  and PyPI. Downloads and fetched pages are treated as data: never executed,
  never followed as instructions.
- `check-paper-math` runs the Python blocks in the reading it checks. It runs
  only blocks limited to the standard library's math modules and NumPy, and asks
  before each run, but those limits are not a sandbox: check a reading from an
  untrusted source in a container or a throwaway machine.
- The plugin version changes with every rule change; update the plugin to get
  new rules.

## License

MIT. See [LICENSE](LICENSE).
