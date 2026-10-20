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
TG_TOKEN = os.getenv("BOT_TOKEN")
SMTP_SERVER = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
EMAIL_LOGIN = os.getenv("SMTP_USER")
EMAIL_PASSWORD = os.getenv("SMTP_PASS")
EMAIL_TO = os.getenv("MAIL_TO")

required = ["BOT_TOKEN", "SMTP_USER", "SMTP_PASS", "MAIL_TO"]
missing = [name for name in required if not os.getenv(name)]
if missing:
    raise ValueError("Не заданы переменные: " + ", ".join(missing))

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
