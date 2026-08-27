# R² Quality Gate

Before committing pricing changes, run:

```bash
python3 scripts/check_r2.py
```

This runs the ML pipeline and compares R² to the saved baseline. If R² drops more than 0.02, the script exits with code 1, indicating you should review your changes.

## Commands

| Flag | Description |
|------|-------------|
| `--baseline 0.85` | Check against a specific baseline value |
| `--save` | Save current R² as the new baseline |
| `--max-drop 0.03` | Customize drop tolerance (default: 0.02) |

## ML Retrain Discipline (Criteria Fingerprint)

ML coefficients must be retrained after EVERY criteria-extraction change; `check_r2.py` fails on fingerprint mismatch.

`scripts/06_ml_refine.py` writes `data/processed/coefficients.json` with a `criteria_fingerprint` — a stable sha256 of the sorted training feature-column list actually used for training plus the criteria CSV's column list (shared helper in `src/ml_fingerprint.py`). After the R² check, `check_r2.py` loads the stored fingerprint and recomputes the current fingerprint from `data/processed/items_criteria.csv` (same helper). Mismatch → it prints `ML coefficients stale: criteria matrix changed since last training — retrain before trusting ML-blended prices` and exits non-zero. Fix: `python3 scripts/06_ml_refine.py` then re-run `check_r2.py`.

## Baseline

The baseline is stored in `data/.r2_baseline`. If no baseline file exists, the default target of 0.80 is used.

## Pre-Commit Hook (Optional)

To run automatically before each commit, add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
if [ -f "scripts/check_r2.py" ]; then
    python3 scripts/check_r2.py
    if [ $? -ne 0 ]; then
        echo "R² quality gate failed. Commit aborted."
        exit 1
    fi
fi
```
