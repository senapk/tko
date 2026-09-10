from __future__ import annotations
from loguru import logger
import re
from tko.i18n import Msg

DEFAULT_DIRECTORY_PATTERN = "@.in @.sol"



_PATTERN_WILDCARD_ONLY_ONCE = Msg.text(
    pt="  fail: o curinga @ deve ser usado apenas uma vez por padrão",
    en="  fail: the wildcard @ should be used only once per pattern",
)
_PATTERN_INPUT_WILDCARD_REQUIRES_OUTPUT = Msg.text(
    pt="  fail: se input_pattern tem o curinga @, output_pattern deve ter também",
    en="  fail: if input_pattern has wildcard @, output_pattern should have it too",
)
_PATTERN_OUTPUT_WILDCARD_REQUIRES_INPUT = Msg.text(
    pt="  fail: se output_pattern tem o curinga @, input_pattern deve ter também",
    en="  fail: if output_pattern has wildcard @, input_pattern should have it too",
)
_PATTERN_OUTPUT_FILE_NOT_FOUND = Msg.text(
    pt="fail: arquivo {file} não encontrado",
    en="fail: file {file} not found",
)
_PATTERN_INVALID_FORMAT = Msg.text(
    pt="  fail: o padrão deve conter exatamente os nomes de entrada e saída",
    en="  fail: the pattern must contain exactly input and output filenames",
)


class FileSource:
    def __init__(self, label: str, input_file: str, output_file: str):
        self.label = label
        self.input_file = input_file
        self.output_file = output_file

    def __eq__(self, other: FileSource) -> bool: # type: ignore
        return self.label == other.label and self.input_file == other.input_file and \
                self.output_file == other.output_file


class PatternLoader:
    def __init__(self, pattern: str = DEFAULT_DIRECTORY_PATTERN):
        parts = pattern.split()
        if len(parts) != 2:
            raise ValueError(_PATTERN_INVALID_FORMAT.t().plain())
        self.input_pattern, self.output_pattern = parts
        self._check_pattern()

    def _check_pattern(self):
        self.__check_double_wildcard()
        self.__check_missing_wildcard()

    def __check_double_wildcard(self):
        if self.input_pattern.count("@") > 1 or self.output_pattern.count("@") > 1:
            raise ValueError(_PATTERN_WILDCARD_ONLY_ONCE.t().plain())

    def __check_missing_wildcard(self):
        if "@" in self.input_pattern and "@" not in self.output_pattern:
            raise ValueError(_PATTERN_INPUT_WILDCARD_REQUIRES_OUTPUT.t().plain())
        if "@" not in self.input_pattern and "@" in self.output_pattern:
            raise ValueError(_PATTERN_OUTPUT_WILDCARD_REQUIRES_INPUT.t().plain())

    def make_file_source(self, label: str) -> FileSource:
        return FileSource(label, self.input_pattern.replace("@", label), self.output_pattern.replace("@", label))

    def get_file_sources(self, filename_list: list[str]) -> list[FileSource]:
        input_re = re.escape(self.input_pattern).replace("@", "(.+?)")
        file_source_list: list[FileSource] = []
        for filename in filename_list:
            match = re.fullmatch(input_re, filename)
            if not match:
                continue
            label = match.group(1) if "@" in self.input_pattern else ""
            file_source = self.make_file_source(label)
            if file_source.output_file not in filename_list:
                logger.error(_PATTERN_OUTPUT_FILE_NOT_FOUND.t().format(file=file_source.output_file))
            else:
                file_source_list.append(file_source)
        return file_source_list

    def get_odd_files(self, filename_list: list[str]) -> list[str]:
        matched: list[str] = []
        sources: list[FileSource] = self.get_file_sources(filename_list)
        for source in sources:
            matched.append(source.input_file)
            matched.append(source.output_file)
        unmatched = [file for file in filename_list if file not in matched]
        return unmatched
