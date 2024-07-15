#include <iostream>

int main() {
    int x = 0;
    while (true) {
        std::cin >> x;
        if (x == 3) {
            throw std::runtime_error("pane no sistema");
        } else {
            std::cout << x << '\n';
        }
    }
}