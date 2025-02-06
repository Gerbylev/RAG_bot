import ast
from markdownify import markdownify
import requests
from bs4 import BeautifulSoup
from jinja2 import Template
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from services.GPTService import GPTService
from services.RAGService import RAGService, RAGInfo
from services.registry import REGISTRY
import yaml
import re
from duckduckgo_api_haystack import DuckduckgoApiWebSearch

from utils.logger import get_logger

prompt_file_path = 'prompts.yml'
with open(prompt_file_path, 'r', encoding='utf-8') as file:
    data = yaml.safe_load(file)

agent_prompt = Template(data['agent_prompt'])

log = get_logger("QueryService")


class QueryService:

    def __init__(self):
        self.gpt_service: GPTService = REGISTRY.get(GPTService)
        self.rag_service: RAGService = REGISTRY.get(RAGService)
        self.websearch = DuckduckgoApiWebSearch(top_k=5)

    def extract_action(self, output):
        match = re.search(r"Действие:\s*(\w+)\((.*?)\)", output)
        if match:
            action_name = match.group(1)
            action_input = match.group(2).strip()
            log.info(f"call tool: {action_name}, arguments: {action_input}")
            return action_name, action_input
        log.info(f"not found tool calling")
        return None, None

    def web_search(self, query: str):
        try:
            query = query if "гуап" in query.lower() else "ГУАП " + query
            results = self.websearch.run(query=query)

            documents = results["documents"]
            links = results["links"]

            res =[]
            for doc, link in zip(documents, links):
                res.append(RAGInfo(id =100, text=str(doc.content), link=str(link), rank=1))

            return res
        except Exception as e:
            log.error(f"Query: {query}, web_search dosent work", exc_info=e)
            return RAGInfo(id =100, text=f"Ошибка: {e}", link='', rank=1)

    async def action(self, history, info: list[RAGInfo], max_iterations=5):
        text = ""
        response = await self.gpt_service.fetch_completion_history(history)
        for _ in range(max_iterations):
            history.append({'role': 'assistant', 'content': response})
            trace = ""
            action_name, action_input = self.extract_action(response)
            if not action_name:
                trace += "Error: No action detected\n"
                history.append({'role': 'system', 'content': trace})
            elif action_name == "web_search":
                observation = self.web_search(action_input[1:-1])
                inf = '\n'.join([f"{len(info)+index}. {rag.text}" for index, rag in enumerate(observation)])
                info.extend(observation)
                trace += f"Observation: {inf}"
                history.append({'role': 'system', 'content': trace})
            elif action_name == "final_answer":
                answer = action_input[1:-1]
                history.append({'role': 'system', 'content': f"Какая информация помогла ответить на вопрос?"})
                text = answer
                # return answer
            elif action_name == "helpful_infos":
                answer = action_input
                # history.append({'role': 'system', 'content': f"Какая информация помогла ответить на вопрос?"})
                ids = ast.literal_eval(answer)
                res = [info[id - 1] for id in ids if id in range(len(info)+1)]
                unique_links = set()
                unique_res = []

                for obj in res:
                    if obj.link not in unique_links:
                        unique_links.add(obj.link)
                        unique_res.append(obj)
                return text, unique_res
            elif action_name == "insult_in_request":
                answer = "Ваш запрос содержит оскорбления. Пожалуйста, избегайте такого языка."
                history.append({'role': 'system', 'content': f"Final Answer: {answer}"})
                return answer, []
            elif action_name == "off_topic_question":
                answer = "Ваш запрос не относится к теме этого бота."
                history.append({'role': 'system', 'content': f"Final Answer: {answer}"})
                return answer, []
            else:
                trace += f"Error: Unknown action: {action_name}\n"
                history.append({'role': 'system', 'content': trace})
            log.info(f"Agent trace: {trace}")
            response = await self.gpt_service.fetch_completion_history(history)

        return "Ответ не удалось получить за указанное число итераций.", []

    async def process(self, message: str, update: Update, context: CallbackContext):
        info = self.rag_service.vector_search(message)
        log.info(f"Find info: {info}")
        current_prompt = agent_prompt.render(user_question=message, data=info)
        log.info(f"Agent prompt: {current_prompt}")
        response = await self.action([{'role': 'user', 'content': current_prompt}], info)
        log.info(f"Agent response text:\n{response[0]}\nhelpful info: {response[1]}")
        buttons = []
        for index, rag_info in enumerate(response[1][:5]):
            print(index, rag_info)
            if "@" not in rag_info.link:
                buttons.append(InlineKeyboardButton(text=f"Ссылка {index + 1}", url=rag_info.link))

        keyboard = []
        for i in range(0, len(buttons), 2):
            keyboard.append(buttons[i:i + 2])

        await context.bot.send_message(chat_id=update.effective_chat.id,
                                       text=response[0], reply_markup=InlineKeyboardMarkup(keyboard))

