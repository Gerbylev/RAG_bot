from telegram import Message

from bot.template import t
from services.QueryService import QueryService
from services.RAGService import RAGService
from services.registry import REGISTRY
from tol.interface import BaseInitBotModule, BaseAction, BaseReaction


class MainModule(BaseInitBotModule):

    def __init__(self):
        super().__init__()
        self.module_id = "/main"
        self.action = self.Action
        self.callback = "default"
        self.state("/main/question_department", "question_department_impl")
        self.state("/main/question_deanery", "question_deanery_impl")
        self.regex(t.championships, "championships")
        self.regex(t.scholarships, "scholarships")
        self.regex(t.schedules, "schedules")
        self.regex(t.diplomas, "diplomas")
        self.regex(t.science, "science")
        self.regex(t.account, "account")
        self.regex(t.question_deanery, "question_deanery")
        self.regex(t.question_department, "question_department")
        self.regex(t.return_back, "back")

        self.regex('','bot_request') # Должен быть последним

    class Action(BaseAction):
        def __init__(self, req: BaseReaction):
            super().__init__(req)
            self.query_service: QueryService = REGISTRY.get(QueryService)

        async def account(self, query: Message):
            await self.reaction.go('/account')

        async def question_department(self, query: Message):
            await self.reaction.answer("Задайте свой вопрос кафедре, спустя время на него ответят!", [[t.return_back]])
            await self.reaction.state("/main/question_department")

        async def championships(self, query: Message):
            await self.reaction.answer("Будет добавлено позже")

        async def scholarships(self, query: Message):
            await self.reaction.answer("Будет добавлено позже")

        async def schedules(self, query: Message):
            await self.reaction.answer("Будет добавлено позже")

        async def diplomas(self, query: Message):
            await self.reaction.answer("Будет добавлено позже")

        async def science(self, query: Message):
            await self.reaction.answer("Будет добавлено позже")

        async def question_department_impl(self, query: Message):
            # TODO отправить вопрос пользователя
            pass

        async def question_deanery(self, query: Message):
            await self.reaction.answer("Задайте свой вопрос деканату, спустя время на него ответят!", [[t.return_back]])
            await self.reaction.state("/main/question_department")

        async def question_deanery_impl(self, query: Message):
            # TODO отправить вопрос пользователя
            pass

        async def bot_request(self, query: Message):
            # TODO отправлять запрос в RAG систему
            if not query.text:
                await self.reaction.answer("Пока я понимаю только текст!")
                return
            await self.query_service.process(query.text, self.reaction.request_context.update, self.reaction.request_context.context)


        async def default(self, query: Message):
            await self.reaction.answer("Главная страница, тут вы можете задать вопрос боту или выбрать нужный раздел!",
                                       [[t.question_deanery, t.question_department],
                                        [t.championships, t.scholarships],
                                        [t.schedules, t.diplomas],
                                        [t.science ,t.account]])

        async def back(self, query: Message):
            await self.reaction.go(self.reaction.state_context.previous_state)
