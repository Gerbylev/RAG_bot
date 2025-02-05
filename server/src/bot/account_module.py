import json

from telegram import Message

from bot.template import t
from tol.interface import BaseInitBotModule, BaseAction

# TODO доделать
class AccountModule(BaseInitBotModule):

    def __init__(self):
        super().__init__()
        self.module_id = "/account"
        self.action = self.Action
        self.callback = "account"
        self.state('/account/form', 'edit')
        self.regex(t.return_back, "back")
        self.regex(t.edit_account, 'edit')
        self.regex(t.logout, 'logout')

    class Action(BaseAction):

        async def account(self, query: Message):
            # TODO get account info
            await self.reaction.answer("Oleg Gerbylev группа 4318 кафедра 44\nОтредактировать информацию", [[t.edit_account],[t.return_back, t.leave_form]])


        async def edit(self, query: Message):
            login_form = [
                {"label": "Имя", "value": "Oleg", "is_optional": False, "is_passed": True,
                 "validator": "check_length(2, 100)"},
                {"label": "Фамилия", "value": "Gerbylev", "is_optional": False, "is_passed": True,
                 "validator": "check_length(2, 100)"},
                {"label": "Отчество", "value": None, "is_optional": True, "is_passed": True,
                 "validator": "check_length(2, 100)"},
                {"label": "Номер группы", "value": "4318", "is_optional": False, "is_passed": True,
                 "validator": "check_length(2, 10)"},
                {"label": "Номер кафедры", "value": 44, "is_optional": False, "is_passed": True,
                 "validator": "check_number_range(1, 100)"}
            ]
            await self.reaction.go('/form', json.dumps(login_form))

        async def logout(self, query: Message):
            # TODO delete info by account
            pass

        async def edit_account(self, query: Message):
            form = self.reaction.state_context.json_state
            # TODO обновить форму
            await self.reaction.go(self.reaction.state_context.previous_state, change_previous_state=False)




        async def back(self, query: Message):
            await self.reaction.go(self.reaction.state_context.previous_state)

