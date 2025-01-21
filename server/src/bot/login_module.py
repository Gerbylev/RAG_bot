from tol.interface import BaseInitBotModule, BaseBotModule, BaseAction, BaseReaction


class MyModule(BaseInitBotModule):


    def __init__(self) -> BaseBotModule:
        super().__init__()
        self.module_id = "/auth"
        self.action  = self.Action
        self.callback = "ff"
        self.state("/login", "dd")
        # self.state("/outlog", "cc")
        # self.regex(r"\bПривет\b", lambda x: print(f"Привет пользователь {x}!"))
        self.regex(r"\bПривет\b", "dd")

    class Action(BaseAction):

        def __init__(self, req: BaseReaction):
            super().__init__(req)

        def default(self, query: str):
            print("default")

        def ff(self, query: str):
            print("ff")

        async def dd(self, query: str):
            await self.reaction.answer("Привет как твои дела?")
            return