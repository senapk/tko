import os

class Drafts:
    ts_draft = r"""
const input = () => ""; //essa função será gerada pelo tko na execução
export {};

function main() {
    console.log("qxcode");
}
main();
"""[1:]

    c_draft = r"""
#include <stdio.h>

int main() {
    puts("qxcode");
    return 0;
}

"""[1:]

    cpp_draft = r"""
#include <iostream>

int main() {
    std::cout << "qxcode\n";
}

"""[1:]

    java_draft = r"""
public class draft {
    public static void main(String args[]) {
        System.out.println("qxcode");
    }
}

"""[1:]

    go_draft = (
        r"package main""\n"
        r'import "fmt"'"\n"
        r"func main() {""\n"
        r'    fmt.Println("qxcode")''\n'
        r"}""\n"
    )
    
    yaml_draft = r"""
build: comando para construir o executável
run: comando para rodar o programa
"""[1:]
    
    hs_draft = r"""
main :: IO ()
main = putStrLn "qxcode"
"""[1:]


    drafts = {'c': c_draft, 'cpp': cpp_draft, 'ts': ts_draft, 'java': java_draft, 'go': go_draft, 'hs': hs_draft, 'yaml': yaml_draft}

    @staticmethod
    def load_drafts_only(folder: str, lang: str, extra: list[str] | None = None) -> list[str]:
        if extra is None:
            extra = []
        folder = os.path.normpath(os.path.abspath(folder))
        draft_list: list[str] = []
        allowed = extra
        if lang != "":
            allowed.append(lang)
        if "c" in allowed:
            allowed.append("h")
        if "cpp" in allowed:
            allowed.append("h")
            allowed.append("hpp")
        if not os.path.isdir(folder):
            return []
        for root, _, files in os.walk(folder):
            cut_root = root[len(folder):]
            pieces = cut_root.split(os.sep)
            if any([piece.startswith(".") for piece in pieces]) or any([piece.startswith("_") for piece in pieces]):
                continue
            for file in files:
                if file.endswith(tuple(allowed)):
                    draft_list.append(os.path.join(root, file))
        return draft_list
