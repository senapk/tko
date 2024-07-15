#include "fn.hpp" // https://raw.githubusercontent.com/senapk/cppaux/master/fn.hpp

// Nesse rascunho esta faltando a parte de dirigir o carro

//++1
class Car {
public:
    int pass;
    int passMax;
    int gas;
    int gasMax;
    int km;
//++1

    Car() {
        pass = 0;
        passMax = 2;
        gas = 0;
        gasMax = 100;
        km = 0;
    }

    void enter() {
        if (pass < passMax) {
            pass++;
        } else {
            fn::write("fail: limite de pessoas atingido");
        }
    }

    void leave() {
        if (pass > 0) {
            pass--;
        } else {
            fn::write("fail: nao ha ninguem no carro");
        }
    }

    void fuel(int gas) {
        this->gas += gas;
        if (this->gas > gasMax) {
            this->gas = gasMax;
        }
    }
//--
    void drive(int km) {
        if (pass == 0) {
            fn::write("fail: nao ha ninguem no carro");
        } else if (gas == 0) {
            fn::write("fail: tanque vazio");
        } else if (this->gas < km) {
            fn::print("fail: tanque vazio apos andar {} km\n", this->gas);
            this->km += this->gas;
            this->gas = 0;
        } else {
            this->km += km;
            this->gas -= km;
        }
    }
    
//++1
    std::string str() {
        return fn::format("pass: {}, gas: {}, km: {}", pass, gas, km);
    }
};

//==
int main() {
    Car car;
    while (true) {
        auto line = fn::input();
        auto args = fn::split(line, ' ');
        fn::write("$" + line);

        if      (args[0] == "show")  { fn::write(car.str());                }
        else if (args[0] == "enter") { car.enter();                         } 
        else if (args[0] == "leave") { car.leave();                         }
        else if (args[0] == "fuel")  { car.fuel(+args[1]);                  }
//--
        else if (args[0] == "drive") { car.drive(+args[1]);                 }
//==
        else if (args[0] == "end")   { break;                               }
        else                         { fn::write("fail: comando invalido"); }
    }
}
