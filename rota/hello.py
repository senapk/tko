import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("name", type=str, help="Your name")
    args = parser.parse_args()
    print(f"Hello, {args.name}!")
    say_hello()    

def say_hello():
    print("Olá, mundo!")

def sum(a: int, b: int) -> int:
    return a + b

if __name__ == "__main__":
    main()
