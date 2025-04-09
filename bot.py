from flask import Flask, request
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
import os
import re
import math

TOKEN = os.environ.get("7557401455:AAEgd82mh4srSqmcAwmzXVqb8ZYXQHLvqRM")
BOT_USERNAME = "QuadraticEquations1_bot"

app = Flask(__name__)
telegram_app = ApplicationBuilder().token(TOKEN).build()


def parse_equation(equation):
    try:
        equation = equation.replace(" ", "").replace("^2", "**2")
        match = re.fullmatch(r"([-+]?\d*)x\*\*2([-+]\d*)x([-+]\d+)=0", equation)
        if not match:
            return None
        a = int(match.group(1)) if match.group(1) not in ("", "+", "-") else int(match.group(1) + "1")
        b = int(match.group(2))
        c = int(match.group(3))
        return a, b, c
    except Exception:
        return None


def solve_by_discriminant(a, b, c):
    D = b ** 2 - 4 * a * c
    steps = [f"Находим дискриминант: D = b² - 4ac = {b}² - 4×{a}×{c} = {D}"]
    if D > 0:
        x1 = (-b + math.sqrt(D)) / (2 * a)
        x2 = (-b - math.sqrt(D)) / (2 * a)
        steps.append(f"D > 0, уравнение имеет два корня:")
        steps.append(f"x₁ = (-b + √D) / 2a = ({-b} + √{D}) / (2×{a}) = {x1}")
        steps.append(f"x₂ = (-b - √D) / 2a = ({-b} - √{D}) / (2×{a}) = {x2}")
    elif D == 0:
        x = -b / (2 * a)
        steps.append(f"D = 0, уравнение имеет один корень:")
        steps.append(f"x = -b / 2a = {-b} / (2×{a}) = {x}")
    else:
        steps.append("D < 0, действительных корней нет.")
    return "\n".join(steps)


def solve_by_vieta(a, b, c):
    D = b ** 2 - 4 * a * c
    if D < 0:
        return "По теореме Виета: корней нет, так как дискриминант отрицательный."
    x1 = (-b + math.sqrt(D)) / (2 * a)
    x2 = (-b - math.sqrt(D)) / (2 * a)
    s = x1 + x2
    p = x1 * x2
    return f"""По теореме Виета:
Сумма корней: x₁ + x₂ = -b/a = {-b}/{a} = {s}
Произведение корней: x₁·x₂ = c/a = {c}/{a} = {p}
Корни: x₁ = {x1}, x₂ = {x2}"""


def solve_by_square_completion(a, b, c):
    h = b / (2 * a)
    completed = h ** 2 - c / a
    steps = [
        f"Приводим к виду a(x + b/2a)² = ...",
        f"x² + ({b}/{a})x + {c}/{a} = 0 → (x + {h})² = {completed}",
    ]
    if completed < 0:
        steps.append("Подкоренное выражение отрицательно — корней нет.")
    else:
        sqrt_val = math.sqrt(completed)
        x1 = -h + sqrt_val
        x2 = -h - sqrt_val
        steps.append(f"x₁ = {-h} + √{completed} = {x1}")
        steps.append(f"x₂ = {-h} - √{completed} = {x2}")
    return "\n".join(steps)


@telegram_app.message_handler(filters.TEXT & ~filters.COMMAND)
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    parsed = parse_equation(text)
    if not parsed:
        await update.message.reply_text("Некорректный формат. Пример правильного ввода: 2x^2 - 4x + 2 = 0")
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


@app.route(f"/{BOT_USERNAME}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    telegram_app.update_queue.put_nowait(update)
    return "ok"


@app.before_first_request
def setup():
    telegram_app.bot.set_webhook(
        url=f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME')}/{BOT_USERNAME}"
    )

if __name__ == "__main__":
    app.run(port=10000)