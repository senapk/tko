#include <stdio.h>
int main() {
    int a = 0, b = 0, c = 0;
    scanf("%d %d %d", &a, &b, &c);

    if ((a >= b + c) || (b >= a + c) || (c > a + b))
        puts("False");
    else
        puts("True");
}

