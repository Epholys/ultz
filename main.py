from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem


from ultz.ultz import process_input


class KeywordQueryEventListener(EventListener):
    def return_error(self, msg):
        item = ExtensionResultItem(name=msg)
        return RenderResultListAction([item])

    def on_event(self, event, extension):
        expr = event.get_argument()
        if not expr:
            return DoNothingAction()

        result, description, icon = process_input(
            expr, extension.preferences["date-format"]
        )

        item = ExtensionResultItem(icon=icon, name=result, description=description)

        return RenderResultListAction([item])


class TzExtension(Extension):
    def __init__(self):
        super(TzExtension, self).__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())


if __name__ == "__main__":
    TzExtension().run()
