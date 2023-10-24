import json
import os
import re
import uuid
from concurrent.futures import ThreadPoolExecutor
import keyring
import requests
import typer
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, PointStruct, VectorParams
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress

from ...constants import (
    SERVICE_ID,
    VECTORDB_CREATE_ENDPOINT,
    VECTORDB_DELETE_ENDPOINT,
    VECTORDB_LIST_ENDPOINT,
    VECTORDB_SEARCH_ENDPOINT,
    VECTORDB_UPSERT_ENDPOINT,
    get_headers,
)
from ..list_sources import set_sources
from .brain import local_get_embedding, _chunk_data
from .local_source import crawl_files
from .web_source import crawl_website

PACKAGE_DIR = os.path.dirname(__file__)

progress = Progress()


def get_local_qdrant_db():
    QDRANT_LOCKFILE_PATH = os.path.join(PACKAGE_DIR, ".lock")
    if os.path.exists(QDRANT_LOCKFILE_PATH):
        os.remove(QDRANT_LOCKFILE_PATH)
    return QdrantClient(path=PACKAGE_DIR)


def exists_qdrant_db(collection_name="test"):
    qdrant_client = get_local_qdrant_db()
    return collection_name in [x.name for x in qdrant_client.get_collections().collections]


def create_remote_qdrant_db(collection_name, link=None, path=None):
    user_id = keyring.get_password(SERVICE_ID, "user_id")

    if link:
        data, metadata = None, None
    if path:
        data, metadata = crawl_files(path)

    def make_request(args):
        i, curr_data, metadata_value, live = args
        json_data = {
            "user_id": user_id,
            "collection_name": collection_name,
            "data": [curr_data],
            "metadata": [metadata_value],
        }
        if i == 0:
            response = requests.post(VECTORDB_CREATE_ENDPOINT, json=json_data, headers=get_headers(), stream=True)
        else:
            response = requests.post(VECTORDB_UPSERT_ENDPOINT, json=json_data, headers=get_headers(), stream=True)

        if response.status_code == 200:
            for chunk in response.iter_lines():
                # process line here
                live.update(
                    Panel(
                        f"Indexing: {chunk.decode()}",
                        title="[bold green]Indexer[/bold green]",
                        border_style="green",
                    )
                )

    console = Console()
    with Live(
        Panel(
            "Creating Embeddings...",
            title="[bold green]Indexer[/bold green]",
            border_style="green",
        ),
        console=console,
        transient=True,
        auto_refresh=True,
        vertical_overflow="visible",
    ) as live:
        if data:
            with ThreadPoolExecutor(max_workers=10) as executor:
                args_list = [(i, curr_data, metadata[i], live) for i, curr_data in enumerate(data)]
                list(executor.map(make_request, args_list))
        else:
            json_data = {
                "user_id": user_id,
                "collection_name": collection_name,
                "url": link,
            }
            response = requests.post(VECTORDB_CREATE_ENDPOINT, json=json_data, headers=get_headers(), stream=True)
            if response.status_code == 200:
                for chunk in response.iter_lines():
                    # process line here
                    link = chunk.decode("utf-8")
                    live.update(
                        Panel(
                            f"{link}",
                            title="[bold green]Indexer[/bold green]",
                            border_style="green",
                        )
                    )

    typer.secho(f"Created Source: {collection_name}", fg=typer.colors.GREEN, bold=True)
    set_sources()
    return True


def create_local_qdrant_db(collection_name="test", link=None, path=None):
    data, metadata = [], []
    if link:
        data, metadata = crawl_website(link)
    elif path:
        data, metadata = crawl_files(path)

    qdrant_client = get_local_qdrant_db()

    final_data, final_metadata = [], []

    console = Console()
    with Live(
        Panel(
            "Indexing files...",
            title="[bold green]Indexer[/bold green]",
            border_style="green",
        ),
        console=console,
        transient=True,
        auto_refresh=True,
        vertical_overflow="visible",
    ) as live:
        # For each data chunk it based on number of tokens
        live.update(
            Panel(
                "Creating Embeddings...",
                title="[bold green]Indexer[/bold green]",
                border_style="green",
            )
        )

        final_data, final_metadata, vectors = [], [], []
        for dat, meta in zip(data, metadata):
            chunk_data, chunk_meta, chunk_vec = _chunk_data(dat, meta)
            final_data.extend(chunk_data)
            final_metadata.extend(chunk_meta)
            vectors.extend(chunk_vec)

        qdrant_client.recreate_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE),
        )

        for vector, f_metadata in zip(vectors, final_metadata):
            filepath = f_metadata["source"]

            live.update(
                Panel(
                    f"Indexing: {filepath}",
                    title="[bold green]Indexer[/bold green]",
                    border_style="green",
                )
            )

            qdrant_client.upsert(
                collection_name=collection_name,
                points=[PointStruct(vector=vector, payload=f_metadata, id=uuid.uuid4().hex)],
            )

    typer.secho(f"Created Source: {collection_name}", fg=typer.colors.GREEN, bold=True)

    set_sources()
    return qdrant_client


def list_remote_qdrant_db():
    json_data = {
        "user_id": keyring.get_password(SERVICE_ID, "user_id"),
    }
    response = requests.post(VECTORDB_LIST_ENDPOINT, json=json_data, headers=get_headers())
    response.raise_for_status()  # Raise an exception if the request failed
    return response.json()


def list_local_qdrant_db():
    QDRANT_JSON_PATH = os.path.join(PACKAGE_DIR, "meta.json")
    if os.path.exists(QDRANT_JSON_PATH):
        with open(QDRANT_JSON_PATH) as json_file:
            collection = json.load(json_file)
            collection_names = list(collection["collections"].keys())
    else:
        collection_names = []
    return collection_names


def remote_qdrant_search(source_name, user_input, data=None, metadata=None):
    json_data = {
        "user_id": keyring.get_password(SERVICE_ID, "user_id"),
        "collection_name": source_name,
        "search_query": user_input,
        "data": data,
        "metadata": metadata,
    }
    response = requests.post(VECTORDB_SEARCH_ENDPOINT, json=json_data, headers=get_headers())
    response.raise_for_status()  # Raise an exception if the request failed
    set_sources()
    return response.json()


def local_qdrant_search(source_name, user_input):
    qdrant_client = get_local_qdrant_db()

    query_vector = local_get_embedding([user_input])[0]

    hits = qdrant_client.search(
        limit=5,
        collection_name=source_name,
        query_vector=query_vector[0],
    )
    hits = [{"score": hit.score, "payload": hit.payload} for hit in hits]
    return hits


def transient_qdrant_search(user_input, data, metadata):
    qdrant_client = QdrantClient(location=":memory:")
    collection_name = str(uuid.uuid4().hex)

    search_vector = local_get_embedding([user_input])[0]

    qdrant_client.recreate_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(size=768, distance=Distance.COSINE)
    )

    final_data, final_metadata, vectors = [], [], []
    for dat, meta in zip(data, metadata):
        chunk_data, chunk_meta, chunk_vec = _chunk_data(dat, meta)
        final_data.extend(chunk_data)
        final_metadata.extend(chunk_meta)
        vectors.extend(chunk_vec)

    qdrant_client.upsert(
        collection_name=collection_name,
        points=[PointStruct(vector=vector, payload=f_metadata, id=uuid.uuid4().hex) for vector, f_metadata in zip(vectors, final_metadata)]
    )

    limit = 20

    hits = qdrant_client.search(
        collection_name=collection_name,
        query_vector=search_vector,
        limit=limit,
    )
    hits = [{"score": hit.score, "payload": hit.payload} for hit in hits]
    return hits


def delete_remote_qdrant_db(collection_name="test"):
    json_data = {
        "user_id": keyring.get_password(SERVICE_ID, "user_id"),
        "collection_name": collection_name,
    }
    response = requests.post(VECTORDB_DELETE_ENDPOINT, json=json_data, headers=get_headers())
    response.raise_for_status()  # Raise an exception if the request failed
    set_sources()
    return response.json()


def delete_local_qdrant_db(collection_name="test"):
    qdrant_client = get_local_qdrant_db()
    qdrant_client.delete_collection(collection_name=collection_name)
    set_sources()
