# import yaml # type: ignore
# from tko.logger.log_item_base import LogItemBase
# from tko.logger.log_enum_item import LogEnumItem

# class DailyListener:
#     def __init__(self):
#         self.history: dict[str, dict[str, TaskBasic]] = {} # dict[day, dict[key, [key, cov, how]]]
#         self.actual: dict[str, TaskBasic] = {}
#         self.daily_file: str | None
        
#     def listener(self, action: LogItemBase, new_entry: bool = False):
#         if action.get_key() == "":
#             return
#         self.log_task(action.get_timestamp(), action.get_key(), action.get_cov(), action.get_app(), action.get_aut())

#     def set_daily_file(self, daily_file: str):
#         self.daily_file = daily_file
#         return self

#     def log_task(self, timestamp: str, key: str, coverage: int = -1, autonomy: int = -1, skill: int = -1):
#         if key not in self.actual:
#             self.actual[key] = TaskBasic(key)
#         self.actual[key].set_coverage(coverage).set_approach(autonomy).set_autonomy(skill)

#         day = timestamp.split(" ")[0]
#         if day not in self.history:
#             self.history[day] = {}
#         if key not in self.history[day]:
#             self.history[day][key] = self.actual[key]
#         else:
#             self.history[day][key].set_coverage(coverage).set_approach(autonomy).set_autonomy(skill)
#         # self.save_yaml()

#     def __str__(self) -> str:
#         output: dict[str, dict[str, str]] = {}
#         for day in sorted(self.history.keys()):
#             output[day] = {}
#             for key in self.history[day]:
#                 output[day][key] = str(self.history[day][key])
#         return yaml.dump(output)
    
#     def save_yaml(self):
#         if self.daily_file is None:
#             return
#         with open(self.daily_file, 'w') as file:
#             file.write(str(self))
