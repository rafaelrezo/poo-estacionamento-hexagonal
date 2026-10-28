// Teste de contrato: as mesmas verificações valem para qualquer adaptador da
// porta RepositorioTickets. Um adaptador novo deve passar por elas.

#include <cstdio>
#include <filesystem>
#include <fstream>
#include <stdexcept>
#include <string>

#include "adaptadores/saida/repositorio_arquivo.hpp"
#include "adaptadores/saida/repositorio_memoria.hpp"
#include "testes/verificacao.hpp"

using namespace estacionamento;
using teste::verificar;

namespace {

const TarifaPorHora tarifa(800, 15);

void verificar_contrato(RepositorioTickets& repositorio, const std::string& nome) {
    const Placa placa("ABC1D23");
    verificar(repositorio.contar_abertos() == 0 && !repositorio.buscar_aberto(placa),
              nome + ": começa vazio");

    repositorio.salvar(Ticket(placa, 480));
    verificar(repositorio.buscar_aberto(placa).has_value() && repositorio.contar_abertos() == 1,
              nome + ": encontra o ticket aberto");

    Ticket fechado = *repositorio.buscar_aberto(placa);
    fechado.fechar(575, tarifa);
    repositorio.salvar(fechado);
    verificar(!repositorio.buscar_aberto(placa) && repositorio.contar_abertos() == 0,
              nome + ": ticket fechado deixa de estar aberto");
    verificar(repositorio.listar().size() == 1, nome + ": fechar substitui, não duplica");

    repositorio.salvar(Ticket(placa, 575));
    verificar(repositorio.listar().size() == 2 && repositorio.contar_abertos() == 1,
              nome + ": reentrada no mesmo minuto cria outro registro");
}

}  // namespace

int main() {
    RepositorioMemoria memoria;
    verificar_contrato(memoria, "memória");

    const std::string caminho =
        (std::filesystem::temp_directory_path() / "teste_estacionamento.txt").string();
    std::remove(caminho.c_str());
    {
        RepositorioArquivo arquivo(caminho);
        verificar_contrato(arquivo, "arquivo");
    }
    RepositorioArquivo reaberto(caminho);
    verificar(reaberto.listar().size() == 2 && reaberto.contar_abertos() == 1,
              "arquivo: dados sobrevivem a uma nova instância");

    {
        std::ofstream corrompido(caminho, std::ios::trunc);
        corrompido << "ABC1D23;480;-;-\nXYZ9876;abc;-;-\n";
    }
    std::string mensagem;
    try {
        RepositorioArquivo invalido(caminho);
    } catch (const std::runtime_error& erro) {
        mensagem = erro.what();
    }
    verificar(mensagem.find("linha 2") != std::string::npos,
              "arquivo: registro corrompido indica a linha");
    std::remove(caminho.c_str());

    return teste::resultado("repositórios");
}
