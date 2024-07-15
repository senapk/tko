#include <iostream>

int main() {
    int x = 0;
    while (true) {
        std::cin >> x;
        if (x == 3) {
            int vet[1];
            for (int i = 0; i < 10000; i++)
                vet[i] = 0;
            std::cout << vet[0];
        } else {
            std::cout << x << '\n';
        }
    }
}