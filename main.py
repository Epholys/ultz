from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction

from enum import Enum
from datetime import datetime, date, time
from pytz import timezone, all_timezones

import logging
logger = logging.getLogger(__name__)


ok = True
err = False

def parse_date(strdate):    
    if strdate == 'now':
        return (datetime.now(), ok)

    # First try a simple time:
    try:
        HHMM = time.fromisoformat(strdate)
        mmdd = datetime.combine(date.today(), HHMM)
        return (mmdd, ok)
    except ValueError:
        pass

    # Okay, then a date:
    try:
        mmdd = datetime.fromisoformat(strdate)
        return (mmdd, ok)
    except ValueError:
        return (None, err)

    
class ExprCode(Enum):
    ERR = -1
    TZ_ONLY = 0
    TZ_DATE = 1
    
# Of course, formal grammar is ridiculous invention which only goal is
# to avoid the creation of such beautifully clean code like the one below
# I expertedly crafted.
def parse_expression(expr):
    split = expr.split(' in ')
    length = len(split)

    timezone = split[-1].strip()
    if length == 1:
        return ExprCode.TZ_ONLY, timezone, None

    date = parse_date(split[-2].strip())
    if length == 2:
        return ExprCode.TZ_DATE, timezone, date

    return ExprCode.ERR, None, None

    
class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        expr = event.get_argument()               
        if not expr:
            return DoNothingAction()
        
        code, where, when = parse_expression(expr)
        logger.debug("parse returned: where={}, when={}, code={}".format(where, when, code))        
        
        if code == ExprCode.ERR:
            item = ExtensionResultItem(name='Incorrect expression')
            return RenderResultListAction([item])

        date = datetime.now()        
        if code == ExprCode.TZ_DATE:
            if when[1] == err:
                item = ExtensionResultItem(name='Incorrect date')
                return RenderResultListAction([item])                        
            date, _ = when
                

        if where in all_timezones:
            time_there = date.astimezone(timezone(where)).strftime("%Y-%m-%d %H:%M")
            item = ExtensionResultItem(icon='images/icon.png',
                                       name=time_there,
                                       description='Time in {0}'.format(where))
        else:
            item = ExtensionResultItem(name='Incorrect timezone')

        return RenderResultListAction([item])



class TzExtension(Extension):

    def __init__(self):
        super(TzExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


    
if __name__ == '__main__':
    TzExtension().run()
