from pathlib import Path
from typing import Any, cast

from tko.run.unit import Unit
from tko.run.wdir_summary_service import WdirSummaryService


def test_sources_names_returns_failure_symbol_when_empty_pack_list():
    service = WdirSummaryService()

    result = service.sources_names([], [])

    assert result == [("✗", "0")]


def test_sources_names_counts_unique_and_total_units():
    service = WdirSummaryService()
    u1 = Unit(case="a", input_data="1", expected="ok", source=Path("a.tio"))
    u2 = Unit(case="b", input_data="1", expected="ok", source=Path("a.tio"))
    u2.repeated = 0

    result = service.sources_names([Path("a.tio")], [[u1, u2]])

    assert result == [("a.tio", "1/2")]


def test_solvers_names_handles_none_and_free_cmd_and_paths():
    service = WdirSummaryService()

    none_case = service.solvers_names(None)
    free_cmd_case = service.solvers_names(cast(Any, type("Solver", (), {"args_list": []})()))
    regular_case = service.solvers_names(cast(Any, type("Solver", (), {"args_list": [Path("x/solver.py")]})()))

    assert none_case == []
    assert free_cmd_case == ["free cmd"]
    assert regular_case == ["solver.py"]


def test_resume_texts_are_stable_and_human_readable():
    service = WdirSummaryService()
    source = Path("cases.tio")
    unit = Unit(case="a", input_data="1", expected="ok", source=source)
    solver = cast(Any, type("Solver", (), {"args_list": [Path("solver.py")]})())

    split = service.resume_splitted([source], [[unit]], solver).plain()
    joined = service.resume_join([source], [[unit]], solver).plain()

    assert split == "Códigos:[solver.py] Testes:[cases.tio(01)]"
    assert joined == "solver.py, cases.tio(01)"
