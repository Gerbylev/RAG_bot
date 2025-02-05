from telegram import Message

from tol.interface import BaseInitBotModule, BaseAction


# TODO
class DiplomasModule(BaseInitBotModule):

    def __init__(self):
        super().__init__()
        self.module_id = "/diplomas"
        self.action = self.Action
        self.callback = "diplomas"

    class Action(BaseAction):

        async def diplomas(self, query: Message):
            pass