import os
import random
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

# Diccionario para guardar progreso de cada usuario
usuarios = {}

# Leer el token desde las variables de entorno
TOKEN = os.environ["BOT_TOKEN"]

# Crear la aplicación
app = ApplicationBuilder().token(TOKEN).build()

# Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    usuarios[user_id] = {"indice": 0, "correctas": 0}
    await update.message.reply_text(preguntas[0]["texto"])

# Handler para respuestas de texto
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

    # Guardar en CSV
    with open("respuestas.csv", "a") as f:
        f.write(f"{user_id},{i},{texto},{usuarios[user_id]['correctas']}\n")

    usuarios[user_id]["indice"] += 1

    if usuarios[user_id]["indice"] < len(preguntas):
        await update.message.reply_text(preguntas[usuarios[user_id]["indice"]]["texto"])
    else:
        correctas = usuarios[user_id]["correctas"]
        total = len(preguntas)
        porcentaje = (correctas / total) * 100
        await update.message.reply_text(f"🎉 Terminaste. Puntaje: {porcentaje:.0f}%")

# Registrar handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, responder))

# Iniciar el bot con polling
app.run_polling()
