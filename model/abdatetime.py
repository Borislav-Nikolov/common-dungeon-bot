from datetime import datetime


class AbDatetime:

    def __init__(
            self,
            year: int,
            month: int,
            day: int,
            hour: int,
            minute: int,
            second: int
    ):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second

    def __str__(self):
        return f"AbDatetime(year='{self.year}', month='{self.month}', day='{self.day}', hour='{self.hour}')"
