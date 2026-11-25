# VLDB artifact coverage

This directory is the code and offline reproduction package for *Where Verification Loses Correct Answers: An Execution Audit of Scientific QA*. Start with `python3 reproduce.py --no-figures`. Add the optional pinned plotting dependencies to regenerate figures. All commands use frozen records.

| Manuscript material | Reproduction in this package |
| --- | --- |
| Main 120-task experiment, request dependencies, usage and paired comparisons | Rescore saved answers against released references, reconstruct SQLite relations, and recompute statistics |
| CURE implementation, agreement and draft retention | Verify saved prompts and replay saved requests through the four-stage implementation in `src/cure_audit/workflow.py` |
| Loss sensitivity and paper figures | Recompute loss masks and generate figures from reconstructed data and the stored schematic |
| Initial test, panel and online repeats | Reaggregate released observations and retain initial-cohort summaries |
| 30-task component study | Recover the 27 jointly scored tasks from 120 episode rows and check matches, calls and mean reported tokens |
| 40-task tool development study | Recompute all-attempt matches, nonreturns and usage, and aggregate released stage, fallback and source-review indicators |
| 24-task tool pilot | Verify all four methods' paired match vectors and recompute usage and accepted strict mismatch counts |

The additional study outputs are `component_summary.csv`, `tool_development_summary.csv`, `tool_pilot_summary.csv`, and `supplementary_studies.json`. The component percentage uses the unrounded means of 41,617.04 and 26,371.37 tokens, giving 36.6% savings to one decimal place.

## Historical source index

The paths below are relative to the original research project's `code/` directory. They document the original inputs and scripts. Reviewers can run the released package independently of that directory.

| Material | Original source |
| --- | --- |
| Initial and extension execution | `scripts/run_icde2027_ledger.py`, `scripts/run_icde2027_extension.py` |
| Components | `outputs/icde2027/next_revision/test/`, `scripts/analyze_icde2027_cure.py` |
| Tool development | `outputs/icde2027/recovery_input_development/`, `scripts/analyze_icde2027_recovery_development.py` |
| Tool pilot | `outputs/icde2027/common_evidence_development/`, `scripts/analyze_icde2027_recent_candidates.py` |

`export_supplementary.py` extracts scalar fields from these saved observations, replaces historical task IDs with cohort-local IDs, and records source hashes. The projected CSVs omit question text, generated answers, provider payloads and retrieved sources for these three supplementary studies. Recomputing their original scoring and document acquisition requires the historical inputs and runtime. Distribution of the original inputs needs a separate rights assessment. See `DATA.md` for data attribution and software rights.
