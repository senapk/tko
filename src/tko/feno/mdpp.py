#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import argparse
import enum
from tko.feno.filter import Filter
from tko.util.decoder import Decoder


class Action(enum.Enum):
    RUN = 1
    CLEAN = 2

class TocMaker:
    @staticmethod
    def __only_hashtags(x: str) -> bool:
        return len(x) == x.count("#") and len(x) > 0

    # generate md link for the text
    @staticmethod
    def __get_md_link(title: str | None) -> str:
        if title is None:
            return ""
        # remove html comments
        if "<!--" in title and "-->" in title:
            title = title.split("<!--")[0]

        if "[](" in title:
            title = title.split("[](")[0]

        title = title.lstrip(" #")
        title = title.lower()
        out = ''
        for c in title:
            if c == ' ' or c == '-':
                out += '-'
            elif c == '_':
                out += '_'
            elif c == '\\':
                pass
            elif c.isalnum():
                out += c
        return out

    @staticmethod
    def __get_level(line: str) -> int:
        return len(line.split(" ")[0])

    @staticmethod
    def __get_content(line: str) -> str:
        if "<!--" in line and "-->" in line:
            line = line.split("<!--")[0]
        return " ".join(line.split(" ")[1:]).replace("\\", "\\\\")

    @staticmethod
    def __remove_code_fences(content: str) -> str:
        regex = r"^```.*?```\n"
        return re.sub(regex, "", content, 0, re.MULTILINE | re.DOTALL)


    @staticmethod
    def __extract_entries(content: str) -> list[tuple[int, str]]:
        content = TocMaker.__remove_code_fences(content)

        lines = content.splitlines()
        disable_tag = "[]()"
        lines = [line for line in lines if TocMaker.__only_hashtags(line.split(" ")[0]) and line.find(disable_tag) == -1]

        entries: list[tuple[int, str]] = []
        for line in lines:
            level = TocMaker.__get_level(line)
            text = "[" + TocMaker.__get_content(line) + "](#" + TocMaker.__get_md_link(line) + ")"
            entries.append((level, text))
        return entries

    
    @staticmethod
    def execute_toch(content: str) -> str:
        entries = TocMaker.__extract_entries(content)
        links = [b for (a, b) in entries if a == 2]
        table = ["--" for _ in links]
        return " | ".join(links) + "\n" + " | ".join(table)
        

    @staticmethod
    def execute_toc(content: str) -> str:
        entries = TocMaker.__extract_entries(content)
        toc_lines = ["  " * (level - 2) + "- " + link for (level, link) in entries if level > 1]
        toc_text = "\n".join(toc_lines)
        return toc_text

class Toc:
    @staticmethod
    def execute(content: str, action: Action = Action.RUN) -> str:
        regex = r"<!-- toc -->\n" + r"(.*?)"+ r"<!-- toc -->"
        if action == Action.RUN:
            new_toc = TocMaker.execute_toc(content)
            subst = r"<!-- toc -->\n" + new_toc + r"\n<!-- toc -->"
        else:
            subst = r"<!-- toc -->\n<!-- toc -->"
        return re.sub(regex, subst, content, 0, re.MULTILINE | re.DOTALL)

class Toch:
    @staticmethod
    def execute(content: str, action: Action = Action.RUN) -> str:
        regex = r"<!-- toch -->\n" + r"(.*?)"+ r"<!-- toch -->"
        if action == Action.RUN:
            new_toc = TocMaker.execute_toch(content)
            subst = r"<!-- toch -->\n" + new_toc + r"\n<!-- toch -->"
        else:
            subst = r"<!-- toch -->\n<!-- toch -->"
        return re.sub(regex, subst, content, 0, re.MULTILINE | re.DOTALL)

class Links:

    @staticmethod
    def load_links(readme_dir: str, filter_dir: str):
        def traverse_directory(directory: str, depth: int = 0):
            output = ""
            if os.path.isdir(directory):
                entries = sorted(os.listdir(directory))
                for entry in entries:
                    if entry.startswith("."):
                        continue
                    full_path = os.path.join(directory, entry)
                    if os.path.isdir(full_path):
                        output += "  " * depth + "- " + entry + "\n"
                        output += traverse_directory(full_path, depth + 1)
                    else:
                        path = os.path.relpath(full_path, readme_dir).replace("\\", "/")
                        output += "  " * depth + "- [" + entry + "](" + path + ")\n"
            return output
        
        origin = os.path.join(readme_dir, filter_dir)
        return traverse_directory(origin)

    @staticmethod
    def execute(path: str, content: str, action: Action = Action.RUN) -> str:
        regex = r"<!-- links (\S*?) -->\n(.*?)<!-- links -->"
        matches = re.finditer(regex, content, re.MULTILINE | re.DOTALL)
        
        # replace content of group 2 with load_links of group 1 for each match
        for match in matches:
            filter_dir = match.group(1)
            lregex = r"<!-- links " + filter_dir + r" -->\n(.*?)<!-- links -->"
            if action == Action.RUN:
                readme_dir = os.path.normpath(os.path.dirname(path))
                new_links = Links.load_links(readme_dir, filter_dir)
                subst = r"<!-- links " + filter_dir + r" -->\n" + new_links + r"<!-- links -->"
            else:
                subst = r"<!-- links " + filter_dir + r" -->\n<!-- links -->"
            content = re.sub(lregex, subst, content, 0, re.MULTILINE | re.DOTALL)

        return content

class Load:

    @staticmethod
    def extract_between_tags(content: str, tag: str) -> str:
        regex = r"\[\[" + tag + r"\]\].*?^(.*)^[\S ]*\[\[" + tag + r"\]\]"
        matches = re.finditer(regex, content, re.MULTILINE | re.DOTALL)
        for match in matches:
            return match.group(1)
        return ""

    @staticmethod
    def rmcom(target: str, content: str) -> str:
        com = "//"
        if target.endswith(".py"):
            com = "#"
        if target.endswith(".puml"):
            com = "'"
        lines = content.splitlines()
        output: list[str] = []
        for line in lines:
            if not line.lstrip().startswith(com):
                output.append(line)
        return "\n".join(output)


    @staticmethod
    def execute(content: str, target_dir: str, action: Action = Action.RUN) -> str:
        new_content = ""
        last = 0

        regex = r"<!-- load (\S*?) (\S*?) -->\n(.*?)<!-- load -->"
        matches = re.finditer(regex, content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            path = match.group(1)
            abspath = os.path.abspath(os.path.join(target_dir, path))
            tags = match.group(2)
            words: list[str] = tags.split(":")

            fenced: list[str] = [tag for tag in words if tag.startswith("fenced")]
            words = [tag for tag in words if not tag.startswith("fenced")]

            filter: list[str] = [tag for tag in words if tag.startswith("filter")]
            words = [tag for tag in words if not tag.startswith("filter")]

            rmcom: list[str] = [tag for tag in words if tag.startswith("rmcom")]
            words = [tag for tag in words if not tag.startswith("rmcom")]


            extract: list[str] = [tag for tag in words if tag.startswith("extract")]
            words = [tag for tag in words if not tag.startswith("extract")]


            ext = os.path.splitext(path)[1][1:]
            if len(words) > 0:
                ext = words[0]
            if len(fenced) == 1:
                parts = fenced[0].split("=")
                if len(parts) == 2:
                    ext = parts[1]


            new_content += content[last:match.start()] # inserindo texto entre matches
            last = match.end()
            # new_content += "[](load)[](" + path + ")[](" + tags + ")\n"
            new_content += "<!-- load " + path + " " + tags + " -->\n"

            # se não for run, deve limpar o conteúdo não inserindo os arquivos
            if action == Action.RUN:
                if len(fenced) > 0:
                    new_content += "\n```" + ext + "\n"
                if os.path.isfile(abspath):
                    if len(filter) > 0:
                        data = Filter(path).process(Decoder.load(abspath)) + "\n"
                        new_content += data
                        if data[-1] != "\n":
                            new_content += "\n"
                    elif len(rmcom) > 0:
                        full_data = Decoder.load(abspath)
                        data =  Load.rmcom(abspath, full_data) + "\n"
                        new_content += data
                        if data[-1] != "\n":
                            new_content += "\n"
                    elif len(extract) > 0:
                        tag = extract[0].split("=")[1]
                        full_data = Decoder.load(abspath)
                        data = Load.extract_between_tags(full_data, tag)
                        new_content += data
                        if len(data) == 0 or data[-1] != "\n":
                            new_content += "\n"
                    else:
                        data = Decoder.load(abspath)
                        new_content += data
                        if data[-1] != "\n":
                            new_content += "\n"
                else:
                    print("warning: file", path, "not found")
                if fenced:
                    new_content += "```\n\n"
            new_content += "<!-- load -->"
        
        new_content += content[last:]
        return new_content


            

class Save:
    @staticmethod
    # execute filename and content
    def execute(file_content: str) -> None:
        regex = r"\[\]\(save\)\[\]\((.*?)\)\n```[a-z]*\n(.*?)```\n\[\]\(save\)"
        matches = re.finditer(regex, file_content, re.MULTILINE | re.DOTALL)
        content_old = ""        
        for match in matches:
            path = match.group(1)
            content = match.group(2)
            exists = os.path.isfile(path)
            if exists:
                content_old = Decoder.load(path)
            if not exists or content != content_old:
                Decoder.save(path, content)
                print("file", path, "updated")

class MdppMain:
    @staticmethod
    def fix_path(target: str):
        target = os.path.normpath(target)
        if os.path.isdir(target):
            target = os.path.join(target, "Readme.md")
        return target

    @staticmethod
    def open_file(path: str) -> tuple[bool, str]: 
        if os.path.isfile(path):
            file_content = Decoder.load(path)
            return True, file_content
        print("Warning: File", path, "not found")
        return False, "" 

class Mdpp:
    @staticmethod
    def update_file(target: str, action: Action = Action.RUN, quiet: bool = False) -> bool:
        path = MdppMain.fix_path(target)
        target_dir = os.path.dirname(path)
        found, original = MdppMain.open_file(path)
        if not found:
            return False
        updated = original
        updated_toc = Toc.execute(updated, action)
        updated_toc = Toch.execute(updated_toc, action)
        if updated != updated_toc:
            updated = updated_toc
        updated = Load.execute(updated, target_dir, action)
        updated = Links.execute(target, updated, action)
        Save.execute(updated)
        
        if updated != original:
            Decoder.save(path, updated)
            # hook = os.path.abspath(path).split(os.sep)[-2]
            return True

        return False

def mdpp_main(args: argparse.Namespace):

    if len(args.targets) == 0:
        print("No targets selected")
        exit()
    
    action = Action.RUN if not args.clean else Action.CLEAN

    for target in args.targets:
        Mdpp.update_file(target, action, args.quiet)
