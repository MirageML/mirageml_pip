from .utils.vectordb import delete_qdrant_db

def delete_source(name: str):
    delete_qdrant_db(name)
    print(f"Deleted Source: {name}")