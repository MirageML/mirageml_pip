"""
This file is the entry point for the commands module.
It initializes the module and imports the necessary modules.
"""
from .add_plugin import add_plugin
from .add_source import add_source
from .chat import chat
from .config import set_config, show_config
from .delete_source import delete_source
from .list_plugins import list_plugins
from .list_sources import list_sources
from .login import login
from .signup import signup
from .sync_plugin import sync_plugin

__all__ = [
    "login",
    "signup",
    "set_config",
    "show_config",
    "chat",
    "list_plugins",
    "list_sources",
    "add_plugin",
    "add_source",
    "delete_source",
    "sync_plugin",
]
