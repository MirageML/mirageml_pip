import os
import re
import uuid
import requests
import tiktoken
from qdrant_client import QdrantClient
from qdrant_client.http.models import Batch, VectorParams, Distance

from ..config import load_config
from .brain import get_embedding

PACKAGE_DIR = os.path.dirname(__file__)


def get_qdrant_db():
    return QdrantClient(path=PACKAGE_DIR)

def exists_qdrant_db(collection_name="test"):
    qdrant_client = get_qdrant_db()
    return collection_name in [x.name for x in qdrant_client.get_collections().collections]

def list_qdrant_db():
    qdrant_client = get_qdrant_db()
    return [x.name for x in qdrant_client.get_collections().collections]

def delete_qdrant_db(collection_name="test"):
    qdrant_client = get_qdrant_db()
    qdrant_client.delete_collection(collection_name=collection_name)
    
def create_qdrant_db(data, metadata, collection_name="test"):
    config = load_config()
    qdrant_client = get_qdrant_db()

    final_data, final_metadata = [], []

    # For each data chunk it based on number of tokens
    enc = tiktoken.get_encoding("cl100k_base")
    for curr_data, curr_metadata in zip(data, metadata):
        split_data = re.split(r"(?<=\.)\s+", curr_data)
        i, chunks, meta = 0, [], []
        while i < len(split_data):
            curr_chunk = ""
            while i < len(split_data) and len(enc.encode(str(curr_chunk))) < 1000:
                curr_chunk += " " + split_data[i]
                i += 1
            chunks.append(curr_chunk)
            meta.append({"data": curr_chunk, "source": curr_metadata["source"]})
        final_data.extend(chunks)
        final_metadata.extend(meta)

    vectors = get_embedding(final_data, local=config["local_model"])

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
            ids=[uuid.uuid4().hex for _ in range(len(final_data))],
            payloads=final_metadata,
        )
    )

    print(f"Created Source: {collection_name}")

    return qdrant_client
