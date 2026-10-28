# Guia de arquitetura

Este guia explica as decisões do projeto. Os nomes de arquivos valem para C++ (`cpp/`)
e Python (`python/estacionamento/`).

---

## 1. De onde partimos

A versão mais curta deste sistema caberia em uma função: ler uma linha do teclado,
consultar um vetor global, calcular o preço e imprimir. Ela funciona até que alguém peça:

- testar a cobrança de 95 minutos **sem esperar 95 minutos**;
- guardar o histórico em arquivo, depois em banco;
- oferecer a mesma operação numa tela web.

Em cada pedido, a regra de cobrança é reescrita ou copiada, porque ela está misturada
com teclado, arquivo e relógio. A arquitetura hexagonal ataca exatamente esse problema.

## 2. Arquitetura hexagonal (Portas e Adaptadores)

Proposta por Alistair Cockburn em 2005. O hexágono é só um desenho: o número de lados
não importa. A ideia é separar **dentro** (regras) de **fora** (tecnologias).

| Elemento | Pergunta que responde | Neste projeto |
|---|---|---|
| Domínio | quais são as regras do negócio? | `Placa`, `Ticket`, `Tarifa` |
| Casos de uso | o que o sistema oferece? | `ServicoEstacionamento` |
| Porta de entrada | como o mundo pede algo ao núcleo? | operações públicas do serviço |
| Porta de saída | do que o núcleo precisa do mundo? | `RepositorioTickets`, `Relogio` |
| Adaptador de entrada | quem traduz um pedido externo? | `InterfaceTexto`, os testes |
| Adaptador de saída | quem implementa uma porta com uma tecnologia? | `RepositorioMemoria`, `RepositorioArquivo`, `RepositorioSQLite`, `RelogioSistema`, `RelogioSimulado` |
| Montagem | quem escolhe as peças concretas? | `main.cpp`, `__main__.py` |

**Por que o relógio é uma porta?** Ler a hora do computador é entrada externa, como ler
um arquivo. Tratado como porta, o teste controla o tempo com `RelogioSimulado` e
verifica 15, 16, 60 e 61 minutos instantaneamente.

**Por que a tarifa não é uma porta?** Ela é regra do negócio, não tecnologia. Varia por
Strategy *dentro* do núcleo. Nem toda interface é uma porta.

## 3. A regra de dependência

> Dependências de código apontam para dentro. O núcleo não inclui nem importa adaptadores.

```text
adaptadores  ──►  aplicacao  ──►  dominio
     │                               ▲
     └───────────────────────────────┘
```

Quem implementa uma porta (adaptador) depende dela; a porta não depende de quem a
implementa. É a inversão de dependência (o "D" de SOLID) aplicada a todas as bordas.

A regra é verificada automaticamente por `tools/verificar_arquitetura.py`, que também
proíbe E/S no núcleo (`<iostream>`, `<fstream>`, `<chrono>`; `sqlite3`, `time`, `sys`...).
Uma revisão de código ainda é necessária: a ferramenta vê `#include` e `import`, não
intenções.

## 4. Clean Architecture: a mesma regra em círculos

Robert C. Martin (2012) reuniu a hexagonal e propostas parecidas num desenho de
círculos concêntricos. A regra de dependência é a mesma.

| Clean Architecture | Hexagonal | Neste projeto |
|---|---|---|
| Entities | domínio | `dominio/` |
| Use Cases | casos de uso + portas | `aplicacao/` |
| Interface Adapters | adaptadores | `adaptadores/` |
| Frameworks & Drivers | tecnologia usada pelos adaptadores | `std::fstream`, `sqlite3`, terminal |

A Clean acrescenta vocabulário (presenters, gateways, modelos de entrada e saída). Ele é
útil em sistemas grandes, mas não é necessário para entender a ideia central. Aqui,
cada caso de uso devolve um `Ticket` e o adaptador formata a resposta.

### Cuidado com nomes iguais e significados diferentes

| Termo | Significado aqui | Outro significado comum |
|---|---|---|
| Adaptador (hexagonal) | qualquer componente na borda que liga uma tecnologia a uma porta | **Adapter (GoF)**: traduz uma interface existente para a interface esperada. Um adaptador hexagonal pode ou não usar esse padrão. |
| Controller (Clean) | adaptador de entrada que recebe um pedido | um "controlador" de automação que **decide** atuação é regra, logo núcleo |
| Repository | porta de saída para guardar e recuperar objetos do domínio | não é sinônimo de "classe que fala com o banco": a interface é do núcleo; o SQL é do adaptador |

## 5. Padrões que aparecem no projeto

| Padrão | Onde | Problema que resolve |
|---|---|---|
| Strategy | `Tarifa`, `TarifaPorHora`, `TarifaFixa` | trocar a cobrança sem mudar o serviço |
| Repository | `RepositorioTickets` e adaptadores | o serviço pede tickets, não monta SQL nem lê linhas |
| Adapter | `RepositorioArquivo`, `RepositorioSQLite`, `InterfaceTexto` | traduzir arquivo, tabela ou texto para objetos do domínio |
| Objeto de valor | `Placa` | uma placa inválida não chega a existir |
| Composição | `RepositorioArquivo` contém um `RepositorioMemoria` | reaproveitar comportamento sem herança |
| Teste de contrato | `teste_repositorios` / `test_repositorios` | todo adaptador de uma porta obedece às mesmas regras |

## 6. Comparação de estilos de organização

| Técnica/Padrão | Melhor uso | Esforço | Entregável | Limitação |
|---|---|---|---|---|
| Tudo em `main` | script curto, descartável | mínimo | um arquivo | regra presa à E/S; difícil testar |
| Camadas tradicionais (apresentação → negócio → dados) | CRUD com uma tecnologia estável | baixo | pastas por camada | negócio costuma depender do banco |
| Hexagonal | regras que precisam de testes rápidos e de tecnologias trocáveis | médio | núcleo, portas, adaptadores, montagem | mais interfaces; excesso de portas vira burocracia |
| Clean Architecture | sistemas grandes, várias equipes e interfaces | alto | círculos, modelos de entrada e saída, presenters | vocabulário extenso para problemas pequenos |

**Recomendação prática**

- Programa de uma tela e uma regra: comece simples e extraia quando a dor aparecer.
- Regra importante com relógio, arquivo, rede ou banco: hexagonal leve, como aqui.
- Crie porta só onde há tecnologia externa ou substituição real (teste ou produção).
- Adote o vocabulário completo da Clean quando o tamanho do sistema justificar.

## 7. Fontes de referência

- Alistair Cockburn, [*Hexagonal Architecture*](https://alistair.cockburn.us/hexagonal-architecture/).
- Robert C. Martin, [*The Clean Architecture*](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html).
- [C++ Core Guidelines — Interfaces](https://isocpp.github.io/CppCoreGuidelines/CppCoreGuidelines#S-interfaces).
- [Python — `abc`](https://docs.python.org/3/library/abc.html) e [`sqlite3`](https://docs.python.org/3/library/sqlite3.html).
