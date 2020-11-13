import logging
from datetime import datetime as dtdatetime, date as dtdate, time as dttime
from enum import Enum

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

from pytz_wrapper import timezone, UnknownTimeZoneError

logger = logging.getLogger(__name__)

ok = True
err = False


def parse_date(string):
    if string == "now":
        return (dtdatetime.now(), ok)

    # First try a simple time in HH:MM:SS format:
    try:
        time = dttime.fromisoformat(string)
        date = dtdatetime.combine(dtdate.today(), time)
        return (date, ok)
    except ValueError:
        pass

    # Okay, then complete date
    try:
        date = dtdatetime.fromisoformat(string)
        return (date, ok)
    except ValueError:
        return (None, err)


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
        date = parse_date(split_in[0])
        return ExprCode.TZ_DATEIN, location, date

    if len_in == 1 and len_at == 2:
        # [location] at [time]
        location = split_at[0]
        date = parse_date(split_at[1])
        return ExprCode.TZ_DATEAT, location, date

    return ExprCode.ERR, None, None


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        expr = event.get_argument()
        if not expr:
            return DoNothingAction()

        code, where, when = parse_expression(expr)
        logger.debug(
            "parse returned: where={}, when={}, code={}".format(where, when, code)
        )

        if code == ExprCode.ERR:
            item = ExtensionResultItem(name="Incorrect expression")
            return RenderResultListAction([item])

        date = dtdatetime.now()
        if code == ExprCode.TZ_DATEIN or code == ExprCode.TZ_DATEAT:
            if when[1] == err:
                item = ExtensionResultItem(name="Incorrect date")
                return RenderResultListAction([item])
            date, _ = when

        tz = None
        try:
            logger.debug("Trying tz")
            tz = timezone(where)
        except UnknownTimeZoneError:
            item = ExtensionResultItem(name="Incorrect timezone")
            return RenderResultListAction([item])

        if code == ExprCode.TZ_DATEAT:
            # Reverse everything
            date = dtdatetime.combine(date.date(), date.time(), tz)
            tz = None  # = here

        raw_result = date.astimezone(tz)
        result = raw_result.strftime("%Y-%m-%d %H:%M")

        description = ""
        if code == ExprCode.TZ_ONLY:
            description = "Time in {} now".format(where)
        elif code == ExprCode.TZ_DATEIN:
            description = "Time in {1}, at {0} here".format(
                date.strftime("%H:%M"), where
            )
        else:  # code == ExprCode.TZ_DATEAT:
            description = "Time here, in {1} at {0}".format(
                date.strftime("%H:%M"), where
            )

        item = ExtensionResultItem(
            icon="images/icon.png", name=result, description=description
        )

        return RenderResultListAction([item])


class TzExtension(Extension):
    def __init__(self):
        super(TzExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


if __name__ == "__main__":
    TzExtension().run()
