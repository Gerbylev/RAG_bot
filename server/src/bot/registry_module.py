import json

from telegram import Message

from bot.template import t
from tol.interface import BaseInitBotModule, BaseBotModule, BaseAction, BaseReaction


class RegistryModule(BaseInitBotModule):

    def __init__(self):
        super().__init__()
        self.module_id = "/registry"
        self.action  = self.Action
        self.callback = "registry"
        self.state("/registry/form", "save_login_form")
        self.regex(t.student, "student_login")
        self.regex(t.teacher, "teacher_login")

    class Action(BaseAction):

        def __init__(self, req: BaseReaction):
            super().__init__(req)

        async def teacher_login(self, query: Message):
            await self.reaction.answer("Введите свой токен или QR-code", [[t.return_back]])
            await self.reaction.go("/login/teacher")

        async def student_login(self, query: Message):
            login_form = [
                {"label": "Имя", "value": None, "is_optional": False, "is_passed": False, "validator": "check_length(2, 100)" },
                {"label": "Фамилия", "value": None, "is_optional": False, "is_passed": False, "validator": "check_length(2, 100)"},
                {"label": "Отчество", "value": None, "is_optional": True, "is_passed": False, "validator": "check_length(2, 100)"},
                {"label": "Номер группы", "value": None, "is_optional": False, "is_passed": False, "validator": "check_length(2, 10)"},
                {"label": "Номер кафедры", "value": None, "is_optional": False, "is_passed": False, "validator": "check_number_range(1, 100)"}
            ]

            await self.reaction.go("/form", json.dumps(login_form, ensure_ascii=False)) # Ввести json

        async def save_login_form(self, query: Message):
            form = json.loads(self.reaction.state_context.json_state)
            # TODO Логика сохранения
            await self.reaction.answer("Можете попробовать задать вопрос чат боту и моментально получить ответ.\nДля этого просто введите вопрос в этом меню.")
            await self.reaction.go('/main')

        async def registry(self, query: Message):
            message = """Вам необходимо пройти регистрацию, укажите кем вы являетесь"""
            await self.reaction.answer(message, [[t.student, t.teacher]])