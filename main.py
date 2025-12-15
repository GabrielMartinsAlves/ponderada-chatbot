import asyncio
import os

import dotenv
from google.adk import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from src.agent import create_auditor_agent

# Carrega variáveis de ambiente
dotenv.load_dotenv()


async def main():
    print("--- Auditoria do Toby: Sistema Integrado (Google ADK) ---")

    if not os.getenv("GEMINI_API_KEY"):
        print("\n[ERRO] A variável de ambiente GEMINI_API_KEY não foi definida.")
        print("Por favor, verifique seu arquivo .env.")
        return

    try:
        # Cria o agente orquestrador (auditor)
        agent = create_auditor_agent()

        # Cria o serviço de sessão
        session_service = InMemorySessionService()

        # Cria o runner para executar o agente
        runner = Runner(
            agent=agent, session_service=session_service, app_name="auditor_app"
        )

        # Cria uma sessão
        session = await session_service.create_session(
            user_id="user", app_name="auditor_app"
        )

        print("Agente Auditor pronto! (Digite 'sair' para encerrar)")

        while True:
            user_input = input("\nVocê: ")
            if user_input.lower() in ["sair", "exit", "quit"]:
                break

            # Executa o agente com a entrada do usuário
            message_content = types.Content(
                role="user", parts=[types.Part(text=user_input)]
            )
            final_response_text = ""
            async for event in runner.run_async(
                user_id="user", session_id=session.id, new_message=message_content
            ):
                if hasattr(event, "content") and event.content:
                    content = event.content
                    if hasattr(content, "role") and content.role == "model":
                        if hasattr(content, "parts"):
                            for part in content.parts:
                                if hasattr(part, "text") and part.text:
                                    final_response_text = part.text

            if final_response_text:
                print(f"\nAuditor: {final_response_text}")

    except Exception as e:
        print(f"\n[ERRO CRÍTICO] Ocorreu um erro na execução do agente: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
