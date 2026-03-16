# github classroom

- Crie uma turma no GitHub Classroom
- Crie uma tarefa apontando para um repositório vazio.
  - Se quiser integração com o codespace, aponte para um repositório como o [tko_template](https://github.com/qxcode-course/tko_template) que já tem a configuração pronta. Basta o aluno digitar `./setup.sh`, escolher a linguagem e todo setup será instalado automaticamente.
  - A tarefa pode ser configurada com data limite para aceitar push.
- Distribua o link da tarefa para os alunos criarem seus repositórios da atividade.
- Envie para os alunos o link ou comando de configuração da atividade.
  - Exemplo para carregar apenas as atividades de seleção do repositório oficial de fup de Quixadá:
    - ex: tko remote add fup @fup --quest seleção
  - Para apontar para seu repositório personalizado, o comando seria algo como:
    - ex: tko remote add origin https://github.com/seu-usuario/seu-repositorio
- Os alunos resolvem as tarefas localmente usando o TKO
- O TKO registra eventos de execução e atividade
- Os alunos fazem commits e push diários para salvar a evolução
- O professor usa o gh para coletar todos os repositórios
- O professor analisa o histórico através de ferramentas de coleta de dados do TKO ou manualmente