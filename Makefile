CXX ?= g++
CXXFLAGS ?= -std=c++17 -Wall -Wextra -Werror -pedantic
PYTHON ?= python3
BUILD := build
ARGS ?= --vagas 2

FONTES := $(shell find cpp/dominio cpp/aplicacao cpp/adaptadores -name '*.cpp')
OBJETOS := $(patsubst cpp/%.cpp,$(BUILD)/obj/%.o,$(FONTES))
TESTES := $(patsubst cpp/testes/%.cpp,$(BUILD)/testes/%,$(wildcard cpp/testes/teste_*.cpp))

.SECONDARY:

.PHONY: build test arquitetura test-cpp test-python test-cli run-cpp run-python clean

build: $(BUILD)/estacionamento $(TESTES)

$(BUILD)/estacionamento: $(OBJETOS) $(BUILD)/obj/main.o
	$(CXX) $(CXXFLAGS) $^ -o $@

$(BUILD)/testes/%: $(BUILD)/obj/testes/%.o $(OBJETOS)
	@mkdir -p $(@D)
	$(CXX) $(CXXFLAGS) $^ -o $@

$(BUILD)/obj/%.o: cpp/%.cpp
	@mkdir -p $(@D)
	$(CXX) $(CXXFLAGS) -Icpp -MMD -MP -c $< -o $@

-include $(shell find $(BUILD)/obj -name '*.d' 2>/dev/null)

# Um único comando local; a CI executa exatamente o mesmo.
test: arquitetura test-cpp test-python test-cli

arquitetura:
	$(PYTHON) tools/verificar_arquitetura.py

test-cpp: build
	@for t in $(TESTES); do ./$$t || exit 1; done

test-python:
	cd python && $(PYTHON) -m unittest discover -s tests -v

test-cli: build
	$(PYTHON) tools/comparar_cli.py --cpp $(BUILD)/estacionamento

run-cpp: build
	./$(BUILD)/estacionamento $(ARGS)

run-python:
	cd python && $(PYTHON) -m estacionamento $(ARGS)

clean:
	rm -rf $(BUILD)
