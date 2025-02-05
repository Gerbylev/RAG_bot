from telegram import Message

from tol.interface import BaseInitBotModule, BaseAction

#TODO
class ChampionshipsModule(BaseInitBotModule):

    def __init__(self):
        super().__init__()
        self.module_id = "/championships"
        self.action = self.Action
        self.callback = "championships"

    class Action(BaseAction):

        async def championships(self, query: Message):
            pass