# Chatbot de Auditoria - Dunder Mifflin (Google AI SDK)

Este projeto é uma solução de Inteligência Artificial desenvolvida para a atividade "A Auditoria do Toby". O sistema consiste em um agente de IA com múltiplas ferramentas, capaz de realizar tarefas de auditoria e investigação nos documentos da filial de Scranton da Dunder Mifflin, **utilizando o Google AI SDK nativamente**.

## Arquitetura da Solução

O sistema foi construído de forma modular, com cada funcionalidade encapsulada em seu próprio script Python no diretório `src`. Um arquivo `main.py` serve como orquestrador, oferecendo uma interface de linha de comando (CLI) para o usuário.

A arquitetura foi **refatorada para usar o Google AI SDK diretamente**, minimizando dependências de frameworks de orquestração.

### 1. Agente de Compliance (Chatbot RAG)

- **Arquivo:** `src/compliance_chatbot.py`
- **Técnica:** RAG (Retrieval-Augmented Generation) com implementação nativa.
- **Funcionamento:**
  1.  O documento `politica_compliance.txt` é carregado e dividido em "chunks" (pedaços).
  2.  Utilizando `google.generativeai.embed_content` (modelo `text-embedding-004`), cada chunk é transformado em um vetor de embedding.
  3.  Os vetores são armazenados e indexados em um banco de dados vetorial em memória (FAISS).
  4.  Quando o usuário faz uma pergunta, ela também é convertida em um vetor usando o mesmo modelo. O FAISS realiza uma busca de similaridade para encontrar os chunks de texto mais relevantes.
  5.  Os chunks relevantes são inseridos em um prompt, que é enviado ao `GenerativeModel` (`gemini-pro`) para gerar uma resposta contextual.

### 2. Investigador de Conspiração

- **Arquivo:** `src/conspiracy_detector.py`
- **Técnica:** Análise de texto com chamada direta ao LLM.
- **Funcionamento:**
  1.  O script lê e filtra os e-mails de `emails_internos.txt` que foram enviados por "Michael Scott" e mencionam "Toby".
  2.  Os e-mails filtrados são formatados em um prompt que instrui o `GenerativeModel` (`gemini-pro`) a agir como um auditor e determinar se há evidências de uma conspiração.
  3.  A resposta do modelo é exibida diretamente.

### 3. Auditores de Fraude (Simples e Complexo)

- **Arquivos:** `src/fraud_detector_simple.py` e `src/fraud_detector_complex.py`
- **Técnica:** Análise de transações com LLM.
- **Funcionamento:**
  - **Simples:** Para cada transação, um prompt é construído com os detalhes da transação e a política de compliance. O `GenerativeModel` avalia se há uma violação direta.
  - **Complexo:** O sistema primeiro busca e-mails relevantes para cada transação. Se houver correspondências, um prompt mais elaborado, contendo a transação, os e-mails e a política, é enviado ao `GenerativeModel` para procurar por fraudes contextuais que exigem interpretação cruzada de documentos.

## Tecnologias Utilizadas

- **Python 3.x**
- **Google AI SDK (`google-generativeai`):** Biblioteca nativa para interagir com os modelos Gemini (embeddings e geração de texto).
- **FAISS (`faiss-cpu`):** Biblioteca para busca de similaridade vetorial, usada no RAG.
- **NumPy:** Dependência para operações numéricas com os vetores.
- **Python-Dotenv:** Para gerenciamento de variáveis de ambiente (chave de API).

## Como Rodar o Projeto

Siga os passos abaixo para configurar e executar o sistema de auditoria.

### 1. Clonar o Repositório

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd <NOME_DO_DIRETORIO>
```

### 2. Instalar as Dependências

É recomendado criar um ambiente virtual primeiro.

```bash
# Para Windows
python -m venv venv
venv\Scripts\activate

# Para macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

Em seguida, instale os pacotes necessários a partir do arquivo `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 3. Configurar a Chave de API

1.  Na raiz do projeto, crie um arquivo chamado `.env`.
2.  Dentro deste arquivo, adicione sua chave de API do Google Gemini, como no exemplo abaixo:
    ```
    GEMINI_API_KEY="SUA_CHAVE_DE_API_AQUI"
    ```
    **Importante:** O arquivo `.gitignore` já está configurado para que o `.env` não seja enviado para o repositório do GitHub.

### 4. Executar o Sistema

Com tudo configurado, execute o programa principal:

```bash
python main.py
```

Você verá um menu interativo onde poderá escolher qual ferramenta de auditoria deseja usar.

## Vídeo de Demonstração

https://drive.google.com/drive/folders/1Gm8R7hhlFMGt8_4LQ2vN5EjtUsp1wFEM?usp=sharing
