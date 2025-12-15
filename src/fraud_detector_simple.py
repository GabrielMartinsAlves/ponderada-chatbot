import csv
import os

import dotenv
import google.generativeai as genai

# Carrega as variáveis de ambiente e configura a API
dotenv.load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError(
        "A chave de API do Gemini não foi encontrada. Defina a variável de ambiente GEMINI_API_KEY."
    )
genai.configure(api_key=api_key)


def ler_transacoes(caminho_arquivo):
    """Lê o arquivo CSV de transações e retorna uma lista de dicionários."""
    transacoes = []
    with open(caminho_arquivo, mode="r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            transacoes.append(row)
    return transacoes


def ler_politica(caminho_arquivo):
    """Lê o arquivo de texto da política de compliance e retorna seu conteúdo."""
    with open(caminho_arquivo, "r", encoding="utf-8") as f:
        return f.read()


def analisar_transacoes_simples(
    caminho_transacoes, caminho_politica, batch_size=50, max_batches=3
):
    """
    Analisa transações bancárias em busca de violações DIRETAS da política de compliance.

    Args:
        batch_size: Transações por lote (padrão: 50)
        max_batches: Número máximo de lotes a processar
    """
    transacoes = ler_transacoes(caminho_transacoes)
    politica = ler_politica(caminho_politica)

    model = genai.GenerativeModel("gemini-2.5-flash")

    violacoes_encontradas = []
    total_batches = min((len(transacoes) + batch_size - 1) // batch_size, max_batches)

    print(
        f"[Fraude Simples] Analisando {min(len(transacoes), batch_size * max_batches)} transações em {total_batches} lotes (limitado para teste)..."
    )

    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(transacoes))
        batch = transacoes[start_idx:end_idx]

        print(f"[Fraude Simples] Lote {batch_num + 1}/{total_batches}...")

        # Formata as transações do lote
        transacoes_formatadas = ""
        for i, transacao in enumerate(batch):
            transacoes_formatadas += f"#{start_idx + i + 1} | ID: {transacao['id_transacao']} | {transacao['data']} | {transacao['funcionario']} | ${transacao['valor']} | {transacao['descricao']}\n"

        prompt = f"""Você é um auditor de compliance da Dunder Mifflin.

                    TAREFA: Identificar transações que, POR SI SÓ, violam a política de compliance.
                    (Não considere conspirações ou contexto de e-mails - apenas se a transação viola regras diretamente)

                    POLÍTICA DE COMPLIANCE:
                    {politica}

                    TRANSAÇÕES PARA ANÁLISE:
                    {transacoes_formatadas}

                    INSTRUÇÕES:
                    1. Verifique cada transação contra as regras da política
                    2. Uma violação DIRETA é quando a transação, por si só, quebra uma regra (ex: valor acima do limite, categoria proibida)
                    3. Liste APENAS violações diretas no formato:
                    ID: [id] | Funcionário: [nome] | Violação: [descrição breve da regra quebrada]
                    4. Se nenhuma transação violar diretamente a política, responda APENAS: "Nenhuma violação direta detectada."

                    RELATÓRIO:
                """

        try:
            response = model.generate_content(prompt)
            resultado = response.text.strip()

            if "Nenhuma violação direta detectada." not in resultado:
                violacao = {
                    "batch": f"{start_idx + 1}-{end_idx}",
                    "justificativa_ia": resultado,
                }
                violacoes_encontradas.append(violacao)
        except Exception as e:
            print(f"[Fraude Simples] Erro no lote {batch_num + 1}: {e}")

    return violacoes_encontradas


if __name__ == "__main__":
    violacoes = analisar_transacoes_simples(
        "documents/transacoes_bancarias.csv", "documents/politica_compliance.txt"
    )

    print("\n--- Relatório de Fraudes Simples (Violações Diretas) ---")
    if not violacoes:
        print("Nenhuma violação direta de compliance foi detectada.")
    else:
        print(f"Lotes com violações: {len(violacoes)}\n")
        for v in violacoes:
            print(f"--- Lote {v['batch']} ---")
            print(v["justificativa_ia"])
            print()
