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
        }
    }

    void leave() {
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
