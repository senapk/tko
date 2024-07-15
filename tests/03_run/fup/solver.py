a = float(input())
b = float(input())
c = float(input())

delta = b**2 - 4*a*c
if delta < 0:
    print("nao ha raiz real")
elif delta == 0:
    root = b / (2*a)
    print(root)
else:
    root1 = (-b + delta**0.5) / (2*a)
    root2 = (-b - delta**0.5) / (2*a)
    print(root1)
    print(root2)