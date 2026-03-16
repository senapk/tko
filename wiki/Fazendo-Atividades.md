# Tutorial do Aluno — Como Estudar e Resolver Tarefas com o TKO

Este guia explica como estudar e resolver tarefas utilizando o **tko** de forma eficiente.

## Tópicos abordados

- Como fazer as tarefas utilizando o tko
- Como funcionam os testes automáticos
- Tipos de atividades em um repositório
- Como começar uma nova questão
- O que fazer ao terminar uma questão
- Boas práticas de commits e push
- Como usar IA durante o estudo

---

# Como fazer as tarefas utilizando o tko

O fluxo de trabalho no tko segue um ciclo simples:

```
ler o problema
↓
pensar na solução
↓
escrever código
↓
executar testes
↓
analisar erros
↓
corrigir
↓
repetir
```

Esse ciclo é importante porque o aprendizado ocorre principalmente através de **tentativas e correções**.

Fluxo típico:

1. abrir o repositório de tarefas
2. escolher uma tarefa disponível
3. abrir o arquivo de rascunho
4. implementar sua solução
5. executar os testes
6. corrigir erros até passar em todos os testes

---

# Como funcionam os testes automáticos

Algumas tarefas possuem testes automáticos.

Esses testes verificam se o programa funciona corretamente para diferentes entradas.

Exemplo:

```
entrada: 3 5
saída esperada: 8
```

Quando você executa os testes:

1. seu programa é executado
2. uma entrada é fornecida
3. a saída do seu programa é comparada com a saída esperada

Exemplo de resultado:

```
✓ teste 1 passou
✓ teste 2 passou
✗ teste 3 falhou
```

Enquanto houver falhas, sua solução ainda precisa ser corrigida.

---

# Tipos de atividades em um repositório

Existem dois tipos principais de tarefas.

## tarefas com testes automáticos (`:leet`)

Essas tarefas possuem verificação automática.

Você deve implementar o programa até que todos os testes passem.

Vantagens:

- feedback rápido
- correção automática
- validação objetiva

## tarefas abertas (`:open`)

Essas tarefas não possuem testes automáticos.

Nesse caso você deve:

- testar manualmente
- validar sua lógica com exemplos
- discutir a solução

Essas tarefas focam mais em **raciocínio e exploração**.

---

# Como começar uma nova questão

### 1. Leia o problema com atenção

Antes de programar pergunte:

- qual é a entrada?
- qual é a saída?
- o que exatamente o programa deve fazer?

### 2. Pense em exemplos

Antes de escrever código, teste mentalmente alguns casos.

### 3. Planeje a solução

Pergunte:

- preciso de um `if`?
- preciso de um `loop`?
- preciso de um acumulador?

### 4. Comece simples

Resolva primeiro o caso mais simples e depois evolua a solução.

---

# Estratégia recomendada

```
resolver um caso simples
↓
rodar testes
↓
corrigir erros
↓
melhorar o código
```

Evite tentar resolver tudo de uma vez.

---

# O que fazer ao terminar a questão

Quando todos os testes passarem:

1. revise seu código
2. verifique se está claro
3. entenda **por que sua solução funciona**

Se possível:

- teste novos exemplos
- discuta sua solução

O objetivo não é apenas passar nos testes, mas **entender o problema**.

---

# Boas práticas de commits e push

Durante o desenvolvimento registre seu progresso.

### Faça commits frequentes

Exemplo:

```
git commit -m "resolve caso básico"
git commit -m "corrige erro no loop"
git commit -m "passa todos os testes"
```

Commits pequenos ajudam a acompanhar sua evolução.

### Faça push regularmente

```
git push
```

Envie seu progresso diariamente ou após completar tarefas importantes.

---

# Como usar IA durante as tarefas

Ferramentas de IA podem ajudar no aprendizado, mas devem ser usadas com responsabilidade.

O objetivo do curso é desenvolver **seu raciocínio**, não apenas gerar código.

## Sempre: estudar conceitos

Use IA para entender conceitos.

Exemplos:

- explicar como funciona um `for`
- diferença entre tipos de divisão
- explicar estruturas de controle

## Ocasionalmente: entender o problema

Se tiver dificuldade com o enunciado, peça ajuda para:

- explicar o problema
- gerar exemplos de entrada e saída

## Raramente: debugar

Se você já tentou resolver e não encontra o erro, peça ajuda para:

- identificar possíveis erros
- explicar o comportamento do código

Evite pedir que a IA escreva a solução completa.

## Quase nunca: gerar código

Evite perguntas como:

```
Resolva esse problema em Python
```

Isso impede o aprendizado.

## Sempre após terminar: explorar soluções

Depois de resolver o problema sozinho, use IA para aprender mais:

- outras formas de resolver
- soluções mais eficientes
- diferentes abordagens

---

# Regra simples para usar IA

```
IA para aprender → sempre
IA para entender o problema → às vezes
IA para debugar → raramente
IA para gerar código → quase nunca
IA para explorar soluções → sempre após terminar
```

Seguindo essa regra, a IA se torna uma ferramenta de aprendizado e não um atalho.


# Ao final, faça sua auto-avaliação informando

- Com quem fez a tarefa (se fez sozinho ou com ajuda)
- Quanto tempo se dedicou
- Se usou IA e como usou