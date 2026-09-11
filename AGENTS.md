# Instruções para agentes

## Tipagem Python

- Todo código novo ou alterado deve ter tipagem estática explícita e completa.
- Não introduza valores, parâmetros, retornos ou atributos com tipo desconhecido para o Pylance.
- Prefira tipos concretos e protocolos bem definidos; use `Any` apenas quando inevitável e documente a razão localmente.
- Ajuste anotações dos limites entre camadas (UI, domínio e repositório) para que tipos desconhecidos não se propaguem.
- Ao receber uma dependência que usa apenas parte de outra classe, declare um `Protocol` com essa interface mínima em vez de exigir a classe concreta. Isso deve permitir dublês de teste tipados estruturalmente, sem `cast` ou `# type: ignore`.
- Antes de concluir alterações que envolvam tipos, execute o verificador também nos testes modificados; não configure o projeto para ocultar diagnósticos dos testes.
