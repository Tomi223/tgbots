from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import re
import math

# ---------- Парсинг уравнения ----------
def parse_equation(eq: str):
    eq = eq.replace(" ", "").lower()
    match = re.match(r'([+-]?\d*)x\^2([+-]?\d*)x([+-]?\d+)=0', eq)
    if not match:
        raise ValueError("Неверный формат уравнения. Используй: ax^2 + bx + c = 0")

    def to_num(s):
        if s in ('+', ''): return 1
        if s == '-': return -1
        return int(s)

    a = to_num(match.group(1))
    b = to_num(match.group(2))
    c = int(match.group(3))
    return a, b, c

# ---------- Решение через дискриминант ----------
def solve_discriminant(a, b, c):
    steps = ["📘 Метод дискриминанта:"]
    D = b**2 - 4*a*c
    steps.append(f"D = b² - 4ac = {b}² - 4×{a}×{c} = {D}")
    if D > 0:
        x1 = (-b + math.sqrt(D)) / (2*a)
        x2 = (-b - math.sqrt(D)) / (2*a)
        steps.append(f"D > 0 ⇒ два корня:")
        steps.append(f"x₁ = (-b + √D) / 2a = ({-b} + √{D}) / {2*a} = {x1}")
        steps.append(f"x₂ = (-b - √D) / 2a = ({-b} - √{D}) / {2*a} = {x2}")
    elif D == 0:
        x = -b / (2*a)
        steps.append("D = 0 ⇒ один корень:")
        steps.append(f"x = -b / 2a = {-b} / {2*a} = {x}")
    else:
        steps.append("D < 0 ⇒ действительных корней нет.")
    return steps

# ---------- Решение по теореме Виета ----------
def solve_vieta(a, b, c):
    steps = ["📗 Теорема Виета:"]
    if a == 0:
        steps.append("a = 0 ⇒ не квадратное уравнение")
        return steps
    S = -b / a
    P = c / a
    steps.append(f"x₁ + x₂ = -b/a = {-b}/{a} = {S}")
    steps.append(f"x₁·x₂ = c/a = {c}/{a} = {P}")
    D = b**2 - 4*a*c
    if D < 0:
        steps.append("Нет действительных корней ⇒ не применимо.")
    else:
        x1 = (-b + math.sqrt(D)) / (2*a)
        x2 = (-b - math.sqrt(D)) / (2*a)
        steps.append(f"Корни: x₁ = {x1}, x₂ = {x2}")
    return steps

# ---------- Метод выделения полного квадрата ----------
def solve_square_completion(a, b, c):
    steps = ["📙 Метод выделения полного квадрата:"]
    if a == 0:
        steps.append("a = 0 ⇒ не квадратное уравнение")
        return steps
    b1 = b / a
    c1 = c / a
    steps.append(f"Приводим к виду x² + {b1}x + {c1} = 0")
    half_b = b1 / 2
    complete_square = half_b**2
    rhs = complete_square - c1
    steps.append(f"(x + {half_b})² = {complete_square} ⇒ (x + {half_b})² = {rhs}")
    if rhs < 0:
        steps.append("Правая часть < 0 ⇒ корней нет")
    elif rhs == 0:
        x = -half_b
        steps.append(f"x = {-half_b}")
    else:
        sqrt_rhs = math.sqrt(rhs)
        x1 = -half_b + sqrt_rhs
        x2 = -half_b - sqrt_rhs
        steps.append(f"x₁ = {x1}, x₂ = {x2}")
    return steps

# ---------- Telegram обработчики ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я бот для решения квадратных уравнений.\n\n"
        "Просто отправь мне уравнение вида:\n"
        "`2x^2+3x+1=0`", parse_mode="Markdown"
    )

async def solve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        equation = update.message.text
        a, b, c = parse_equation(equation)

        response = [f"📐 Уравнение: {a}x² + {b}x + {c} = 0\n"]
        response += solve_discriminant(a, b, c)
        response += ['\n'] + solve_vieta(a, b, c)
        response += ['\n'] + solve_square_completion(a, b, c)

        await update.message.reply_text("\n".join(response))
    except ValueError as ve:
        await update.message.reply_text(str(ve))
    except Exception:
        await update.message.reply_text("⚠️ Произошла ошибка. Убедись, что формат уравнения такой: `ax^2+bx+c=0`", parse_mode="Markdown")

# ---------- Запуск бота ----------
def main():
    token = "7557401455:AAEgd82mh4srSqmcAwmzXVqb8ZYXQHLvqRM"  #токен от BotFather

    app = ApplicationBuilder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, solve))

    print("✅ Бот запущен. Ждёт уравнения...")
    app.run_polling()

if __name__ == "__main__":
    main()