import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Вставь сюда свои данные (лучше вынести их в переменные окружения!)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GMAIL_EMAIL = os.getenv("GMAIL_EMAIL")
GMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

def send_email(from_name, text):
    msg = MIMEMultipart()
    msg["From"] = GMAIL_EMAIL
    msg["To"] = GMAIL_EMAIL  # можно поменять на другую почту
    msg["Subject"] = f"Обращение от {from_name}"

    body = f"Отправитель: {from_name}\n\nТекст обращения:\n{text}"
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_EMAIL, GMAIL_PASSWORD)
        server.send_message(msg)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Здравствуйте! Вы можете отправить своё обращение — мы его получим.")

@dp.message()
async def handle_message(message: types.Message):
    user = message.from_user
    name = user.full_name or user.username or "Неизвестный"
    text = message.text or "(текст отсутствует)"

    # Отправляем письмо
    send_email(name, text)

    await message.answer("Ваше обращение принято.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
