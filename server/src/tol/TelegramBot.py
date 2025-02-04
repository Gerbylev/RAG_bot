import importlib
import pkgutil
from dataclasses import dataclass

from services.context_var import request_id_var
from tol.interface import BaseBot, BaseInitBotModule, BaseBotModule, BaseAction, BaseReaction

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, CallbackContext, MessageHandler, filters, Application, \
    CallbackQueryHandler
from config.Config import CONFIG
from tol.reaction import TelegramReaction
from utils.logger import get_logger




log = get_logger("TelegramBot")

request_id = 0

class TelegramBot(BaseBot):

    async def command_start(self, update: Update, context: CallbackContext):
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id

    async def handle_message(self, update: Update, context: CallbackContext):
        global request_id

        request_id += 1
        request_id_var.set(request_id)
        # chat_id = update.effective_chat.id
        # user_id = update.effective_user.id
        # user_message = update.message.text
        log.info(f"Запрос от пользователя: {update.message.text}\nИз чата: {update.effective_chat.id}")
        request_context, state_context = await TelegramReaction.create(update, context)
        tg_reaction = TelegramReaction(request_context, state_context)
        await self.all_modules[tg_reaction.state_context.state].callback(tg_reaction, update.message.text)
        # await query_service.process(user_message, update, context)

    async def handle_callback(self, update: Update, context: CallbackContext):
        global request_id

        request_id += 1
        request_id_var.set(request_id)

        query = update.callback_query
        await query.answer()

    def start(self):
        self.initialize_modules('./bot', 'bot')
        application = Application.builder().token(CONFIG.bot_token).build()

        # Handlers
        application.add_handler(CommandHandler("start", self.handle_message))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        application.add_handler(CallbackQueryHandler(self.handle_callback))

        log.info("Telegram bot started")
        TelegramReaction.all_modules = self.all_modules
        application.run_polling(allowed_updates=Update.ALL_TYPES)


    @staticmethod
    def initialize_modules(folder_path: str, package_name: str):
        for _, module_name, _ in pkgutil.iter_modules([folder_path]):
            full_module_name = f"{package_name}.{module_name}"
            importlib.import_module(full_module_name)




# if __name__ == "__main__":
#     bot = MyBot()
#     bot.start()