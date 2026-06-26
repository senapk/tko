from tko.collect.collect_actions import CollectActions
from tko.collect.task_collected import TaskCollected
from tko.config.run_settings import RunSettings
from tko.repository.repository_builder import RepositoryBuilder
from tko.repository.repository_paths import RepositoryPaths

from tko.util.rt import RT
from tko.i18n import Msg

import csv
from pathlib import Path
from typing import Any
from tko.util.console import Console

CMD_COLLECT_REPO_NOT_FOUND = Msg.parse(
    pt="Repositório não encontrado em {path}",
    en="Repository not found in {path}",
)
CMD_COLLECT_TKO_REPO_NOT_FOUND = Msg.parse(
    pt="Repositório TKO não encontrado em {path}",
    en="TKO repo not found in {path}",
)
CMD_COLLECT_MULTIPLE_REPOS_FOUND = Msg.parse(
    pt="[r] - Múltiplos repositórios TKO encontrados, usando o primeiro.[]",
    en="[r] - Multiple TKO repos found, using the first one.[]",
)
CMD_COLLECT_RUNNING_IN = Msg.parse(
    pt="{username: <{padding}} Executando tko collect em {folder}",
    en="{username: <{padding}} Running tko collect in {folder}",
)
CMD_COLLECT_JSON_PARSE_FAILED = Msg.parse(
    pt="Erro: Falha ao analisar saída JSON para {username}",
    en="Error: Failed to parse JSON output for {username}",
)
CMD_COLLECT_ERROR = Msg.parse(
    pt="{username: <{padding}} Erro: {error}",
    en="{username: <{padding}} Error: {error}",
)
CMD_COLLECT_SAVING_EXTRACTED_DATA = Msg.parse(
    pt="[g]Salvando dados extraídos em {path}[]",
    en="[g]Saving extracted data to {path}[]",
)

Resume = dict[str, TaskCollected]

class CollectMany:
    @staticmethod
    def find_common_prefix(folders: list[str]) -> str:
        if not folders:
            return ""
        common = ""
        for chars in zip(*folders):
            if all(c == chars[0] for c in chars):
                common += chars[0]
            else:
                break
        return common


    @staticmethod
    def execute(rs: RunSettings, git_dir_list: list[Path], csv_path: str | None = None):
        git_dir_list = [git_dir for git_dir in git_dir_list if git_dir.is_dir()]
        common_prefix = CollectMany.find_common_prefix([folder.name for folder in git_dir_list])

        usernames = [repo.name[len(common_prefix):].strip("/\\") for repo in git_dir_list]
        padding = max(len(username) for username in usernames) + 1

        output_map: dict[str, Resume] = {}
        for git_dir, username in zip(git_dir_list, usernames):
            tko_rep_folder_list = RepositoryPaths.rec_search_for_repo_subdir(git_dir)
            if not tko_rep_folder_list:
                Console.print(RT(f"{username: <{padding}}", "r") + CMD_COLLECT_TKO_REPO_NOT_FOUND.t().format(path=git_dir).set_style("r"))
                continue
            tko_folder = tko_rep_folder_list[0]
            Console.print(CMD_COLLECT_RUNNING_IN.t().format(folder=tko_folder, username=username, padding=padding))
            if len(tko_rep_folder_list) > 1:
                Console.print(CMD_COLLECT_MULTIPLE_REPOS_FOUND.t())
            rs = RunSettings(changedir=tko_folder)
            rb = RepositoryBuilder(rs)
            repo, _ = rb.verbose(False).load_config_and_game(True).build()
            if repo is None:
                Console.print(RT(f"{username: <{padding}}", "r") + CMD_COLLECT_REPO_NOT_FOUND.t().format(path=tko_folder).set_style("r"))
                continue
            
            output_map[username] = CollectActions.get_resume(repo)

        header_keys = ["username"] +  TaskCollected().csv_keys()
        if csv_path is not None:
            with open(csv_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=header_keys)
                writer.writeheader()
                for student_key, info in output_map.items():
                    for key, data in info.items():
                        if "@" in key:
                            key = key.split("@")[1]

                        row: dict[str, Any] = { "username": student_key }
                        row.update(data.get_kv(include_key=True, include_quest=True))
                        row = {k:v for k,v in row.items() if k in header_keys}
                        writer.writerow(row)
            Console.print(CMD_COLLECT_SAVING_EXTRACTED_DATA.t().format(path=csv_path))