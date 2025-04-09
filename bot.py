import re
import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Application, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("7557401455:AAEgd82mh4srSqmcAwmzXVqb8ZYXQHLvqRM")
HOSTNAME = os.getenv("QuadraticEquations1_bot")

WEBHOOK_PATH = f"/{TOKEN}"
WEBHOOK_URL = f"https://{HOSTNAME}{WEBHOOK_PATH}"

bot = Bot(token=TOKEN)
app = Flask(__name__)

telegram_app = Application.builder().token(TOKEN).build()

# 📘 Метод дискриминанта
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

# 📗 Метод Виета
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

# 📙 Метод выделения полного квадрата
def solve_by_square_completion(a, b, c):
    if a == 0:
        return "Не квадратное уравнение."
    h = b / (2*a)
    completed = f"(x + {h})² = {h**2 - c/a}" if a > 0 else f"(x - {abs(h)})² = {h**2 - c/a}"
    return f"Приводим уравнение к виду: {a}(x + {
