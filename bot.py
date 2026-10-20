import os
import smtplib
import json
import telebot
from email.mime.text import MIMEText
from datetime import datetime, timezone, timedelta

BOT_TOKEN = os.environ["BOT_TOKEN"]
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ["SMTP_USER"]
SMTP_PASS = os.environ["SMTP_PASS"]
MAIL_TO   = os.environ["MAIL_TO"]

COUNTER_FILE = "/data/counter.json"

bot = telebot.TeleBot(BOT_TOKEN)

MINSK = timezone(timedelta(hours=3))


def next_number():
    n = 1
    try:
        with open(COUNTER_FILE) as f:
            n = json.load(f) + 1
    except (FileNotFoundError, ValueError):
        pass
    os.makedirs("/data", exist_ok=True)
    with open(COUNTER_FILE, "w") as f:
        json.dump(n, f)
    return n


def build_appeal(text, user):
    num = next_number()
    now = datetime.now(MINSK).strftime("%d.%m.%Y %H:%M")
    username = f"@{user.username}" if user.username else "нет username"
    subject = f"Обращение №{num} от {user.full_name}"
    body = (
        f"ОБРАЩЕНИЕ №{num}\n"
        f"Дата и время: {now}\n\n"
        f"Отправитель: {user.full_name}\n"
        f"Username Telegram: {username}\n"
        f"Telegram ID: {user.id}\n\n"
        f"Текст обращения:\n"
        f"{text}"
    )
    return subject, body


def send_email(subject, body):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = SMTP_USER
    msg["To"] = MAIL_TO
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as s:
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)


@bot.message_handler(commands=["start"])
def start(m):
    bot.reply_to(m, "Привет! Напишите ваше обращение — я передам его на почту.")


@bot.message_handler(content_types=["text"])
def handle(m):
    try:
        subject, body = build_appeal(m.text, m.from_user)
        send_email(subject, body)
        bot.reply_to(m, f"Ваше обращение №{body.split('№')[1].split()[0]} отправлено.")
    except Exception as e:
        print("Ошибка:", e)
        bot.reply_to(m, "Не получилось отправить, попробуйте позже.")


bot.infinity_polling()
