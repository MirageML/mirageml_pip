import os
import uuid
import requests
from qdrant_client import QdrantClient
from qdrant_client.http.models import Batch, VectorParams, Distance

from .brain import load_embedding_model, get_embedding

PACKAGE_DIR = os.path.dirname(__file__)


def get_qdrant_db():
    return QdrantClient(path=PACKAGE_DIR)

def create_qdrant_db(data, metadata, collection_name="test"):
    qdrant_client = get_qdrant_db()
    vectors = get_embedding(data)

    if collection_name in [x.name for x in qdrant_client.get_collections().collections]:
        return qdrant_client

    # qdrant_client.add(
    #     collection_name="demo_collection",
    #     documents=data,
    #     metadata=metadata,
    #     ids=[uuid.uuid4().hex for _ in range(len(data))]
    # )

    qdrant_client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
    )
    


    qdrant_client.upsert(
        collection_name=collection_name,
        points=Batch(
            vectors=vectors,
            ids=[uuid.uuid4().hex for _ in range(len(data))],
            payloads=metadata,
        )
    )

    return qdrant_client
