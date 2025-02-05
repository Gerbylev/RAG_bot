import cv2
import numpy as np
from telegram import Message

from bot.template import t
from tol.interface import BaseInitBotModule, BaseAction, BaseReaction
from pyzxing import BarCodeReader


# TODO: Убрать CV2 поставил временно так как, не имею возможность сейчас починить систему (не ставятся либы через apt install)

class LoginModule(BaseInitBotModule):

    def __init__(self):
        super().__init__()
        self.module_id = "/login"
        self.action  = self.Action
        self.callback = "default"
        self.state("/login/teacher", "teacher_login")
        self.regex(t.return_back, "return_back")

    class Action(BaseAction):

        def __init__(self, req: BaseReaction):
            super().__init__(req)

        async def teacher_login(self, query: Message):
            if not query.text and not query.photo:
                await self.reaction.answer("Не правильный формат сообщения")
                return
            token = await self.get_qr(query)
            # TODO Проверка в db
            print(token)

        async def get_qr(self, query: Message):
            if query.text:
                return query.text.strip()
            file = await query.photo[-1].get_file()
            img_bytes = await file.download_as_bytearray()

            img_array = np.frombuffer(img_bytes, dtype=np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            reader = BarCodeReader()
            decoded_objects = reader.decode_array(img)

            if decoded_objects and "parsed" in decoded_objects[0]:
                return decoded_objects[0]["parsed"].decode("utf-8")
            else:
                await self.reaction.answer("QR-code не распознан")
                return

        async def return_back(self, query: Message):
            await self.reaction.go(self.reaction.state_context.previous_state)

        async def default(self, query: Message):
            await self.reaction.answer("Произошла ошибка, мы уже проинформированы о ней и в скором времени обязательно поправим!")
            await self.reaction.go("/registry")