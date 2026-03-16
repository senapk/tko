# Clonando o seu repositório da disciplina

Na disciplina, você provavelmente vai criar repositórios no GitHub para armazenar e versionar seus códigos. Para trabalhar localmente no seu computador, você precisará clonar esses repositórios.

Dentro desses repositórios, você vai criar uma pasta de trabalho do tko, onde você vai desenvolver suas atividades. A inicialização dessa pasta deverá ser feita de acordo com a atividade que vai ser desenvolvida (POO, FUP ou ED) e as atividades que seu professor vai querer que você faça.

Vou dar um exemplo de organização genérica para o seu sistema de arquivos se estiver trabalhando numa pasta chamada `projetos` dentro do seu diretório pessoal:

```txt
├── projetos/
│   ├── rep-git-bloco-a/
│   │   ├── sandbox/
│   │   └── ed/
│   ├── rep-git-bloco-b/
│   │   ├── sandbox/
│   │   └── ed/
│   └── rep-git-bloco-c/
│       ├── sandbox/
│       └── ed/
```

Seu fluxo de trabalho deve ser algo como:

```bash
# entra na sua pasta pessoal
cd projetos

# baixa o seu repositório do github do bloco
git clone https://github.com/algumacoisa/rep-git-bloco-a

# entra no repositório que foi clonado
cd rep-git-bloco-a 

# cria sua pasta de tarefas do tko vazia para esse bloco de atividades
tko init
# Define a fonte remota de onde as tarefas serão carregadas, por exemplo:
tko remote add ed @ed # para carregar todos repositório padrão de Estrutura de dados

# abre sua pasta de tarefas de forma interativa
tko open
```
