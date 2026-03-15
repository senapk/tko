# QA

## Criação e Execução

- criar repositório vazio
  - tko init
- tentar criar um repositório vazio dentro de um repositório tko existente ele deve impedir
  - mkdir pasta
  - cd pasta
  - tko init
- se tentar criar um repositório tko numa pasta que dentro dela já existe um repositório tko ele deve impedir
  - cd ..
  - tko init
- abrir
  - tko open
- criar 2 rascunhos usando atalho
  - verificar se é possível criar dois rascunhos com o mesmo nome
  - executar em diferentes linguagens
  - voltar
- entrar em uma subpasta sandbox/00_rascunhos, abrir novamente para verificar a busca recursiva nos nós pais
  - tko open
- executar os rascunhos em diferentes linguagens com e sem os testes

## Build

- gerar um arquivo de testes a partir do readme

## Collect

- fazer pull em lote descartando operações locais
- fazer collect em lote