import logging
import tomllib
from pathlib import Path

from tko.util.decoder import Decoder
from tko.i18n import Msg, t


logger = logging.getLogger(__name__)


_CONFIG_LANG_EMPTY = Msg(
    pt="Configurações de linguagem vazias",
    en="Language settings are empty",
)
_CONFIG_LANG_LOAD_FAILED = Msg(
    pt="Erro ao carregar as configurações de linguagem {path}, resetando para as configurações padrão",
    en="Error loading language settings {path}, resetting to default settings",
)


class LangSettings:
    def __init__(self, build_cmd: list[str], run_cmd: list[str], draft: str):
        self.build_cmd: list[str] = build_cmd
        self.run_cmd: list[str] = run_cmd
        self.draft: str = draft

    def to_dict(self):
        return self.__dict__

    def from_dict(self, attr_dict: dict[str, str | list[str]]):
        build_cmd = attr_dict.get("build_cmd", [])
        if isinstance(build_cmd, list):
            self.build_cmd = build_cmd
        run_cmd = attr_dict.get("run_cmd", [])
        if isinstance(run_cmd, list):
            self.run_cmd = run_cmd
        draft = attr_dict.get("draft", "")
        if isinstance(draft, str):
            self.draft = draft
        return self

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

ts_draft = r"""
const input = () => ""; // MACRO
export {};
console.log("Hello, World!");
"""[1:]


class LanguagesSettings:

    default_lang_settings: dict[str, LangSettings] = {
        "rust": LangSettings(
            build_cmd=["rustc", "{files}", "-o", "{output}"],
            run_cmd=["{output}"],
            draft=draft_rust
        ),
        "go": LangSettings(
            build_cmd=["go", "build", "-o", "{output}", "{files}"],
            run_cmd=["{output}"],
            draft=draft_go
        ),
        "py": LangSettings(
            build_cmd=[],
            run_cmd=["python3",  "{files}"],
            draft="# Escreva seu código aqui\nprint('Hello, World!')"
        ),
        "js": LangSettings(
            build_cmd=[],
            run_cmd=["node", "{files}"],
            draft=draft_js,
        ), 
        "hs": LangSettings(
            build_cmd=["ghc", "{files}", "-o", "{output}"],
            run_cmd=["{output}"],
            draft=haskell_draft
        ),
        "c": LangSettings(
            build_cmd=["gcc", "-Wall", "{files}", "-o", "{output}", "-lm"],
            run_cmd=["{output}"],
            draft=c_draft
        ),
        "cpp": LangSettings(
            build_cmd=["g++", "-std=c++17", "-Wall", "-Wextra", "-Werror", "-Wno-deprecated", "{files}", "-o", "{output}"],
            run_cmd=["{output}"],
            draft=cpp_draft
        ),
        "java": LangSettings(
            build_cmd=["javac", "{files}", "-d", "{cache}"],
            run_cmd=["java", "-cp", "{cache}", "{main}"],
            draft=java_draft
        ),
        "ts": LangSettings(
            build_cmd=["npx", "esbuild", "{files}", "--outdir={cache}", "--format=cjs", "--log-level=error"],
            run_cmd=["node", "{entry}"],
            draft=ts_draft
        ),
    }

    def get_languages(self) -> dict[str, LangSettings]:
        return self.lang_settings

    def get_languages_with_drafts(self) -> dict[str, str]:
        dict_lang_drafts: dict[str, str] = {}
        for lang_ext in self.lang_settings.keys():
            dict_lang_drafts[lang_ext] = self.lang_settings[lang_ext].draft
        return dict_lang_drafts

    def __init__(self, path: Path):
        self.path = path
        self.lang_settings: dict[str, LangSettings] = self.default_lang_settings.copy()

    def build_file_sample(self) -> str:
        output: list[str] = []
        for lang_ext, language_settings in self.default_lang_settings.copy().items():
            output.append(f"[{lang_ext}]")
            for key, value in language_settings.to_dict().items():
                if isinstance(value, str):
                    value = value.strip()
                    if value == "":
                        output.append(f"{key} = ''")
                    else:
                        output.append(f"{key} = '''\n{value}\n'''")
                elif isinstance(value, list):
                    if len(value) == 0: # type: ignore
                        output.append(f"{key} = []")
                    else:
                        output.append(f"{key} = [" + ", ".join([f"'{item}'" for item in value]) + "]") # type: ignore
            output.append("")
        return "\n".join(output)

    def load_file_settings(self):
        if not self.path.exists():
            return self
        try:
            content = Decoder.load(self.path)
            if content.strip() == "":
                raise Exception(t(_CONFIG_LANG_EMPTY))
            data = tomllib.loads(content)
            for lang_ext, settings in data.items():
                self.lang_settings[lang_ext] = LangSettings(
                    build_cmd=settings.get("build_cmd", []),
                    run_cmd=settings.get("run_cmd", []),
                    draft=settings.get("draft", "")
                )
        except Exception:
            logger.exception(t(_CONFIG_LANG_LOAD_FAILED, path=self.path))
        return self
