SRC = solver.cpp
EXEC = .build/solver.out
INPUT_FILE = .build/input.txt

build: $(SRC)
	g++ -Wall $(SRC) -o $(EXEC)

# A entrada é coletada pelo cat
# Depois é repassada para o executável
run: $(EXEC)
	@cat > $(INPUT_FILE)
	./$(EXEC) < $(INPUT_FILE)
