draft_rust = r"""
fn main() {
    println!("Hello, World!");
}"""[1:]

draft_go = r"""
package main
import "fmt"
func main() {
    fmt.Println("Hello, World!")
}"""[1:]

draft_js = r"""
const input=(()=>{let l,i=0,P;return()=>process.stdin.isTTY?((P=P||require("readline-sync")).question()):(l=l||require("fs").readFileSync(0,"utf-8").split(/\r?\n/),l[i++])})();
console.log("Hello, World!");
"""

haskell_draft = r"""
main :: IO ()
main = putStrLn "Hello, World!"
"""

c_draft = r"""
#include <stdio.h>
int main() {
    printf("Hello, World!\n");
    return 0;
}
"""

cpp_draft = r"""
#include <iostream>
int main() {
    std::cout << "Hello, World!" << std::endl;
    return 0;
}
"""

java_draft = r"""
public class draft {
    public static void main(String args[]) {
        System.out.println("Hello, World!");
    }
}
"""

ts_draft = r"""
const input = () => ""; // MACRO
export {};
console.log("Hello, World!");
"""[1:]

readme_draft: str = r"""Escreva aqui as informações que você quer salvar, esse é o seu rascunho.
O texto abaixo é informativo e você pode apagar depois de aprender como usar os rascunhos.

## Como usar os rascunhos

- A chave do seu rascunho é o nome da pasta.
- O título do seu rascunho é carregado a partir da primeira linha desse arquivo \#
- Tudo que você fizer nos rascunhos também será rastreado pelo tko.

## Como criar seus próprios testes

Um teste é composto de um `input` (o texto que será fornecido para o programa) e um `output` (o texto que o programa deve retornar para esse input) e pode ter opcionalmente um `label` para facilitar a identificação do teste.

Seus casos de teste personalizados podem ser escritos diretamente aqui na descrição do problema dentro de um fenced code block com a linguagem `toml` ou em um arquivo `tests.toml` na pasta do problema. O TKO irá carregar automaticamente os testes quando a tarefa for aberta ou executada novamente.

Exemplo de teste para ler dois números, um por linha, e imprimir a soma e a subtração deles.

Se quiser habilitar esses casos de teste e ver funcionando, insira algo no input e no output.

```toml
# Exemplo de entrada em uma linha, adicione algo entre as crases para habilitar o teste
[[tests]]
input = ''
output = ''

# Exemplo de entrada em múltiplas linhas, escreva algo nas linhas entre as crases para habilitar o teste
[[tests]]
input = '''
'''
output = '''
'''
```

"""

md_draft = r"""
# Rascunho

Se a tarefa exigir um relatório, escreva ele aqui. Você pode usar markdown, imagens e o que mais quiser para criar um relatório bem completo.
"""[1:]