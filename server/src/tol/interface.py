import importlib
import pkgutil
import re
from abc import ABC, abstractmethod
from typing import Type, Any, Callable, List

from telegram import Update
from telegram.ext import CallbackContext


class BaseBot(ABC):
    """
    Abstract base class for a bot. It manages all registered bot modules.

    Attributes:
        all_modules (dict): A dictionary containing all bot modules registered in the system.
    """

    def __init__(self):
        self.all_modules = BaseInitBotModule._registry

    @abstractmethod
    def start(self):
        """Start the bot. This method should be implemented in subclasses."""
        pass


class BaseReaction(ABC):
    """
    Abstract base class for managing bot reactions to user interactions.

    Methods:
        answer(answer: str, button: list): Sends a response with optional buttons.
        state(state: str): Updates the bot's internal state.
        go(): Switches to a specific state or class.
    """

    @abstractmethod
    def answer(self, answer: str, button: List[Any] = None):
        pass

    @abstractmethod
    def state(self, state: str, json_info: str):
        pass

    @abstractmethod
    def go(self):
        """Switches to a specific state or class."""
        pass


class BaseAction(ABC):
    """
    Base class for actions performed by the bot in response to user input.

    Attributes:
        reaction (BaseReaction): The reaction object associated with this action.
    """

    def __init__(self, reaction: BaseReaction):
        self.reaction = reaction


class BaseBotModule(ABC):
    """
    Represents a module for the bot, handling specific actions and default behavior.

    Attributes:
        module_id (str): Unique identifier for the module.
        actions (List[Callable]): List of actions to be executed for specific queries.
        default_function (Callable): Fallback function for unhandled queries.

    Methods:
        callback(req: BaseReaction, query: str): Processes the query by executing appropriate actions.
    """

    def __init__(self, module_id: str, default_function: Callable, actions: List[Callable[[BaseAction, str], bool]] = None):
        self.module_id = module_id
        self.actions = actions or []
        self.default_function = default_function

    async def callback(self, req: BaseReaction, query: str):
        """
        Processes the query by checking all actions. If none match, calls the default function.
        """
        for action in self.actions:
            if await action(req, query):
                return
        await self.default_function(req, query)


class BaseInitBotModule(ABC):
    """
    Base class for initializing bot modules. Automatically registers subclasses and their modules.

    Attributes:
        _registry (dict): Global registry of all bot modules.
        module_id (str): ID of the main module.
        action (Type[BaseAction]): The action class associated with the module.
        callback (str): Default callback function for the module.
        main_module (BaseBotModule): The main module object.
        actions (List[Callable]): List of additional actions for the main module.
        bot_modules (List[BaseBotModule]): List of additional bot modules.

    Methods:
        get_modules() -> List[BaseBotModule]: Returns all additional bot modules.
        create_main_module(): Creates the main bot module.
        state(state: str, action_method: str): Registers a new state with an associated action method.
        regex(pattern: str, action_method: str): Registers a regex-based action.
    """

    _registry = {}

    def __init_subclass__(cls, **kwargs):
        """Automatically registers subclasses and their modules."""
        super().__init_subclass__(**kwargs)
        bot_class_module = cls()
        bot_class_module.create_main_module()
        BaseInitBotModule._registry[bot_class_module.main_module.module_id] = bot_class_module.main_module
        bot_modules = bot_class_module.get_modules()
        for module in bot_modules:
            BaseInitBotModule._registry[module.module_id] = module

    def __init__(self):
        self.module_id = None
        self.action = None
        self.callback = None
        self.main_module = None
        self.actions = []
        self.bot_modules = []

    def get_modules(self) -> List[BaseBotModule]:
        """Returns the list of additional bot modules."""
        return self.bot_modules

    def create_main_module(self):
        """Creates the main module for the bot."""
        if self.module_id is None:
            raise RuntimeError("module_id is not initialized.")
        if self.action is None:
            raise RuntimeError("action class is not initialized.")
        if self.callback is None:
            raise RuntimeError("callback is not initialized.")
        self._check_if_method_exist(self.callback)
        async def wrapper(react: BaseReaction, query: str):
            await getattr(self.action(react), self.callback)(query)
        self.main_module = BaseBotModule(self.module_id, wrapper, self.actions)

    def state(self, state: str, action_method: str):
        """
        Registers a new state with an associated action method.
        """
        self._check_if_method_exist(action_method)

        async def wrapper(react: BaseReaction, query: str):
            await getattr(self.action(react), action_method)(query)

        self.bot_modules.append(BaseBotModule(state, wrapper))

    def regex(self, pattern: str, action_method: str):
        """
        Registers a regex-based action with an associated action method.
        """
        self._check_if_method_exist(action_method)

        async def wrapper(react: BaseReaction, query: str):
            if re.match(pattern, query):
                await getattr(self.action(react), action_method)(query)
                return True
            return False

        self.actions.append(wrapper)

    def _check_if_method_exist(self, action_method: str):
        """
        Checks if a given method exists and is callable.
        """
        if not hasattr(self.action, action_method):
            raise AttributeError(f"Method '{action_method}' not found in class '{self.action.__name__}'.")
        if not callable(getattr(self.action, action_method)):
            raise TypeError(f"'{action_method}' in class '{self.action.__name__}' is not callable.")
