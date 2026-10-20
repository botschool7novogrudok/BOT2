import os
import smtplib
import mimetypes
from email.message import EmailMessage

from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup

BOT_TOKEN = os.environ["BOT_TOKEN"]
GMAIL_USER = os.environ["GMAIL_USER"]          # ваш gmail-адрес
GMAIL_APP_PASSWORD = os.environ["GMAIL_APP_PASSWORD"]  # пароль приложения
TO_EMAIL = os.environ.get("TO_EMAIL", GMAIL_USER)      # куда отправлять письма

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()


class Form(StatesGroup):
    text = State()


start_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="✉️ Написать обращение")]],
    resize_keyboard=True,
)


def send_email(subject: str, body: str, attachments: list) -> None:
    msg = EmailMessage()
    msg["From"] = GMAIL_USER
    msg["To"] = TO_EMAIL
    msg["Subject"] = subject
    msg.set_content(body)
    for name, content in attachments:
        mime, _ = mimetypes.guess_type(name)
        maintype, _, subtype = (mime or "application/octet-stream").partition("/")
        msg.add_attachment(content, maintype=maintype, subtype=subtype, filename=name)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        s.send_message(msg)


@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Здравствуйте! Это бот для сбора обращений.\n"
        "Нажмите «✉️ Написать обращение» и изложите суть. "
        "Можно приложить фото или документы.",
        reply_markup=start_kb,
    )


@dp.message(F.text == "✉️ Написать обращение")
async def new_appeal(message: Message, state: FSMContext):
    await state.set_state(Form.text)
    await state.update_data(text="", files=[])
    await message.answer(
        "Напишите текст обращения. Можно отправлять несколько сообщений и "
        "прикреплять фото или документы.\n"
        "Чтобы отправить — напишите /done."
    )


# вложения: фото, документы, видео
@dp.message(Form.text, F.photo | F.document | F.video)
async def save_file(message: Message, state: FSMContext):
    data = await state.get_data()
    files = data.get("files", [])
    if message.photo:
        files.append(("photo.jpg", message.photo[-1].file_id))
    elif message.document:
        files.append((message.document.file_name or "file", message.document.file_id))
    elif message.video:
        files.append(("video.mp4", message.video.file_id))
    await state.update_data(files=files)
    await message.answer("Файл добавлен ✅ Всего файлов: %d. Пишите /done, когда закончите." % len(files))


# текст обращения
@dp.message(Form.text, F.text)
async def save_text(message: Message, state: FSMContext):
    data = await state.get_data()
    old = data.get("text", "")
    await state.update_data(text=(old + "\n" + message.text).strip())
    await message.answer("Добавлено. Пишите /done, чтобы отправить обращение.")


@dp.message(Form.text, Command("done"))
async def finish(message: Message, state: FSMContext):
    data = await state.get_data()
    text = data.get("text", "")
    files = data.get("files", [])
    if not text:
        await message.answer("Текст пустой — сначала опишите обращение.")
        return

    user = message.from_user
    body = (
        "Новое обращение из Telegram-бота\n\n"
        f"От: {user.full_name} (@{user.username or '—'})\n"
        f"Telegram ID: {user.id}\n\n"
        f"{text}\n\nВложений: {len(files)}"
    )
    attachments = []
    for name, file_id in files:
        bio = await bot.download(file_id)
        attachments.append((name, bio.read()))

    try:
        send_email(f"Обращение от {user.full_name}", body, attachments)
    except Exception:
        await message.answer("Не удалось отправить обращение. Попробуйте позже.")
        return

    await state.clear()
    await message.answer("Обращение отправлено ✅ Спасибо!", reply_markup=start_kb)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
