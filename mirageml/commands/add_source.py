import os
from .utils.vectordb import create_qdrant_db
from .utils.web_source import crawl_website
from .utils.local_source import crawl_files
from .config import load_config


def add_web_source(name, link, remote=False):
    config = load_config()
    remote = False if config["local_mode"] else True
    print(f"Indexing {link}...")
    # if exists_qdrant_db(collection_name=name):
    #     print(f"Collection already exists, please delete with `mirageml delete source {name}` first.")
    #     return

    data, metadata = crawl_website(link)
    create_qdrant_db(data, metadata, collection_name=name, remote=remote)


def add_local_source(path=None, name=None):
    config = load_config()
    if path == "local":
        path = "."
    remote = False if config["local_mode"] else True
    print("Indexing Local Files...")
    # Crawl the files under the current directory
    data, metadata = crawl_files(path)
    # collection_name should be absolute path
    collection_name = os.path.abspath(".").replace("/", "_") if name is None else name
    collection_name = collection_name.replace(" ", "_")
    create_qdrant_db(data, metadata, collection_name=collection_name, remote=remote)
    return collection_name


def add_source(name, link):
    name = name.replace(" ", "_")
    if link:
        add_web_source(name, link)
    else:
        add_local_source()
