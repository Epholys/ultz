import logging

from enum import Enum
from typing import Optional, Tuple
import datetime as dt

import ultz.tzwrap as tzwrap
from ultz.parser import ExprCode, parse_expression

_logger = logging.getLogger(__name__)


class ErrCode(Enum):
    EXPR = (0,)
    DATE = (1,)
    TZ = 2


def get_datetime(code: ExprCode, when: Optional[dt.datetime]) -> Optional[dt.datetime]:
    date: Optional[dt.datetime] = dt.datetime.now()
    if code == ExprCode.TZ_DATEIN or code == ExprCode.TZ_DATEAT:
        if when:
            date = when
        else:
            date = None
    return date


def get_tz(where: Optional[str]) -> Optional[tzwrap.PyTzInfo]:
    tz = None
    try:
        tz = tzwrap.timezone(where)
    except tzwrap.UnknownTimeZoneError:
        pass
    return tz


def reverse_trip(
    datetime: dt.datetime, tz: tzwrap.PyTzInfo
) -> Tuple[dt.datetime, Optional[tzwrap.PyTzInfo]]:
    # Does not work otherwise!
    # As said in pytz/tzinfo.py:
    # > This method should be used to construct localtimes, rather
    # > than passing a tzinfo argument to a datetime constructor.
    datetime = tz.localize(datetime)
    here = None
    return datetime, here


def get_error_msg(code: ErrCode) -> str:
    return {
        ErrCode.EXPR: "Incorrect expression",
        ErrCode.DATE: "Incorrect date",
        ErrCode.TZ: "Incorrect timezone",
    }.get(code, "Unknown error code! Contact the dev")


def generate_description(
    code: ExprCode, where: Optional[str], datetime: dt.datetime
) -> str:
    return {
        ExprCode.TZ_ONLY: f"Time in {where} now",
        ExprCode.TZ_DATEIN: f'Time in {where}, at {datetime.strftime("%H:%M")} here',
        ExprCode.TZ_DATEAT: f'Time here, in {where} at {datetime.strftime("%H:%M")}',
    }.get(code, "Unknown return code! Contact the dev")


def format_datetime(datetime: dt.datetime) -> str:
    return datetime.strftime("%Y-%m-%d %H:%M")


def process_input(text_input: Optional[str]) -> Tuple[str, str, str]:
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
