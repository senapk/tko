#pragma once
#include "fn.hpp"

#include <iostream>
class Car {
public:
    int pass;
    int passMax;
    int gas;
    int gasMax;
    int km;

    Car() {
        pass = 0;
        passMax = 2;
        gas = 0;
        gasMax = 0;
        km = 0;
    }

    void enter() {
        if (pass < passMax) {
            pass++;
        } else {
            std::cout << "fail: limite de pessoas atingido\n";
        }
    }

    void leave() {
        if (pass > 0) {
            pass -= 1;
        } else {
            fn::write("fail: nao ha ninguem no carro");
        }
    }

    void fuel(int gas) {
        (void) gas;
    }

    void drive(int km) {
        (void) km;
    }

    std::string str() const {
        return fn::format("pass: {}, gas: {}, km: {}", pass, gas, km);
    }
};

inline std::ostream& operator<<(std::ostream& os, const Car& car) {
    return os << car.str();
}
