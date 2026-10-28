#include "adaptadores/saida/repositorio_arquivo.hpp"

#include <fstream>
#include <sstream>
#include <stdexcept>
#include <utility>

namespace estacionamento {

namespace {

std::optional<int> ler_campo(const std::string& campo) {
    if (campo == "-") {
        return std::nullopt;
    }
    std::size_t usados = 0;
    const int valor = std::stoi(campo, &usados);
    if (usados != campo.size()) {
        throw std::invalid_argument("número inválido: " + campo);
    }
    return valor;
}

std::string escrever_campo(std::optional<int> valor) {
    return valor.has_value() ? std::to_string(*valor) : "-";
}

}  // namespace

RepositorioArquivo::RepositorioArquivo(std::string caminho) : caminho_(std::move(caminho)) {
    carregar();
}

void RepositorioArquivo::carregar() {
    std::ifstream arquivo(caminho_);
    if (!arquivo) {
        return;  // arquivo ainda não existe: histórico vazio
    }
    std::string linha;
    int numero = 0;
    while (std::getline(arquivo, linha)) {
        ++numero;
        if (linha.empty()) {
            continue;
        }
        try {
            std::istringstream partes(linha);
            std::string placa, entrada, saida, valor;
            if (!std::getline(partes, placa, ';') || !std::getline(partes, entrada, ';') ||
                !std::getline(partes, saida, ';') || !std::getline(partes, valor)) {
                throw std::invalid_argument("esperados 4 campos");
            }
            memoria_.salvar(Ticket::restaurar(Placa(placa), *ler_campo(entrada),
                                              ler_campo(saida), ler_campo(valor)));
        } catch (const std::exception& erro) {
            throw std::runtime_error(caminho_ + ", linha " + std::to_string(numero) +
                                     ": registro inválido (" + erro.what() + ")");
        }
    }
}

void RepositorioArquivo::gravar() const {
    std::ofstream arquivo(caminho_, std::ios::trunc);
    if (!arquivo) {
        throw std::runtime_error("não foi possível gravar " + caminho_);
    }
    for (const Ticket& ticket : memoria_.listar()) {
        arquivo << ticket.placa().texto() << ';' << ticket.entrada() << ';'
                << escrever_campo(ticket.saida()) << ';'
                << escrever_campo(ticket.valor_centavos()) << '\n';
    }
}

void RepositorioArquivo::salvar(const Ticket& ticket) {
    memoria_.salvar(ticket);
    gravar();
}

std::optional<Ticket> RepositorioArquivo::buscar_aberto(const Placa& placa) const {
    return memoria_.buscar_aberto(placa);
}

int RepositorioArquivo::contar_abertos() const { return memoria_.contar_abertos(); }

std::vector<Ticket> RepositorioArquivo::listar() const { return memoria_.listar(); }

}  // namespace estacionamento
