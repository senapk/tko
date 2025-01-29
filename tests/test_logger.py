# import unittest
# from datetime import datetime
# from unittest.mock import MagicMock
# from tko.util.logger import Logger, LoggerMemory, ActionData.Type, ActionData

# class TestLogger(unittest.TestCase):

#     def setUp(self):
#         self.logger_store = LoggerMemory()
#         self.logger = Logger(self.logger_store)
#         self.logger.set_history_file("test_rep")


#     def test_record_event(self):
#         self.logger.record_other_event(ActionData.Type.OPEN, "task1", "payload1")
#         entries = self.logger_store.get_action_entries()
#         self.assertEqual(len(entries), 1)
#         self.assertEqual(entries[0].action_value, ActionData.Type.OPEN.value)
#         self.assertEqual(entries[0].task_key, "task1")
#         self.assertEqual(entries[0].payload, "payload1")

#     def test_get_last_hash(self):
#         self.logger.record_other_event(ActionData.Type.OPEN, "task1", "payload1")
#         last_hash = self.logger.get_last_hash()
#         self.assertEqual(last_hash, self.logger_store.entries[0].hash)

#     def test_check_log_file_integrity(self):
#         self.logger.record_other_event(ActionData.Type.OPEN, "task1", "payload1")
#         self.logger.record_other_event(ActionData.Type.QUIT, "task2", "payload2")
#         integrity_issues = self.logger.check_log_file_integrity()
#         self.assertEqual(len(integrity_issues), 0)

#     def test_store_in_cached(self):
#         action_data = ActionData(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), ActionData.Type.SELF.value, "task1", "payload1")
#         self.assertTrue(self.logger.store_in_cached(action_data))
#         self.logger.cached_action = action_data
#         self.assertTrue(self.logger.store_in_cached(action_data))

#     def test_record_action_data(self):
#         action_data = ActionData("um", ActionData.Type.SELF.value, "task1", "payload1")
#         self.logger.record_action_data(action_data)
#         action_data = ActionData("dois", ActionData.Type.SELF.value, "task1", "payload2")
#         self.logger.record_action_data(action_data)
#         self.assertEqual(len(self.logger_store.entries), 0)
#         action_data = ActionData("tres", ActionData.Type.SELF.value, "task2", "payload1")
#         self.logger.record_action_data(action_data)
#         self.assertEqual(len(self.logger_store.entries), 1)
#         action_data = ActionData("quatro", ActionData.Type.QUIT.value, "test_rep")
#         self.logger.record_action_data(action_data)
#         self.assertEqual(len(self.logger_store.entries), 3)
#         self.assertEqual(self.logger_store.entries[0].task_key, "task1")
#         self.assertEqual(self.logger_store.entries[1].task_key, "task2")
#         self.assertEqual(self.logger_store.entries[2].action_value, ActionData.Type.QUIT.value)

#     def test_check_log_file_integrity2(self):
#         self.logger.record_other_event(ActionData.Type.OPEN, "task1", "payload1")
#         self.logger.record_other_event(ActionData.Type.QUIT, "task2", "payload2")
#         self.logger.record_other_event(ActionData.Type.QUIT, "task3", "payload3")
#         integrity_issues = self.logger.check_log_file_integrity()
#         self.assertEqual(len(integrity_issues), 0)
#         self.logger_store.entries[1].hash = "wrong_hash"
#         integrity_issues = self.logger.check_log_file_integrity()
#         self.assertEqual(len(integrity_issues), 1)

# if __name__ == '__main__':
#     unittest.main()