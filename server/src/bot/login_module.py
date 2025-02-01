from tol.interface import BaseInitBotModule, BaseBotModule, BaseAction, BaseReaction


class MyModule(BaseInitBotModule):


    def __init__(self):
        super().__init__()
        self.module_id = "/login"
        self.action  = self.Action
        self.callback = "dd"
        self.state("/login_repeat", "ff")
        # self.state("/outlog", "cc")
        # self.regex(r"\bПривет\b", lambda x: print(f"Привет пользователь {x}!"))
        self.regex(r"\bПривет\b", "dd")

    class Action(BaseAction):

        def __init__(self, req: BaseReaction):
            super().__init__(req)

        def default(self, query: str):
            print("default")

        async def ff(self, query: str):
            await self.reaction.answer("Зарегайся дэбик")

        async def dd(self, query: str):
            await self.reaction.answer("Привет как твои дела?")
            await self.reaction.go("/login_repeat")
            return