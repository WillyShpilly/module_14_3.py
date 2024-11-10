from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

api = ""
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())

start_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Информация'),
            KeyboardButton(text='Рассчитать')
        ],
        [KeyboardButton(text='Купить')]
    ], resize_keyboard=True
)

check_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Рассчитать норму калорий", callback_data="calories")],
        [InlineKeyboardButton(text="Формулы расчёта", callback_data="formulas")]
    ]
)

buy_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Product1", callback_data="product_buying"),
            InlineKeyboardButton(text="Product2", callback_data="product_buying"),
            InlineKeyboardButton(text="Product3", callback_data="product_buying"),
            InlineKeyboardButton(text="Product4", callback_data="product_buying")
        ]
    ]
)


@dp.message_handler(commands=['start'])
async def start(message):
    print('стартуем! я сказала стартуем!!!')
    await message.answer("Привет! Я бот помогающий твоему здоровью.", reply_markup=start_menu)


@dp.message_handler(text='Купить')
async def get_buying_list(message):
    with open("image1.jpg", "rb") as One:
        await message.answer_photo(One, f"Название: Product1 | Описание: One | Цена: {1*100}")
    with open("image2.jpg", "rb") as Two:
        await message.answer_photo(Two, f"Название: Product2 | Описание: Two | Цена: {2*100}")
    with open("image3.jpg", "rb") as Three:
        await message.answer_photo(Three, f"Название: Product3 | Описание: Three | Цена: {3*100}")
    with open("image4.jpg", "rb") as Four:
        await message.answer_photo(Four, f"Название: Product4 | Описание: Four | Цена: {4*100}")
    await message.answer("Выберите продукт для покупки:", reply_markup=buy_menu)


@dp.callback_query_handler(text="product_buying")
async def send_confirm_message(call):
    await call.message.answer("Вы успешно приобрели продукт!")
    await call.answer()


@dp.message_handler(text="Рассчитать")
async def main_menu(message):
    await message.answer("Выберите опцию", reply_markup=check_menu)


@dp.callback_query_handler(text="formulas")
async def get_formulas(call):
    formula_message = (
        "Формула Миффлина-Сан Жеора:\n"
        "Для мужчин: 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) + 5\n"
        "Для женщин: 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) - 161"
    )
    await call.message.answer(formula_message)
    await call.answer()


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()
    male = State()


@dp.callback_query_handler(text="calories")
async def set_age(call):
    await call.message.answer("Введите свой возраст:")
    await UserState.age.set()
    await call.answer()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=int(message.text))
    await message.answer("Введите свой рост:")
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=int(message.text))
    await message.answer("Введите свой вес:")
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def set_weight(message, state):
    await state.update_data(weight=int(message.text))
    await message.answer('Укажите свой пол: (Ж)Жентельмен или (М)Мадам')
    await UserState.male.set()


@dp.message_handler(state=UserState.male)
async def set_male(message, state):
    await state.update_data(male=message.text)

    data = await state.get_data()
    age = data['age']
    growth = data['growth']
    weight = data['weight']
    male = data['male']

    if male == 'ж' or 'Ж':
        calories = 10 * weight + 6.25 * growth - 5 * age + 5
    elif male == 'м' or 'М':
        calories = 10 * weight + 6.25 * growth - 5 * age - 161

    await message.answer(f'Ваша норма калорий: {calories:.2f} ккал в сутки.')



@dp.message_handler()
async def all_massages(message):
    await message.answer('Моя твоя не понимать!!!!!!/start, чтобы начать общение.')


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)