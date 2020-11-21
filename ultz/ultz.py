import logging

from enum import Enum
import datetime as dt

import ultz.tzwrap as pytz
from ultz.parser import ExprCode, parse_expression

_logger = logging.getLogger(__name__)


class ErrCode(Enum):
    EXPR = (0,)
    DATE = (1,)
    TZ = 2


def get_datetime(code, when):
    date = dt.datetime.now()
    if code == ExprCode.TZ_DATEIN or code == ExprCode.TZ_DATEAT:
        if when:
            date = when
        else:
            date = None
    return date


def get_tz(where):
    tz = None
    try:
        tz = pytz.timezone(where)
    except pytz.UnknownTimeZoneError:
        pass
    return tz


def reverse_trip(datetime, tz):
    # Does not work otherwise!
    # As said in pytz/tzinfo.py:
    # > This method should be used to construct localtimes, rather
    # > than passing a tzinfo argument to a datetime constructor.
    datetime = tz.localize(datetime)
    tz = None  # = here
    return datetime, tz


def get_error_msg(code):
    return {
        ErrCode.EXPR: "Incorrect expression",
        ErrCode.DATE: "Incorrect date",
        ErrCode.TZ: "Incorrect timezone",
    }.get(code, "Unknown error code! Contact the dev")


def generate_description(code, where, datetime):
    return {
        ExprCode.TZ_ONLY: f"Time in {where} now",
        ExprCode.TZ_DATEIN: f'Time in {where}, at {datetime.strftime("%H:%M")} here',
        ExprCode.TZ_DATEAT: f'Time here, in {where} at {datetime.strftime("%H:%M")}',
    }.get(code, "Unknown return code! Contact the dev")


def format_datetime(datetime):
    return datetime.strftime("%Y-%m-%d %H:%M")


def process_input(text_input):
    code, where, when = parse_expression(text_input)
    _logger.debug(f"parse returned: where={where}, when={when}, code={code}")

    if code == ExprCode.ERR:
        return get_error_msg(ErrCode.EXPR), "", ""

    datetime = get_datetime(code, when)
    if not datetime:
        return get_error_msg(ErrCode.DATE), "", ""

    tz = get_tz(where)
    if not tz:
        return get_error_msg(ErrCode.TZ), "", ""

    if code == ExprCode.TZ_DATEAT:
        datetime, tz = reverse_trip(datetime, tz)

    raw_result = datetime.astimezone(tz)
    result = format_datetime(raw_result)

    description = generate_description(code, where, datetime)

    return result, description, "images/icon.png"
