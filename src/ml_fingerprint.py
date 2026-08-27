"""Shared helper for ML retrain discipline: criteria fingerprint.

Fingerprint is a stable sha256 of the sorted feature-column list actually
used for training plus the criteria CSV's column list. Both scripts
06_ml_refine.py and check_r2.py share this implementation so the hash
computation is identical at write and gate time.
"""
from __future__ import annotations

import csv
import hashlib
from pathlib import Path
from typing import Iterable

COEFFICIENTS_JSON = Path("data/processed/coefficients.json")
CRITERIA_CSV = Path("data/processed/items_criteria.csv")


def compute_fingerprint(
    feature_columns: Iterable[str],
    criteria_columns: Iterable[str],
) -> str:
    """Stable sha256 over sorted feature cols + sorted criteria cols.

    Payload is ``sorted(feature_columns)`` joined by newline, delimiter,
    then ``sorted(criteria_columns)`` joined by newline. Trimming and
    string-coercion is applied so " a " == "a". Returns 64-char hex.
    Whitespace/blank-insensitive by design: entries are stripped and empty
    strings are ignored before hashing.
    """
    sorted_features = sorted(str(c).strip() for c in feature_columns if str(c).strip() != "")
    sorted_criteria = sorted(str(c).strip() for c in criteria_columns if str(c).strip() != "")
    payload = "\n".join(sorted_features) + "\n---\n" + "\n".join(sorted_criteria)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_criteria_columns(path: Path | None = None) -> list[str]:
    """Load criteria column list from the canonical criteria matrix.

    Reads ONLY data/processed/items_criteria.csv (or the explicit ``path``
    if provided). Missing or unreadable file raises a clear exception — no
    silent fallback to unrelated pipeline outputs (e.g. items_variant_adjusted.csv
    or items_priced.csv). Only reads the header row — no pandas required.
    """
    target = Path(path) if path is not None else CRITERIA_CSV
    if not target.exists():
        raise FileNotFoundError(
            f"criteria CSV not found: {target} — run the criteria extraction pipeline to generate {CRITERIA_CSV}"
        )
    try:
        with open(target, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            if header is None:
                raise ValueError(f"criteria CSV is empty: {target}")
            header = [h for h in header if h and str(h).strip() != ""]
            if not header:
                raise ValueError(f"criteria CSV has no columns: {target}")
            return header
    except (FileNotFoundError, ValueError):
        raise
    except OSError as e:
        raise OSError(f"failed to read criteria CSV {target}: {e}") from e
    except Exception as e:
        raise OSError(f"failed to read criteria CSV {target}: {e}") from e


def get_training_feature_columns() -> list[str]:
    """Reconstruct the exact feature set build_features() would produce.

    Lazy-imports FEATURE_COLS / RARITY_DUMMIES / ITEM_TYPE_DUMMIES from
    scripts/06_ml_refine.py so there is a single source of truth. Only the
    documented lazy-import structure is guarded — genuine import errors
    propagate rather than being silently swallowed.

    Fingerprints are whitespace/blank-insensitive by design: feature and
    criteria column names are stripped and empty entries ignored before
    hashing (see compute_fingerprint).
    """
    ml_refine_path = Path("scripts/06_ml_refine.py")
    if not ml_refine_path.exists():
        # try relative to repo root via parent traversal
        ml_refine_path = Path(__file__).resolve().parents[1] / "scripts" / "06_ml_refine.py"
    import importlib.util

    spec = importlib.util.spec_from_file_location("_ml_refine_fingerprint", ml_refine_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load spec for {ml_refine_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[attr-defined]
    feature_cols = list(getattr(mod, "FEATURE_COLS", []))
    rarity_dummies = list(getattr(mod, "RARITY_DUMMIES", []))
    type_dummies = list(getattr(mod, "ITEM_TYPE_DUMMIES", []))
    cols: list[str] = []
    cols.extend(feature_cols)
    cols.extend(f"rarity_{r}" for r in rarity_dummies)
    cols.extend(["attune_open", "attune_class"])
    cols.extend(f"type_{t}" for t in type_dummies)
    cols.append("has_ability_mods")
    return cols


def current_fingerprint(criteria_path: Path | None = None) -> str:
    """Convenience: fingerprint for the current checkout's criteria matrix."""
    feature_cols = get_training_feature_columns()
    criteria_cols = load_criteria_columns(criteria_path)
    return compute_fingerprint(feature_cols, criteria_cols)
