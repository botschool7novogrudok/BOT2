import os
import smtplib
import telebot
from email.mime.text import MIMEText

BOT_TOKEN = os.environ["BOT_TOKEN"]
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "465"))
SMTP_USER = os.environ["SMTP_USER"]   # адрес почты, с которой идут письма
SMTP_PASS = os.environ["SMTP_PASS"]   # пароль приложения
MAIL_TO   = os.environ["MAIL_TO"]     # адрес, куда приходят письма

bot = telebot.TeleBot(BOT_TOKEN)

def send_email(text, sender_info):
    body = f"От кого: {sender_info}\n\n{text}"
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = "Новое сообщение из Telegram-бота"
    msg["From"] = SMTP_USER
    msg["To"] = MAIL_TO
    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as s:
        s.login(SMTP_USER, SMTP_PASS)
        s.send_message(msg)


@bot.message_handler(commands=["start"])
def start(m):
    bot.reply_to(m, "Привет! Напишите сообщение — я перешлю его на почту.")


@bot.message_handler(content_types=["text"])
def handle(m):
    sender = f"{m.from_user.full_name} (@{m.from_user.username or 'без username'}, id {m.from_user.id})"
    try:
        send_email(m.text, sender)
        bot.reply_to(m, "Отправлено!")
    except Exception as e:
        print("Ошибка отправки письма:", e)
        bot.reply_to(m, "Не получилось отправить, попробуйте позже.")


bot.infinity_polling()
