from .utils.vectordb import list_qdrant_db

def list_sources():
    sources = list_qdrant_db()
    if len(sources) == 0:
        print("No sources. Create a source with `mirageml add source`")
        return
    print("Sources:")
    for source in sources:
        print(source)