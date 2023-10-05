
// Nesse rascunho esta faltando a parte de dirigir o carro

//++1

class Car{
    pass: number; // Passageiros
    passMax: number; // limite de Passageiros
    gas: number; // tanque
    gasMax: number; // limite do tanque
    km: number; // quantidade de quilometragem
//++1

    constructor() {
        this.pass = 0; // Passageiros
        this.passMax = 2; // limite de Passageiros
        this.gas = 0; // tanque
        this.gasMax = 100; // limite do tanque
        this.km = 0; // quantidade de quilometragem
    }

    enter(): void {
        if (this.pass < this.passMax) {
            this.pass += 1;
            return;
        }
        write("fail: limite de pessoas atingido");
    }

    leave(): void {
        if (this.pass > 0) {
            this.pass-=1;
            return;
        }
        write("fail: nao ha ninguem no carro");
    }

    fuel(gas: number): void {
        this.gas += gas;
        if(this.gas > this.gasMax)
            this.gas = this.gasMax;
    }
    
//--
    drive (km: number): void {
        if(this.pass == 0) {
            write("fail: nao ha ninguem no carro");
        } else if(this.gas == 0) {
            write("fail: tanque vazio");
        }
        else if(this.gas < km) {
            write("fail: tanque vazio apos andar " + this.gas + " km");
            this.km += this.gas;
            this.gas = 0;
        } else{
            this.gas = this.gas - km;
            this.km = this.km + km;
        }
    }

//++1
    toString(): string {
        return "pass: " + this.pass + ", gas: " + this.gas + ", km: " + this.km;
    }
};

//==

let _cin_ : string[] = [];
try { _cin_ = require("fs").readFileSync(0).toString().split(/\r?\n/); } catch(e){}
let input = () : string => _cin_.length === 0 ? "" : _cin_.shift()!;
let write = (text: any, end:string="\n")=> process.stdout.write("" + text + end);

function main() {
    let car = new Car();

    while (true) {
        let line = input();
        write("$" + line);
        let args = line.split(" ");

        if      (args[0] === "show")  { write(car.toString());          }
        else if (args[0] === "enter") { car.enter();                    }
        else if (args[0] === "leave") { car.leave();                    }
        else if (args[0] === "fuel")  { car.fuel(+args[1]);             }
//--
        else if (args[0] === "drive") { car.drive(+args[1]);            }
//==
        else if (args[0] === "end")   { break;                          }
        else                          { write("fail: comando invalido");}
    }
}

main()

