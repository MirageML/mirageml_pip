from .utils.vectordb import delete_qdrant_db

def delete_source(name: str, remote=False):
    delete_qdrant_db(name, remote=remote)
    print(f"Deleted Source: {name}")