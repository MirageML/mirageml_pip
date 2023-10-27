"""
This file is the entry point for the commands module.
It initializes the module and imports the necessary modules.
"""
from .add_model import add_model
from .add_plugin import add_plugin
from .add_source import add_source
from .add_system_prompt import add_system_prompt
from .chat import chat
from .config import set_config, show_config
from .delete_source import delete_source
from .delete_system_prompt import delete_system_prompt
from .list_models import list_models
from .list_plugins import list_plugins
from .list_sources import list_sources
from .list_system_prompts import list_system_prompts
from .login import login
from .profile import profile
from .sync_plugin import sync_plugin

__all__ = [
    "login",
    "profile",
    "set_config",
    "show_config",
    "chat",
    "list_system_prompts",
    "list_plugins",
    "list_models",
    "list_sources",
    "add_plugin",
    "add_model",
    "add_system_prompt",
    "add_source",
    "delete_source",
    "delete_system_prompt",
    "sync_plugin",
]
