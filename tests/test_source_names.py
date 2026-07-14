from __future__ import annotations

import importlib.util
import csv
import subprocess
import sys
import textwrap
from pathlib import Path

from src.source_names import translate_source


REPO_ROOT = Path(__file__).resolve().parents[1]
CURRENT_PIPELINE_INPUT = REPO_ROOT / "data" / "processed" / "items_validated.csv"
CURRENT_PIPELINE_OUTPUT = REPO_ROOT / "output" / "pricing_guide.csv"

KNOWN_GOOD_LOCAL_SOURCE_NAMES = {
    "MonstersOfDrakkenheim": "Monsters of Drakkenheim",
    "DungeonsDrakkenheim": "Dungeons of Drakkenheim",
    "ExploringEberron24": "Exploring Eberron (2024)",
    "ChroniclesOfEberron": "Chronicles of Eberron",
    "FoEQuickstone": "Frontiers of Eberron: Quickstone",
    "SAT": "Sigil and the Outlands",
}


def load_script_module(script_name: str):
    script_path = REPO_ROOT / "scripts" / script_name
    spec = importlib.util.spec_from_file_location(script_name.removesuffix(".py"), script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_translate_source_uses_reference_map_for_wtthc_and_rmbre():
    assert translate_source("WttHC") == "Stranger Things: Welcome to the Hellfire Club"
    assert translate_source("RMBRE") == "The Lost Dungeon of Rickedness: Big Rick Energy"


def test_translate_source_falls_back_to_source_code_for_unknown_values():
    assert translate_source("DefinitelyNotARealSource") == "DefinitelyNotARealSource"


def test_translate_source_preserves_known_good_local_supplements():
    for source_code, display_name in KNOWN_GOOD_LOCAL_SOURCE_NAMES.items():
        assert translate_source(source_code) == display_name


def test_translate_source_translates_pipe_separated_source_codes():
    assert translate_source("WttHC|RMBRE") == (
        "Stranger Things: Welcome to the Hellfire Club, "
        "The Lost Dungeon of Rickedness: Big Rick Energy"
    )


def test_output_and_html_scripts_share_central_source_helper():
    output_module = load_script_module("10_generate_output.py")
    html_module = load_script_module("11_generate_html.py")

    assert output_module.translate_source is translate_source
    assert html_module.translate_source is translate_source


def test_output_scripts_import_when_sys_path_starts_at_scripts_dir():
    smoke_code = textwrap.dedent(
        f"""
        import runpy
        import sys
        from pathlib import Path

        repo_root = Path({str(REPO_ROOT)!r}).resolve()
        scripts_dir = repo_root / "scripts"
        excluded = {{repo_root, scripts_dir}}

        filtered_path = []
        for path_entry in sys.path:
            if not path_entry:
                continue
            resolved_entry = Path(path_entry).resolve()
            if resolved_entry in excluded:
                continue
            filtered_path.append(path_entry)

        sys.path = [str(scripts_dir), *filtered_path]

        runpy.run_path(str(scripts_dir / "10_generate_output.py"), run_name="source_name_import_smoke")
        runpy.run_path(str(scripts_dir / "11_generate_html.py"), run_name="source_name_import_smoke")
        """
    )

    result = subprocess.run(
        [sys.executable, "-c", smoke_code],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr


def test_current_pipeline_sources_keep_known_good_display_names_from_current_output():
    with CURRENT_PIPELINE_INPUT.open(newline="", encoding="utf-8") as input_file:
        current_source_codes = {
            source.strip()
            for row in csv.DictReader(input_file)
            for source in str(row.get("source", "")).split("|")
            if source.strip()
        }

    with CURRENT_PIPELINE_OUTPUT.open(newline="", encoding="utf-8") as output_file:
        current_output_display_names = {
            row["Source"] for row in csv.DictReader(output_file) if row.get("Source")
        }

    covered_known_good_sources = {
        source_code: display_name
        for source_code, display_name in KNOWN_GOOD_LOCAL_SOURCE_NAMES.items()
        if source_code in current_source_codes
    }

    assert covered_known_good_sources
    for source_code, display_name in covered_known_good_sources.items():
        assert display_name in current_output_display_names
        assert translate_source(source_code) == display_name
        assert translate_source(source_code) != source_code
