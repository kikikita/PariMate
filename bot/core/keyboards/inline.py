from typing import Optional
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


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


def get_main_menu():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Выбрать привычку",
        callback_data=MenuCallbackFactory(action="habit")
    )
    builder.button(
        text="Мои пари",
        callback_data=MenuCallbackFactory(action="pari")
    )
    builder.button(
        text="Профиль",
        callback_data=MenuCallbackFactory(action="profile")
    )

    builder.adjust(1, 2)
    return builder.as_markup()


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
