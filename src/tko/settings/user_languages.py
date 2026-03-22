import tomllib
from pathlib import Path
from platformdirs import user_data_dir

class LangSettings:
    def __init__(self, build_cmd: str, run_cmd: str, draft: str):
        self.build_cmd: str = build_cmd
        self.run_cmd: str = run_cmd
        self.draft: str = draft
    
    def to_dict(self):
        return self.__dict__
    
    def from_dict(self, attr_dict: dict[str, str]):
        self.build_cmd = attr_dict.get("build_cmd", self.build_cmd)
        self.run_cmd = attr_dict.get("run_cmd", self.run_cmd)
        self.draft = attr_dict.get("draft", self.draft)
        return self

draft_zip = r"""
const std = @import("std");

pub fn main() !void {
    try std.fs.File.stdout().writeAll("hello world!\n");
}"""[1:]

draft_rust = r"""
fn main() {
    println!("Hello, World!");
}"""[1:]

draft_go = r"""
package main
import "fmt"
func main() {
    fmt.Println("Hello, World!")
}"""[1:]

draft_js = r"""
const input=(()=>{let l,i=0,P;return()=>process.stdin.isTTY?((P=P||require("readline-sync")).question()):(l=l||require("fs").readFileSync(0,"utf-8").split(/\r?\n/),l[i++])})();
console.log("Hello, World!");
"""

haskell_draft = r"""
main :: IO ()
main = putStrLn "Hello, World!"
"""

c_draft = r"""
#include <stdio.h>
int main() {
    printf("Hello, World!\n");
    return 0;
}
"""

cpp_draft = r"""
#include <iostream>
int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
"""

java_draft = r"""
public class draft {
    public static void main(String args[]) {
        System.out.println("Hello, World!");
    }
}
"""

class UserLanguages:

    default_lang_settings: dict[str, LangSettings] = {
        "zig": LangSettings(
            build_cmd="zig build-exe {files} -femit-bin={output}",
            run_cmd="{output}",
            draft=draft_zip
        ),
        "rust": LangSettings(
            build_cmd="rustc {files} -o {output}",
            run_cmd="{output}",
            draft=draft_rust
        ),
        "go": LangSettings(
            build_cmd="go build -o {output} {files}",
            run_cmd="{output}",
            draft=draft_go
        ),
        "py": LangSettings(
            build_cmd="",
            run_cmd="python3 {files}",
            draft="# Escreva seu código aqui\nprint('Hello, World!')"
        ),
        "js": LangSettings(
            build_cmd="",
            run_cmd="node {files}",
            draft=draft_js,
        ), 
        "hs": LangSettings(
            build_cmd="ghc {files} -o {output}",
            run_cmd="{output}",
            draft=haskell_draft
        ),
        "c": LangSettings(
            build_cmd="gcc -Wall {files} -o {output} -lm",
            run_cmd="{output}",
            draft=c_draft
        ),
        "cpp": LangSettings(
            build_cmd="g++ -std=c++17 -Wall -Wextra -Werror -Wno-deprecated {files} -o {output}",
            run_cmd="{output}",
            draft=cpp_draft
        ),
        "java": LangSettings(
            build_cmd="javac {files} -d {cache}",
            run_cmd="java -cp {cache} {main}",
            draft=java_draft
        )
    }
    def get_languages(self) -> dict[str, LangSettings]:
        return self.lang_settings

    def __init__(self, path: Path):
        self.path = path
        self.lang_settings: dict[str, LangSettings] = {}

    def set_default_path(self):
        self.path = Path(user_data_dir("tko")) / "languages.toml"
        return self

    def reset(self):
        self.lang_settings = self.default_lang_settings.copy()
        return self

    def save_file_settings(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "w") as f:
            for lang, settings in self.lang_settings.items():
                f.write(f"[{lang}]\n")
                for key, value in settings.to_dict().items():
                    if value == "":
                        f.write(f"{key} = ''\n")
                    else:
                        f.write(f"{key} = '''\n{value.strip()}\n'''\n")
                f.write("\n")
        return self

    def load_file_settings(self):
        if not self.path.exists():
            self.reset()
            self.save_file_settings()
        try:
            with open(self.path, "rb") as f:
                content = f.read()
                data = tomllib.loads(content.decode("utf-8"))
                for lang, settings in data.items():
                    self.lang_settings[lang] = LangSettings(
                        build_cmd=settings.get("build_cmd", ""),
                        run_cmd=settings.get("run_cmd", ""),
                        draft=settings.get("draft", "")
                    )
        except Exception as e:
            print(f"Erro ao carregar as configurações de linguagem {self.path}, resetando para as configurações padrão. Erro: {e}")
            self.reset()
            self.save_file_settings()
        return self
