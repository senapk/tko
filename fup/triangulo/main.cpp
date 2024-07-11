#include <iostream>
#include <vector>
#include <sstream>
#include "lib.hpp"

int main(){
    std::string line;
    std::getline(std::cin, line);
    std::stringstream ss(line);
    std::vector<int> vet;
    int value {};
    while(ss >> value) {
        vet.push_back(value);
    }
    processa(vet);
}