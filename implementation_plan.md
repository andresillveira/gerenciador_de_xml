# Plano de Implementação: Gerenciador de XML Fiscal (100% Offline & Nativo) - APROVADO

Este documento detalha o plano de desenvolvimento para uma aplicação desktop nativa e offline projetada para gerenciar, visualizar, filtrar e gerar relatórios a partir de milhares (até 50.000+) de arquivos XML de documentos fiscais eletrônicos brasileiros (NF-e, NFC-e, CT-e).

---

## Arquitetura de Alto Nível & Escolha da Stack

Para atender aos requisitos de **alta performance (50.000+ XMLs)**, **100% offline**, **interface moderna e responsiva**, e **compatibilidade com múltiplos monitores e temas (claro/escuro)**, adotamos a seguinte stack:

1. **Linguagem**: Python 3.10+ (Robusto, excelente suporte a XML, banco de dados e manipulação de arquivos).
2. **Interface Gráfica (GUI)**: **PySide6 (Qt6 oficial para Python)**.
   * O PySide6 (Qt6) oferece controle refinado de memória e renderização para listas massivas através do padrão Model/View (usando `QTableView` + `QAbstractTableModel`). Isso permite carregar 50.000 registros na memória consumindo poucos megabytes, com rolagem fluida, suporte a múltiplos monitores (High-DPI scaling nativo) e detecção dinâmica do tema do sistema operacional.
3. **Banco de Dados Local**: **SQLite3** (embutido no Python).
   * Os arquivos XML originais continuam na pasta do usuário. O software cria um índice no SQLite contendo os metadados cruciais extraídos. Isso permite buscas instantâneas (< 5ms) mesmo com 100.000 registros.
4. **Leitor de XML**: `xml.etree.ElementTree` nativo do Python (extremamente veloz).
5. **Gerenciador de Processos Paralelos**: `QThreadPool` + `QRunnable` para realizar a varredura e leitura de XMLs em segundo plano, garantindo que a interface gráfica nunca trave.
6. **Gerador de PDF (DANFE/DACTE)**: Utilizaremos a biblioteca **`brazilfiscalreport`** (disponível no GitHub / PyPI). Ela gera PDFs padrão oficiais de DANFE e DACTE a partir do XML usando `fpdf2`, garantindo conformidade com a SEFAZ e qualidade profissional.

---

## Diretrizes do Usuário (Feedback Integrado)

> [!IMPORTANT]
> **1. Visualização em PDF (DANFE/DACTE)**: Implementado estritamente com a biblioteca oficial **`brazilfiscalreport`** para gerar visualizações/PDFs com conformidade fiscal e layout padrão (DANFE para NF-e/NFC-e e DACTE para CT-e).
>
> **2. Exclusão Física com Confirmação**: Quando o usuário solicitar a exclusão de um XML de dentro da aplicação, o software exibirá uma caixa de diálogo de confirmação clara, alertando que o arquivo correspondente no disco rígido também será excluído definitivamente, aguardando aprovação explícita para prosseguir.
>
> **3. Campo Entrada/Saída (`tpNF`)**: No banco de dados e no XML Parser, extrairemos o campo `tpNF` (`0` para Entrada, `1` para Saída). Este campo será exibido na listagem e disponibilizado como um dos filtros principais na barra lateral.

---

## Proposed Changes

Organização modular do projeto:

```
gerenciador_de_xml/
│
├── main.py                     # Ponto de entrada da aplicação
├── config.py                   # Configurações globais e de tema
│
├── core/                       # Regras de Negócio e Banco de Dados
│   ├── __init__.py
│   ├── database.py             # Schema SQLite, índices e consultas com campo tpNF
│   ├── xml_parser.py           # Parser ultra-rápido para NF-e/NFC-e/CT-e (extrai tpNF)
│   └── file_watcher.py         # Sincronizador de diretórios (Disk Sync)
│
├── gui/                        # Interface de Usuário (PySide6)
│   ├── __init__.py
│   ├── styles.py               # QSS (CSS do Qt) e paletas Claro/Escuro
│   ├── main_window.py          # Janela principal e controle de layouts
│   ├── components/
│   │   ├── table_view.py       # Tabela de alta performance baseada em QAbstractTableModel
│   │   ├── filter_sidebar.py   # Painel de filtros avançados (inclui Entrada/Saída)
│   │   ├── xml_viewer.py       # Visualizador de tags e exibição do PDF gerado pelo brazilfiscalreport
│   │   └── settings_dialog.py  # Configurações de pastas e temas
│   └── workers.py              # Threads de segundo plano para indexação
│
└── reports/                    # Geração de Relatórios
    ├── __init__.py
    ├── excel_exporter.py       # Exportação para XLS/CSV
    └── pdf_exporter.py         # Integração com brazilfiscalreport para exportação individual/lote
```

---

### Componentes Detalhados

#### 1. Módulo Core (Banco de Dados & Parser XML)
* **`core/database.py`**:
  * Criação do banco SQLite em `~/.gerenciador_xml/data.db`.
  * Schema contendo colunas: `chave_acesso`, `numero`, `serie`, `modelo`, `data_emissao`, `cnpj_emitente`, `nome_emitente`, `cnpj_destinatario`, `nome_destinatario`, `valor_total`, `tipo_nf` (0 = Entrada, 1 = Saída), `caminho_arquivo`.
  * Índices nas colunas de busca frequente para garantir performance com 50k+ XMLs.
* **`core/xml_parser.py`**:
  * Parsing rápido de XML.
  * Extração de `tpNF` (`<tpNF>`) para NF-e/NFC-e. Para CT-e, assumimos Entrada/Saída correspondente ou nulo conforme aplicável.
* **`core/file_watcher.py`**:
  * Varredura recursiva de diretórios selecionados para manter o SQLite sincronizado com o disco.

#### 2. Módulo GUI (Interface Moderna em PySide6)
* **`gui/styles.py`**:
  * Visual moderno (glassmorphism leve, cores HSL premium, cantos arredondados, transições sutis de hover) adaptável ao tema do sistema operacional.
* **`gui/main_window.py`**:
  * Layout responsivo de 3 painéis: Filtros (Esquerda), Lista Principal (Centro) e Visualizador / Detalhes (Direita).
  * Exclusão de arquivos: aciona mensagem de confirmação nativa (`QMessageBox.warning`) alertando que a remoção apagará o arquivo físico correspondente.
* **`gui/components/table_view.py`**:
  * `QTableView` utilizando paginação sob demanda ou `QAbstractTableModel` virtualizado para exibição instantânea de 50.000+ linhas sem gargalos de memória.
* **`gui/components/xml_viewer.py`**:
  * Exibe o XML bruto identado com realce de sintaxe.
  * Integração com `brazilfiscalreport` para renderizar visualização em PDF gerada na hora e exibida na tela.

#### 3. Módulo de Relatórios (`reports/`)
* **`reports/excel_exporter.py`**:
  * Exporta registros filtrados para CSV e Excel (.xlsx).
* **`reports/pdf_exporter.py`**:
  * Integração direta com `brazilfiscalreport` para gerar e salvar PDFs de DANFE/DACTE em lote ou individualmente.


---

## Plano de Execução em Etapas

Para garantir o sucesso do desenvolvimento de um aplicativo tão complexo, dividiremos a execução em **4 Etapas Incrementais**:

### Etapa 1: Base de Dados, Parser de XML e Motor de Busca (Core)
* Criar estrutura de banco de dados SQLite otimizada.
* Implementar o parser robusto de XML para os modelos NF-e, NFC-e e CT-e.
* Criar testes unitários automáticos com XMLs reais/fictícios para garantir resiliência contra variações de formatos de XML do governo (SEFAZ).

### Etapa 2: Layout Base, Tema Dinâmico e Tabela de Alta Performance (GUI Base)
* Desenvolver a janela principal responsiva com PySide6.
* Configurar o gerenciador de estilos (QSS) com suporte a tema escuro/claro automático baseado no SO (`darkdetect`).
* Construir a tabela de listagem de XMLs de alta performance capaz de rolar 50.000+ linhas instantaneamente.

### Etapa 3: Sincronização de Pastas em Background e Filtros Avançados
* Implementar threads secundárias (`QThreadPool`) para varrer e indexar pastas de XMLs sem congelar a UI.
* Construir a barra de filtros interativa (Filtro por emitente, destinatário, valor, data inicial/final, tipo de documento e palavra-chave).
* Adicionar suporte a marcadores/tags personalizadas no banco de dados para organização lógica.

### Etapa 4: Visualizador (Tags + PDF) e Relatórios
* Implementar o visualizador de XML em árvore e texto com destaque de sintaxe.
* Desenvolver a visualização bonita do documento fiscal (estilo DANFE simplificado) e motor de exportação direta para PDF físico.
* Criar a exportação de planilhas Excel/CSV a partir dos filtros ativos na tabela.

---

## Plano de Verificação

### Testes Automatizados
* **Script de Geração de Carga**: Criaremos um script utilitário em Python para gerar de 10.000 a 50.000 arquivos XML fictícios com dados variados para testar o estresse, tempo de indexação e velocidade da tabela.
* **Verificação de Parser**: Validação do parser contra um conjunto diversificado de XMLs (com e sem eventos fiscais, com diferentes tributações).

### Verificação Manual
* Teste de redimensionamento da janela e movimentação entre monitores com diferentes resoluções e densidades de pixel (High-DPI).
* Teste de alternância dinâmica do tema no Windows (de Claro para Escuro) para garantir que o app se adapta sem precisar reiniciar.
