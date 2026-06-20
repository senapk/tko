from loguru import logger
import math
from pathlib import Path

from tko.loader.loader import Loader
from tko.i18n import Msg
from tko.run.unit import Unit




_RUN_PACK_LOAD_FAILED = Msg.text(
    pt="Falha ao carregar pacote de unidades em {source}",
    en="Failed to load unit pack from {source}",
)


class WdirUnitsService:
    @staticmethod
    def load_packs(source_list: list[Path]) -> tuple[list[list[Unit]], int]:
        pack_list: list[list[Unit]] = []
        loading_failures = 0
        for source in source_list:
            try:
                raw_list: list[Unit] = Loader.parse_source(source)
                unit_list: list[Unit] = []
                for unit in raw_list:
                    if unit.get_expected() == "" and unit.get_input() == "":
                        continue
                    unit_list.append(unit)
                pack_list.append(unit_list)
            except FileNotFoundError:
                logger.exception(_RUN_PACK_LOAD_FAILED.t().format(source=source))
                loading_failures += 1
        return pack_list, loading_failures

    @staticmethod
    def merge_unique_units(pack_list: list[list[Unit]]) -> list[Unit]:
        unit_list: list[Unit] = []
        input_dict: dict[str, int] = {}
        index = 0
        for pack in pack_list:
            for unit in pack:
                input_data = unit.get_input()
                if input_data in input_dict:
                    unit.repeated = input_dict[input_data]
                else:
                    input_dict[input_data] = index
                    unit.index = index
                    unit_list.append(unit)
                    index += 1
        return unit_list

    @staticmethod
    def calculate_grade_reduction(unit_list: list[Unit]):
        unique_count = len([item for item in unit_list if not item.repeated])
        for unit in unit_list:
            if unit.grade is None:
                unit.grade_reduction = math.floor(100 / unique_count)
            else:
                unit.grade_reduction = unit.grade

    @staticmethod
    def pad_units(unit_list: list[Unit]):
        if len(unit_list) == 0:
            return
        max_case = max([len(unit.case) for unit in unit_list])
        max_source = max([len(str(unit.source)) for unit in unit_list])
        for unit in unit_list:
            unit.case_pad = max_case
            unit.source_pad = max_source

    @staticmethod
    def calc_grade(unit_list: list[Unit]) -> int:
        grade = 100
        for case in unit_list:
            if not case.repeated and (case.get_received() is None or case.get_expected() != case.get_received()):
                grade -= case.grade_reduction
        return max(0, grade)