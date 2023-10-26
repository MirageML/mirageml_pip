import os

from .config import load_config
from .utils.vectordb import create_local_qdrant_db, create_remote_qdrant_db


def fix_name(name):
    if name.startswith("http"):
        name = "_".join(name.split("/")[1:])

    name = name.replace(" ", "_")
    name = name.replace("/", "_")
    if name.startswith("_") or name.startswith("/"):
        name = name[1:]
    return name


def add_web_source(link, name=None, remote=False):
    config = load_config()
    remote = False if config["local_mode"] else True

    if not name:
        name = fix_name(link)
    else:
        name = fix_name(name)

    if remote:
        create_remote_qdrant_db(collection_name=name, link=link)
    else:
        print(f"Indexing {link}...")
        create_local_qdrant_db(collection_name=name, link=link)
    return name


def add_local_source(path=None, name=None):
    if path == "local":
        path = "."
    print("Indexing Local Files...")

    # collection_name should be absolute path
    collection_name = os.path.abspath(path) if name is None else name
    collection_name = fix_name(collection_name)

    create_local_qdrant_db(collection_name=collection_name, path=path)
    return collection_name


def add_source(name, link):
    name = fix_name(name)

    if link:
        add_web_source(link, name)
    else:
        add_local_source()
