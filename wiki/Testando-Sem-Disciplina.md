# Testando a ferramenta sem estar vinculado à uma disciplina de programação

```bash
# cria uma pasta nova para o repositório do tko
mkdir tko-teste
cd tko-teste
# inicializa um repositório do tko vazio
tko init
# Define a fonte remota de onde as tarefas serão carregadas, por exemplo:
tko remote add fup @fup # para carregar todas as atividades de fup
tko remote add ed @ed # para carregar todas as atividades de ed
tko remote add poo @poo # para carregar todas as atividades de poo
# abre o repositório interativamente
tko open
```

## Criando seus rascunhos e suas próprias atividades

- Após o tko open, digite 'r' para criar um rascunho de atividade
- Escolha um nome para a atividade, por exemplo: 'minha-atividade'
- Após navegar até a atividade, dê enter para abrir, enter para rodar os testes
- Aperte 'e' para editar o rascunho
- Você pode alterar a descrição, o código executado e até adicionar testes personalizados
