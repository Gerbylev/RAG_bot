import json
from dataclasses import dataclass
from itertools import zip_longest
from typing import List, Any, Optional

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import CallbackContext

from tol.interface import BaseReaction, RequestContext, StateContext
from dao.state_dao import ChatStateDAO
from models.models import ChatState




class TelegramReaction(BaseReaction):

    all_modules = {}

    def __init__(self, request_context: RequestContext, state_context: StateContext):
        super().__init__()
        self.request_context: RequestContext = request_context
        self.state_context: StateContext = state_context

    @classmethod
    async def create(cls, update: Update, context: CallbackContext):
        request_context = RequestContext(update, context)
        state_context = await cls.__get_state(request_context)
        return request_context, state_context

    async def answer(self, answer: str, buttons: List[List[str]] = None):
        reply_markup = None
        if buttons:
            reply_markup = ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text=btn) for btn in row] for row in buttons],
                resize_keyboard=True
            )

        await self.request_context.context.bot.send_message(
            chat_id=self.request_context.update.effective_chat.id,
            text=answer,
            reply_markup=reply_markup
        )

    async def change_json_info(self, json_info: Optional[str] = None):
        chat_id = self.request_context.update.effective_chat.id
        existing_state = await ChatStateDAO.find_one_or_none_by_id(chat_id)

        await ChatStateDAO.update({"id": chat_id}, state=existing_state.state, json_state_info=json_info,
                                  previous_state=existing_state.previous_state)


    async def state(self, state: str, json_info: Optional[str] = None, change_previous_state=True):
        """Сохраняет новое состояние в базе данных."""
        chat_id = self.request_context.update.effective_chat.id
        existing_state = await ChatStateDAO.find_one_or_none_by_id(chat_id)

        if existing_state:
            if change_previous_state:
                await ChatStateDAO.update({"id": chat_id}, state=state, json_state_info=json_info, previous_state=existing_state.state)
            else:
                await ChatStateDAO.update({"id": chat_id}, state=state, json_state_info=json_info,
                                          previous_state=existing_state.previous_state)
        else:
            await ChatStateDAO.add(id=chat_id, state=state, json_state_info=json_info, previous_state=state)

    async def go(self, state: str, json_info: Optional[str] = None, change_previous_state=True):
        chat_id = self.request_context.update.effective_chat.id
        existing_state = await ChatStateDAO.find_one_or_none_by_id(chat_id)

        if change_previous_state:
            await ChatStateDAO.update({"id": chat_id}, state=state, json_state_info=json_info,
                                 previous_state=existing_state.state)
        else:
            await ChatStateDAO.update({"id": chat_id}, state=state, json_state_info=json_info,
                                 previous_state=existing_state.previous_state)

        self.state_context.json_state=json_info
        self.state_context.state=state
        self.state_context.previous_state=existing_state.previous_state
        await TelegramReaction.all_modules[state].callback(self, self.request_context.update.message, True)

    @staticmethod
    async def __get_state(request_context: RequestContext):
        chat_id = request_context.update.effective_chat.id
        existing_state: ChatState = await ChatStateDAO.find_one_or_none_by_id(chat_id)

        if existing_state is not None:
            return StateContext(existing_state.state, existing_state.json_state_info, existing_state.previous_state)
        else:
            await ChatStateDAO.add(id=chat_id, state="/registry", json_state_info=None, previous_state="/registry")
            return StateContext("/registry", None, None)
           