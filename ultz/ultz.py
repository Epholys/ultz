"""Take a timezone conversion, expression, parse it, interpret it, and returns a result
for ulauncher."""

import datetime as dt
import logging
from enum import Enum
from typing import Optional, Tuple

import ultz.tzwrap as tzwrap
from ultz.parser import ExprCode, parse_expression

_logger = logging.getLogger(__name__)


def get_datetime(code: ExprCode, when: Optional[dt.datetime]) -> Optional[dt.datetime]:
    """Provide a :py:class:`datetime` from the result of :func:`parse_expression`

    This function simply checks if :func:`parse_expression` found a valid date, and if
    not returns the current datetime

    :param code: The result code of :func:`parse_expression`
    :param when: The datetime found by the parser. Can be ``None``.
    :returns: `when` if both `code` and `when` are valid, ``None`` if ``code`` isn't
              valid, :py:func:`datetime.now()` otherwise.
    """

    date: Optional[dt.datetime] = dt.datetime.now()  # Test
    if code in (ExprCode.TZ_DATEIN, ExprCode.TZ_DATEAT):
        if when:
            date = when
        else:
            date = None
    return date


def get_tz(where: Optional[str]) -> Optional[tzwrap.PyTzInfo]:
    """Returns the `pytz <https://pythonhosted.org/pytz/>`_'s :py:class:`tzinfo`
    associated with the string input


    :param where: The queried timezone found by the parse. Can be ``None``.
    :returns: The associated `pytz <https://pythonhosted.org/pytz/>`_'s
              :py:class:`tzinfo` if ``where`` is a valid timezone, ``None`` otherwise.
    """

    timezone = None
    try:
        timezone = tzwrap.timezone(where)
    except tzwrap.UnknownTimeZoneError:
        pass
    return timezone


def reverse_trip(
    datetime: dt.datetime, timezone: tzwrap.PyTzInfo
) -> Tuple[dt.datetime, Optional[tzwrap.PyTzInfo]]:
    """Reverse the direction of the conversion.

    By default, the program converts a time at the user location in a target
    location. This function inverse the datetime and tzinfo to do the inverse operation:
    converts the time at a certain location in the user's local timezone.

    :param datetime: The datetime to reverse.
    :param timezone: The timezone to reverse.
    :returns: The datetime and timezone, reversed for the next computation.
    """

    # Does not work otherwise!
    # As said in pytz/tzinfo.py:
    # > This method should be used to construct localtimes, rather
    # > than passing a tzinfo argument to a datetime constructor.
    datetime = timezone.localize(datetime)
    here = None
    return datetime, here


class ErrCode(Enum):
    """Enumeration for the possible error codes of :func:`process_input`"""

    EXPR = 0
    """The input is an invalid expression."""

    DATE = 1
    """The input contains an invalid date."""

    TZ = 2
    """The input contains an invalid timezone."""


def get_error_msg(code: ErrCode) -> str:
    """Switch case to get a corresponding error message from a :class:`ErrCode`

    :param code: An error code to explain to the user.
    :returns: A message explaining the error.
    """

    return {
        ErrCode.EXPR: "Incorrect expression",
        ErrCode.DATE: "Incorrect date",
        ErrCode.TZ: "Incorrect timezone",
    }.get(code, "Unknown error code! Contact the dev")


def generate_description(
    code: ExprCode, where: Optional[str], datetime: dt.datetime
) -> str:
    """Switch case to generate a description from the result of the computation.

    :param code: The :mod:`parser` code indicating which computation was done.
    :param where: The queried location.
    :param datetime: The queried datetime.
    :returns: A description of the result.
    """
    return {
        ExprCode.TZ_ONLY: f"Time in {where} now",
        ExprCode.TZ_DATEIN: f'Time in {where}, at {datetime.strftime("%H:%M")} here',
        ExprCode.TZ_DATEAT: f'Time here, in {where} at {datetime.strftime("%H:%M")}',
    }.get(code, "Unknown return code! Contact the dev")


def format_datetime(datetime: dt.datetime) -> str:
    """Format a datetime into a ISO-like format

    :param datetime: The datetime to format
    :returns: A string in the format ``yyyy-mm-dd HH:MM``
    """
    return datetime.strftime("%Y-%m-%d %H:%M")


def process_input(text_input: Optional[str], form: str = "ISO") -> Tuple[str, str, str]:
    """Process an expression for timezone conversion.

    The expression must be one of the following format:

    - ``timezone``: Query the current time in ``timezone`` at current time here.
    - ``datetime in timezone``: Query the time in ``timezone`` at ``datetime`` here.
    - ``timezone at datetime``: Query the time here,  at ``datetime`` in ``timezone``

    :param text_input: The expression to parse and interpret.
    :param form: The format for parsing the date.
    :returns: - If ``text_input`` is correct, the datetime result. Otherwise, a
                descriptive error message.
              - If ``text_input`` is correct, a description of the result. Otherwise,
                empty string.
              - If ``text_input`` is correct, the path to the result icon. Otherwise,
                empty string.

    """

    code, where, when = parse_expression(text_input, form)
    _logger.debug("parse returned: where=%s, when=%s, code=%s", where, when, code)

    if code == ExprCode.ERR:
        return get_error_msg(ErrCode.EXPR), "", ""

    datetime = get_datetime(code, when)
    if not datetime:
        return get_error_msg(ErrCode.DATE), "", ""

    timezone = get_tz(where)
    if not timezone:
        return get_error_msg(ErrCode.TZ), "", ""

    if code == ExprCode.TZ_DATEAT:
        datetime, timezone = reverse_trip(datetime, timezone)

    raw_result = datetime.astimezone(timezone)
    result = format_datetime(raw_result)

    description = generate_description(code, where, datetime)

    return result, description, "images/icon.png"
