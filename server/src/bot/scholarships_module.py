from telegram import Message

from tol.interface import BaseInitBotModule, BaseAction

# TODO
class ScholarshipsModule(BaseInitBotModule):

    def __init__(self):
        super().__init__()
        self.module_id = "/scholarships"
        self.action = self.Action
        self.callback = "scholarships"

    class Action(BaseAction):

        async def scholarships(self, query: Message):
            pass
