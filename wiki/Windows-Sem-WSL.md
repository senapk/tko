# Windows sem WSL - legado

Este caminho não é recomendado para turmas atuais.

Use apenas se a máquina não puder usar WSL, Ubuntu nativo ou GitHub Codespaces. O suporte principal da documentação do TKO assume ambiente Linux, preferencialmente Ubuntu no WSL.

## Caminhos recomendados antes deste

1. [Windows com WSL e Ubuntu](Windows-WSL.md)
2. [GitHub Codespaces](Codespaces.md)
3. [Ubuntu / WSL: Git, Python, pipx e TKO](ubuntu_git_python_tko.md)

## Meta mínima

Se ainda for necessário usar Windows sem WSL, a máquina precisa ter:

- VS Code instalado.
- Git instalado e disponível no terminal.
- Autenticação com GitHub funcionando.
- Python 3 instalado.
- `pipx` instalado e disponível no PATH.
- TKO instalado via `pipx`.
- Linguagens da disciplina instaladas.
- `tko --version` e `tko --help` funcionando.

## Orientação

Instale cada ferramenta seguindo a documentação atual do fornecedor:

- VS Code: site oficial do Visual Studio Code.
- Git: instalador oficial do Git for Windows.
- Python: site oficial do Python ou método indicado pela instituição.
- pipx: documentação oficial do pipx.

Depois de instalar Python e pipx, o TKO normalmente pode ser instalado com:

```powershell
pipx install tko
```

Verifique:

```powershell
tko --version
tko --help
```

Se houver erro de PATH, terminal, compilador ou permissão, procure uma correção específica para a ferramenta que falhou. Em contexto de turma, prefira migrar para WSL ou Codespaces em vez de gastar muito tempo depurando diferenças do Windows nativo.
