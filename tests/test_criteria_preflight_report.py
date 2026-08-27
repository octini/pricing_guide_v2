import json
import importlib.util
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parent.parent / "scripts" / "reports" / "criteria_preflight_2026_07_12.py"
SPEC = importlib.util.spec_from_file_location("criteria_preflight_2026_07_12", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
criteria_preflight = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(criteria_preflight)
run = criteria_preflight.run


def test_run_skips_cleanly_when_raw_file_missing(tmp_path, capsys):
    missing_input = tmp_path / "missing_item_list.json"
    output_path = tmp_path / "criteria_preflight.md"

    exit_code = run(input_path=missing_input, output_path=output_path)

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "Skipping criteria preflight" in captured.out
    assert str(missing_input) in captured.out
    assert not output_path.exists()


def test_run_writes_deterministic_phase_1_report(tmp_path):
    input_path = tmp_path / "items.json"
    output_path = tmp_path / "criteria_preflight.md"
    items = [
        {
            "name": "Test Musket",
            "source": "SRC",
            "type": "R",
            "reload": 1,
            "entries": [],
        },
        {
            "name": "Test Plate Armor",
            "source": "SRC",
            "type": "HA|XPHB",
            "ac": 18,
            "strength": "15",
            "entries": [],
        },
        {
            "name": "Test Shield",
            "source": "SRC",
            "type": "S",
            "ac": 2,
            "entries": [],
        },
        {
            "name": "Test Heavy Pack",
            "source": "SRC",
            "type": "G",
            "strength": "10",
            "entries": [],
        },
        {
            "name": "Null Strength Armor",
            "source": "SRC",
            "type": "HA|XPHB",
            "strength": None,
            "entries": [],
        },
        {
            "name": "Test Wagon",
            "source": "SRC",
            "type": "VEH",
            "vehSpeed": 2,
            "vehAc": 10,
            "vehHp": 40,
            "crew": 1,
            "capCargo": 1000,
            "entries": [],
        },
        {
            "name": "Demon Signet Ring",
            "source": "SRC",
            "entries": [
                "While you wear it, you have advantage on Charisma ({@skill Intimidation}) checks made to influence demons and gnolls."
            ],
        },
        {
            "name": "Cursed Greaves",
            "source": "SRC",
            "entries": [
                "While wearing these greaves, you have disadvantage on Dexterity checks and Wisdom saving throws."
            ],
        },
        {
            "name": "Static Wand",
            "source": "SRC",
            "entries": ["A target must succeed on a DC 15 Dexterity saving throw or fall prone."],
        },
        {
            "name": "Burning Blade",
            "source": "SRC",
            "entries": ["When you hit, the attack deals an extra 1d8 damage."],
        },
    ]
    input_path.write_text(json.dumps(items), encoding="utf-8")

    assert run(input_path=input_path, output_path=output_path) == 0
    first_report = output_path.read_text(encoding="utf-8")

    assert run(input_path=input_path, output_path=output_path) == 0
    assert output_path.read_text(encoding="utf-8") == first_report

    assert "Total items analyzed: 10" in first_report
    assert "| `reload` | 1 |" in first_report
    assert "| raw `ac` | 2 |" in first_report
    assert "| extracted `armor_ac` | 1 |" in first_report
    assert "| raw `strength` | 3 |" in first_report
    assert "| extracted `armor_strength_req` | 1 |" in first_report
    assert "| any `vehicle_*` | 1 |" in first_report
    assert "| extracted `check_advantage` | 1 |" in first_report
    assert "| extracted `check_disadvantage` | 1 |" in first_report
    assert "| extracted `save_disadvantage` | 1 |" in first_report
    assert "| extracted `save_dc` | 1 |" in first_report
    assert "| raw prose extra/additional damage candidates | 1 |" in first_report
    assert "| extracted `extra_damage_avg` | 1 |" in first_report
    assert "- Test Musket (SRC): `reload=1`" in first_report
    assert "- Test Plate Armor (SRC): `armor_ac=18`" in first_report
    assert "- Test Plate Armor (SRC): `armor_strength_req=15`" in first_report
    assert "- Test Wagon (SRC): `vehicle_speed=2, vehicle_ac=10, vehicle_hp=40, vehicle_crew=1, vehicle_cargo_capacity=1000`" in first_report
    assert "- Demon Signet Ring (SRC): `charisma (intimidation)`" in first_report
    assert "- Cursed Greaves (SRC): `dexterity`" in first_report
    assert "- Cursed Greaves (SRC): `wisdom`" in first_report
    assert "- Static Wand (SRC): `save_dc=15`" in first_report
    assert "- Burning Blade (SRC): `extra_damage_avg=4.5, extra_damage_dice=1d8`" in first_report
    assert "{@skill" not in first_report
