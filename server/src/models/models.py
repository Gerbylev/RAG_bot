from pgvector.sqlalchemy import VECTOR
from sqlalchemy import Column, Integer, BigInteger, Text

from config.database import Base


class Texts(Base):
    __tablename__ = 'texts'

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text, nullable=False)
    embedding = Column(VECTOR(1024))
    link = Column(Text)


class ChatState(Base):
    __tablename__ = 'chats_state'

    id = Column(BigInteger, primary_key=True)
    state = Column(Text, nullable=False)
    json_state_info = Column(Text)
    previous_state = Column(Text, nullable=False)