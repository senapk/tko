from tko.logger.log_item_exec import LogItemExec
from tko.logger.task_listener import TaskListener


def test_task_log_uses_exact_identity() -> None:
    listener: TaskListener = TaskListener()
    for key in ("course@carro", "course@labs/carro", "other@labs/carro"):
        item: LogItemExec = LogItemExec()
        item.key = key
        listener.handle_log_entry(item)

    assert listener.get_task_log("course@carro") is listener.task_dict["course@carro"]
    assert listener.get_task_log("course@labs/carro") is listener.task_dict["course@labs/carro"]
    assert listener.get_task_log("course@plan/carro") is None
    assert listener.get_task_log("other@carro") is None
