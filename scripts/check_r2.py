#!/usr/bin/env python3
"""
Pre-commit R² quality gate for pricing pipeline.

Usage:
    python3 scripts/check_r2.py --baseline 0.85  # Check against baseline
    python3 scripts/check_r2.py --save           # Save current R² as baseline

Returns exit code 1 if R² drops more than 0.02 from baseline.
"""

import argparse
import subprocess
import sys
import re
from pathlib import Path

BASELINE_FILE = Path("data/.r2_baseline")
DEFAULT_BASELINE = 0.80
MAX_DROP = 0.02


def run_ml_pipeline():
    """Run ML refinement script and capture R² from output."""
    result = subprocess.run(
        ["python3", "scripts/06_ml_refine.py"],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        print(f"❌ Pipeline failed:\n{result.stderr}")
        return None

    # Parse R² from output
    # Looking for: "Final blended R² (log-space): 0.8532"
    match = re.search(r"Final blended R².*?:\s*([\d.]+)", result.stdout)
    if not match:
        print("❌ Could not parse R² from pipeline output")
        print(f"Pipeline output:\n{result.stdout[-500:]}")
        return None

    return float(match.group(1))


def load_baseline():
    """Load baseline R² from file or use default."""
    if BASELINE_FILE.exists():
        return float(BASELINE_FILE.read_text().strip())
    return DEFAULT_BASELINE


def save_baseline(r2):
    """Save current R² as baseline."""
    BASELINE_FILE.parent.mkdir(parents=True, exist_ok=True)
    BASELINE_FILE.write_text(f"{r2:.4f}\n")
    print(f"✅ Baseline saved: {r2:.4f}")


def main():
    parser = argparse.ArgumentParser(description="R² quality gate for pricing pipeline")
    parser.add_argument("--baseline", type=float, help="Set baseline R² value")
    parser.add_argument("--save", action="store_true", help="Save current R² as baseline")
    parser.add_argument(
        "--max-drop",
        type=float,
        default=MAX_DROP,
        help=f"Maximum allowed R² drop (default: {MAX_DROP})",
    )

    args = parser.parse_args()

    print("🔄 Running ML pipeline...")
    r2 = run_ml_pipeline()

    if r2 is None:
        sys.exit(1)

    print(f"📊 Current R²: {r2:.4f}")

    if args.save:
        save_baseline(r2)
        sys.exit(0)

    if args.baseline:
        baseline = args.baseline
    else:
        baseline = load_baseline()

    print(f"📏 Baseline R²: {baseline:.4f}")

    drop = baseline - r2

    if drop > args.max_drop:
        print(f"❌ R² dropped by {drop:.4f} (max allowed: {args.max_drop})")
        print("⚠️  Review changes before committing!")
        sys.exit(1)
    elif drop > 0:
        print(f"⚠️  R² dropped by {drop:.4f} (within tolerance)")
    else:
        print(f"✅ R² improved by {abs(drop):.4f}")

    if r2 < DEFAULT_BASELINE:
        print(f"⚠️  Warning: R² below target ({DEFAULT_BASELINE})")

    sys.exit(0)


if __name__ == "__main__":
    main()
