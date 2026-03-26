import os
import requests
import asyncio
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Lista de preguntas verdadero/falso
preguntas = [
    {"texto": "¿Una hipótesis relaciona variables? (V/F)", "respuesta": "V"},
    {"texto": "¿La variable independiente es la causa? (V/F)", "respuesta": "V"},
    {"texto": "¿La variable dependiente es la causa? (V/F)", "respuesta": "F"},
    {"texto": "¿Una muestra representa a la población? (V/F)", "respuesta": "V"},
    {"texto": "¿El método científico no requiere observación? (V/F)", "respuesta": "F"},
    {"texto": "¿Una correlación implica causalidad? (V/F)", "respuesta": "F"},
    {"texto": "¿Los datos cualitativos son numéricos? (V/F)", "respuesta": "F"},
    {"texto": "¿Un experimento controla variables? (V/F)", "respuesta": "V"},
    {"texto": "¿La teoría se basa en evidencia? (V/F)", "respuesta": "V"},
    {"texto": "¿El sesgo puede afectar resultados? (V/F)", "respuesta": "V"},
    {"texto": "¿La encuesta es una técnica de recolección de datos? (V/F)", "respuesta": "V"},
    {"texto": "¿Una variable constante cambia durante el estudio? (V/F)", "respuesta": "F"}
]

usuarios = {}

TOKEN = os.environ["BOT_TOKEN"]
PORT = int(os.environ.get("PORT", 5000))
RENDER_URL = os.environ.get("RENDER_EXTERNAL_URL")  # Render te da esta variable automáticamente
HF_API_KEY = os.environ.get("HF_API_KEY")  # Hugging Face API Key

bot_app = ApplicationBuilder().token(TOKEN).build()

# --- Función para consultar Hugging Face ---
def chat_gpt(prompt: str) -> str:
    response = requests.post(
        "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
        headers={"Authorization": f"Bearer {HF_API_KEY}"},
        json={"inputs": prompt}
    )
    data = response.json()
    print("Respuesta HuggingFace:", data)  # Esto lo ves en los logs de Render

    # Manejo flexible de formatos
    if isinstance(data, list) and "generated_text" in data[0]:
        return data[0]["generated_text"]
    elif isinstance(data, dict) and "generated_text" in data:
        return data["generated_text"]
    elif "error" in data:
        return f"⚠️ Error HuggingFace: {data['error']}"
    else:
        return "⚠️ Respuesta inesperada: " + str(data)

# --- Comando /start ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    usuarios[user_id] = {"indice": 0, "correctas": 0, "modo_chatgpt": False}
    await update.message.reply_text(
        "👋 ¡Hola! Bienvenido al bot de preguntas V/F.\n"
        "Te propongo responder un breve cuestionario para poner a prueba tus conocimientos."
    )
    await update.message.reply_text(preguntas[0]["texto"])

# --- Handler para respuestas ---
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    texto = update.message.text.strip().upper()

    # Si el usuario está en modo ChatGPT
    if user_id in usuarios and usuarios[user_id].get("modo_chatgpt"):
        respuesta = chat_gpt(update.message.text)
        await update.message.reply_text(respuesta)
        return

    # Si el usuario no está registrado, iniciar cuestionario
    if user_id not in usuarios:
        usuarios[user_id] = {"indice": 0, "correctas": 0, "modo_chatgpt": False}
        await update.message.reply_text(preguntas[0]["texto"])
        return

    i = usuarios[user_id]["indice"]

    if texto == preguntas[i]["respuesta"]:
        await update.message.reply_text("✅ Correcto")
        usuarios[user_id]["correctas"] += 1
    else:
        await update.message.reply_text("❌ Incorrecto")

    usuarios[user_id]["indice"] += 1

    if usuarios[user_id]["indice"] < len(preguntas):
        await update.message.reply_text(preguntas[usuarios[user_id]["indice"]]["texto"])
    else:
        correctas = usuarios[user_id]["correctas"]
        total = len(preguntas)
        porcentaje = (correctas / total) * 100
        await update.message.reply_text(
            f"🎉 Terminaste. Puntaje: {porcentaje:.0f}%\n"
            "Ahora podés hacerme una pregunta sobre metodología de las ciencias sociales."
        )
        usuarios[user_id]["modo_chatgpt"] = True

# Registrar handlers
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

# --- Flask para Render ---
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot de preguntas V/F con Hugging Face está corriendo en Render."

if __name__ == "__main__":
    # Configurar webhook con loop explícito
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    bot_app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=TOKEN,
        webhook_url=f"{RENDER_URL}/{TOKEN}"
    )
