from tko.game.quest_parser import QuestParser
from tko.game.task_parser import TaskParser
from tko.game.cluster import Cluster
from tko.game.quest import Quest
from tko.game.task import Task
from tko.util.get_md_link import get_md_link
from tko.util.to_asc import uni_to_asc
import os
from icecream import ic # type: ignore

class GameBuilder:
    def __init__(self, source_db: str, filename: str, quests_filter_view: list[str] | None, rep_folder: str, load_local: bool = False):
        self.source_db = source_db
        self.filename = filename
        self.rep_folder = rep_folder
        self.database = source_db
        self.database_path = os.path.join(self.rep_folder, self.source_db)
        self.ordered_clusters: list[str] = [] # ordered clusters
        self.clusters: dict[str, Cluster] = {}
        self.active_cluster: Cluster | None = None
        self.active_quest: Quest | None = None
        self.quests_filter_view: list[str] | None = quests_filter_view
        self.load_local = load_local

    def build_from(self, content: str, language: str):
        self.__parse_file_content(content)
        if self.load_local:
            self.__parse_database_for_user_tasks()
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
        if self.quests_filter_view is not None:
            return

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
        database_path = self.database_path
        local_tasks_cluster: Cluster = Cluster(0, "Atividades Locais", "local_task_cluster").set_database(self.source_db)
        self.__add_cluster(local_tasks_cluster)
        tasks = self.collect_tasks()
        if not os.path.exists(database_path):
            os.makedirs(database_path)
        for entry in os.listdir(database_path):
            path = os.path.join(database_path, entry)
            if not os.path.isdir(path):
                continue
            if entry in tasks:
                continue
            # create task for folder
            task = Task()
            task.set_title(entry)
            task.set_key(entry)
            task.set_rep_folder(self.rep_folder)
            task.set_database(self.source_db)
            task.link_type = Task.Types.STATIC_FILE
            self.__add_task(task)

    def __parse_file_content(self, content: str):
        lines = content.splitlines()
        for line_num, line in enumerate(lines):
            cluster = self.__load_cluster(self.source_db, line, line_num)
            if cluster is not None:
                self.__add_cluster(cluster)
                continue
            
            quest = QuestParser(self.source_db).parse_quest(self.filename, line, line_num + 1)
            if quest is not None:
                self.__add_quest(quest)
                continue

            tp = TaskParser(self.filename, self.database, self.rep_folder)
            task = tp.parse_line(line, line_num + 1).check_path_try().get_task()
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
        self.clusters[cluster.get_db_key()] = cluster
        if not cluster.get_db_key() in self.ordered_clusters:
            self.ordered_clusters.append(cluster.get_db_key())
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
            qkey = self.__get_active_cluster().get_db_key() + "_sem_quest"
            self.__add_quest(Quest("Sem Quest", qkey))
        self.__get_active_quest().add_task(task)

    # se existir um cluster nessa linha, insere na lista de clusters e 
    # retorno o objeto cluster inserido
    def __load_cluster(self, source: str, line: str, line_num: int) -> None | Cluster:
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
            

        
        cluster = Cluster(line_num, titulo, only_key, color).set_database(source)
        skey = cluster.get_db_key()
        if skey in self.clusters.keys():
            c = self.clusters[skey]
            print(f"Cluster {skey} já existe")
            print(f"{self.filename}:{line_num}")
            print(f"{self.filename}:{c.line_number}")
            print("  " + str(c))
            print("  " + str(cluster))
            exit(1)
                
        self.clusters[skey] = cluster
        self.ordered_clusters.append(skey)
        return cluster

    def __clear_empty_or_other_language(self, language: str): #call before create_cross_references
        # apagando quests vazias da lista de quests
        for cluster in self.clusters.values():
            cluster.remove_empty_and_other_language_and_filtered(language, self.quests_filter_view) 

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