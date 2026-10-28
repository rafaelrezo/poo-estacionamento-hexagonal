// Ponto de montagem (composition root): o único lugar que conhece todas as
// classes concretas. Trocar uma tecnologia muda esta montagem, não o núcleo.

#include <iostream>
#include <memory>
#include <stdexcept>
#include <string>

#include "adaptadores/entrada/interface_texto.hpp"
#include "adaptadores/saida/relogios.hpp"
#include "adaptadores/saida/repositorio_arquivo.hpp"
#include "adaptadores/saida/repositorio_memoria.hpp"
#include "aplicacao/servico_estacionamento.hpp"
#include "dominio/tarifa.hpp"

using namespace estacionamento;

namespace {

struct Opcoes {
    int vagas = 3;
    std::string tarifa = "hora";
    std::string relogio = "simulado";
    std::string arquivo;  // vazio: repositório em memória
};

const char* const USO =
    "uso: estacionamento [--vagas N] [--tarifa hora|fixa] [--relogio simulado|sistema] "
    "[--arquivo CAMINHO]";

Opcoes ler_opcoes(int argc, char* argv[]) {
    Opcoes opcoes;
    for (int i = 1; i < argc; i += 2) {
        const std::string nome = argv[i];
        if (i + 1 >= argc) {
            throw std::invalid_argument(USO);
        }
        const std::string valor = argv[i + 1];
        if (nome == "--vagas") {
            opcoes.vagas = std::stoi(valor);
        } else if (nome == "--tarifa" && (valor == "hora" || valor == "fixa")) {
            opcoes.tarifa = valor;
        } else if (nome == "--relogio" && (valor == "simulado" || valor == "sistema")) {
            opcoes.relogio = valor;
        } else if (nome == "--arquivo") {
            opcoes.arquivo = valor;
        } else {
            throw std::invalid_argument(USO);
        }
    }
    return opcoes;
}

}  // namespace

int main(int argc, char* argv[]) {
    try {
        const Opcoes opcoes = ler_opcoes(argc, argv);

        // Estratégia de cobrança.
        TarifaPorHora por_hora(800, 15);  // R$ 8,00 por hora iniciada, 15 min grátis
        TarifaFixa fixa(2000);            // R$ 20,00 por permanência
        const Tarifa* tarifa = opcoes.tarifa == "fixa" ? static_cast<const Tarifa*>(&fixa)
                                                       : static_cast<const Tarifa*>(&por_hora);

        // Adaptadores de saída.
        RelogioSimulado simulado(8 * 60);  // começa às 08:00
        RelogioSistema sistema;
        const Relogio* relogio = opcoes.relogio == "sistema"
                                     ? static_cast<const Relogio*>(&sistema)
                                     : static_cast<const Relogio*>(&simulado);

        std::unique_ptr<RepositorioTickets> repositorio;
        if (opcoes.arquivo.empty()) {
            repositorio = std::make_unique<RepositorioMemoria>();
        } else {
            repositorio = std::make_unique<RepositorioArquivo>(opcoes.arquivo);
        }

        // Núcleo e adaptador de entrada.
        ServicoEstacionamento servico(opcoes.vagas, *tarifa, *repositorio, *relogio);
        InterfaceTexto interface(servico, opcoes.relogio == "simulado" ? &simulado : nullptr);
        interface.executar(std::cin, std::cout);
        return 0;
    } catch (const std::exception& erro) {
        std::cerr << "falha: " << erro.what() << '\n';
        return 1;
    }
}
