class Drafts:
    ts_draft = r"""
const input = () => ""; //essa função será gerada pelo TKO na execução
export {};

function main() {
    console.log("qxcode");
}
main();
"""[1:]

    c_draft = r"""
#include <stdio.h>

int main() {
    puts("qxcode");
    return 0;
}

"""[1:]

    cpp_draft = r"""
#include <iostream>

int main() {
    std::cout << "qxcode\n";
}

"""[1:]

    java_draft = r"""
public class draft {
    public static void main(String args[]) {
        System.out.println("qxcode");
    }
}

"""[1:]

    go_draft = (
        r"package main""\n"
        r'import "fmt"'"\n"
        r"func main() {""\n"
        r'    fmt.Println("qxcode")''\n'
        r"}""\n"
    )
    
    yaml_draft = r"""
build: comando para construir o executável
run: comando para rodar o programa
"""[1:]


    drafts = {'c': c_draft, 'cpp': cpp_draft, 'ts': ts_draft, 'java': java_draft, 'go': go_draft, 'yaml': yaml_draft}