from tko.collect.collect_single import CollectSingle
from tko.i18n import t
from tko.repository.repository_paths import RepositoryPaths
from tko.util.rt import RT
from loguru import logger
from tko.i18n import Msg

import csv
import json
from pathlib import Path
from typing import Any

CMD_COLLECT_REPO_NOT_FOUND = Msg(
    pt="Repositório não encontrado em {path}",
    en="Repository not found in {path}",
)
CMD_COLLECT_TKO_REPO_NOT_FOUND = Msg(
    pt="Repositório TKO não encontrado em {path}",
    en="TKO repo not found in {path}",
)
CMD_COLLECT_MULTIPLE_REPOS_FOUND = Msg(
    pt=" - Múltiplos repositórios TKO encontrados, usando o primeiro.",
    en=" - Multiple TKO repos found, using the first one.",
)
CMD_COLLECT_RUNNING_IN = Msg(
    pt="Executando tko collect em {folder}",
    en="Running tko collect in {folder}",
)
CMD_COLLECT_JSON_PARSE_FAILED = Msg(
    pt="Erro: Falha ao analisar saída JSON para {username}",
    en="Error: Failed to parse JSON output for {username}",
)
CMD_COLLECT_ERROR = Msg(
    pt="Erro: {error}",
    en="Error: {error}",
)
CMD_COLLECT_SAVING_EXTRACTED_DATA = Msg(
    pt="Salvando dados extraídos em {path}",
    en="Saving extracted data to {path}",
)


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
    def execute(git_dir_list: list[Path], json_path: str | None = None, csv_path: str | None = None, block_prefix: str | None = None):
        git_dir_list = [git_dir for git_dir in git_dir_list if git_dir.is_dir()]
        common_prefix = CollectMany.find_common_prefix([str(folder.name) for folder in git_dir_list])

        usernames = [repo.name[len(common_prefix):].strip("/\\") for repo in git_dir_list]
        padding = max(len(username) for username in usernames) + 1

        output_map: dict[str, Any] = {}
        for git_dir, username in zip(git_dir_list, usernames):
            tko_rep_folder_list = RepositoryPaths.rec_search_for_repo_subdir(git_dir)
            if not tko_rep_folder_list:
                print(RT(f"{username: <{padding}}", "r") + RT(t(CMD_COLLECT_TKO_REPO_NOT_FOUND, path=git_dir), "r"))
                continue
            tko_folder = tko_rep_folder_list[0]
            multiple_found = RT(t(CMD_COLLECT_MULTIPLE_REPOS_FOUND), "r") if len(tko_rep_folder_list) > 1 else RT()
            print(RT(f"{username: <{padding}}", "y" if multiple_found else "g") + t(CMD_COLLECT_RUNNING_IN, folder=tko_folder) + multiple_found)
            output = CollectSingle.collect_to_json(tko_folder, daily=False, resume=True, game=False)

            try:
                json_output: dict[str, Any] = json.loads(output) if output != "" else {}
            except json.JSONDecodeError:
                logger.exception(t(CMD_COLLECT_JSON_PARSE_FAILED, username=username))
                continue
            if "error" in json_output:
                print(RT(f"{username: <{padding}}", "r") + RT(t(CMD_COLLECT_ERROR, error=json_output['error']), "r"))
                continue

            output_map[username] = json_output["resume"] if "resume" in json_output else {}
        if json_path is not None:
            with open(json_path, "w", encoding="utf-8") as f:
                print(RT(t(CMD_COLLECT_SAVING_EXTRACTED_DATA, path=json_path), "g"))
                json.dump(output_map, f, indent=4, ensure_ascii=False)

        header_keys = ["username", "key", "quest", "minutes", "versions", "executions", "rate", "study", "self", "friend", "concept", "problem", "code", "debug", "refactor", "guided"]
        if block_prefix is not None:
            header_keys = ["block"] + header_keys
        if csv_path is not None:
            with open(csv_path, "w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=header_keys)
                writer.writeheader()
                for student_key, info in output_map.items():
                    for key, data in info.items():
                        if "@" in key:
                            key = key.split("@")[1]

                        row: dict[str, Any] = {
                            "username": student_key,
                            "key": data.get("key", ""),
                            "quest": data.get("quest", ""),
                            "minutes": data.get("minutes", 0),
                            "versions": data.get("versions", 0),
                            "executions": data.get("executions", 0),
                            "rate": round(float(data.get("rate", 0.0))),
                            "study": data.get("study", 0),
                            "self": data.get("self", ""),
                            "friend": data.get("friend", ""),
                            "concept": data.get("concept", ""),
                            "problem": data.get("problem", ""),
                            "code": data.get("code", ""),
                            "debug": data.get("debug", ""),
                            "refactor": data.get("refactor", ""),
                            "guided": data.get("guided", "")
                        }

                        if block_prefix is not None:
                            row["block"]= f"{block_prefix}"
                        writer.writerow(row)
            print(RT(t(CMD_COLLECT_SAVING_EXTRACTED_DATA, path=csv_path), "g"))