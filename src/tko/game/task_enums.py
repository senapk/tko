import enum


class TaskEval(enum.Enum):
    NULL = "null"  # default mode, DO if TEST, READ if USER
    TEST = "test"  # rate uses % of test cases passed
    SELF = "self"  # rate uses user self-evaluation


class TaskLoss(enum.Enum):
    NULL = "null"  # default mode, FREE if READ, PART if DO
    FREE = "free"  # help allowed without penalty
    PART = "part"  # help allowed with partial penalty
    ZERO = "zero"  # if help is given, task is not completed (0% progress)


class TaskType(enum.Enum):
    READ = "read"  # md_file, url, pdf or other resource link, not editable
    MAKE = "make"  # editable task
    NULL = "null"