import calendar
import datetime

import pytz

tz = pytz.timezone('Europe/Moscow')


def astz(dt: datetime.datetime):
    return dt.astimezone(tz)


def get_timezone_now():
    """Получаем текущую дату с учётом нашей timezone"""
    return datetime.datetime.now().astimezone(tz)


def add_months(date_obj: datetime.date, months: int) -> datetime.date:
    """
    Добавляет указанное количество месяцев к дате, корректно обрабатывая случаи, когда в целевом месяце
    меньше дней, чем в исходной дате.
    """
    # Рассчитываем новый месяц и год
    new_month = date_obj.month - 1 + months
    new_year = date_obj.year + new_month // 12
    new_month = new_month % 12 + 1
    # Определяем последний день нового месяца
    last_day = calendar.monthrange(new_year, new_month)[1]
    # Если исходный день больше последнего дня нового месяца, выбираем последний день
    new_day = min(date_obj.day, last_day)
    return datetime.date(new_year, new_month, new_day)


def date_to_tz_datetime(date: datetime.date) -> datetime.datetime:
    """Преобразование даты к дате+время по текущей таймзоне. Время устанавливается как 0"""
    return astz(datetime.datetime(date.year, date.month, date.day, 0, 0))


def datetime_to_date(dt: datetime.datetime) -> datetime.date:
    """Преобразование даты+время по текущей таймзоне к дате"""
    return datetime.date(dt.year, dt.month, dt.day)
