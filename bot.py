import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TG_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

required = ["BOT_TOKEN", "OWNER_ID"]
missing = [name for name in required if not os.getenv(name)]
if missing:
    raise ValueError("Не заданы переменные: " + ", ".join(missing))

bot = Bot(token=TG_TOKEN)
dp = Dispatcher()


async def forward_to_owner(name: str, text: str):
    message_text = f"Обращение от {name}:\n\n{text}"
    await bot.send_message(OWNER_ID, message_text)


async def cmd_start(message: types.Message):
    await message.answer("Здравствуйте! Напишите ваше обращение — я передам его напрямую.")


async def handle_message(message: types.Message):
    name = message.from_user.full_name or "Неизвестный пользователь"
    text = message.text or "(без текста)"
    try:
        await forward_to_owner(name, text)
        await message.answer("Ваше сообщение передано. Спасибо за обращение!")
        print(f"Обращение от {name} переслано владельцу")
    except Exception as e:
        print(f"Ошибка пересылки: {e}")
        await message.answer("Произошла ошибка при передаче. Попробуйте позже.")


async def main():
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(handle_message)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
