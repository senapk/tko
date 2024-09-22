class Drafts:
    ts_draft = r"""
function input(): string { let X: any = input; X.L = X.L || require("fs").readFileSync(0).toString().split(/\r?\n/); return X.L.shift(); } // _TEST_ONLY_
// function input(): string { let X: any = input; X.P = X.P || require("readline-sync"); return X.P.question() } // _FREE_ONLY_
function write(text: any, endl="\n") { process.stdout.write("" + text + endl); }
export {};

function main() {
    write("qxcode");
}
main();
"""[1:]

    js_draft = r"""
function input() { let X = input; X.L = X.L || require("fs").readFileSync(0).toString().split(/\r?\n/); return X.L.shift(); }  // _TEST_ONLY_
// function input() { let X = input; X.P = X.P || require("readline-sync"); return X.P.question() }  // _FREE_ONLY_
function write(text, endl="\n") { process.stdout.write("" + text + endl); }

function main() {
    write("qxcode");
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


    drafts = {'c': c_draft, 'cpp': cpp_draft, 'ts': ts_draft, 'js': js_draft, 'java': java_draft, 'go': go_draft}