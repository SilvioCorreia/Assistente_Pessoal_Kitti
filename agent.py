##  .\executar_Kitt\Scripts\Activate.ps1
##  .\executar_Kitt\Scripts\python.exe agent.py dev
##  .\executar_Kitt\Scripts\python.exe agent.py start
##  .\executar_Kitt\Scripts\python.exe server.py

import os
from dotenv import load_dotenv

load_dotenv()

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, WorkerOptions, cli, JobContext
from livekit.plugins import google, deepgram, elevenlabs, silero, noise_cancellation

from prompts import AGENT_INSTRUCTIONS, SESSION_INSTRUCTIONS
from tools import get_weather, search_web, send_email

from livekit.api import AccessToken, VideoGrants

# Gerando token para o app Android se conectar
token = (
    AccessToken(os.getenv("LIVEKIT_API_KEY"), os.getenv("LIVEKIT_API_SECRET"))
    .with_identity("android-app")
    .with_grants(VideoGrants(room_join=True, room="sala-teste"))
    .to_jwt()
)

print("\n" + "="*50)
print("COPIE ESTE TOKEN PARA O ANDROID STUDIO:")
print(token)
print("="*50 + "\n")


def runtime_configured() -> bool:
    required_values = [
        os.getenv("LIVEKIT_URL"),
        os.getenv("LIVEKIT_API_KEY"),
        os.getenv("LIVEKIT_API_SECRET"),
        os.getenv("GOOGLE_API_KEY"),
        os.getenv("DEEPGRAM_API_KEY"),
        os.getenv("ELEVEN_API_KEY"),
    ]
    return all(v is not None and v.strip() for v in required_values)


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTIONS,
            tools=[
                get_weather,
                search_web,
                send_email,
            ],
        )


async def entrypoint(ctx: JobContext):
    await ctx.connect()

    import logging
    logger = logging.getLogger("kitt")
    logger.info("Participante conectado, iniciando sessão...")

    session = AgentSession(
        vad=silero.VAD.load(
            min_silence_duration=0.8,
            activation_threshold=0.6,
        ),
        stt=deepgram.STT(language="pt-BR"),
        llm=google.LLM(model="gemini-3.1-flash-lite"),
        tts=elevenlabs.TTS(voice_id=os.getenv("ELEVEN_VOICE_ID")),
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    logger.info("Sessão iniciada, gerando saudação...")
    try:
        await session.generate_reply(
            instructions=SESSION_INSTRUCTIONS,
        )
        logger.info("Saudação gerada com sucesso")
    except Exception as e:
        logger.error(f"Erro ao gerar saudação: {e}")


if __name__ == "__main__":
    if not runtime_configured():
        print("Erro: Verifique se todas as chaves de API estão configuradas no arquivo .env")
    else:
        cli.run_app(
            WorkerOptions(
                entrypoint_fnc=entrypoint,
                agent_name="Kitt",
            )
        )
