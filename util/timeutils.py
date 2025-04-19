from datetime import datetime

from model.abdatetime import AbDatetime


def month_name_from_number(month) -> str:
    if month == 1:
        return "January"
    elif month == 2:
        return "February"
    elif month == 3:
        return "March"
    elif month == 4:
        return "April"
    elif month == 5:
        return "May"
    elif month == 6:
        return "June"
    elif month == 7:
        return "July"
    elif month == 8:
        return "August"
    elif month == 9:
        return "September"
    elif month == 10:
        return "October"
    elif month == 11:
        return "November"
    elif month == 12:
        return "December"
    else:
        raise ValueError("Invalid month number")


def get_ab_string(ab_time: AbDatetime):
    return f'{ab_time.day} {month_name_from_number(ab_time.month)} {ab_time.year} AB'


def parse_date_str(date_str: str) -> datetime:
    return datetime.strptime(date_str, '%Y-%m-%d')


def parse_datetime_str(datetime_str: str) -> datetime:
    return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
