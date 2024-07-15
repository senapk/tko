#include <iostream>

int main() {
    int vet[1];
    for (int i = 0; i < 10000; i++)
        vet[i] = 0;
    std::cout << vet[0];
}