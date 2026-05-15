from tko.run.unit import Unit
from tko.run.wdir_manipulation_service import WdirManipulationService
from tko.util.param import Param


def test_apply_filters_repeated_units_first():
    u1 = Unit(case="a", input_data="1", expected="ok")
    u2 = Unit(case="b", input_data="1", expected="ok")
    u2.repeated = 0

    result = WdirManipulationService.apply([u1, u2], Param.Manip())

    assert result == [u1]


def test_apply_sorts_by_input_size_when_requested():
    u1 = Unit(case="a", input_data="111", expected="ok")
    u2 = Unit(case="b", input_data="1", expected="ok")
    param = Param.Manip().set_to_sort(True)

    result = WdirManipulationService.apply([u1, u2], param)

    assert result == [u2, u1]


def test_apply_unlabel_and_number_can_be_combined():
    u1 = Unit(case="10 old", input_data="1", expected="ok")
    u2 = Unit(case="second", input_data="2", expected="ok")
    param = Param.Manip().set_unlabel(True).set_to_number(True)

    result = WdirManipulationService.apply([u1, u2], param)

    assert [unit.case for unit in result] == ["00", "01"]
