# Gerenciador de XML Fiscal (100% Offline & Nativo)

Um gerenciador desktop de arquivos XML de documentos fiscais eletrônicos brasileiros (**NF-e**, **NFC-e** e **CT-e**). O sistema foi projetado para ser 100% offline, altamente performático e capaz de gerenciar e filtrar bases massivas com **mais de 50.000 documentos** de forma fluida.

---

## ✨ Funcionalidades Principais

* 🚀 **Alta Performance (Model/View)**: Tabela virtualizada que suporta rolagem e exibição de mais de 50.000 XMLs instantaneamente, rodando a 60 FPS com consumo mínimo de memória.
* 🔍 **Busca e Filtros Dinâmicos**: Filtre notas por CNPJ/CPF de emitentes e destinatários, data de emissão, valores mínimo/máximo, modelo da nota e tipo do documento (**Entrada ou Saída**).
* 📁 **Sincronização em Background**: A varredura de arquivos do disco ocorre em segundo plano via thread pool, evitando qualquer travamento da interface.
* 📄 **Visualizador Duplo**:
  * **DANFE/DACTE Rápido**: Preview instantâneo dos dados da nota e a tabela completa dos produtos reais contidos no XML.
  * **Código XML**: Exibição das tags estruturadas com realce de sintaxe colorido.
* 🖨️ **Geração de PDF Oficial**: Integração com a biblioteca `brazilfiscalreport` para compilar e abrir PDFs oficiais padrão SEFAZ no leitor nativo do sistema operacional.
* 🗑️ **Exclusão Física Protegida**: Opção de exclusão com pop-up de aviso duplo explícito para confirmar a destruição física definitiva do arquivo no disco.
* 📊 **Relatórios em Lote**: Exportação das notas filtradas no grid ativo para planilhas Excel (`.xlsx`) ou CSV com colunas auto-ajustadas.
* 🎨 **Visual Premium com Tema Claro/Escuro**: Interface responsiva com folhas de estilo QSS avançadas, adaptando-se automaticamente ao tema do sistema operacional.

---

## 🛠️ Stack Tecnológica

* **Linguagem**: Python 3.11+
* **Interface Gráfica (GUI)**: PySide6 (Qt6 oficial para Python)
* **Banco de Dados**: SQLite3 (para indexação de busca ultrarrápida < 5ms)
* **Geração de PDFs**: brazilfiscalreport (fpdf2)
* **Relatórios e Planilhas**: Pandas & openpyxl
* **Detecção de Tema**: darkdetect

---

## 🚀 Como Instalar e Rodar

### Prerrequisitos
* Python 3.10 ou 3.11 instalado.
* Gerenciador de pacotes [uv](https://github.com/astral-sh/uv) (opcional, mas recomendado por ser extremamente rápido) ou `pip`.

### 1. Clonar o repositório
```bash
git clone <url-do-seu-repositorio>
cd gerenciador_de_xml
```

### 2. Configurar o Ambiente Virtual
Utilizando `uv` (recomendado):
```bash
# Cria o ambiente virtual com Python 3.11
uv venv --python 3.11

# Instala as dependências necessárias
uv pip install PySide6 brazilfiscalreport darkdetect pandas openpyxl pillow
```

Utilizando o `venv` padrão do Python:
```bash
python -m venv .venv
source .venv/bin/activate  # No Linux/macOS
.venv\Scripts\activate     # No Windows

pip install PySide6 brazilfiscalreport darkdetect pandas openpyxl pillow
```

### 3. Executar o Aplicativo
```bash
# No Windows
.\.venv\Scripts\python.exe main.py

# No Linux/macOS
python main.py
```

---

## 🧪 Teste de Carga (Simulação com 5.000+ XMLs)

Disponibilizamos um script utilitário para gerar arquivos de simulação estruturados e válidos em formato para que você teste o limite de performance do sistema.

1. **Gere 5.000 XMLs fictícios na pasta `meus_xmls`**:
   ```bash
   .\.venv\Scripts\python.exe generate_test_xmls.py ./meus_xmls 5000
   ```
   *(Você pode gerar até 10.000, 20.000 ou 50.000 arquivos para validar o estresse de carga)*

2. **Abra o aplicativo, vá em 'Selecionar Pasta' e aponte para `./meus_xmls`**.
3. O software iniciará a sincronização assíncrona exibindo a barra de progresso. Após finalizar, teste a fluidez da busca e filtros.

---

## 📄 Licença

Este projeto é de uso livre para fins comerciais, acadêmicos e de gerenciamento interno.
