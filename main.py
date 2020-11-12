from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction

from datetime import datetime
from pytz import timezone, all_timezones

import logging
logger = logging.getLogger(__name__)

class DemoExtension(Extension):

    def __init__(self):
        super(DemoExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        # logger.info(datetime.now().astimezone(timezone('UTC')))

        where = event.get_argument()
        items = []
        if where in all_timezones:
            time_there=datetime.now().astimezone(timezone(where)).strftime("%Y-%m-%d %H:%M")
            items.append(ExtensionResultItem(icon='images/icon.png',
                                             name=time_there,
                                             description='Time in {0}'.format(where)))
        else:
            items.append(ExtensionResultItem(icon='images/icon.png',
                                             name='Incorrect timezone entered'))
                         
        return RenderResultListAction(items)

if __name__ == '__main__':
    DemoExtension().run()
