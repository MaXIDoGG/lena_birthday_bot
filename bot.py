import asyncio
import logging
import sys
import json
from dotenv import load_dotenv
from os import getenv

from aiogram import Bot, Dispatcher, html, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from keyboards import start_keyboard

load_dotenv()
TOKEN = getenv("BOT_TOKEN")


class Form(StatesGroup):
    start = State()
    drink = State()
    tea = State()
    emoji = State()
    disgust = State()
    joker = State()
    video = State()


with open("messages.json", "r", encoding="utf-8") as file:
    messages = json.load(file)


dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    This handler receives messages with `/start` command
    """
    try:
        await state.set_state(Form.start)
        await message.answer(messages["START_MESSAGE"], reply_markup=start_keyboard)
    except Exception as e:
        logging.error(f"Ошибка в командном старте: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")


@dp.callback_query(Form.start, F.data.startswith("start_"))
async def start_handler(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    try:
        await callback.answer("")
        if callback.data.endswith("no"):
            await callback.message.answer_sticker(
                sticker=FSInputFile("sticker.webp"), reply_markup=start_keyboard
            )
        else:
            await state.set_state(Form.drink)
            await callback.message.answer(messages["DRINK_MESSAGE"])
    except Exception as e:
        logging.error(f"Ошибка в командном старте: {e}")
        await callback.message.answer("Произошла ошибка. Попробуйте позже.")


@dp.message(Form.drink)
async def drink_handler(message: Message, state: FSMContext, bot: Bot) -> None:
    try:
        if message.text.lower() != "чай":
            await message.answer("Попей ещё.")
        else:
            await state.set_state(Form.tea)
            await message.answer(messages["TEA_MESSAGE"])
            await message.answer_photo(photo=FSInputFile("tea.jpg"))
            await message.answer("Продолжаем?", reply_markup=start_keyboard)
    except Exception as e:
        logging.error(f"Ошибка в командном старте: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")


@dp.callback_query(Form.tea, F.data.startswith("start_"))
async def tea_handler(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    try:
        await callback.answer("")
        if callback.data.endswith("no"):
            await callback.message.answer_sticker(
                sticker=FSInputFile("sticker.webp"), reply_markup=start_keyboard
            )
        else:
            await state.set_state(Form.emoji)
            await callback.message.answer(messages["EMOJI_MESSAGE"])
    except Exception as e:
        logging.error(f"Ошибка в командном старте: {e}")
        await callback.message.answer("Произошла ошибка. Попробуйте позже.")


@dp.message(Form.emoji)
async def emoji_handler(message: Message, state: FSMContext, bot: Bot) -> None:
    try:
        if message.text.lower() != "брезгливость":
            await message.answer("Боже, как это противно читать.")
        else:
            await message.answer(messages["DISGUST_MESSAGE"])
            await asyncio.sleep(3)
            await state.set_state(Form.joker)
            await message.answer(messages["JOKER_MESSAGE"])
    except Exception as e:
        logging.error(f"Ошибка в командном старте: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")


@dp.message(Form.joker)
async def joker_handler(message: Message, state: FSMContext, bot: Bot) -> None:
    try:
        if message.text.lower() != "шутница":
            await message.answer(messages["JOKER_ANSWER"])
        else:
            await state.set_state(Form.video)
            await message.answer("Всё верно, Елена шучу глазами Михална")
            await message.answer_video(video=FSInputFile("video.mp4"))
    except Exception as e:
        logging.error(f"Ошибка в командном старте: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
