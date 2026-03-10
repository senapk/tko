from tko.down.drafts import Drafts
from tko.game.quest_parser import QuestParser
from tko.game.task_parser import TaskParser
from tko.game.cluster import Cluster
from tko.game.quest import Quest
from tko.game.task import Task
from tko.util.get_md_link import get_md_link
from tko.util.to_asc import uni_to_asc
from tko.settings.rep_source import RepSource
from tko.util.decoder import Decoder
import os
from icecream import ic # type: ignore

class GameBuilder:
    def __init__(self, source: RepSource):
        self.source = source
        self.ordered_clusters: list[str] = [] # ordered clusters
        self.clusters: dict[str, Cluster] = {}
        self.active_cluster: Cluster | None = None
        self.active_quest: Quest | None = None
        self.unique_keys: set[str] = set()

    def build_from(self, language: str):
        filename = self.source.get_source_readme()
        content: str = ""
        if filename == "":
            pass
        elif not os.path.exists(filename):
            print(f"Aviso: fonte {filename} não encontrada no source {self.source.name}")
        else:
            content = Decoder.load(filename)
        self.__parse_file_content(content)
        self.__clear_empty_or_other_language(language)
        self.__create_requirements_pointers()
        self.__create_cross_references()
        return self


    def collect_tasks(self) -> dict[str, Task]:
        tasks: dict[str, Task] = {}
        for cluster in self.clusters.values():
            for quest in cluster.get_quests():
                for task in quest.get_tasks():
                    tasks[task.get_db_key()] = task
        return tasks

    def collect_quests(self) -> dict[str, Quest]:
        quests: dict[str, Quest] = {}
        for cluster in self.clusters.values():
            for quest in cluster.get_quests():
                quests[quest.get_db_key()] = quest
        return quests

    def __create_requirements_pointers(self):
        quests, tasks = self.source.get_filters()
        if quests is not None or tasks is not None:
            return

        filename: str = self.source.get_source_readme()
        quests = self.collect_quests()
        # verificar se todas as quests requeridas existem e adicionar o ponteiro
        for q in quests.values():
            for r in q.requires:
                if r in quests:
                    q.requires_ptr.append(quests[r])
                else:
                    # print(f"keys: {self.quests.keys()}")
                    print(f"Quest\n{filename}:{q.line_number}\n{str(q)}\nrequer {r} que não existe")
                    exit(1)

    @staticmethod
    # extract yaml keys in front matter format and return as dict, also return content without yaml front matter
    def extract_yaml_keys_and_file_data(content: str) -> tuple[dict[str, str], str]:
        yaml_keys: dict[str, str] = {}
        lines = content.splitlines()
        if len(lines) > 0 and lines[0].strip() == "---":
            for line in lines[1:]:
                if line.strip() == "---":
                    break
                if ":" in line:
                    key, val = line.split(":", 1)
                    yaml_keys[key.strip()] = val.strip()
                if "=" in line:
                    key, val = line.split("=", 1)
                    yaml_keys[key.strip()] = val.strip()
            content = "\n".join(lines[len(yaml_keys) + 2:])
        return yaml_keys, content

    def __parse_quest_folder(self, task_dir_path: str, tasks_with_missing_keys: list[str]):
        database_path = task_dir_path
        alias = self.source.name
        if not os.path.exists(database_path):
            os.makedirs(database_path)
        for task_dirname in sorted(os.listdir(database_path)):
            task_dir_path = os.path.join(database_path, task_dirname)
            if not os.path.isdir(task_dir_path):
                continue
            if not os.path.isfile(os.path.join(task_dir_path, "README.md")):
                continue
            # parse readme content for yaml front matter with key
            yaml_keys, _ = self.extract_yaml_keys_and_file_data(Decoder.load(os.path.join(task_dir_path, "README.md")))
            if "key" not in yaml_keys or yaml_keys["key"] in self.unique_keys:
                tasks_with_missing_keys.append(task_dir_path)
                # print(f"Readme {task_dir_path}/README.md não possui chave yaml única, será ignorado")
            else:
                self.unique_keys.add(yaml_keys["key"])
                self.create_task_from_folder(alias, yaml_keys["key"], task_dirname, task_dir_path)

    def create_task_from_folder(self, alias: str, yaml_key: str, task_dirname: str, task_dir_path: str):
        task = Task()
        title = task_dirname
        title = f"@{yaml_key} {task_dirname}"
        task.set_key(yaml_key)
        task.set_title(title)
        task.set_alias(alias)
        task.set_origin_folder(task_dir_path)
        if self.source.is_read_only():
            task.set_workspace_folder(self.source.get_task_workspace(yaml_key))
        self.__add_task(task)

    def __parse_cluster_folder(self, folder: str):
        alias = self.source.name
        if not os.path.exists(folder):
            return
        tasks_with_missing_keys: list[str] = []
        for entry in sorted(os.listdir(folder)):
            quest_folder = os.path.join(folder, entry)
            if not os.path.isdir(quest_folder):
                continue
            cluster_key = self.__get_active_cluster().get_key_only()
            self.__add_quest(Quest(entry, f"{cluster_key}:{entry}").set_alias(alias))
            self.__parse_quest_folder(quest_folder, tasks_with_missing_keys)
        if len(tasks_with_missing_keys) > 0:
            print(f"Os seguintes diretórios de tarefas não possuem chave yaml única e foram ignorados:")
            for path in tasks_with_missing_keys:
                print(f"  {path}")
            print("Você deseja gerar chaves únicas para essas tarefas? (s/n): ", end="")
            answer = input().strip().lower()
            if answer == "s":
                max_number = Drafts.find_max_numbered_key(list(self.unique_keys))
                for path in tasks_with_missing_keys:
                    max_number += 1
                    yaml_key = Drafts.create_draft_key(max_number)
                    yaml_keys, info = self.extract_yaml_keys_and_file_data(Decoder.load(os.path.join(path, "README.md")))
                    yaml_keys["key"] = yaml_key
                    new_content = "---\n"
                    for k, v in yaml_keys.items():
                        new_content += f"{k}: {v}\n"
                    new_content += "---\n\n" + info
                    with open(os.path.join(path, "README.md"), "w", encoding="utf-8") as f:
                        f.write(new_content)
                    self.create_task_from_folder(alias, yaml_key, os.path.basename(path), path)



    def __is_autoload_quest_cmd(self, line: str) -> tuple[bool, str]:
        words = line.split(f"{self.source.AUTOLOAD_QUEST_COMMAND}=")
        if len(words) == 2:
            path = words[1].strip("-> ")
            readme_folder = os.path.dirname(self.source.get_source_readme())
            folder = os.path.join(readme_folder, path)
            return True, folder
        return False, ""
    
    def __is_autoload_cluster_cmd(self, line: str) -> tuple[bool, str]:
        words = line.split(f"{self.source.AUTOLOAD_CLUSTER_COMMAND}=")
        if len(words) == 2:
            path = words[1].strip("-> ")
            readme_folder = os.path.dirname(self.source.get_source_readme())
            folder = os.path.join(readme_folder, path)
            folder = os.path.abspath(folder)
            return True, folder
        return False, ""


    def __parse_file_content(self, content: str):
        lines = content.splitlines()
        alias = self.source.name
        filename = self.source.get_source_readme()
        for line_num, line in enumerate(lines):
            autoload, quest_folder = self.__is_autoload_quest_cmd(line)
            if autoload:
                self.__parse_quest_folder(quest_folder, [])
                continue

            autoload, cluster_folder = self.__is_autoload_cluster_cmd(line)
            if autoload:
                self.__parse_cluster_folder(cluster_folder)
                continue

            cluster = self.__load_cluster(line, line_num)
            if cluster is not None:
                self.__add_cluster(cluster)
                continue
            quest = QuestParser(alias).parse_quest(filename, line, line_num + 1)
            if quest is not None:
                self.__add_quest(quest)
                continue

            tp = TaskParser(filename, alias)
            task = tp.parse_line(line, line_num + 1).check_path_try().get_task()
            if task is not None:
                if self.source.is_read_only() and not task.is_link():
                    task.set_workspace_folder(self.source.get_task_workspace(task.get_key_only()))
                self.__add_task(task)

    def __get_active_cluster(self) -> Cluster:
        if self.active_cluster is None:
            ckey = "sem_cluster"
            return self.__add_cluster(Cluster(0, "Sem Cluster", ckey))
        return self.active_cluster

    def __get_active_quest(self) -> Quest:
        if self.active_quest is None:
            qkey = self.__get_active_cluster().get_db_key() + "_sem_quest"
            return self.__add_quest(Quest("Sem Quest", qkey))
        return self.active_quest

    def __add_cluster(self, cluster: Cluster) -> Cluster:
        self.clusters[cluster.get_db_key()] = cluster
        if not cluster.get_db_key() in self.ordered_clusters:
            self.ordered_clusters.append(cluster.get_db_key())
        self.active_cluster = cluster
        self.active_quest = None
        return cluster

    def __add_quest(self, quest: Quest) -> Quest:
        self.__get_active_cluster().add_quest(quest)
        self.active_quest = quest
        return quest

    def __add_task(self, task: Task):
        self.__get_active_quest().add_task(task)

    # se existir um cluster nessa linha, insere na lista de clusters e 
    # retorno o objeto cluster inserido
    def __load_cluster(self, line: str, line_num: int) -> None | Cluster:
        if not line.startswith("## "):
            return None
        line = line[3:]

        titulo = line
        tags_raw = ""
        if "<!--" in line:
            pieces = line.split("<!--")
            titulo = pieces[0]
            middle_end = pieces[1].split("-->")
            tags_raw = middle_end[0]
            titulo += middle_end[1]

        tags = [tag.strip() for tag in tags_raw.split(" ")]        
        only_key = uni_to_asc(get_md_link(titulo))
        try:
            color = [tag[2:] for tag in tags if tag.startswith("c:")][0]
        except IndexError as _e:
            color = None
            

        
        cluster = Cluster(line_num, titulo, only_key, color).set_alias(self.source.name)
        filename = self.source.get_source_readme()
        skey = cluster.get_db_key()
        if skey in self.clusters.keys():
            c = self.clusters[skey]
            print(f"Cluster {skey} já existe")
            print(f"{filename}:{line_num}")
            print(f"{filename}:{c.line_number}")
            print("  " + str(c))
            print("  " + str(cluster))
            exit(1)
                
        self.clusters[skey] = cluster
        self.ordered_clusters.append(skey)
        return cluster

    def __clear_empty_or_other_language(self, language: str): #call before create_cross_references
        # apagando quests vazias da lista de quests
        for cluster in self.clusters.values():
            quest_filters, task_filters = self.source.get_filters()
            cluster.remove_empty_and_other_language_and_filtered(language, quest_filters, task_filters) 

        # apagando quests vazias dos clusters e clusters vazios
        ordered_clusters: list[str] = []
        clusters: dict[str, Cluster] = {}
        for key in self.ordered_clusters:
            cluster = self.clusters[key]
            if len(cluster.get_quests()) > 0:
                ordered_clusters.append(cluster.get_db_key())
                clusters[cluster.get_db_key()] = cluster
        self.ordered_clusters = ordered_clusters
        self.clusters = clusters

    def __create_cross_references(self): #call after clear_empty
        for cluster in self.clusters.values():
            for quest in cluster.get_quests():
                quest.cluster_key = cluster.get_db_key()
                for task in quest.get_tasks():
                    task.cluster_key = cluster.get_db_key()
                    task.quest_key = quest.get_db_key()