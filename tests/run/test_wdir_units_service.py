from pathlib import Path
from typing import Any, cast

import pytest

from tko.run.unit import Unit
from tko.run.wdir_units_service import WdirUnitsService


def test_merge_unique_units_marks_repeated_and_keeps_unique_indexes():
    u1 = Unit(case="a", input_data="1", expected="ok", source=Path("a.tio"))
    u2 = Unit(case="b", input_data="2", expected="ok", source=Path("b.tio"))
    u3 = Unit(case="c", input_data="1", expected="ok", source=Path("c.tio"))

    merged = WdirUnitsService.merge_unique_units([[u1, u2], [u3]])

    assert [u.case for u in merged] == ["a", "b"]
    assert u1.index == 0
    assert u2.index == 1
    assert u3.repeated == 0


def test_calculate_grade_reduction_and_calc_grade_respects_received_output():
    u1 = Unit(case="a", input_data="1", expected="ok")
    u2 = Unit(case="b", input_data="2", expected="ok")
    u3 = Unit(case="c", input_data="1", expected="ok")
    u3.repeated = 0

    units = [u1, u2, u3]
    WdirUnitsService.calculate_grade_reduction(units)

    assert u1.grade_reduction == 33
    assert u2.grade_reduction == 33

    u1.set_received("ok")
    u2.set_received("wrong")

    assert WdirUnitsService.calc_grade(units) == 34


def test_load_packs_filters_empty_units_and_counts_failures(monkeypatch: pytest.MonkeyPatch):
    good_source = Path("good.tio")
    bad_source = Path("bad.tio")

    def _fake_parse_source(source: Path) -> list[Unit]:
        if source == bad_source:
            raise FileNotFoundError("missing")
        return [
            Unit(case="", input_data="", expected="", source=source),
            Unit(case="x", input_data="1", expected="ok", source=source),
        ]

    monkeypatch.setattr("tko.run.wdir_units_service.Loader.parse_source", _fake_parse_source)

    packs, failures = WdirUnitsService.load_packs(cast(Any, [good_source, bad_source]))

    assert failures == 1
    assert len(packs) == 1
    assert len(packs[0]) == 1
    assert packs[0][0].case == "x"
