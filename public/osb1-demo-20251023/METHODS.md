# OSB-1 Hypothesis + Score — Methods (Minimal)

**What this is:** An *evaluation* service that converts a user’s question into a falsifiable hypothesis with numeric thresholds and returns:
- `hypo.json` — structured hypothesis (verdict/reason/predictions/datasets/thresholds)
- `summary.txt` — plain-English summary
- `score_out.json` — standardized reasoning metrics from a separate scorer

**What it is NOT:** This is *not* peer-reviewed science or a claim of discovery. The “p_value” and “bayes_factor” fields in `hypo.json` are **requested thresholds** for decisive tests, not computed statistical proofs. The scorer’s metrics are **heuristics** for structure and clarity in the reasoning text.

## Pipeline
1. **Question → Hypothesis JSON** via `agent_json` prompt with enforced numeric thresholds.
2. **Summary** — derived directly from `hypo.json`.
3. **Scorer** — converts summary text to JSONL “thought” steps and scores structure (planning/recursion/numeric grounding). This is **separate** from the hypothesis verdict.
4. **Leaderboard** — optional, anonymized aggregation of scored runs.

## Sanity checks
- **Null test:** included here as `null_text.txt` → `null_logs.jsonl` → `null_score.json`. Expect weak/“reject” metrics.
- **Example run:** included here as `hypo.json`, `summary.txt`, and optional `score_out.json`.

## Limitations / Caveats
- No claims without data. Thresholds are targets a scientist could test, not evidence that they were met.
- Bio questions are **high-level only** (no lab or clinical protocols).
- Markets are **evaluation-only** (no trading advice).

## Repro
- All files in this folder are raw artifacts. SHA256 checksums below for integrity.
