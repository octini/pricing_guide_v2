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
