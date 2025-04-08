from tko.game.task_parser import TaskParser
from tko.game.cluster import Cluster
from tko.game.quest import Quest
from tko.game.task import Task
from tko.game.quest import Quest, QuestParser
from tko.game.task import Task
from tko.util.get_md_link import get_md_link
from tko.util.to_asc import uni_to_asc
import os

from typing import Dict, List


class GameBuilder:
    def __init__(self, filename: str, database_folder: str):
        self.filename = filename
        self.database_folder = database_folder
        self.ordered_clusters: List[str] = [] # ordered clusters
        self.clusters: Dict[str, Cluster] = {}
        self.active_cluster: Cluster | None = None
        self.active_quest: Quest | None = None

    def build_from(self, content: str, language: str):
        self.__parse_file_content(content)
        self.__parse_database_for_user_tasks()
        self.__clear_empty_or_other_language(language)
        self.__create_requirements_pointers()
        self.__create_cross_references()
        return self


    def collect_tasks(self) -> dict[str, Task]:
        tasks: Dict[str, Task] = {}
        for cluster in self.clusters.values():
            for quest in cluster.get_quests():
                for task in quest.get_tasks():
                    tasks[task.key] = task
        return tasks

    def collect_quests(self) -> dict[str, Quest]:
        quests: Dict[str, Quest] = {}
        for cluster in self.clusters.values():
            for quest in cluster.get_quests():
                quests[quest.key] = quest
        return quests

    def __create_requirements_pointers(self):
        quests = self.collect_quests()
        # verificar se todas as quests requeridas existem e adicionar o ponteiro
        for q in quests.values():
            for r in q.requires:
                if r in quests:
                    q.requires_ptr.append(quests[r])
                else:
                    # print(f"keys: {self.quests.keys()}")
                    print(f"Quest\n{self.filename}:{q.line_number}\n{str(q)}\nrequer {r} que não existe")
                    exit(1)

    def __parse_database_for_user_tasks(self):
        folder = self.database_folder
        local_tasks_cluster: Cluster = Cluster(0, "Atividades Locais", "local_task_cluster")
        self.__add_cluster(local_tasks_cluster)
        tasks = self.collect_tasks()
        if not os.path.exists(folder):
            os.makedirs(folder)
        for entry in os.listdir(folder):
            path = os.path.join(folder, entry)
            if not os.path.isdir(path):
                continue
            if entry in tasks:
                continue
            # create task for folder
            task = Task()
            task.key = entry
            task.title = entry
            task.folder = path
            self.__add_task(task)

    def __parse_file_content(self, content: str):
        lines = content.splitlines()
        for line_num, line in enumerate(lines):
            cluster = self.__load_cluster(line, line_num)
            if cluster is not None:
                self.__add_cluster(cluster)
                continue
            
            quest = QuestParser().parse_quest(self.filename, line, line_num + 1)
            if quest is not None:
                self.__add_quest(quest)
                continue
            
            tp = TaskParser(self.filename, self.database_folder)
            task = tp.parse_line(line, line_num + 1)
            if task is not None:
                self.__add_task(task)

    def __get_active_cluster(self) -> Cluster:
        if self.active_cluster is None:
            raise Warning("Active Cluster Missing")
        return self.active_cluster

    def __get_active_quest(self) -> Quest:
        if self.active_quest is None:
            raise Warning("Active Quest Missing")
        return self.active_quest

    def __add_cluster(self, cluster: Cluster):
        self.clusters[cluster.key] = cluster
        self.ordered_clusters.append(cluster.key)
        self.active_cluster = cluster
        self.active_quest = None

    def __add_quest(self, quest: Quest):
        self.__get_active_cluster().add_quest(quest)
        self.active_quest = quest

    def __add_task(self, task: Task):
        if self.active_cluster is None:
            ckey = "sem_cluster"
            self.__add_cluster(Cluster(0, "Sem Cluster", ckey))
        if self.active_quest is None:
            qkey = self.__get_active_cluster().key + "_sem_quest"
            self.__add_quest(Quest("Sem Quest", qkey))
        self.__get_active_quest().add_task(task, self.filename)

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
        key = uni_to_asc(get_md_link(titulo))
        try:
            color = [tag[2:] for tag in tags if tag.startswith("c:")][0]
        except IndexError as _e:
            color = None
        
        cluster = Cluster(line_num, titulo, key, color)

        if key in self.clusters.keys():
            c = self.clusters[key]
            print(f"Cluster {key} já existe")
            print(f"{self.filename}:{line_num}")
            print(f"{self.filename}:{c.line_number}")
            print("  " + str(c))
            print("  " + str(cluster))
            exit(1)
                
        self.clusters[key] = cluster
        self.ordered_clusters.append(key)
        return cluster

    def __clear_empty_or_other_language(self, language: str): #call before create_cross_references

        # apagando quests vazias da lista de quests
        for cluster in self.clusters.values():
            cluster.remove_empty_or_other_language(language)

        # apagando quests vazias dos clusters e clusters vazios
        ordered_clusters: List[str] = []
        clusters: Dict[str, Cluster] = {}
        for key in self.ordered_clusters:
            cluster = self.clusters[key]
            if len(cluster.get_quests()) > 0:
                ordered_clusters.append(cluster.key)
                clusters[cluster.key] = cluster
        self.ordered_clusters = ordered_clusters
        self.clusters = clusters

    def __create_cross_references(self): #call after clear_empty
        for cluster in self.clusters.values():
            for quest in cluster.get_quests():
                quest.cluster_key = cluster.key
                for task in quest.get_tasks():
                    task.cluster_key = cluster.key
                    task.quest_key = quest.key