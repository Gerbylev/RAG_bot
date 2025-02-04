from bot.template import t
from tol.interface import BaseInitBotModule, BaseBotModule, BaseAction, BaseReaction


class LoginModule(BaseInitBotModule):
    # Мб не нужен пока что

    def __init__(self):
        super().__init__()
        self.module_id = "/login"
        self.action  = self.Action
        self.callback = "default"
        self.state("/login/student", "student_login")
        # self.state("/login/teacher", "teacher_login")
        self.regex(t.return_back, "return_back")

    class Action(BaseAction):

        def __init__(self, req: BaseReaction):
            super().__init__(req)

        async def student_login(self, query: str):
            await self.reaction.answer(
"""
Для прохождения регистрации вам придётся заполнить следующую форму
  - Имя
  - Фамилия
  - Отчество (опционально)
  - Номер группы
  - Номер вашей кафедры
""",
                [[t.return_back]])
            await self.reaction.state("/form")

        async def return_back(self, query: str):
            await self.reaction.go(self.reaction.state_context.previous_state)

        async def default(self, query: str):
            await self.reaction.answer("Произошла ошибка, мы уже проинформированы о ней и в скором времени обязательно поправим!")
            await self.reaction.go("/registry")