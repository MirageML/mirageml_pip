import os
from qdrant_client import QdrantClient
from langchain.vectorstores import Qdrant

from .brain import load_embedding_model

PACKAGE_DIR = os.path.dirname(__file__)


def get_qdrant_db(collection_name):
    print("Creating Qdrant DB...", PACKAGE_DIR)
    client = QdrantClient(location=PACKAGE_DIR)
    qdrant = Qdrant(client, collection_name=collection_name, embeddings=load_embedding_model())

    return qdrant

def create_qdrant_db(collection_name, docs, force_recreate=False):
    import pdb; pdb.set_trace()
    qdrant = Qdrant.from_documents(
        docs,
        load_embedding_model(),
        location=PACKAGE_DIR,
        collection_name=collection_name,
        force_recreate=force_recreate,
    )
    return qdrant