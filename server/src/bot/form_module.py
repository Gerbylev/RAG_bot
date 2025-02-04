import json
from wsgiref.validate import validator

from bot.template import t
from dao.state_dao import ChatStateDAO
from tol.Validator import Validator
from tol.interface import BaseInitBotModule, BaseAction, BaseReaction


class FormModule(BaseInitBotModule):

    def __init__(self):
        super().__init__()
        self.module_id = "/form"
        self.action = self.Action
        self.callback = "start_form"
        self.state('/form/process', 'process')
        self.state('/form/edit', 'edit')
        self.regex(t.leave_form, "leave_form")


    class Action(BaseAction):

        def __init__(self, req: BaseReaction):
            super().__init__(req)

        async def edit(self, query: str):
            form = await self.reaction.get_json_state()
            if query == t.save_form:
                # await self.reaction.answer(
                #     f"Форма успешно сохранена!")
                await self.reaction.go(f"{self.reaction.state_context.previous_state}/form", json.dumps(form))
                return
            validator = Validator(query)
            if not validator.check_number_range(0, len(form) - 1):
                await self.reaction.answer(validator.error_message)
                return
            await self.reaction.answer(
                f"Введите {form[int(query)]['label']}{'*' if form[int(query)]['is_optional'] else ''}",
                [[t.leave_form], [t.skip]] if form[int(query)]['is_optional'] else [[t.leave_form]])
            form[int(query)]['is_passed'] = False
            form[int(query)]['value'] = None
            await self.reaction.state('/form/process', json.dumps(form, ensure_ascii=False), False)

        async def process(self, query: str):
            form = await self.reaction.get_json_state()
            for index, field in enumerate(form):
                if not field['is_passed']:
                    validator = Validator(query)
                    if not validator.execute_validation(field['validator']):
                        await self.reaction.answer(f"{field['label']} {validator.error_message}")
                        return

                    field['value'] = None if field['is_optional'] and query == t.skip else query
                    field['is_passed'] = True
                    await self.reaction.change_json_info(json.dumps(form, ensure_ascii=False))
                    break

            if all([field['is_passed'] for field in form]):
                def print_form():
                    return '\n'.join([str(index) + ' ' + str(field['label']) + ': ' + str(
                        field['value'] if field['value'] else 'пропуск') for index, field in enumerate(form)])

                await self.reaction.answer(
                    f"""Форма успешно заполнена!
Убедитесь что всё заполнено правильно, если нужно, что то поменять введите номер поля.
{print_form()}
""", [[t.leave_form], [t.save_form]])
                await self.reaction.state('/form/edit', json.dumps(form, ensure_ascii=False), False)
                return
            for index, field in enumerate(form):
                if not field['is_passed']:
                    await self.reaction.answer(f"Введите {field['label']}{'*' if field['is_optional'] else ''}",
                                               [[t.leave_form], [t.skip]] if field['is_optional'] else [[t.leave_form]])
                    return

        async def start_form(self, query: str):
            form = await self.reaction.get_json_state()

            def print_form():
                return '\n'.join(
                    [str(index) + ' ' + str(field['label']) + str('*' if field['is_optional'] else '') for index, field
                     in enumerate(form)])

            await self.reaction.answer(
f"""Заполните данную форму
{print_form()}
""")
            await self.reaction.answer(f"Введите {form[0]['label']}{'*' if form[0]['is_optional'] else ''}",
                                       [[t.leave_form], [t.skip]] if form[0]['is_optional'] else [[t.leave_form]])
            await self.reaction.state('/form/process', json.dumps(form, ensure_ascii=False), False)


        async def leave_form(self, query):
            await self.reaction.go(self.reaction.state_context.previous_state)