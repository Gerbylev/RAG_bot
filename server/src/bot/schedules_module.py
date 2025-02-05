from telegram import Message

from tol.interface import BaseInitBotModule, BaseAction

# TODO
class SchedulesModule(BaseInitBotModule):

    def __init__(self):
        super().__init__()
        self.module_id = "/schedules"
        self.action = self.Action
        self.callback = "schedules"

    class Action(BaseAction):

        async def schedules(self, query: Message):
            pass


