#include <iostream>
#include <cmath>

int main() {
    double a {0.0};
    double b {0.0};
    double c {0.0};

    std::cin >> a >> b >> c;
    double delta = b * b - 4 * a * c;

    if (delta < 0 || a == 0) {
        throw std::invalid_argument("Impossivel calcular");
    } else {
        double r1 = (-b + sqrt(delta)) / (2 * a);
        double r2 = (-b - sqrt(delta)) / (2 * a);
        std::cout.precision(5);
        std::cout << std::fixed << r1 << std::endl;
        std::cout << std::fixed << r2 << std::endl;
    }
}