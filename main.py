import logging
import datetime as dt
from enum import Enum

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

import pytz_wrapper as pytz

_logger = logging.getLogger(__name__)


def parse_date(date_str):
    # Try to find a date in "mm-dd" format first
    # (This is not supported by datetime, as it wants "yyyy-" first)
    month_day = date_str.split("-")
    if len(month_day) == 2:
        try:
            year = dt.date.today().year
            month = (int)(month_day[0])
            day = (int)(month_day[1])
            date = dt.date(year, month, day)
            return date
        except ValueError:
            pass

    # Okay, then try the complete date
    try:
        date = dt.date.fromisoformat(date_str)
        return date
    except ValueError:
        pass

    return None


def parse_time(time_str):
    # Try to parse a simple time in HH:MM:SS format:
    # (HH alone, and HH:MM alone are also supported)
    try:
        time = dt.time.fromisoformat(time_str)
        return time
    except ValueError:
        pass

    return None


def parse_datetime(datetime_str):
    # Note: suppose the day, month, or year will not change the next second
    datetime_split = list(map(str.strip, datetime_str.split(" ")))
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


class ExprCode(Enum):
    ERR = -1
    TZ_ONLY = 0
    TZ_DATEIN = 1
    TZ_DATEAT = 2


def parse_expression(expr):
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


class KeywordQueryEventListener(EventListener):
    def return_error(self, msg):
        item = ExtensionResultItem(name=msg)
        return RenderResultListAction([item])

    def on_event(self, event, extension):
        expr = event.get_argument()
        if not expr:
            return DoNothingAction()

        code, where, when = parse_expression(expr)
        _logger.debug(f"parse returned: where={where}, when={when}, code={code}")

        if code == ExprCode.ERR:
            return self.return_error("Incorrect expression")

        date = dt.datetime.now()
        if code == ExprCode.TZ_DATEIN or code == ExprCode.TZ_DATEAT:
            if not when:
                return self.return_error("Incorrect date")
            date = when

        tz = None
        try:
            tz = pytz.timezone(where)
        except pytz.UnknownTimeZoneError:
            return self.return_error("Incorrect timezone")

        if code == ExprCode.TZ_DATEAT:
            # Reverse everything
            # Does not work otherwise!
            # As said in pytz/tzinfo.py:
            # > This method should be used to construct localtimes, rather
            # > than passing a tzinfo argument to a datetime constructor.
            date = tz.localize(date)
            tz = None  # = here

        raw_result = date.astimezone(tz)
        displayed_result = raw_result.strftime("%Y-%m-%d %H:%M")

        description = {
            ExprCode.TZ_ONLY: f"Time in {where} now",
            ExprCode.TZ_DATEIN: f'Time in {where}, at {date.strftime("%H:%M")} here',
            ExprCode.TZ_DATEAT: f'Time here, in {where} at {date.strftime("%H:%M")}',
        }.get(code, "Unknown return code! Contact the dev")

        item = ExtensionResultItem(
            icon="images/icon.png", name=displayed_result, description=description
        )

        return RenderResultListAction([item])


class TzExtension(Extension):
    def __init__(self):
        super(TzExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


if __name__ == "__main__":
    TzExtension().run()
