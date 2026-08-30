# GitHub Codespaces

GitHub Codespaces é uma alternativa recomendada quando o aluno não consegue preparar a máquina local ou quando a disciplina fornece um ambiente pronto.

Nesse fluxo, o ambiente de desenvolvimento roda em uma máquina Linux na nuvem, acessada pelo navegador ou pelo VS Code.

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

1. Acesse o repositório indicado pelo professor.
2. Clique em Code.
3. Abra a aba Codespaces.
4. Crie ou abra um Codespace.

Quando o ambiente terminar de carregar, abra o terminal integrado.

## Rodar setup do template

Se o repositório tiver script de configuração, siga a orientação da disciplina. Em alguns templates, o fluxo é:

```bash
./setup.sh
```

Escolha a linguagem da disciplina quando o script pedir.

## Verificar ferramentas

No terminal do Codespace:

```bash
git --version
python3 --version
tko --version
tko --help
```

Se `tko` não estiver instalado e o ambiente permitir instalação por `pipx`, use:

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
