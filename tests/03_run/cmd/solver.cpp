#include <iostream>

int main() {
    int a {}, b{};
    std::cin >> a >> b;
    auto [c, d] = std::make_pair(a, b);
    std::cout << (c + d) << "\n";
}