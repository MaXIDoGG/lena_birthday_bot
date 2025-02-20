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
from aiogram.fsm.storage.base import StorageKey
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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
    shovel = State()
    eminem = State()
    groups = State()
    arena = State()
    end = State()


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
        logging.error(f"Ошибка: {e}")
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
        logging.error(f"Ошибка: {e}")
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
        logging.error(f"Ошибка: {e}")
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
        logging.error(f"Ошибка: {e}")
        await callback.message.answer("Произошла ошибка. Попробуйте позже.")


@dp.message(Form.emoji)
async def emoji_handler(message: Message, state: FSMContext, bot: Bot) -> None:
    try:
        if message.text.lower() != "брезгливость":
            await message.answer("Боже, как это противно читать.")
        else:
            await message.answer(messages["DISGUST_MESSAGE"])
            await asyncio.sleep(30)
            await state.set_state(Form.joker)
            await message.answer(messages["JOKER_MESSAGE"])
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")


@dp.message(Form.joker)
async def joker_handler(message: Message, state: FSMContext, bot: Bot) -> None:
    try:
        if message.text.lower() != "шутница":
            await message.answer(messages["JOKER_ANSWER"])
        else:
            await state.set_state(Form.video)
            await message.answer("Всё верно, Елена шучу глазами Михална")
            await message.answer_video(
                video=FSInputFile("video.mp4"), width=720, height=1180
            )
            await message.answer(
                "Для Знакомства со следующей личностью нужно выполнить задание:\nВышли секретное видео об одном из своих попутчиков."
            )
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")


@dp.message(F.video, Form.video)
async def video_handler(message: Message, state: FSMContext, bot: Bot) -> None:
    try:
        await message.answer("Подождите, видео в обработке...")
        await bot.send_video(
            chat_id="566488188",
            video=message.video.file_id,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Подтвердить",
                            callback_data=f"approve_{message.from_user.id}",
                        ),
                        InlineKeyboardButton(
                            text="Отклонить",
                            callback_data=f"reject_{message.from_user.id}",
                        ),
                    ]
                ]
            ),
        )
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")


@dp.callback_query(F.data.startswith("approve_") | F.data.startswith("reject_"))
async def approve_reject_handler(callback: CallbackQuery, bot: Bot) -> None:
    try:
        await callback.answer("")
        # Извлекаем действие (approve или reject) и ID первого пользователя
        action, user_id = callback.data.split("_")
        user_id = int(user_id)

        state_with: FSMContext = FSMContext(
            # bot=bot,  # объект бота
            storage=dp.storage,
            key=StorageKey(chat_id=user_id, user_id=user_id, bot_id=bot.id),
        )
        await state_with.update_data()

        if action == "approve":
            await bot.send_message(
                chat_id=user_id, text="Ну ты настоящий Хелен ШПИОН, такого я не ожидал."
            )
            await asyncio.sleep(60)
            await bot.send_message(
                chat_id=user_id,
                text="Кажется мы застряли, Лен, как насчет лопаты и хоть раз в жизни нормально поработать? Ток скинь фотку, а то я не поверю.",
            )
            await state_with.set_state(Form.shovel)
        elif action == "reject":
            await bot.send_message(chat_id=user_id, text="Ваше видео было отклонено.")

        await callback.answer()
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await callback.message.answer("Произошла ошибка. Попробуйте позже.")


@dp.message(F.photo, Form.shovel)
async def photo_handler(message: Message, state: FSMContext, bot: Bot) -> None:
    try:
        await message.answer("Подожди, фото в обработке...")
        await bot.send_photo(
            chat_id="566488188",
            photo=message.photo[0].file_id,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Подтвердить",
                            callback_data=f"approve2_{message.from_user.id}",
                        ),
                        InlineKeyboardButton(
                            text="Отклонить",
                            callback_data=f"reject2_{message.from_user.id}",
                        ),
                    ]
                ]
            ),
        )
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")


@dp.callback_query(F.data.startswith("approve2_") | F.data.startswith("reject2_"))
async def approve_reject_handler2(callback: CallbackQuery, bot: Bot) -> None:
    try:
        await callback.answer("")
        # Извлекаем действие (approve или reject) и ID первого пользователя
        action, user_id = callback.data.split("_")
        user_id = int(user_id)

        state_with: FSMContext = FSMContext(
            # bot=bot,  # объект бота
            storage=dp.storage,
            key=StorageKey(chat_id=user_id, user_id=user_id, bot_id=bot.id),
        )
        await state_with.update_data()

        if action == "approve2":
            await bot.send_message(
                chat_id=user_id,
                text="Ну вот вошла в чат ещё одна твоя субличность ЕленаТрудоголик. Она не дает всем другим выйти в этот мир.",
            )
            await asyncio.sleep(60)
            await bot.send_message(
                chat_id=user_id,
                text="Кто не любит песни?\nА то я узнал, что голос твой совершенный, мои помощники тебе подскажут что делать дальше. И подскажут тебе кодовое слово",
            )
            await state_with.set_state(Form.eminem)
        elif action == "reject2":
            await bot.send_message(chat_id=user_id, text="Ваше фото было отклонено.")

        await callback.answer()
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await callback.message.answer("Произошла ошибка. Попробуйте позже.")


messages2 = [
    "А можно записать в группу на 32 урок? Мы как на пробный хотим.",
    "Мы хотим в субботу на майнкрафт записаться",
    "А скиньте расписание пробных уроков.",
    "А когда запустится группа?",
    "А мы хотим добавить в группу друга.",
    "А чем отличается ваш Roblox?",
    "Можно записаться на мастер-класс?",
    "Нам бы отработку поставить.",
    "Мама Веры Киселевой звонила, спрашивала работает еще Елена в нашей школе или нет. Почему она не отвечает на сообщения",
    "Елена, мы пропустим урок, мы улетаем в Дубаи",
    "Можно онлайн подключиться?",
    "Мы бы хотели поменять преподавателя.",
    "Куда вносить оплату?",
    "Ну где ссылка? сколько можно ждать?",
    "Можно в Лагерь записаться на 20 смену?",
    "Мы хотим в группу только к Василине.",
    "Мы всё ещё ждём ссылку…",
    "А сколько максимум человек может быть в группе?",
]


@dp.message(Form.eminem)
async def eminem_handler(message: Message, state: FSMContext, bot: Bot) -> None:
    try:
        if message.text.lower() != "eminem":
            await message.answer("Неправильно!")
        else:
            await message.answer(
                "Не зря твоя фамилия Фионова, а как известно принцесса Фиона обладала волшебным голосом, эта личность в тебе от неё."
            )
            await asyncio.sleep(28)
            for m in messages2:
                await asyncio.sleep(2)
                await message.answer(m)

            await state.set_state(Form.groups)
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")


@dp.message(Form.groups)
async def groups_handler(message: Message, state: FSMContext, bot: Bot) -> None:
    try:
        if int(message.text) > 18:
            await message.answer("Меньше!")
        elif int(message.text) < 18:
            await message.answer("Больше!")
        else:
            await message.answer("Ну и вот она Елена Впихну Невпихуемое")
            await message.answer_video(video=FSInputFile("video2.mp4"))
            await message.answer(
                "Буду ждать следующего слова. Мои помощники подскажут вновь."
            )

            await state.set_state(Form.arena)
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")


@dp.message(Form.arena)
async def arena_handler(message: Message, state: FSMContext, bot: Bot) -> None:
    try:
        if message.text.lower() != "сибирь арена":
            await message.answer("Неправильно!")
        else:
            await message.answer(
                "Ты знаешь сколько стоит это построить? Иначе как сибирской щедростью это не назовёшь, хотя кому я рассказываю, Щедрая Елена. Дальше уже дело за моими помощниками.\nНу а я поздравляю тебя с твоим днем рождения и желаю тебе всегда находить баланс между всеми твоими личностями, а их ещё ооооочень много 🤍"
            )

            await state.set_state(Form.end)
    except Exception as e:
        logging.error(f"Ошибка: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
