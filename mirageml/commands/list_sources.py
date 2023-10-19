from .utils.vectordb import list_qdrant_db, list_remote_qdrant_db

def list_sources():
    sources = list_qdrant_db()
    if len(sources) == 0:
        print("No local sources. Create a source with `mirageml add source`")
    else:
        print("Sources:")
        for source in sources:
            print(source)
    remote_sources = list_remote_qdrant_db()
    if len(remote_sources) == 0:
        print("No remote sources. Create a source with `mirageml add source`")
    else:
        print("Remote Sources:")
        for source in remote_sources:
            print(source)

