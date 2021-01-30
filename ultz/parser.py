""" Parser module of :mod:`ultz`

    .. note::The datetime is parsed and completed at the datetime of execution, and so\
    may be off-by-one by the end of the parsing if parsed close to a limit (year,\
    month, day, hour, minute, etc).
"""

import datetime as dt
from enum import Enum
from typing import Optional, Tuple


def parse_date(expr: str, form: str = "ISO") -> Optional[dt.date]:
    """Parse a string to a date.

    Four format are supported:

    - If ``form`` is "ISO" (or everything other than "ALT"), the ISO 8601 format is used:
        - Complete format: ``yyyy-mm-dd`` (like 2019-05-13).
        - Shortened format: ``mm-dd`` format (like 11-24) that sets the year to the current one.
    - Else, when ``form`` is "ALT", the following format is used:
        - Complete format: ``dd-mm-yyyy`` (like 13-05-2019).
        - Shortened format: ``dd-mm`` format (like 24-11) that sets the year to the current one.

    :param expr: The date to parse.
    :param form: The format of the date to parse
    :returns: The date if ``expr`` was correctly passed, ``None`` otherwise
    """

    print("=============== {} ===========".format(form))
    alternative = form == "ALT"

    # Try to find a date in the short format first
    month_day = expr.split("-")
    if len(month_day) == 2:
        try:
            year = dt.date.today().year
            month = (int)(month_day[0])
            day = (int)(month_day[1])
            if alternative:
                # Reverse
                month, day = day, month
            date = dt.date(year, month, day)
            return date
        except ValueError:  # pragma: nocover  # Test the next format
            pass

    # Then try the complete date
    try:
        if not alternative:
            date = dt.date.fromisoformat(expr)
            return date

        # else:
        day_month_year = expr.split("-")
        if len(day_month_year) != 3:
            raise ValueError
        day = (int)(month_day[0])
        month = (int)(month_day[1])
        year = (int)(month_day[2])
        date = dt.date(year, month, day)
        return date
    except ValueError:  # pragma: nocover
        pass

    return None


def parse_time(expr: str) -> Optional[dt.time]:
    """Parse a string to a time

    The format supported is the same as :py:meth:`datetime.time.fromisoformat`, meaning
    a string in the format: ``HH[:MM[:SS[.fff[fff]]]][+HH:MM[:SS[.ffffff]]]``

    :param expr: The time to parse.
    :returns: The time if ``expr`` was correctly parsed, ``None`` otherwise
    """

    try:
        time = dt.time.fromisoformat(expr)
        return time
    except ValueError:
        pass

    return None


def parse_datetime(datetime_expr: str, form: str = "ISO") -> Optional[dt.datetime]:
    """Parse a string into a full datetime

    The format supported is the combination of :func:`parse_date` and func:`parse_time`,
    in the format `date time`, date and time being optional if the other is present.

    :param expr: The datetime to parse.
    :param form: The format for parsing the date part.
    :returns: The datetime if ``expr`` was correctly parsed, ``None`` otherwise
    """

    # Try to split into the two components.
    datetime_split = list(map(str.strip, datetime_expr.split(" ")))
    num = len(datetime_split)
    if num > 2:
        # Too much components, wrong expression.
        return None

    if num == 2:
        # The two components are here, extract them.
        date_str, time_str = datetime_split[:2]
    else:
        # Only one of them, we don't know which yet.
        date_str = time_str = datetime_split[0]

    # Parse both of them
    date = parse_date(date_str, form)
    time = parse_time(time_str)

    # None of them were correctly parsed
    if not (date or time):
        return None

    # Note: it may be necessary to add a condition to check if *both* are true for n==1,
    # as that would mean datetime_str would have be recognized as a time and date at the
    # same time. Not necessary now, but may be in the future where we could have an
    # ambiguity between a day and a hour.

    # If one of them is wrongly parsed, set it to current date/time
    if not date:
        date = dt.date.today()

    if not time:
        time = dt.datetime.now().time()

    datetime = dt.datetime.combine(date, time)
    return datetime


class ExprCode(Enum):
    """Enumeration for the possible results of :func:`parse_expression`"""

    ERR = 0
    """Error: expression could not be parsed"""

    TZ_ONLY = 1
    """The expression only contained a timezone """

    TZ_DATEIN = 2
    """The expression contained a timezone and a datetime in the format ``datetime in
    timezone``"""

    TZ_DATEAT = 3
    """The expression contained a timezone and a datetime in the format ``timezone at
    datetime``"""


_ParsingResult = Tuple[ExprCode, Optional[str], Optional[dt.datetime]]


def parse_expression(expr: Optional[str], form: str = "ISO") -> _ParsingResult:
    """Parse an expression querying a timezone and optionally date.

    The expression is one of the follow formats:

    * ``timezone``
    * ``datetime in timezone``
    * ``timezone at datetime``

    :param expr: The expression to parse.
    :param form: The format for parsing the date.
    :returns: - A return code indicating if the expression was correctly parsed and if\
    so the format
              - A raw ``str`` timezone if applicable, ``None`` otherwise
              - A full ``datetime`` if applicable, ``None`` otherwise
    """

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
        date = parse_datetime(split_in[0], form)
        return ExprCode.TZ_DATEIN, location, date

    if len_in == 1 and len_at == 2:
        # [location] at [time]
        location = split_at[0]
        date = parse_datetime(split_at[1], form)
        return ExprCode.TZ_DATEAT, location, date

    return ExprCode.ERR, None, None
