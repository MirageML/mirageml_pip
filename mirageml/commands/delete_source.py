from .utils.vectordb import delete_qdrant_db

def delete_source(args):
    delete_qdrant_db(args.name)
    print(f"Deleted Source: {args.name}")