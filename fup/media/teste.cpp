#include <iostream>
#include <iomanip>

int main() {
  int a {}, b{};
  std::cin >> a >> b;
  std::cout << std::fixed << std::setprecision(1) << (a/2.0 + b/2.0) << '\n';
}
