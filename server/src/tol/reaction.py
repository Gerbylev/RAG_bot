from dataclasses import dataclass
from typing import List, Any, Optional

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import CallbackContext

from tol.interface import BaseReaction
from dao.state_dao import ChatDao
from models.models import ChatState


@dataclass
class RequestContext:
    update: Update
    context: CallbackContext

@dataclass
class StateContext:
    state: str
    json_state: Optional[str]

class TelegramReaction(BaseReaction):

    all_modules = {}

    def __init__(self, request_context: RequestContext, state_context: StateContext):
        self.request_context = request_context
        self.state_context = state_context

    @classmethod
    async def create(cls, update: Update, context: CallbackContext):
        request_context = RequestContext(update, context)
        state_context = await cls.__get_state(request_context)
        return request_context, state_context

    async def answer(self, answer: str, buttons: List[str] = None):
        reply_markup = None
        if buttons:
            reply_markup = ReplyKeyboardMarkup([[btn] for btn in buttons], resize_keyboard=True)

        await self.request_context.context.bot.send_message(
            chat_id=self.request_context.update.effective_chat.id,
            text=answer,
            reply_markup=reply_markup
        )

    async def state(self, state: str, json_info: Optional[str] = None):
        """Сохраняет новое состояние в базе данных."""
        chat_id = self.request_context.update.effective_chat.id
        existing_state = await ChatDao.find_one_or_none_by_id(chat_id)

        if existing_state:
            await ChatDao.update({"id": chat_id}, state=state, json_state_info=json_info)
        else:
            await ChatDao.add(id=chat_id, state=state, json_state_info=json_info)

    async def go(self, state: str, json_info: Optional[str] = None):
        # chat_id = self.request_context.update.effective_chat.id
        # existing_state = await ChatDao.find_one_or_none_by_id(chat_id)
        #
        # if existing_state:
        #     await ChatDao.update({"id": chat_id}, state=state, json_state_info=json_info)
        # else:
        #     await ChatDao.add(id=chat_id, state=state, json_state_info=json_info)

        await TelegramReaction.all_modules[state].callback(self, self.request_context.update.message.text)

    @staticmethod
    async def __get_state(request_context: RequestContext):
        chat_id = request_context.update.effective_chat.id
        existing_state: ChatState = await ChatDao.find_one_or_none_by_id(chat_id)

        if existing_state is not None:
            return StateContext(existing_state.state, existing_state.json_state_info)
        else:
            await ChatDao.add(id=chat_id, state="/registry", json_state_info=None)
            return StateContext("/registry", None)
           