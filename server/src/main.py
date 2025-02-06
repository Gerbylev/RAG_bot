from services.GPTService import GPTService
from services.QueryService import QueryService
from services.RAGService import RAGService
from services.registry import REGISTRY
from tol.TelegramBot import TelegramBot
from utils.logger import get_logger

log = get_logger("main")


def main() -> None:
    """Start the bot."""
    TelegramBot().start()


if __name__ == "__main__":
    REGISTRY.put(GPTService())
    REGISTRY.put(RAGService())
    REGISTRY.put(QueryService())
    main()