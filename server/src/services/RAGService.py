import json
import os
import tempfile
from dataclasses import dataclass
from sentence_transformers import SentenceTransformer
import psycopg2
from config.Config import CONFIG
from utils.logger import get_logger

log = get_logger("RAGService")

@dataclass
class RAGInfo:
    id: int
    text: str
    link: str
    rank: float

class RAGService:
    def __init__(self):
        self.model = SentenceTransformer("intfloat/multilingual-e5-large")
        self.top_k = 20
        DB_PARAMS = {
            "dbname": CONFIG.db.name,
            "user": CONFIG.db.user,
            "password": CONFIG.db.password,
            "host": CONFIG.db.host,
            "port": CONFIG.db.port
        }
        self.conn = psycopg2.connect(**DB_PARAMS)
        log.info("RAG init")

    def vector_search(self, query: str):
        """Искать похожие тексты"""
        query_embedding = self._get_embedding(query)
        query_embedding_str = ",".join(map(str, query_embedding))

        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, text, link, 1 - (embedding <=> %s::vector) AS similarity
                FROM texts
                ORDER BY similarity DESC
                LIMIT %s
                """,
                (query_embedding, self.top_k)
            )
            results = cur.fetchall()

        log.info(f"vector search result: {str(json.dumps(results, indent=2, ensure_ascii=False))}")
        return [RAGInfo(id=row[0], text=row[1], link=row[2], rank=row[3]) for row in results]

    def add_record(self, text: str, link: str):
        embedding = self._get_embedding(text)
        with self.conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO texts (text, link, embedding)
                VALUES (%s, %s, %s)
                RETURNING id;
                """,
                (text, link, embedding)
            )
            record_id = cur.fetchone()[0]
        self.conn.commit()

        log.info(f"Add to index text:\n{text}\nlink: {link}")

    def _get_embedding(self, text: str) -> list:
        """Получить векторное представление текста"""
        formatted_text = 'query: ' + text
        embedding = self.model.encode(formatted_text, normalize_embeddings=True)
        return embedding.tolist()

