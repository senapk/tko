#!/bin/env python

import os
import argparse
from tko.util.text import Text
from .class_task import ClassTask
from .student_repo import StudentRepo
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import subprocess

class Pull:

    @staticmethod
    def run_git_command(directory: str, command_args: list[str]) -> tuple[str, str, int]:
        """
        Executa um comando Git em um diretório específico.
        Retorna stdout, stderr, e returncode.
        """
        # Certifique-se de que o comando Git é executado no diretório correto
        # cwd (current working directory) é essencial aqui
        try:
            process = subprocess.Popen(
                ['git'] + command_args,
                cwd=directory,  # Executa o comando no diretório do repositório
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True  # Para decodificar automaticamente para string
            )
            stdout, stderr = process.communicate()
            return stdout, stderr, process.returncode
        except FileNotFoundError:
            print(f"Erro: O comando 'git' não foi encontrado. Certifique-se de que o Git está instalado e no seu PATH.")
            return "", f"Erro: 'git' not found.", 127
        except Exception as e:
            print(f"Erro ao executar o comando 'git {' '.join(command_args)}': {e}")
            return "", f"Erro inesperado: {e}", 1


    @staticmethod
    def pull(directory: str) -> Text:
        """
        Pull a single repository in folter ignoring any local file or folder changes.
        If the repository needs a merge, ignore it and just pull the latest changes.
        Args:
            directory (str): The directory of the repository to pull.
        """
        if not os.path.isdir(directory):
            return Text()
        if not os.path.isdir(os.path.join(directory, ".git")):
            return Text()

        output: Text  = Text()

        output += Text("g") + directory + " "
        # 1. Reset Local Hard
        output += Text("y") + "Local "
        stdout, stderr, returncode = Pull.run_git_command(directory, ["reset", "--hard", "HEAD"])
        if returncode != 0:
            output += "\n" + f"Erro no reset --hard: {stderr}"


        # 2. Clean
        output += Text("y") + "Clean "
        stdout, stderr, returncode = Pull.run_git_command(directory, ["clean", "-fd"])
        if returncode != 0:
            output += "\n" + f"Erro no clean -fd: {stderr}"
        # else:
        #     print(f"  {stdout.strip()}")

        # 3. Fetch
        output += Text("y") + "Fetch "
        stdout, stderr, returncode = Pull.run_git_command(directory, ["fetch", "origin"])
        if returncode != 0:
            output += "\n" + f"Erro no fetch: {stderr}"
        # else:
        #     print(f"  {stdout.strip()}")

        # 4. Restore (git reset --hard origin/main)
        # Assumindo que o branch principal é 'main'. Mude para 'master' se for o caso.
        main_branch = "main" # Ou "master"
        output += Text("y") + "Restore "
        stdout, stderr, returncode = Pull.run_git_command(directory, ["reset", "--hard", f"origin/{main_branch}"])
        if returncode != 0:
            output += "\n" + f"Erro no restore (reset --hard origin/{main_branch}): {stderr}"
        else:
            output += "\n" + f"  {stdout.strip()}"

        return output

    @staticmethod
    def pull_all_parallel(repo_list: list[StudentRepo], max_workers: int = 50):
        """
        Pull all repositories in a list of student folders concurrently.
        Args:
            students_folders (list[str]): List of student folder paths.
            max_workers (int): Maximum number of threads to use.
        """
        print(f"\n{Text('y')}Iniciando pull de {len(repo_list)} repositórios com {max_workers} threads...{Text('e')}")
        start_time = time.time()

        # Use ThreadPoolExecutor para gerenciar as threads
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Cria um dicionário para mapear os objetos Future de volta para as pastas
            future_to_folder = {executor.submit(Pull.pull, repo.folder): repo.folder for repo in repo_list}

            # Itera sobre os resultados à medida que ficam prontos
            for future in as_completed(future_to_folder):
                student_folder = future_to_folder[future]
                try:
                    # Obtém o objeto GitOutput retornado pela função pull
                    output = future.result()
                    if output.get_str() != "":
                        print(output)
                except Exception as exc:
                    print(f"{Text('r')}A pasta '{student_folder}' gerou uma exceção não esperada: {exc}{Text('e')}")

        end_time = time.time()
        print(f"\n{Text('y')}Processamento concluído em {end_time - start_time:.2f} segundos.{Text('e')}")

    @staticmethod
    def main(class_task_path: str, n_threads: int = 5) -> None:
        class_task = ClassTask(class_task_path).load_from_file()
        students_repo_list = class_task.load_student_repo_list()
        Pull.pull_all_parallel(students_repo_list, n_threads)


def main():
    parser = argparse.ArgumentParser(description='Pull all git repositories in a directory')
    parser.add_argument('jsons', type=str, nargs="*", help='Directory to pull repositories from')
    parser.add_argument("-f", '--folders', type=str, nargs="*", help='Update git folder')
    parser.add_argument("-t", "--threads", type=int)

    args = parser.parse_args()
    n_threads = 10
    if args.threads:
        n_threads = args.threads

    if args.folders:
        Pull.pull_all_parallel(args.folders, n_threads)

    if args.jsons:
        for json in args.jsons:
            Pull.main(json, n_threads)


if __name__ == '__main__':
    main()
