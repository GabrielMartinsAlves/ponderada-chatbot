import os
import google.generativeai as genai
from google.adk import Agent
from src.tools import compliance_tool, conspiracy_tool, simple_fraud_tool, complex_fraud_tool

def create_auditor_agent():
    # Configura a API Key (já deve estar carregada pelo dotenv no main)
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY não encontrada.")

    # Define as instruções do sistema
    instructions = """
    Você é o Assistente de Auditoria da Dunder Mifflin, trabalhando diretamente para o Toby Flenderson (RH).
    Sua missão é auxiliar em auditorias internas, verificação de compliance e investigações especiais.

    Você tem acesso a várias ferramentas especializadas:
    1. compliance_tool: Para responder dúvidas sobre a política da empresa.
    2. conspiracy_tool: Para investigar e-mails do Michael Scott em busca de complôs contra o Toby.
    3. simple_fraud_tool: Para verificar violações óbvias em transações bancárias.
    4. complex_fraud_tool: Para investigações profundas cruzando transações e e-mails.

    Sempre que o usuário solicitar uma tarefa, analise qual ferramenta é a mais adequada e use-a.
    Se o usuário apenas cumprimentar, responda de forma profissional e ofereça seus serviços de auditoria.

    Ao receber o resultado de uma ferramenta, apresente-o de forma clara e resumida para o usuário.
    """

    # Cria o agente orquestrador
    agent = Agent(
        name="AuditorAgent",
        model="gemini-2.5-flash",
        tools=[compliance_tool, conspiracy_tool, simple_fraud_tool, complex_fraud_tool],
        instruction=instructions
    )

    return agent
