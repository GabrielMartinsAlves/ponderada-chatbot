import os

import dotenv
import faiss
import google.generativeai as genai
import numpy as np
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Carrega as variáveis de ambiente
dotenv.load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError(
        "A chave de API do Gemini não foi encontrada. Defina a variável de ambiente GEMINI_API_KEY."
    )

genai.configure(api_key=api_key)

# --- Variáveis Globais para Caching ---
vector_store = None
text_chunks = None
# ------------------------------------


def criar_chatbot_compliance(caminho_politica):
    """
    Cria e armazena em cache um vector store para o chatbot de compliance usando o Google AI SDK.

    Esta função carrega a política, a divide, gera os embeddings com o modelo do Google
    e os armazena em um índice FAISS.
    """
    global vector_store, text_chunks

    # Retorna o cache se já foi criado
    if vector_store is not None and text_chunks is not None:
        return

    # Carrega o documento de política de compliance
    # (Usando o loader e splitter do LangChain como utilitários, pois são eficientes)
    loader = TextLoader(caminho_politica, encoding="utf-8")
    documentos = loader.load()

    # Divide o documento em chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    text_chunks = splitter.split_documents(documentos)

    # Extrai o conteúdo de texto dos documentos
    text_contents = [chunk.page_content for chunk in text_chunks]

    print(f"Gerando embeddings para {len(text_contents)} chunks de texto...")

    # Gera os embeddings usando o SDK do Google
    # O modelo 'text-embedding-004' é o recomendado atualmente.
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=text_contents,
        task_type="RETRIEVAL_DOCUMENT",
    )

    embeddings = result["embedding"]

    # Cria o índice FAISS
    dimension = len(embeddings[0])
    index = faiss.IndexFlatL2(dimension)

    # Adiciona os vetores ao índice
    index.add(np.array(embeddings))

    # Armazena o índice e os chunks em cache
    vector_store = index
    print("Vector Store criado com sucesso.")


def perguntar_ao_chatbot(pergunta):
    """
    Envia uma pergunta para o chatbot, encontra o contexto relevante e gera uma resposta.
    """
    global vector_store, text_chunks

    if vector_store is None:
        raise RuntimeError(
            "O chatbot de compliance não foi inicializado. Chame criar_chatbot_compliance() primeiro."
        )

    # 1. Gerar o embedding da pergunta
    query_embedding_result = genai.embed_content(
        model="models/text-embedding-004", content=pergunta, task_type="RETRIEVAL_QUERY"
    )
    query_embedding = np.array([query_embedding_result["embedding"]])

    # 2. Buscar no FAISS pelos vizinhos mais próximos
    k = 3  # Número de chunks relevantes a serem recuperados
    distances, indices = vector_store.search(query_embedding, k)

    # 3. Recuperar os chunks de texto correspondentes
    contexto_relevante = "\n---\n".join(
        [text_chunks[i].page_content for i in indices[0]]
    )

    # 4. Construir o prompt e chamar o modelo generativo
    prompt_template = f"""
        Você é um assistente de auditoria da Dunder Mifflin. Sua tarefa é responder a perguntas sobre a política de compliance da empresa.
        Use apenas o contexto fornecido abaixo para basear suas respostas. Seja claro e direto.

        Contexto Relevante:
        {contexto_relevante}

        Pergunta:
        {pergunta}

        Resposta:
    """

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt_template)

    return response.text


# Exemplo de uso quando o script é executado diretamente
if __name__ == "__main__":
    print("Inicializando o chatbot de compliance com o Google AI SDK...")
    criar_chatbot_compliance()
    print("Chatbot pronto! Faça sua pergunta ou digite 'sair' para terminar.")

    while True:
        pergunta_usuario = input("\nSua pergunta: ")
        if pergunta_usuario.lower() == "sair":
            break

        resposta = perguntar_ao_chatbot(pergunta_usuario)
        print("\nResposta do Chatbot:", resposta)
