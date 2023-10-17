import os
from .utils.vectordb import exists_qdrant_db, create_qdrant_db
from .utils.web_source import crawl_website
from .utils.local_source import crawl_files


def add_web_source(args):
    print(f"Indexing {args.link}...")
    if exists_qdrant_db(collection_name=args.name):
        print(f"Collection already exists, please delete with `mirageml delete source {args.name}` first.")
        return
    
    data, metadata = crawl_website(args.link)
    create_qdrant_db(data, metadata, collection_name=args.name)

def add_local_source():
    print("Indexing Local Files...")
    # Crawl the files under the current directory
    data, metadata = crawl_files()
    breakpoint()
    # collection_name should be absolute path
    collection_name = os.path.abspath('.').replace('/', '_')
    create_qdrant_db(data, metadata, collection_name=collection_name)
    return collection_name
    
def add_source(args):
    print(args)
    add_web_source(args)
