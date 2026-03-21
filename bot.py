from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes

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
import os
from telegram.ext import Updater, CommandHandler

# Leer el token desde las variables de entorno
TOKEN = os.environ["BOT_TOKEN"]

# Crear el updater con el token
updater = Updater(token=TOKEN)

dispatcher = updater.dispatcher

# Ejemplo de comando /start
def start(update, context):
    update.message.reply_text("¡Hola! Soy tu bot de preguntas verdadero/falso.")

dispatcher.add_handler(CommandHandler("start", start))

# Iniciar el bot con polling
updater.start_polling()
updater.idle()
usuarios = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    usuarios[user_id] = {"indice": 0, "correctas": 0}
    await update.message.reply_text(preguntas[0]["texto"])

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    texto = update.message.text.strip().upper()
    if user_id not in usuarios:
        usuarios[user_id] = {"indice": 0, "correctas": 0}
        await update.message.reply_text(preguntas[0]["texto"])
        return

    i = usuarios[user_id]["indice"]
    
    if user_id not in usuarios:
        usuarios[user_id] = {"indice": 0, "correctas": 0}

        i = usuarios[user_id]["indice"]
    
    if texto == preguntas[i]["respuesta"]:
        await update.message.reply_text("✅ Correcto")
        usuarios[user_id]["correctas"] += 1
    else:
        await update.message.reply_text("❌ Incorrecto")

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

app = ApplicationBuilder().token("8718846892:AAHbAHqlidrT5_AIPji_tcvJtuE6HRpYiF0").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, responder))

app.run_polling()
