"""
This file is the entry point for the commands module. 
It initializes the module and imports the necessary modules.
"""

from .login import login
from .chat import chat
from .rag import rag_chat

from .list_plugins import list_plugins
from .list_sources import list_sources

from .add_plugin import add_plugin
from .add_source import add_source

from .sync_plugin import sync_plugin