from bot.template import t
from tol.interface import BaseInitBotModule, BaseAction, BaseReaction


class MyModule(BaseInitBotModule):


    def __init__(self):
        super().__init__()
        self.module_id = "/main"
        self.action  = self.Action
        self.callback = "default"
        # self.state("/login/student", "student_login")
        # # self.state("/login/teacher", "teacher_login")
        # self.regex(t.return_back, "return_back")


    class Action(BaseAction):
        def __init__(self, req: BaseReaction):
            super().__init__(req)

        async def default(self, query: str):
            await self.reaction.answer("Ну типо главная страница, тут можно вопрос боту задавать!", [[t.question_deanery, t.question_department]])
