import enum


class TaskEval(enum.Enum):
    NULL = "null"  # default mode, DO if TEST, READ if USER
    TEST = "test"  # rate uses % of test cases passed
    SELF = "self"  # rate uses user self-evaluation

class TaskType(enum.Enum):
    NULL = "null"
    READ = "read"  # md_file, url, pdf or other resource link, not editable
    MAKE = "make"  # editable task