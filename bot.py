
import re
import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("7557401455:AAEgd82mh4srSqmcAwmzXVqb8ZYXQHLvqRM")
HOSTNAME = os.getenv("RENDER_EXTERNAL_HOSTNAME")

WEBHOOK_PATH = f"/{TOKEN}"
WEBHOOK_URL = f"https://{HOSTNAME}{WEBHOOK_PATH}"

bot = Bot(token=TOKEN)
app = Flask(__name__)

telegram_app = Application.builder().token(TOKEN).build()

def solve_by_discriminant(a, b, c):
    D = b**2 - 4*a*c
    steps = f"D = {b}² - 4×{a}×{c} = {D}\n"
    if D < 0:
        steps += "Нет вещественных корней."
    elif D == 0:
        x = -b / (2*a)
        steps += f"Один корень: x = -{b}/(2×{a}) = {x}"
    else:
        x1 = (-b + D**0.5) / (2*a)
        x2 = (-b - D**0.5) / (2*a)
        steps += f"Два корня: x₁ = {x1}, x₂ = {x2}"
    return steps

def solve_by_vieta(a, b, c):
    if a == 0:
        return "Уравнение не квадратное."
    s = -b / a
    p = c / a
    D = b**2 - 4*a*c
    if D < 0:
        return "Корней нет (Viète)."
    elif D == 0:
        x = -b / (2*a)
        return f"Один корень (Viète): x = {x}, сумма x₁+x₂ = {s}, произведение x₁×x₂ = {p}"
    else:
        x1 = (-b + D**0.5) / (2*a)
        x2 = (-b - D**0.5) / (2*a)
        return f"Корни по Виете: x₁ = {x1}, x₂ = {x2}\nПроверка: x₁+x₂ = {x1+x2}, x₁×x₂ = {x1*x2}"

def solve_by_square_completion(a, b, c):
    if a == 0:
        return "Не квадратное уравнение."
    h = b / (2*a)
    completed = f"(x + {h})² = {h**2 - c/a}" if a > 0 else f"(x - {abs(h)})² = {h**2 - c/a}"
    return f"Приводим уравнение к виду: {a}(x + {b/(2*a)})² = {b**2/(4*a**2) - c/a}\nУпрощённо: {completed}"

def parse_equation(equation: str):
    equation = equation.replace(" ", "").replace("^2", "**2").replace("=0", "")
    match = re.match(r"([+-]?\d*)x\*\*2([+-]\d*)x([+-]\d+)", equation)
    if not match:
        return None
    a, b, c = match.groups()
    a = int(a) if a not in ("", "+", "-") else int(a + "1") if a else 1
    b = int(b) if b not in ("", "+", "-") else int(b + "1") if b else 1
    c = int(c)
    return a, b, c

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    parsed = parse_equation(text)
    if not parsed:
        await update.message.reply_text("Некорректный формат. Пример: 2x^2 - 4x + 2 = 0")
        return

    a, b, c = parsed

    result = f"""Решаем уравнение: {a}x² + {b}x + {c} = 0

📘 Метод дискриминанта:
{solve_by_discriminant(a, b, c)}

📗 Метод Виета:
{solve_by_vieta(a, b, c)}

📙 Метод выделения полного квадрата:
{solve_by_square_completion(a, b, c)}
"""
    await update.message.reply_text(result)

telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

@app.route(WEBHOOK_PATH, methods=["POST"])
async def webhook() -> str:
    await telegram_app.update_queue.put(Update.de_json(request.get_json(force=True), bot))
    return "ok"

async def main():
    await bot.set_webhook(url=WEBHOOK_URL)
    await telegram_app.initialize()
    await telegram_app.start()
    await telegram_app.updater.start_polling()

import asyncio
if __name__ == "__main__":
    asyncio.run(main())
