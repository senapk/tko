# GitHub Codespaces

GitHub Codespaces é uma alternativa recomendada quando o aluno não consegue preparar a máquina local ou quando a disciplina fornece um ambiente pronto.

Nesse fluxo, o ambiente de desenvolvimento roda em uma máquina Linux na nuvem, acessada pelo navegador ou pelo VS Code.

O repositório padrão para alunos usando TKO no Codespaces é:

- [senapk/tko-student-starter](https://github.com/senapk/tko-student-starter)

Esse starter já traz scripts para instalar ferramentas de setup e para facilitar operações comuns com Git.

## Meta do ambiente

Ao final, o Codespace deve ter:

- Terminal Linux funcionando.
- Repositório da disciplina aberto.
- Git autenticado pela conta GitHub.
- Python 3 disponível.
- `pipx` disponível, quando necessário.
- TKO instalado ou configurado pelo template da disciplina.
- Linguagem da disciplina instalada.
- `tko --version`, `tko --help` e `tko open` funcionando.

Se algum passo falhar, procure a documentação atual do GitHub Codespaces ou do template da disciplina. O objetivo é cumprir o checklist, não seguir um comando específico a qualquer custo.

## Quando usar

Use Codespaces quando:

- a turma já fornece um template configurado;
- a máquina local tem bloqueios administrativos;
- o WSL não está funcionando;
- o aluno precisa começar rapidamente em um ambiente padronizado.

## Abrir um Codespace

1. Acesse o repositório indicado pelo professor, preferencialmente criado a partir de [senapk/tko-student-starter](https://github.com/senapk/tko-student-starter).
2. Clique em Code.
3. Abra a aba Codespaces.
4. Crie ou abra um Codespace.

Quando o ambiente terminar de carregar, abra o terminal integrado.

## Rodar setup do starter

Se o repositório tiver script de configuração, siga a orientação da disciplina. O starter padrão do TKO já inclui script para instalar ferramentas e preparar o ambiente:

```bash
./setup.sh
```

Escolha a linguagem da disciplina quando o script pedir.

O starter também possui um script para facilitar o uso do Git. Use-o conforme a orientação do professor, especialmente nos primeiros commits e pushes.

## Verificar ferramentas

No terminal do Codespace:

```bash
git --version
python3 --version
tko --version
tko --help
```

Se `tko` não estiver instalado e o ambiente permitir instalação por `pipx`, use o script de setup do starter. Como alternativa, instale manualmente:

```bash
python3 -m pipx ensurepath
pipx install tko
```

Feche e abra o terminal se o PATH for atualizado.

## Abrir TKO

Dentro do repositório da disciplina:

```bash
tko open
```

Se o repositório ainda não for um workspace TKO:

```bash
tko init
```

Depois adicione a fonte indicada pelo professor.

## Observações

- Codespaces depende de internet e da disponibilidade da conta GitHub.
- O ambiente pode ser recriado; mantenha commits e push em dia.
- Arquivos grandes ou dependências pesadas podem consumir cota da conta.
