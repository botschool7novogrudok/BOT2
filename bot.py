import asyncio
import os
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv

load_dotenv()  # загружает .env

# --- Чтение переменных окружения ---
TG_TOKEN = os.getenv("TG_TOKEN")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
EMAIL_LOGIN = os.getenv("EMAIL_LOGIN")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_TO = os.getenv("EMAIL_TO")

if not all([TG_TOKEN, SMTP_SERVER, EMAIL_LOGIN, EMAIL_PASSWORD, EMAIL_TO]):
    raise ValueError("Не все переменные окружения заданы. Проверьте .env")

async def send_email(name: str, text: str):
    subject = f"От {name}"
    body = f"Пользователь: {name}\n\nТекст сообщения:\n{text}"

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = Header(subject, "utf-8")
    msg["From"] = EMAIL_LOGIN
    msg["To"] = EMAIL_TO

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
        server.login(EMAIL_LOGIN, EMAIL_PASSWORD)
        server.send_message(msg)

async def cmd_start(message: types.Message):
    await message.answer("Спасибо, что написали! Ваше сообщение будет отправлено на почту.")

async def handle_message(message: types.Message):
    name = message.from_user.full_name or "Неизвестный пользователь"
    text = message.text or "(без текста)"
    try:
        await send_email(name, text)
        await message.answer("Ваше сообщение успешно отправлено!")
    except Exception as e:
        # Для учебного проекта можно логировать в консоль
        print(f"Ошибка отправки почты: {e}")
        await message.answer("Произошла ошибка при отправке. Попробуйте позже.")

async def main():
    bot = Bot(token=TG_TOKEN)
    dp = Dispatcher()
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(handle_message)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
