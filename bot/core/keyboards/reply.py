from aiogram.types import ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder

remove_kb = ReplyKeyboardRemove()


def get_start_kb():
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.button(text='Найти мотивацию')
    # keyboard_builder.button(text='Узнать подробнее о проекте')
    keyboard_builder.adjust(1)

    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Нажми кнопку,чтобы перейти к выбору цели'
        )


def main_menu_kb():
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.button(text='Найти мотивацию')
    keyboard_builder.button(text='Мои пари')
    keyboard_builder.button(text='Профиль')
    keyboard_builder.button(text='Помощь')
    keyboard_builder.adjust(1, 1, 2)

    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Нажми кнопку,чтобы перейти к выбору цели'
        )


def profile(text: str | list):
    builder = ReplyKeyboardBuilder()

    if isinstance(text, str):
        text = [text]

    [builder.button(text=txt) for txt in text]
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def sex_kb():
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.button(text='Мужчина')
    keyboard_builder.button(text='Женщина')
    keyboard_builder.adjust(2)

    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Нажми кнопку, чтобы выбрать пол'
        )


def category_kb():
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.button(text='Здоровье и спорт')
    keyboard_builder.button(text='Обучение и развитие')
    keyboard_builder.button(text='Личная продуктивность')
    keyboard_builder.button(text='Назад')
    keyboard_builder.adjust(1, 1, 1, 1)

    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Нажми кнопку, чтобы выбрать категорию'
        )


def health_kb():
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.button(text='Заниматься спортом')
    keyboard_builder.button(text='Правильно питаться')
    keyboard_builder.button(text='Пить воду')
    keyboard_builder.button(text='Принимать добавки')
    keyboard_builder.button(text='Делать зарядку')
    keyboard_builder.button(text='Гулять')
    keyboard_builder.button(text='Назад')
    keyboard_builder.adjust(2, 2, 2, 1)
    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Выбери один из вариантов'
    )


def education_kb():
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.button(text='Изучать новый навык')
    keyboard_builder.button(text='Читать')
    keyboard_builder.button(text='Проходить учебный курс')
    keyboard_builder.button(text='Вести дневник')
    keyboard_builder.button(text='Изучать новый язык')
    keyboard_builder.button(text='Медитировать')
    keyboard_builder.button(text='Назад')

    keyboard_builder.adjust(2, 2, 2, 1)

    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Выбери один из вариантов'
    )


def productivity_kb():
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.button(text='Соблюдать режим сна')
    keyboard_builder.button(text='Планировать задачи на день')
    keyboard_builder.button(text='Проводить меньше времени в телефоне')

    keyboard_builder.button(text='Назад')

    keyboard_builder.adjust(2, 1, 1)

    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Выбери один из вариантов'
    )


def frequency_kb(accept: str | None = None):
    keyboard_builder = ReplyKeyboardBuilder()

    day_list = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

    for day in day_list:
        keyboard_builder.button(text=day)
    keyboard_builder.button(text='Ежедневно')
    keyboard_builder.button(text='Назад')
    if accept:
        keyboard_builder.button(text='Подтвердить')

    keyboard_builder.adjust(7, 1, 2)

    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Выбери день недели'
    )


def hours_kb(accept: str | None = None):
    keyboard_builder = ReplyKeyboardBuilder()

    morning = ['5:00', '6:00', '7:00', '8:00', '9:00', '10:00', '11:00']
    day = ['12:00', '13:00', '14:00', '15:00', '16:00', '17:00']
    evening = ['18:00', '19:00', '20:00', '21:00', '22:00', '23:00', '0:00']

    hours_list = (morning + day + evening)

    for hour in hours_list:
        keyboard_builder.button(text=hour)
    keyboard_builder.button(text='Назад')
    if accept:
        keyboard_builder.button(text='Подтвердить')

    keyboard_builder.adjust(5, 5, 5, 5, 2)

    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Выбери время'
    )


# def report_kb():
#     keyboard_builder = ReplyKeyboardBuilder()
#     keyboard_builder.button(text='Утро')
#     keyboard_builder.button(text='День')
#     keyboard_builder.button(text='Вечер')
#     # keyboard_builder.button(text='Напоминания не нужны')

#     keyboard_builder.button(text='Назад')

#     keyboard_builder.adjust(3, 1)

#     return keyboard_builder.as_markup(
#         resize_keyboard=True,
#         one_time_keyboard=True,
#         input_field_placeholder='Выбери один из вариантов'
#     )


def mate_kb():
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.button(text='Мужчина')
    keyboard_builder.button(text='Женщина')
    keyboard_builder.button(text='Не имеет значения')

    keyboard_builder.button(text='Назад')

    keyboard_builder.adjust(2, 1)

    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Выбери один из вариантов'
    )


def pari_find():
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.button(text='Отменить поиск')

    keyboard_builder.adjust(1)

    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Поиск партнера'
    )


def pari_choice():
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.button(text='Подтвердить пари')
    keyboard_builder.button(text='Отказаться')

    keyboard_builder.adjust(1)

    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Подтверждение пари'
    )


def pari_report_cancel():
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.button(text='Отмена')

    keyboard_builder.adjust(1)

    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Загрузи фото'
    )


def pari_report_confirm():
    keyboard_builder = ReplyKeyboardBuilder()
    keyboard_builder.button(text='Отправить на проверку')
    keyboard_builder.button(text='Отмена')

    keyboard_builder.adjust(1, 1)

    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Загрузи фото'
    )
# def confirm_remove():
#     keyboard_builder = ReplyKeyboardBuilder()
#     keyboard_builder.button(text='Отменить подтверждение')

#     keyboard_builder.adjust(1)

#     return keyboard_builder.as_markup(
#         resize_keyboard=True,
#         one_time_keyboard=True,
#         input_field_placeholder='Подтверждение пари',
#         is_persistent=False
#     )

# def mate_report():
#     builder = ReplyKeyboardBuilder()
#     builder.button(
#         text="Опровергнуть",
#         callback_data="report_reject"
#     )
#     builder.button(
#         text="Подтвердить",
#         callback_data="report_approve"
#     )
#     builder.button(
#         text="Отмена",
#         callback_data="сancel_no"
#     )
#     builder.adjust(2, 1)
#     return builder.as_markup()
