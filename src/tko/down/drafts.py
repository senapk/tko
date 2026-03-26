import os
from pathlib import Path
from tko.settings.languages_settings import LanguagesSettings
class Drafts:
    sandbox_key_prefix = "user"

    def __init__(self, user_languages: LanguagesSettings):
        self.user_languages = user_languages

    draft_readme: str = r"""Escreva aqui as informações que você quer salvar, esse é o seu rascunho.
O texto abaixo é informativo e você pode apagar depois de aprender como usar os rascunhos.

## Como usar os rascunhos

- Para renomear seu rascunho, basta renomear a pasta do rascunho.
- Para reorganizar, você pode criar subpastas dentro do sandbox e mover as pastas de rascunhos pra lá.
- Você pode usar o atalho R(Reload) no TKO para recarregar os rascunhos depois de criar, renomear ou reorganizar eles.
- Tudo que você fizer nos rascunhos também será rastreado pela ferramenta.

## Como criar seus próprios testes

Um teste é composto de um `input` (o texto que será fornecido para o programa) e um `output` (o texto que o programa deve retornar para esse input) e pode ter opcionalmente um `label` para facilitar a identificação do teste.

Seus casos de teste personalizados podem ser escritos diretamente aqui na descrição do problema dentro de um fenced code block com a linguagem `toml` ou em um arquivo `tests.toml` na pasta do problema. O TKO irá carregar automaticamente os testes quando a tarefa for aberta ou executada novamente.

Exemplo de teste para ler dois números, um por linha, e imprimir a soma e a subtração deles.

Se quiser habilitar esses casos de teste e ver funcionando, altere o fenced abaixo de `bash` para `toml` e execute novamente a tarefa no TKO.

```bash
[[tests]]
input = '''
3
2
'''
output = '''
5
1
'''

[[tests]]
label = 'números negativos'
input = '''
-3
-4
'''
output = '''
-7
1
'''
```

"""

    ts_draft = r"""
const input = () => ""; // MACRO
export {};
console.log("Hello, World!");
"""[1:]
    
    md_draft = r"""
# Rascunho

Se a tarefa exigir um relatório, escreva ele aqui. Você pode usar markdown, imagens e o que mais quiser para criar um relatório bem completo.
"""[1:]
    
    drafts = {
        'ts': ts_draft, 
        'md': md_draft
    }

    def get_languages_with_drafts(self) -> list[str]:
        keys = list(Drafts.drafts.keys())
        lang_register = self.user_languages.get_languages()
        for lang in lang_register.keys():
            if lang not in keys:
                keys.append(lang)
        keys.sort()
        return keys

    @staticmethod
    def create_draft_key(draft_id: int) -> str:
        return f"{Drafts.sandbox_key_prefix}_{draft_id:03d}"
    
    @staticmethod
    def find_max_numbered_key(task_keys_only: list[str]) -> int:
        numbered_keys: list[int] = []
        for key in task_keys_only:
            if key.startswith(Drafts.sandbox_key_prefix + "_"):
                try:
                    number = int(key[len(Drafts.sandbox_key_prefix) + 1:])
                    numbered_keys.append(number)
                except ValueError:
                    continue
        return max(numbered_keys) if numbered_keys else 0

    @staticmethod
    def load_drafts_only(folder: Path, lang: str, extra: list[str] | None = None) -> list[Path]:
        if extra is None:
            extra = []
        draft_list: list[Path] = []
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
            cut_root = root[len(str(folder)):]
            pieces = cut_root.split(os.sep)
            if any([piece.startswith(".") for piece in pieces]) or any([piece.startswith("_") for piece in pieces]):
                continue
            for file in files:
                if file.endswith(tuple(allowed)):
                    draft_list.append(Path(os.path.join(root, file)))
        return draft_list
    
    @staticmethod
    def create_sandbox_draft(dir: Path, key: str):
        with open (os.path.join(dir, "README.md"), "w", encoding="utf-8") as f:
            f.write(f"---\nkey: {key}\n---\n\n# {os.path.basename(dir)}\n\n" + Drafts.draft_readme)
