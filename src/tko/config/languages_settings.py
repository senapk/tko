from tko.config.languages_drafts import c_draft, cpp_draft, draft_go, draft_js, draft_rust, haskell_draft, java_draft, ts_draft
from tko.i18n import t
from tko.util.decoder import Decoder
from tko.config.languages_setup import LanguageSetup
from tko.i18n import Msg
from loguru import logger
import tomllib
from pathlib import Path



_CONFIG_LANG_EMPTY = Msg(
    pt="Configurações de linguagem vazias",
    en="Language settings are empty",
)
_CONFIG_LANG_LOAD_FAILED = Msg(
    pt="Erro ao carregar as configurações de linguagem {path}, resetando para as configurações padrão",
    en="Error loading language settings {path}, resetting to default settings",
)

class LanguagesSettings:

    default_lang_settings: dict[str, LanguageSetup] = {
        "rust": LanguageSetup(
            build_cmd=["rustc", "{files}", "-o", "{output}"],
            run_cmd=["{output}"],
            draft=draft_rust
        ),
        "go": LanguageSetup(
            build_cmd=["go", "build", "-o", "{output}", "{files}"],
            run_cmd=["{output}"],
            draft=draft_go
        ),
        "py": LanguageSetup(
            build_cmd=[],
            run_cmd=["python3",  "{files}"],
            draft="# Escreva seu código aqui\nprint('Hello, World!')"
        ),
        "js": LanguageSetup(
            build_cmd=[],
            run_cmd=["node", "{files}"],
            draft=draft_js,
        ),
        "hs": LanguageSetup(
            build_cmd=["ghc", "{files}", "-o", "{output}"],
            run_cmd=["{output}"],
            draft=haskell_draft
        ),
        "c": LanguageSetup(
            build_cmd=["gcc", "-Wall", "-Werror", "-Wshadow", "-fsanitize=address,undefined", "{files}", "-o", "{output}", "-lm"],
            run_cmd=["{output}"],
            draft=c_draft
        ),
        "cpp": LanguageSetup(
            build_cmd=["g++", "-std=c++17", "-Wall", "-Wextra", "-Werror", "-Wno-deprecated", "{files}", "-o", "{output}"],
            run_cmd=["{output}"],
            draft=cpp_draft
        ),
        "java": LanguageSetup(
            build_cmd=["javac", "{files}", "-d", "{cache}"],
            run_cmd=["java", "-cp", "{cache}", "{main}"],
            draft=java_draft
        ),
        "ts": LanguageSetup(
            build_cmd=["npx", "esbuild", "{files}", "--outdir={cache}", "--format=cjs", "--log-level=error"],
            run_cmd=["node", "{entry}"],
            draft=ts_draft
        ),
    }

    def get_languages(self) -> dict[str, LanguageSetup]:
        return self.lang_settings

    def get_languages_with_drafts(self) -> dict[str, str]:
        dict_lang_drafts: dict[str, str] = {}
        for lang_ext in self.lang_settings.keys():
            dict_lang_drafts[lang_ext] = self.lang_settings[lang_ext].draft
        return dict_lang_drafts

    def __init__(self, path: Path):
        self.path = path
        self.lang_settings: dict[str, LanguageSetup] = self.default_lang_settings.copy()

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
                self.lang_settings[lang_ext] = LanguageSetup(
                    build_cmd=settings.get("build_cmd", []),
                    run_cmd=settings.get("run_cmd", []),
                    draft=settings.get("draft", "")
                )
        except Exception:
            logger.exception(t(_CONFIG_LANG_LOAD_FAILED, path=self.path))
        return self