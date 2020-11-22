import datetime as dt
from enum import Enum
from typing import Optional, Tuple


class ExprCode(Enum):
    ERR = 0
    TZ_ONLY = 1
    TZ_DATEIN = 2
    TZ_DATEAT = 3


def parse_date(date_expr: str) -> Optional[dt.date]:
    # Try to find a date in "mm-dd" format first
    # (This is not supported by datetime, as it wants "yyyy-" first)
    month_day = date_expr.split("-")
    if len(month_day) == 2:
        try:
            year = dt.date.today().year
            month = (int)(month_day[0])
            day = (int)(month_day[1])
            date = dt.date(year, month, day)
            return date
        except ValueError:  # pragma: nocover
            pass

    # Okay, then try the complete date
    try:
        date = dt.date.fromisoformat(date_expr)
        return date
    except ValueError:  # pragma: nocover
        pass

    return None


def parse_time(time_expr: str) -> Optional[dt.time]:
    # Try to parse a simple time in HH:MM:SS format:
    # (HH alone, and HH:MM alone are also supported)
    try:
        time = dt.time.fromisoformat(time_expr)
        return time
    except ValueError:
        pass

    return None


def parse_datetime(datetime_expr: str) -> Optional[dt.datetime]:
    # Note: suppose the day, month, or year will not change the next second
    datetime_split = list(map(str.strip, datetime_expr.split(" ")))
    n = len(datetime_split)
    if n > 2:
        return None

    if n == 2:
        date_str, time_str = datetime_split[:2]
    else:
        date_str = time_str = datetime_split[0]

    date = parse_date(date_str)
    time = parse_time(time_str)

    if not (date or time):
        return None

    # Note: it may be necessary to add a condition to check if *both* are true for n==1,
    # as that would mean datetime_str would have be recognized as a time and date at the
    # same time.

    if not date:
        date = dt.date.today()

    if not time:
        time = dt.datetime.now().time()

    datetime = dt.datetime.combine(date, time)
    return datetime


_ParsingResult = Tuple[ExprCode, Optional[str], Optional[dt.datetime]]


def parse_expression(expr: Optional[str]) -> _ParsingResult:
    if expr is None or expr == "":
        return ExprCode.ERR, None, None

    # Split & Strip
    split_in = list(map(str.strip, expr.split(" in ")))
    len_in = len(split_in)

    split_at = list(map(str.strip, expr.split(" at ")))
    len_at = len(split_at)

    if len_in == 1 and len_at == 1:
        # [location]
        location = split_in[0]
        return ExprCode.TZ_ONLY, location, None

    if len_in == 2 and len_at == 1:
        # [time] in [location]
        location = split_in[1]
        date = parse_datetime(split_in[0])
        return ExprCode.TZ_DATEIN, location, date

    if len_in == 1 and len_at == 2:
        # [location] at [time]
        location = split_at[0]
        date = parse_datetime(split_at[1])
        return ExprCode.TZ_DATEAT, location, date

    return ExprCode.ERR, None, None
