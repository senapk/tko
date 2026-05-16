Plano de adequação da documentação do TKO (integrada ao repositório de código)

Objetivo geral
Construir uma documentação profissional, consistente e sustentável, com fonte de verdade no próprio repositório, cobrindo onboarding, uso por perfil e manutenção contínua.

Decisão arquitetural de documentação
1. A documentação permanece integrada ao repositório principal.
2. README é a porta de entrada.
3. Wiki contém guias detalhados e operacionais.
4. Opcional: publicação futura em GitHub Pages a partir deste mesmo repositório.

Fase 1.1 - README renovado (concluída)
Objetivo
Ter uma página inicial profissional que responda em menos de 60 segundos:
1. O que é o TKO.
2. Como instalar e rodar.
3. Onde continuar na documentação.

Escopo
1. Hero com proposta de valor.
2. Badges essenciais.
3. Visão geral com fluxo rápido.
4. Quick start mínimo.
5. Navegação por perfis.
6. Contribuição e licença.

Status
1. Estrutura principal do README aplicada.
2. Badges revisadas e estabilizadas.
3. Conteúdo longo de criação de testes movido para a wiki.

Fase 1.2 - Consolidação por perfis (em andamento)
Perfis alvo
1. Professor de disciplina: distribui e coleta atividades (Git, GitHub Classroom recomendado, Dropbox, e-mail).
2. Aluno da disciplina: executa tarefas e acompanha progresso na trilha.
3. Aluno autônomo: baixa exercícios de repositórios oficiais e estuda por conta própria.

Entregáveis
1. Mapa de navegação por perfil no README.
2. Guia do professor com fluxo de autoria e coleta.
3. Guia do aluno da disciplina com caminho de execução.
4. Guia de estudo autônomo com entrada rápida em repositórios oficiais.

Fase 1.3 - Padrão editorial e governança
Padrão editorial
1. PT-BR com acentuação consistente.
2. Nomes de tecnologia padronizados (VS Code, TypeScript, GitHub Classroom).
3. Títulos e links com nomenclatura consistente entre README e wiki.

Governança
1. Toda alteração de fluxo de CLI deve revisar README/wiki no mesmo PR.
2. Checklist de documentação no template de PR.
3. Responsável de revisão de docs por release.

Fase 1.4 - Qualidade e validação
Checklist de qualidade
1. Links principais funcionando.
2. Comandos do quick start validados em Linux/WSL e Windows.
3. Leitura escaneável acima da dobra no README.
4. Preview revisado em desktop e mobile no GitHub.

Métricas de sucesso
1. Tempo até primeiro comando útil menor ou igual a 5 minutos.
2. Redução de dúvidas repetidas de instalação.
3. Menos retrabalho por links quebrados e nomenclatura inconsistente.

Fase 1.5 - Publicação (opcional)
1. Publicar documentação em GitHub Pages sem separar repositório.
2. Manter wiki/README como fonte e usar Pages como camada de apresentação.

Riscos e mitigação
1. README crescer demais.
Mitigação: manter caminho feliz curto e mover detalhes para wiki.
2. Divergência entre código e documentação.
Mitigação: exigir atualização de docs no mesmo PR de mudança funcional.
3. Inconsistência de linguagem entre arquivos.
Mitigação: revisão editorial por release com checklist fixo.

Definition of Done da adequação
1. README responde os 3 pontos principais em menos de 60 segundos.
2. Navegação por perfil está clara e sem ambiguidade.
3. Conteúdo detalhado está na wiki, sem duplicação desnecessária no README.
4. Nomenclatura e linguagem estão consistentes nos guias principais.
5. Processo de manutenção de documentação está definido e ativo.

Próximos passos imediatos
1. Fechar pendências de consistência textual nos guias restantes da wiki.
2. Adicionar checklist de docs no fluxo de PR.
3. Registrar no changelog a conclusão da fase 1 de documentação.