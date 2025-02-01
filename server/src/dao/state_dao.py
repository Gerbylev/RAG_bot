from dao.base import BaseDAO
from models.models import ChatState


class ChatDao(BaseDAO):
    model = ChatState