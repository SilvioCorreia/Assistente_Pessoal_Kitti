# https://cloud.livekit.io/projects/p_3mi18fn6dfs/agents/console?identity=Silvio&agentName=Kitt
#  .\executar_Kitt\Scripts\Activate.ps1
#  python agent.py start
#  python agent.py dev   -- para executar no modo de desenvolvimento
#  python agent.py local -- modo de fallback sem as credenciais completas
#  python agent.py console   --para abrir o microfone no terminal
import os
import sys
from typing import Sequence
from dotenv import load_dotenv

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, WorkerOptions, cli
from livekit.plugins import noise_cancellation, google, deepgram, krisp

from prompts import AGENT_INSTRUCTIONS, SESSION_INSTRUCTIONS
from tools import get_weather, search_web, send_email

from livekit.api import AccessToken, VideoGrants

# Gerando token para o app Android se conectar
token = (
    AccessToken("APITzvtuxcafWBh", "LXBQZvrK3RNbnzDVrc6WGNyeeEodx1HdCoeZRiZ3VcKA")
    .with_identity("android-app")
    .with_grants(VideoGrants(room_join=True, room="sala-teste"))
    .to_jwt()
)

print("\n" + "="*50)
print("COPIE ESTE TOKEN PARA O ANDROID STUDIO:")
print(token)
print("="*50 + "\n")

load_dotenv()


def runtime_configured() -> bool:
    required_values = (
        os.getenv("LIVEKIT_URL"),
        os.getenv("LIVEKIT_API_KEY"),
        os.getenv("LIVEKIT_API_SECRET"),
        os.getenv("GOOGLE_API_KEY"),
    )

    def is_placeholder(value: str | None) -> bool:
        if value is None:
            return True
        cleaned = value.strip()
        return not cleaned or cleaned.upper().startswith("YOUR_") or cleaned.upper() in {"REPLACE_ME", "CHANGE_ME"}

    return all(not is_placeholder(value) for value in required_values)


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTIONS,
            llm=google.beta.realtime.RealtimeModel(
                voice="Aoede",
                temperature=0.8,
            ),
            tools=[
                get_weather,
                search_web,
                send_email,
            ],
        )


async def entrypoint(ctx: agents.JobContext):
    # 1. Primeiro conecta na sala
    await ctx.connect()

    session = AgentSession(
        llm=google.beta.realtime.RealtimeModel(
            voice="Kitt",
    )
    )
    # 2. Depois inicia a sessão do agente
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            video_enabled=True,
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # 3. Gera a saudação inicial (usando a variável no plural)
    await session.generate_reply(
        instructions=SESSION_INSTRUCTIONS,
    )


def run_local_console() -> None:
    print("Starting local fallback mode. LiveKit and Google credentials are not configured.")
    print("Type 'exit' to leave the session.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except KeyboardInterrupt:
            print("\nLocal session closed.")
            break

        if user_input.lower() in {"exit", "quit"}:
            print("Friday: Goodbye, sir.")
            break

        if not user_input:
            continue

        lowered = user_input.lower()
        if "weather" in lowered:
            response = "I can check the weather once the real API keys are configured."
        elif "email" in lowered:
            response = "I can send emails once Gmail credentials are configured."
        elif "search" in lowered:
            response = "I can search the web once the full runtime is available."
        else:
            response = "I’m running in local fallback mode. Provide valid LiveKit and Google credentials to enable the full assistant."

        print(f"Friday: {response}")


if __name__ == "__main__":
    if not runtime_configured():
        run_local_console()
    else:
        cli.run_app(
            WorkerOptions(
                entrypoint_fnc=entrypoint,
                agent_name="Kitt",
            )
        )