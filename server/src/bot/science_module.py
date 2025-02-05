from telegram import Message

from tol.interface import BaseInitBotModule, BaseAction

# TODO
class ScienceModule(BaseInitBotModule):

    def __init__(self):
        super().__init__()
        self.module_id = "/science"
        self.action = self.Action
        self.callback = "science"

    class Action(BaseAction):

        async def science(self, query: Message):
            pass