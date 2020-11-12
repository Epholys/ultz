from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction

from datetime import datetime
from pytz import timezone

import logging
logger = logging.getLogger(__name__)

class DemoExtension(Extension):

    def __init__(self):
        super(DemoExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


class KeywordQueryEventListener(EventListener):

    def on_event(self, event, extension):
        logger.info(datetime.now().astimezone(timezone('UTC')))
        items = []
        items.append(ExtensionResultItem(icon='images/icon.png',
                                     name=datetime.now().astimezone(timezone('UTC')).strftime("%Y-%m-%d %H:%M"),
                                     description='Time in UTC'))
        return RenderResultListAction(items)

if __name__ == '__main__':
    DemoExtension().run()
