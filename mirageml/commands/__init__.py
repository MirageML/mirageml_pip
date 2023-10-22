"""
This file is the entry point for the commands module.
It initializes the module and imports the necessary modules.
"""
from .login import login
from .config import set_config, show_config

from .chat import chat

from .list_plugins import list_plugins
from .list_sources import list_sources

from .add_plugin import add_plugin
from .add_source import add_source

from .delete_source import delete_source

from .sync_plugin import sync_plugin

__all__ = [
    "login",
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
