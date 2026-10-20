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


async def forward_to_owner(text: str):
    await bot.send_message(OWNER_ID, f"Новое обращение:\n\n{text}")


async def cmd_start(message: types.Message):
    await message.answer(WELCOME_TEXT)


async def handle_message(message: types.Message):
    text = message.text or "(без текста)"
    try:
        await forward_to_owner(text)
        await message.answer("Ваше обращение отправлено анонимно. Спасибо!")
        print("Анонимное обращение переслано владельцу")
    except Exception as e:
        print(f"Ошибка пересылки: {e}")
        await message.answer("Произошла ошибка при передаче. Попробуйте позже.")


async def main():
    dp.message.register(cmd_start, Command("start"))
    dp.message.register(handle_message)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
