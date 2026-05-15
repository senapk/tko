from tko.run.unit import Unit
from tko.util.label_factory import LabelFactory
from tko.util.param import Param


class WdirManipulationService:
    @staticmethod
    def apply(unit_list: list[Unit], param: Param.Manip) -> list[Unit]:
        # Keep only unique units by input identity marker.
        result = [unit for unit in unit_list if unit.repeated is None]

        if param.to_sort:
            result.sort(key=lambda value: len(value.input))

        if param.unlabel:
            for unit in result:
                unit.case = ""

        if param.to_number:
            number = 0
            for unit in result:
                unit.case = LabelFactory().label(unit.case).index(number).generate()
                number += 1

        return result