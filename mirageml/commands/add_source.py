import os
from .utils.vectordb import exists_qdrant_db, create_qdrant_db
from .utils.web_source import crawl_website
from .utils.local_source import crawl_files


def add_web_source(name, link, remote=False):
    print(f"Indexing {link}...")
    # if exists_qdrant_db(collection_name=name):
    #     print(f"Collection already exists, please delete with `mirageml delete source {name}` first.")
    #     return

    data, metadata = crawl_website(link)
    create_qdrant_db(data, metadata, collection_name=name, remote=remote)

def add_local_source(name=None, path=None):
    print("Indexing Local Files...")
    # Crawl the files under the current directory
    data, metadata = crawl_files()
    # collection_name should be absolute path
    collection_name = os.path.abspath('.').replace('/', '_') if name is None else name
    collection_name = collection_name.replace(' ', '_')
    create_qdrant_db(data, metadata, collection_name=collection_name)
    return collection_name

def add_source(name, link, remote=False):
    if link:
        add_web_source(name, link, remote)
    else:
        add_local_source()
