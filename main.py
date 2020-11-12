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
    TZ_DATEIN = 1
    TZ_DATEAT = 2

    
# Of course, formal grammar is ridiculous invention which only goal is
# to avoid the creation of such beautifully clean code like the one below
# I expertedly crafted.
def parse_expression(expr):
    splitin = expr.split(' in ')
    lenin = len(splitin)

    splitat = expr.split(' at ')
    lenat = len(splitat)

    if lenin == 1 and lenat == 1:
        # [location]
        return ExprCode.TZ_ONLY, splitin[0].strip(), None

    if lenin == 2 and lenat == 1:
        # [time] in [location]
        return ExprCode.TZ_DATEIN, splitin[1].strip(), parse_date(splitin[0].strip())

    if lenin == 1 and lenat == 2:
        # [location] a [time]
        return ExprCode.TZ_DATEAT, splitat[0].strip(), parse_date(splitat[1].strip())

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
        if code == ExprCode.TZ_DATEIN or code == ExprCode.TZ_DATEAT:
            if when[1] == err:
                item = ExtensionResultItem(name='Incorrect date')
                return RenderResultListAction([item])                        
            date, _ = when


        if where not in all_timezones:
            item = ExtensionResultItem(name='Incorrect timezone')            
            return RenderResultListAction([item])

        tz = timezone(where)
        if code == ExprCode.TZ_DATEAT:
            # Reverse everything            
            date = datetime.combine(date.date(), date.time(), tz)
            tz=None # = here
        
        result = date.astimezone(tz).strftime("%Y-%m-%d %H:%M")
        item = ExtensionResultItem(icon='images/icon.png',
                                   name=result,
                                   description='Time in {0}'.format(where))
        return RenderResultListAction([item])


class TzExtension(Extension):

    def __init__(self):
        super(TzExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


    
if __name__ == '__main__':
    TzExtension().run()
