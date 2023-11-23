from typing import Optional
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


def get_pari(pari_link):
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Досрочно завершить пари",
        callback_data="pari_сancel"
    )
    builder.button(
        text="Перейти в совместный чат",
        url=pari_link
    )
    builder.button(
        text="Отчеты напарника",
        callback_data="mate_report"
    )
    builder.button(
        text="Подтвердить выполнение привычки",
        callback_data="update_report"
    )

    builder.adjust(1, 1)
    return builder.as_markup()


def get_report():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Отправить на проверку",
        callback_data="send_report"
    )
    builder.button(
        text="Добавить фото",
        callback_data="update_report"
    )
    builder.button(
        text="Отмена",
        callback_data="сancel_no"
    )
    builder.adjust(1, 1, 1)
    return builder.as_markup()


def cancel_approve():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Да",
        callback_data="сancel_yes"
    )
    builder.button(
        text="Нет",
        callback_data="сancel_no"
    )

    builder.adjust(2)
    return builder.as_markup()


def mate_report():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Отклонить",
        callback_data="report_reject"
    )
    builder.button(
        text="Подтвердить",
        callback_data="report_approve"
    )

    builder.adjust(2)
    return builder.as_markup()


def pari_report_more():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Нет",
        callback_data="сancel_no"
    )
    builder.button(
        text="Да",
        callback_data="mate_report"
    )

    builder.adjust(2)
    return builder.as_markup()


def cancel_сancel():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Отмена",
        callback_data="сancel_no"
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


def pari_report_confirm():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Отправить на подтверждение",
        callback_data="send_report"
    )
    builder.button(
        text="Отмена",
        callback_data="сancel_no"
    )
    builder.adjust(1, 1)
    return builder.as_markup()


def cancel_report_reject():
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Отмена",
        callback_data="cancel_report_reject"
    )

    builder.adjust(1)
    return builder.as_markup()


def pari_report_from_notify():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Подтвердить выполнение привычки",
        callback_data="update_report"
    )
    builder.adjust(1)
    return builder.as_markup()


def profile_kb():
    builder = InlineKeyboardBuilder()

    builder.button(
        text="Изменить данные о себе",
        callback_data="update_profile"
    )
    builder.button(
        text="Изменить время напоминаний",
        callback_data="notifications"
    )
    builder.adjust(1, 1, 1)
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
