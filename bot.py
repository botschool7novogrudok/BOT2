import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile

TG_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

required = ["BOT_TOKEN", "OWNER_ID"]
missing = [name for name in required if not os.getenv(name)]
if missing:
    raise ValueError("Не заданы переменные: " + ", ".join(missing))

bot = Bot(token=TG_TOKEN)
dp = Dispatcher()

WELCOME_TEXT = """Здравствуйте.

Вы в Контакт-центре доверия Средней школы №7 г. Новогрудка — месте, где можно безопасно сообщить о том, что происходит в школе или вокруг нее.

Мы принимаем обращения:
📍 о конфликтах и травле;
📍 о тяжелом моральном состоянии;
📍 о ситуациях, где нужна помощь взрослых.

Вы можете говорить анонимно или оставить свои контакты для обратной связи.
Все сообщения передаются директору и ответственным специалистам школы.

📲 Если вам нужна срочная помощь — пожалуйста, обратитесь по телефону 112 или в бесплатную службу экстренной психологической помощи — единый номер 133.

Напишите ваше сообщение 👇"""

photo = FSInputFile("logo.jpg")

async def forward_to_owner(text: str):
    await bot.send_message(OWNER_ID, f"Новое обращение:\n\n{text}")

async def forward_photo_to_owner(message: types.Message):
    # message.photo[-1] — самое большое разрешение присланной картинки
    file_id = message.photo[-1].file_id
    caption = message.caption or "(без подписи)"
    await bot.send_photo(OWNER_ID, file_id, caption=f"Фото-обращение:\n\n{caption}")

async def cmd_start(message: types.Message):
    await message.answer_photo(photo, caption=WELCOME_TEXT)

async def handle_message(message: types.Message):
    try:
        if message.photo:
            await forward_photo_to_owner(message)
        else:
            await forward_to_owner(message.text or "(без текста)")
        await message.answer("Ваше обращение отправлено. Спасибо!")
        print("Обращение переслано владельцу")
    except Exception as e:
        print(f"Ошибка пересылки: {e}")
        await message.answer("Произошла ошибка при передаче. Попробуйте позже.")

async def main():
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(handle_message)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
