from tko.logger.log_item_exec import LogItemExec
from tko.logger.task_listener import TaskListener


def test_task_log_falls_back_from_path_key_to_legacy_folder_key() -> None:
    listener = TaskListener()
    item = LogItemExec().set_key("course@carro")
    listener.handle_log_entry(item)

    assert listener.get_task_log("course@labs/carro") is not None


def test_task_log_falls_back_from_legacy_folder_key_to_path_key() -> None:
    listener = TaskListener()
    item = LogItemExec().set_key("course@labs/carro")
    listener.handle_log_entry(item)

    assert listener.get_task_log("course@carro") is not None
