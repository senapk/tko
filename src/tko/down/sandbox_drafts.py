import os
from pathlib import Path

class SandboxDrafts:
    sandbox_key_prefix = "user"

    def __init__(self):
        pass

    draft_readme: str = r"""Escreva aqui as informações que você quer salvar, esse é o seu rascunho.
O texto abaixo é informativo e você pode apagar depois de aprender como usar os rascunhos.

## Como usar os rascunhos

- A chave do seu rascunho é o nome da pasta.
- O título do seu rascunho é carregado a partir da primeira linha desse arquivo \#
- Tudo que você fizer nos rascunhos também será rastreado pelo tko.

## Como criar seus próprios testes

Um teste é composto de um `input` (o texto que será fornecido para o programa) e um `output` (o texto que o programa deve retornar para esse input) e pode ter opcionalmente um `label` para facilitar a identificação do teste.

Seus casos de teste personalizados podem ser escritos diretamente aqui na descrição do problema dentro de um fenced code block com a linguagem `toml` ou em um arquivo `tests.toml` na pasta do problema. O TKO irá carregar automaticamente os testes quando a tarefa for aberta ou executada novamente.

Exemplo de teste para ler dois números, um por linha, e imprimir a soma e a subtração deles.

Se quiser habilitar esses casos de teste e ver funcionando, insira algo no input e no output.

```toml
# Exemplo de entrada em uma linha
[[tests]]
input = ''
output = ''

# Exemplo de entrada em múltiplas linhas
# [[tests]]
# input = '''
# 1
# 2
# '''
# output = '''
# 3
# 4
# '''
```

"""

    md_draft = r"""
# Rascunho

Se a tarefa exigir um relatório, escreva ele aqui. Você pode usar markdown, imagens e o que mais quiser para criar um relatório bem completo.
"""[1:]

    @staticmethod
    def format_draft_key(draft_id: int) -> str:
        return f"{SandboxDrafts.sandbox_key_prefix}_{draft_id:03d}"
    
    @staticmethod
    def find_max_numbered_key(task_keys_only: list[str]) -> int:
        numbered_keys: list[int] = []
        for key in task_keys_only:
            if key.startswith(SandboxDrafts.sandbox_key_prefix + "_"):
                try:
                    number = int(key[len(SandboxDrafts.sandbox_key_prefix) + 1:])
                    numbered_keys.append(number)
                except ValueError:
                    continue
        return max(numbered_keys) if numbered_keys else 0
    
    @staticmethod
    def create_sandbox_draft(dir: Path, title: str):
        with open (os.path.join(dir, "README.md"), "w", encoding="utf-8") as f:
            f.write(f"# {title}\n\n" + SandboxDrafts.draft_readme)
