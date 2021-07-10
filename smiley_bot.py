import asyncio
import json
import aioschedule
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from decouple import config

loop = asyncio.get_event_loop()
API_TOKEN = config("TOKEN")
bot = Bot(token=API_TOKEN, loop=loop, parse_mode=types.ParseMode.HTML)

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

keyboard = InlineKeyboardMarkup()
smile_1 = InlineKeyboardButton(text="😁👍", callback_data="smile_1")
smile_2 = InlineKeyboardButton(text="🙂👌", callback_data="smile_2")
smile_3 = InlineKeyboardButton(text="😡👎", callback_data="smile_3")

keyboard.add(smile_1, smile_2, smile_3)


@dp.message_handler(commands=['start'])
async def get_started(message: types.Message):
    chat_id = str(message.chat.id)
    entry = {"chat_id": chat_id}

    with open("info.json", "r+") as f:
        data = json.load(f)
        if entry not in data:
            data.append(entry)
        f.seek(0)
        json.dump(data, f)

    await message.answer(
        f'Здравствуйте {message.from_user.first_name}! Пожалуйста оцените качество работы наших курьеров.',
        reply_markup=keyboard)


@dp.callback_query_handler(text_contains='smile_')
async def smile(call: types.CallbackQuery):
    if call.data and call.data.startswith("smile_"):
        code = call.data[-1:]
        if code.isdigit():
            code = int(code)
        if code == 1:
            await call.message.edit_text(f'Спасибо за оценку!')
        if code == 2:
            await call.message.edit_text('Хорошо, будем стараться лучше.')
        if code == 3:
            await call.message.edit_text('Напишите кто из курьеров нарушил регламент.')
        else:
            await bot.answer_callback_query(call.id)


@dp.message_handler()
async def send_to_us(message: types.Message):
    await message.bot.send_message(-590906679, f"{message.from_user.first_name} жалуется на {message.text}")


async def notify():
    try:
        with open("info.json") as f:
            data = json.load(f)
        for i in data:
            await bot.send_message(i["chat_id"], "Добрый вечер! Чтобы запустить бота нажмите на /start", parse_mode='markdown')
    except Exception as e:
        print(e)



async def scheduler():
    try:
        aioschedule.every().day.at("01:41").do(notify)
        while True:
            await aioschedule.run_pending()
            await asyncio.sleep(1)
    except Exception as e:
        print(e)


async def on_startup(_):
    try:
        asyncio.create_task(scheduler())
    except Exception as e:
        print(e)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
