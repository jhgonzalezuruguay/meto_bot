import os
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

bot_app = ApplicationBuilder().token(TOKEN).build()

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    usuarios[user_id] = {"indice": 0, "correctas": 0}
    await update.message.reply_text(
        "👋 ¡Hola! Bienvenido al bot de preguntas V/F.\n"
        "Te propongo responder un breve cuestionario para poner a prueba tus conocimientos."
    )
    await update.message.reply_text(preguntas[0]["texto"])

# Handler para respuestas
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    texto = update.message.text.strip().upper()

    if user_id not in usuarios:
        usuarios[user_id] = {"indice": 0, "correctas": 0}
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
            f"🎉 Terminaste. Puntaje: {porcentaje:.0f}%\nGracias por participar, ¡hasta la próxima!"
        )

# Registrar handlers
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(MessageHandler(filters.TEXT, responder))

# --- Flask para Render ---
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "Bot de preguntas V/F está corriendo en Render con Webhook."

import asyncio

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
