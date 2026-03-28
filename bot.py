import os
import requests
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Preguntas V/F
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
HF_API_KEY = os.environ.get("HF_API_KEY")

bot_app = ApplicationBuilder().token(TOKEN).build()

# Hugging Face
def chat_gpt(prompt: str) -> str:
    response = requests.post(
        "https://router.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2",
        headers={"Authorization": f"Bearer {HF_API_KEY}"},
        json={"inputs": prompt}
    )
    try:
        data = response.json()
    except Exception:
        return "⚠️ Error: respuesta inválida de Hugging Face"

    if isinstance(data, list) and "generated_text" in data[0]:
        return data[0]["generated_text"]
    elif isinstance(data, dict) and "generated_text" in data:
        return data["generated_text"]
    elif "error" in data:
        return f"⚠️ Error HuggingFace: {data['error']}"
    else:
        return "⚠️ Respuesta inesperada: " + str(data)

# Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    usuarios[user_id] = {"indice": 0, "correctas": 0, "modo_chatgpt": False}
    await update.message.reply_text("👋 ¡Hola! Bienvenido al bot de preguntas V/F.")
    await update.message.reply_text(preguntas[0]["texto"])

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    texto = update.message.text.strip().upper()

    if user_id in usuarios and usuarios[user_id].get("modo_chatgpt"):
        respuesta = chat_gpt(update.message.text)
        await update.message.reply_text(respuesta)
        return

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

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
# Inicializar la aplicación antes de usar process_update
asyncio.run(bot_app.initialize())
# Flask
flask_app = Flask(__name__)

@flask_app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    # Procesa el update directamente en un loop nuevo
    asyncio.run(bot_app.process_update(update))
    return "ok"

@flask_app.route("/")
def home():
    return "Bot de preguntas V/F con Hugging Face está corriendo en Render."
