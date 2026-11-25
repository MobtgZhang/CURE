# CURE: execution audit of scientific question answering

Reproducibility companion for **Where Verification Loses Correct Answers: An Execution Audit of Scientific QA** (PVLDB Volume 20 submission draft).

CURE links saved candidates, terminal outcomes, shared requests, and reported resource use. The public package reconstructs the paper's primary 120-question audit and supporting replay and loss-sensitivity analyses **offline**. It requires no accounts, service credentials, or network access. Generator and panel identities use role aliases G1 and J1–J3; concrete configuration is documented in the manuscript rather than distributed here.

## Quick start

Use Python 3.12 (tested on Linux). Numeric reconstruction has no third-party dependencies:

```bash
python3 reproduce.py --no-figures
python3 -m unittest discover -s tests -v
```

To also generate the manuscript figures and legacy diagnostic plots:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements.txt
python reproduce.py
```

`requirements.txt` pins the plotting versions used in validation. The analysis remains available with the standard library if those versions are unavailable on another platform. Run from any working directory by supplying the absolute path to `reproduce.py`. Optional arguments:

```bash
python reproduce.py --verify-only
python reproduce.py --output results
```

Outputs include `results/REPORT.md`, `verification.json`, an SQLite audit database, CSV tables, the four manuscript PDFs under `results/paper-figures/`, and eight legacy diagnostic figure pairs. `expected/` contains frozen comparison targets, read only after results have been computed from `data/`. Analysis stops on a mismatch; it does not copy comparison targets into results.

## What is reproduced

- All 1,200 terminal episodes and 2,679 candidate rows are independently rescored from the 120 released primary tasks.
- Six SQL audit queries verify outcome partitions, stage reach, selection coverage, shared failures, and logical usage. Seven relations are checked for integrity and foreign-key consistency.
- Exact saved-message replay runs the provider-independent four-stage algorithm on 456 request identities and all 120 CURE tasks. It also evaluates draft retention, agreement routing, and their combination without new generation.
- The nine paired tests and descriptive intervals are checked against the frozen all-attempt comparison table. Shared draft and pool request IDs and completed CURE coverage are independently checked.
- Seven derived tables check the deeper attribution: pairwise return support and missing-score bounds, family repair/loss counts, shared-pool composition and scoring exceptions, request fan-out and retry depth, and stage-specific replay recovery and observed prefix usage. These are computed from the same frozen inputs, without calling a model or changing the scorer.
- The 101 complete primary trajectories are derived from the saved answers and yield 6,464 policy/mask evaluations. Exact rational weights and closed forms check the reported curves.
- Supplementary files retain initial-cohort aggregates and reaggregate saved panel, online, and temporal observations used in the manuscript. The package also verifies 120 component episodes across 30 tasks, 200 tool-development episodes across 40 tasks, and 96 tool-pilot episodes across 24 tasks. These checks use released match indicators and usage. They reconstruct the 27-task common component support, the tool-development fallback counts, and the source-review label totals.

The primary result is **76 delivered reference matches from 93 matching drafts**, with `76 = 93 + 3 - 1 - 6 - 13`. All ten workflows share the fixed input projection; this is not a reproduction of full original benchmark leaderboards or unrestricted original baseline systems.

## Package layout

| Path | Purpose |
| --- | --- |
| `src/cure_audit/workflow.py` | Four-stage CURE with caller-supplied completion/observation functions; no service integration |
| `src/cure_audit/scoring.py` | Frozen strict scorer, public-input whitelist, answer-only routing |
| `src/cure_audit/analysis.py` | Independent reanalysis, replay, SQL reconstruction, numeric checks |
| `src/cure_audit/supplementary.py` | Component and tool-study table regeneration |
| `src/cure_audit/faults.py` | Exact loss-mask enumeration and closed-form cross-checks |
| `src/cure_audit/figures.py` | Framework plus seven data-derived results figures |
| `src/cure_audit/paper_figures.py` | VLDB manuscript figures from reconstructed tables and the preserved schematic |
| `data/primary/` | Normalized primary tasks, requests, messages, outcomes, and observation edges |
| `data/supplementary/` | Scoped supplementary observations and trajectory flags |
| `export_supplementary.py` | Rebuilds component and tool projections when the original research records are available locally |
| `expected/` | Historical comparison targets, kept separate from analysis inputs |
| `sql/` | Relational schema and six executable audit queries |
| `tests/` | Public-input isolation, routing/failure semantics, dependency integrity, tamper detection |
| `MANIFEST.json` | SHA-256 hashes binding source, inputs, tests, and documentation |

Read [Reproducibility](docs/REPRODUCIBILITY.md), [Data and attribution](docs/DATA.md), [Scope](docs/SCOPE.md), [VLDB artifact coverage](docs/VLDB_ARTIFACT.md), and [Authors](AUTHORS.md). `docs/VALIDATION.json` and `docs/TESTS.txt` describe the earlier release. The current archive is self-contained for offline reconstruction.
