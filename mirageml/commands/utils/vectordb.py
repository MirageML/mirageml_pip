import os
import re
import time
import uuid
import requests
import tiktoken
import threading
from tqdm import tqdm
from qdrant_client import QdrantClient
from qdrant_client.http.models import Batch, VectorParams, Distance

import keyring
from ...constants import SERVICE_ID, VECTORDB_SEARCH_ENDPOINT, VECTORDB_LIST_ENDPOINT, VECTORDB_CREATE_ENDPOINT, VECTORDB_DELETE_ENDPOINT

from ..config import load_config
from .brain import get_embedding

import typer
from rich.progress import Progress

PACKAGE_DIR = os.path.dirname(__file__)

progress = Progress()

def fake_progress_bar(progress, task_id, length):
    for second in range(length):
        if progress.finished:
            return
        time.sleep(5)
        progress.update(task_id, advance=1)

def get_qdrant_db():
    return QdrantClient(path=PACKAGE_DIR)

def exists_qdrant_db(collection_name="test"):
    qdrant_client = get_qdrant_db()
    return collection_name in [x.name for x in qdrant_client.get_collections().collections]

def create_remote_qdrant_db(data, metadata, collection_name="test"):
    json_data = {
        "user_id": keyring.get_password(SERVICE_ID, 'user_id'),
        "data": data,
        "metadata": metadata,
        "collection_name": collection_name
    }

    with Progress(transient=True) as progress:
        task_id = progress.add_task(f"[cyan]Creating Source ({collection_name}) on Remote...", total=len(data))

        # Start the fake progress bar in a separate thread
        thread = threading.Thread(target=fake_progress_bar, args=(progress, task_id, len(data)))
        thread.start()

        response = requests.post(VECTORDB_CREATE_ENDPOINT, json=json_data)

        # If the request is completed but the progress bar is still running,
        # immediately complete the progress bar
        progress.update(task_id, completed=True)

        # Wait for the fake progress bar thread to finish (if it hasn't already)
        thread.join()

    response.raise_for_status()  # Raise an exception if the request failed
    # print(response.json())
    typer.secho(f"Created Source: {collection_name}", fg=typer.colors.GREEN, bold=True)
    return response.json()

def create_qdrant_db(data, metadata, collection_name="test", remote=False):
    if remote: return create_remote_qdrant_db(data, metadata, collection_name=collection_name)
    config = load_config()
    qdrant_client = get_qdrant_db()

    final_data, final_metadata = [], []

    with Progress(transient=True) as progress:
        task_id = progress.add_task("[cyan]Creating Source Locally...", total=len(data))

        # Start the fake progress bar in a separate thread
        thread = threading.Thread(target=fake_progress_bar, args=(progress, task_id, len(data)))
        thread.start()

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

        vectors = get_embedding(final_data, local=config["local_mode"])

        # qdrant_client.add(
        #     collection_name="demo_collection",
        #     documents=data,
        #     metadata=metadata,
        #     ids=[uuid.uuid4().hex for _ in range(len(data))]
        # )

        size = 384 if config["local_mode"] else 1536
        qdrant_client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=size, distance=Distance.COSINE),
        )

        qdrant_client.upsert(
            collection_name=collection_name,
            points=Batch(
                vectors=vectors,
                ids=[uuid.uuid4().hex for _ in range(len(final_data))],
                payloads=final_metadata,
            )
        )

        # If the request is completed but the progress bar is still running,
        # immediately complete the progress bar
        progress.update(task_id, completed=True)

        # Wait for the fake progress bar thread to finish (if it hasn't already)
        thread.join()

    typer.secho(f"Created Source: {collection_name}", fg=typer.colors.GREEN, bold=True)

    return qdrant_client


def list_remote_qdrant_db():
    json_data = {
        "user_id": keyring.get_password(SERVICE_ID, 'user_id'),
    }
    response = requests.post(VECTORDB_LIST_ENDPOINT, json=json_data)
    response.raise_for_status()  # Raise an exception if the request failed
    return response.json()

def list_qdrant_db():
    qdrant_client = get_qdrant_db()
    return [x.name for x in qdrant_client.get_collections().collections]


def remote_qdrant_search(source_name, user_input):
    json_data = {
        "user_id": keyring.get_password(SERVICE_ID, 'user_id'),
        "collection_name": source_name,
        "search_query": user_input
    }
    response = requests.post(VECTORDB_SEARCH_ENDPOINT, json=json_data)
    response.raise_for_status()  # Raise an exception if the request failed
    return response.json()

def qdrant_search(source_name, user_input):
    config = load_config()
    qdrant_client = get_qdrant_db()

    hits = qdrant_client.search(
                limit=5,
                collection_name=source_name,
                query_vector=get_embedding([user_input], local=config["local_mode"])[0],
            )
    hits = [{
        "score": hit.score,
        "payload": hit.payload
    } for hit in hits]
    return hits


def delete_remote_qdrant_db(collection_name="test"):
    json_data = {
        "user_id": keyring.get_password(SERVICE_ID, 'user_id'),
        "collection_name": collection_name,
    }
    response = requests.post(VECTORDB_DELETE_ENDPOINT, json=json_data)
    response.raise_for_status()  # Raise an exception if the request failed
    return response.json()

def delete_qdrant_db(collection_name="test", remote=False):
    if remote: return delete_remote_qdrant_db(collection_name=collection_name)
    qdrant_client = get_qdrant_db()
    qdrant_client.delete_collection(collection_name=collection_name)