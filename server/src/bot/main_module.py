from telegram import Message

from bot.template import t
from tol.interface import BaseInitBotModule, BaseAction, BaseReaction


class MainModule(BaseInitBotModule):

    def __init__(self):
        super().__init__()
        self.module_id = "/main"
        self.action = self.Action
        self.callback = "default"
        # self.state("/login/student", "student_login")
        # # self.state("/login/teacher", "teacher_login")
        # self.regex(t.return_back, "return_back")

    class Action(BaseAction):
        def __init__(self, req: BaseReaction):
            super().__init__(req)

        async def default(self, query: Message):
            await self.reaction.answer("Можете попробовать задать вопрос чат боту и моментально получить ответ.\nДля этого просто введите вопрос в этом меню.",
                                       [[t.question_deanery, t.question_department],
                                        [t.championships, t.scholarships],
                                        [t.schedules, t.diplomas],
                                        [t.science ,t.account]])
