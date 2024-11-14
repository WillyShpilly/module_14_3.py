from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery, FSInputFile
from keyboards import kb, inline_kb, inline_buy
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from crud_functions import initiate_db


initiate_db()

BOT_TOKEN = ''

storage = MemoryStorage()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=storage)


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()
    male = State()



@dp.message(Command(commands='start'))
async def process_start_command(message: Message):
    print('Readey, stady, go!!!')
    await message.answer("Привет! Я бот помогающий твоему здоровью.", reply_markup=kb)


@dp.message(F.text == 'Рассчитать') # попробовать тексту дату
async def main_menu(message: Message):
    await message.answer('Выберите опцию:', reply_markup=inline_kb)


@dp.message(F.text == 'Купить')
async def get_buying_list(message: Message):
    for i in range(1, 5):  # Измените диапазон в зависимости от количества фотографий
        photo = f"image{i}.jpg"
        await message.answer_photo(photo=FSInputFile(photo), caption=f'Название: Product {i} | Описание: описание {i} | Цена: {i * 100}')
    await message.answer('Выберите продукт для покупки:', reply_markup=inline_buy)
    

@dp.callback_query(F.data == 'product_buying')
async def send_confirm_message(callback: CallbackQuery):
    await callback.message.answer('Вы успешно приобрели продукт!')


@dp.callback_query(F.data == 'formulas')
async def get_formulas(callback: CallbackQuery):
    await callback.message.answer(
        "Формула Миффлина-Сан Жеора:\n"
        "Для жентельменов: 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) + 5\n"
        "Для мадамов: 10 * вес (кг) + 6.25 * рост (см) - 5 * возраст (лет) - 161"
    )


@dp.callback_query(F.data == 'calories')
async def set_age(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserState.age)
    await callback.message.answer('Введите свой возраст:')


@dp.message(UserState.age)
async def set_growth(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await state.set_state(UserState.growth)
    await message.answer('Введите свой рост в сантиметрах:')


@dp.message(UserState.growth)
async def set_weigth(message: Message, state: FSMContext):
    await state.update_data(growth=message.text)
    await state.set_state(UserState.weight)
    await message.answer('Введите свой вес в килограммах:')    


@dp.message(UserState.weight)
async def set_male(message: Message, state: FSMContext):
    await state.update_data(weight=message.text)
    await state.set_state(UserState.male)
    await message.answer('Укажите свой пол: (Ж)-Жентельмен или (М)-Мадам')


@dp.message(UserState.male)
async def send_calories(message: Message, state: FSMContext):
    await state.update_data(male=message.text)
    data = await state.get_data()

    if data['male'].lower() == 'ж':
        calories = int(data['weight']) * 10 + int(data['growth']) * 6.25 - int(data['age']) * 5 + 5
    elif data['male'].lower() == 'м':
        calories = int(data['weight']) * 10 + int(data['growth']) * 6.25 - int(data['age']) * 5 - 161

    await message.answer(f'Ваша суточная норма калорий:{calories:.2f}')
    await state.clear()


@dp.message()
async def send_echo(message: Message):
    await message.reply(text='Еще разок, мамаша!')



if __name__ == '__main__':
    dp.run_polling(bot)   