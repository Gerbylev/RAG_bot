from telegram import Message

from bot.template import t
from tol.interface import BaseInitBotModule, BaseAction, BaseReaction


class MainModule(BaseInitBotModule):

    def __init__(self):
        super().__init__()
        self.module_id = "/main"
        self.action = self.Action
        self.callback = "default"
        self.state("/main/question_department", "__question_department")
        self.state("/main/question_deanery", "__question_deanery")
        self.regex(t.question_deanery, "question_deanery")
        self.regex(t.question_department, "question_department")
        self.regex(t.return_back, "back")

        self.regex('','bot_request') # Должен быть последним
        # TODO поправить regex, что бы True всегда было

    class Action(BaseAction):
        def __init__(self, req: BaseReaction):
            super().__init__(req)

        async def question_department(self, query: Message):
            await self.reaction.answer("Задайте свой вопрос кафедре, спустя время на него ответят!", [[t.return_back]])
            await self.reaction.go("/main/question_department")

        async def __question_department(self, query: Message):
            # TODO отправить вопрос пользователя
            pass

        async def question_deanery(self, query: Message):
            await self.reaction.answer("Задайте свой вопрос деканату, спустя время на него ответят!", [[t.return_back]])
            await self.reaction.go("/main/question_department")

        async def __question_deanery(self, query: Message):
            # TODO отправить вопрос пользователя
            pass

        async def bot_request(self, query: Message):
            # TODO отправлять запрос в RAG систему
            pass


        async def default(self, query: Message):
            await self.reaction.answer("",
                                       [[t.question_deanery, t.question_department],
                                        [t.championships, t.scholarships],
                                        [t.schedules, t.diplomas],
                                        [t.science ,t.account]])

        async def back(self, query: Message):
            await self.reaction.go(self.reaction.state_context.previous_state)
