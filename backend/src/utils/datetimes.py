import calendar
import datetime

import pytz

tz = pytz.timezone('Europe/Moscow')


def astz(dt: datetime.datetime):
    """
    Convert a datetime to the Europe/Moscow timezone.

    :param dt: A timezone-aware or naive datetime.
    :return: A timezone-aware datetime in the Europe/Moscow timezone.
    """
    return dt.astimezone(tz)


def get_timezone_now():
    """
    Get the current datetime with the Europe/Moscow timezone applied.

    :return: Current timezone-aware datetime in Europe/Moscow timezone.
    """
    return datetime.datetime.now().astimezone(tz)


def add_months(date_obj: datetime.date, months: int) -> datetime.date:
    """
    Add a given number of months to a date, adjusting the day if the target month has fewer days.

    :param date_obj: The initial date.
    :param months: Number of months to add (can be negative).
    :return: A new date with the added months applied.
    """
    # Calculate the new month and year
    new_month = date_obj.month - 1 + months
    new_year = date_obj.year + new_month // 12
    new_month = new_month % 12 + 1
    # Determine the last day of the new month
    last_day = calendar.monthrange(new_year, new_month)[1]
    # If the original day exceeds the last day of the new month, use the last day instead
    new_day = min(date_obj.day, last_day)
    return datetime.date(new_year, new_month, new_day)


def date_to_tz_datetime(date: datetime.date) -> datetime.datetime:
    """
    Convert a date to a timezone-aware datetime at midnight.

    :param date: A date object.
    :return: A timezone-aware datetime object at 00:00 in Europe/Moscow timezone.
    """
    return astz(datetime.datetime(date.year, date.month, date.day, 0, 0))


def datetime_to_date(dt: datetime.datetime) -> datetime.date:
    """
    Convert a datetime to a date, discarding the time component.

    :param dt: A datetime object.
    :return: The corresponding date object.
    """
    return datetime.date(dt.year, dt.month, dt.day)
