from dataclasses import dataclass
from typing import List, Any

from telegram import Update
from telegram.ext import CallbackContext

from tol.interface import BaseReaction


@dataclass
class RequestContext:
    # chat_client_id: str
    state: str
    update: Update
    context: CallbackContext

class TelegramReaction(BaseReaction):

    def __init__(self, update: Update, context: CallbackContext):
        self.request_context = RequestContext("/reg", update, context)


    async def answer(self, answer: str, button: List[Any] = None):
        await self.request_context.context.bot.send_message(chat_id=self.request_context.update.effective_chat.id,
                                       text=answer, reply_markup=button)

    def state(self, state: str, json_info: str):
        """Сохраняет новое состояние в базе данных."""
        chat_id = self.request_context.update.effective_chat.id
        with self.conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO chat_state (id, state, json_sate_info)
                VALUES (%s, %s, %s)
                ON CONFLICT (id) DO UPDATE
                SET state = EXCLUDED.state;
                """,
                (chat_id, state, None)  # None можно заменить на нужные данные
            )
            self.conn.commit()
        self.request_context.state = state

    def go(self):
        pass