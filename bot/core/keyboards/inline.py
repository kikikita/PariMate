from typing import Optional
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


def get_start_kb():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text='Найти мотивацию',
        callback_data='start_'

                            )
    # keyboard_builder.button(text='Узнать подробнее о проекте')
    keyboard_builder.adjust(1)

    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Нажми кнопку,чтобы перейти к выбору цели'
        )


def profile(text: str | list):
    builder = InlineKeyboardBuilder()

    if isinstance(text, str):
        text = [text]

    [builder.button(text=txt, callback_data=f'info_{text}') for txt in text]
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_main_menu():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Найти мотивацию",
        callback_data="start_"
    )
    builder.button(
        text="Мои пари",
        callback_data="pari"
    )
    builder.button(
        text="Профиль",
        callback_data="profile"
    )
    builder.button(
        text="Помощь",
        callback_data="help"
    )

    builder.adjust(1, 1, 2)
    return builder.as_markup()


def sex_kb():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text='Мужчина',
        callback_data='sex_Мужчина'
                            )
    keyboard_builder.button(
        text='Женщина',
        callback_data='sex_Женщина'
                            )
    keyboard_builder.adjust(2)

    return keyboard_builder.as_markup(
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Нажми кнопку, чтобы выбрать пол'
        )


def category_kb():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text='Здоровье и спорт',
                            callback_data='habit_Здоровье и спорт')
    keyboard_builder.button(text='Обучение и развитие',
                            callback_data='habit_Обучение и развитие')
    keyboard_builder.button(text='Личная продуктивность',
                            callback_data='habit_Личная продуктивность')
    keyboard_builder.adjust(1, 1, 1)

    return keyboard_builder.as_markup()


def health_kb():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text='Заниматься спортом',
        callback_data='choice_Заниматься спортом')
    keyboard_builder.button(
        text='Правильно питаться',
        callback_data='choice_Правильно питаться')
    keyboard_builder.button(
        text='Пить воду',
        callback_data='choice_Пить воду')
    keyboard_builder.button(
        text='Принимать добавки',
        callback_data='choice_Принимать добавки')
    keyboard_builder.button(
        text='Делать зарядку',
        callback_data='choice_Делать зарядку')
    keyboard_builder.button(
        text='Гулять',
        callback_data='choice_Гулять')
    keyboard_builder.button(
        text='Назад',
        callback_data='start_')
    keyboard_builder.adjust(2, 2, 2, 1)
    return keyboard_builder.as_markup()


def education_kb():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        callback_data='choice_Изучать новый навык',
        text='Изучать новый навык')
    keyboard_builder.button(
        callback_data='choice_Читать',
        text='Читать')
    keyboard_builder.button(
        callback_data='choice_Проходить курс',
        text='Проходить курс')
    keyboard_builder.button(
        callback_data='choice_Вести дневник',
        text='Вести дневник')
    keyboard_builder.button(
        callback_data='choice_Изучать новый язык',
        text='Изучать новый язык')
    keyboard_builder.button(
        callback_data='choice_Медитировать',
        text='Медитировать')
    keyboard_builder.button(
        callback_data='start_',
        text='Назад')

    keyboard_builder.adjust(2, 2, 2, 1)

    return keyboard_builder.as_markup()


def productivity_kb():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        callback_data='choice_Соблюдать режим сна',
        text='Соблюдать режим сна')
    keyboard_builder.button(
        callback_data='choice_Планировать задачи',
        text='Планировать задачи')
    keyboard_builder.button(
        callback_data='choice_Меньше сидеть в телефоне',
        text='Меньше сидеть в телефоне')
    keyboard_builder.button(
        text='Назад',
        callback_data='start_')

    keyboard_builder.adjust(1, 1, 1)
    return keyboard_builder.as_markup()


def frequency_kb(habit_category: str, accept: str | None = None):
    keyboard_builder = InlineKeyboardBuilder()

    day_list = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']

    for day in day_list:
        keyboard_builder.button(
            text=day,
            callback_data=f'freq_{day}')
    keyboard_builder.button(
        text='Ежедневно', callback_data='freq_Ежедневно')
    keyboard_builder.button(
        text='Назад', callback_data=f'habit_{habit_category}')
    if accept:
        keyboard_builder.button(
            text='Подтвердить', callback_data='approve_freq')

    keyboard_builder.adjust(7, 1, 2)

    return keyboard_builder.as_markup()


def hours_kb(accept: str | None = None):
    keyboard_builder = InlineKeyboardBuilder()

    morning = ['5:00', '6:00', '7:00', '8:00', '9:00', '10:00', '11:00']
    day = ['12:00', '13:00', '14:00', '15:00', '16:00', '17:00']
    evening = ['18:00', '19:00', '20:00', '21:00', '22:00', '23:00', '0:00']

    hours_list = (morning + day + evening)

    for hour in hours_list:
        keyboard_builder.button(text=hour,
                                callback_data=f'time_{hour}')
    keyboard_builder.button(text='Назад',
                            callback_data='choice_')
    if accept:
        keyboard_builder.button(text='Подтвердить',
                                callback_data='approve_time')

    keyboard_builder.adjust(5, 5, 5, 5, 2)

    return keyboard_builder.as_markup()


def mate_kb():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        callback_data='sex_Мужчина',
        text='Мужчина')
    keyboard_builder.button(
        callback_data='sex_Женщина',
        text='Женщина')
    keyboard_builder.button(
        callback_data='sex_Не имеет значения',
        text='Не имеет значения')

    keyboard_builder.button(text='Назад',
                            callback_data='approve_freq')

    keyboard_builder.adjust(2, 1)

    return keyboard_builder.as_markup()


def pari_find():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text='Отменить поиск',
        callback_data='find_cancel')

    keyboard_builder.adjust(1)

    return keyboard_builder.as_markup()


def pari_choice():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text='Подтвердить пари',
        callback_data='find_accept')
    keyboard_builder.button(
        text='Отказаться',
        callback_data='find_decline')

    keyboard_builder.adjust(1)

    return keyboard_builder.as_markup()


def pari_find_start():
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text='Найти напрарника по привычке',
        callback_data='find_start')
    keyboard_builder.button(
        text='Изменить данные о привычке',
        callback_data='start_change')

    keyboard_builder.adjust(1)

    return keyboard_builder.as_markup()

############################################################
def get_pari(pari_link: str, user_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Досрочно завершить пари",
        callback_data=f"pari_сancel_{user_id}"
    )
    builder.button(
        text="Перейти в совместный чат",
        url=pari_link
    )
    builder.button(
        text="Отчеты напарника",
        callback_data=f"mate_report_{user_id}"
    )
    builder.button(
        text="Подтвердить выполнение привычки",
        callback_data=f"update_report_{user_id}"
    )

    builder.adjust(1, 1)
    return builder.as_markup()


def get_report(user_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Отправить на проверку",
        callback_data=f"send_report_{user_id}"
    )
    builder.button(
        text="Добавить фото",
        callback_data=f"update_report_{user_id}"
    )
    builder.button(
        text="Отмена",
        callback_data=f"сancel_no_{user_id}"
    )
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def cancel_approve(user_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Да",
        callback_data=f"сancel_yes_{user_id}"
    )
    builder.button(
        text="Нет",
        callback_data=f"сancel_no_{user_id}"
    )

    builder.adjust(2)
    return builder.as_markup()


def tech_report(user_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Загрузить отчет",
        callback_data=f"mate_report_tech_{user_id}"
    )
    builder.adjust(1)
    return builder.as_markup()


def mate_report(user_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Отклонить",
        callback_data=f"report_reject_{user_id}"
    )
    builder.button(
        text="Подтвердить",
        callback_data=f"report_approve_{user_id}"
    )

    builder.adjust(2)
    return builder.as_markup()


def pari_report_more(user_id: int | None = None):
    builder = InlineKeyboardBuilder()
    if user_id:
        report = str(user_id)
    else:
        report = 'report'
    builder.button(
        text="Нет",
        callback_data=f"сancel_no_{report}"
    )
    builder.button(
        text="Да",
        callback_data=f"mate_report_{report}"
    )

    builder.adjust(2)
    return builder.as_markup()


def cancel_сancel(user_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Отмена",
        callback_data=f"сancel_no_{user_id}"
    )

    builder.adjust(1)
    return builder.as_markup()


class MenuCallbackFactory(CallbackData, prefix="menu"):
    action: str
    value: Optional[int] = None


def pari_report_confirm(user_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Отправить на подтверждение",
        callback_data=f"send_report_{user_id}"
    )
    builder.button(
        text="Отмена",
        callback_data=f"сancel_no_{user_id}"
    )
    builder.adjust(1, 1)
    return builder.as_markup()


def cancel_report_reject(user_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Отмена",
        callback_data=f"cancel_report_reject_{user_id}"
    )

    builder.adjust(1)
    return builder.as_markup()


def pari_report_from_notify(user_id: int):
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Подтвердить выполнение привычки",
        callback_data=f"update_report_{user_id}"
    )
    builder.adjust(1)
    return builder.as_markup()


def profile_kb(notify: int | None = None):
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Изменить данные о себе",
        callback_data="update_profile"
    )
    # if notify:
    #     builder.button(
    #         text="Изменить время напоминаний",
    #         callback_data="update_notifications"
    #     )
    builder.adjust(1)
    return builder.as_markup()


def get_user_link(user_id: int):
    builder = InlineKeyboardBuilder()
    button_url = f'tg://openmessage?user_id={user_id}'
    builder.button(
        text="Ссылка",
        url=button_url
    )

    return builder.as_markup()


class NumbersCallbackFactory(CallbackData, prefix="fabnum"):
    action: str
    value: Optional[int] = None


def get_keyboard_fab():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="-2", callback_data=NumbersCallbackFactory(action="change",
                                                        value=-2)
    )
    builder.button(
        text="-1", callback_data=NumbersCallbackFactory(action="change",
                                                        value=-1)
    )
    builder.button(
        text="+1", callback_data=NumbersCallbackFactory(action="change",
                                                        value=1)
    )
    builder.button(
        text="+2", callback_data=NumbersCallbackFactory(action="change",
                                                        value=2)
    )
    builder.button(
        text="Подтвердить",
        callback_data=NumbersCallbackFactory(action="finish")
    )
    # Выравниваем кнопки по 4 в ряд, чтобы получилось 4 + 1
    builder.adjust(4)
    return builder.as_markup()
