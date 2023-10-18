import os
from .config import load_config
from .utils.brain import get_embedding, llm_call
from .utils.vectordb import get_qdrant_db
from .add_source import add_local_source


def rag_chat(sources: list = None):
    config = load_config()
    if not sources:
        print("By default Mirage will index the files under the current directory.")
        print("If you want to run RAG over other sources, please specify them with `--sources`.")
        user_input = input("If you'd like to proceed type 'y': ")
        if user_input.lower() == 'y':
            sources = ["local"]
        else: return
    
    if "local" in sources:
        sources.remove("local")
        sources.append(add_local_source())
    
    qdrant_client = get_qdrant_db()

    template = """Answer the question based only on the following context, if the context isn't relevant answer without it. If the context is relevant, mention which sources you used.:
    {context}

    Sources:
    {sources}

    Question: {question}
    """

    print("Starting chat. Type 'exit' to end the chat.")
    user_input = input(f"Chat with Mirage ({', '.join(sources)}): ")

    hits = []
    print("Searching through sources...")
    for source_name in sources:
        try:
            hits.extend(qdrant_client.search(
                collection_name=source_name,
                query_vector=get_embedding([user_input], local=config["local_mode"])[0],
                limit=5
            ))
        except:
            if config["local_mode"]:
                print(f"Source: {source_name} was created with OpenAI's embedding model. Please run with `local_mode=False` or reindex with `mirageml delete source {source_name}; mirageml add source {source_name}`.")
                return
            else:
                print(f"Source: {source_name} was created with a local embedding model. Please run with `local_mode=True` or reindex with `mirageml delete source {source_name}; mirageml add source {source_name}`.")
                return

    sorted_hits = sorted(hits, key=lambda x: x.score, reverse=True)[:10]

    sources = "\n".join([str(x.payload["source"]) for x in sorted_hits])
    context = "\n\n".join([str(x.payload["source"]) + ": " + x.payload["data"] for x in sorted_hits])

    chat_history = [
        {"role": "system", "content": "You are a helpful assistant that responds to questions concisely with the given context in the following format:\n{answer}\n\nSources:\n{sources}"},
        {"role": "user", "content": template.format(context=context, question=user_input, sources=sources)}
    ]
        
    print("Found relevant sources! Answering question...\n")
    response = llm_call(chat_history, model=config["model"], stream=True, local=config["local_mode"])

    ai_response = ""
    for chunk in response.iter_content(1024):
        if chunk:
            decoded_chunk = chunk.decode('utf-8')
            print(decoded_chunk, end='', flush=True)
            ai_response += decoded_chunk
    print("\n\n")

    chat_history.append({"role": "system", "content": ai_response})

    while True:
        try:
            user_input = input("Ask a follow-up: ")
            if user_input.lower() == 'exit':
                break
        except KeyboardInterrupt:
            print("\nChat ended by user.")
            break
        chat_history.append({"role": "user", "content": user_input})
        response = llm_call(chat_history, model=config["model"], stream=True, local=config["local_mode"])

        ai_response = ""
        for chunk in response.iter_content(1024):
            if chunk:
                decoded_chunk = chunk.decode('utf-8')
                print(decoded_chunk, end='', flush=True)
                ai_response += decoded_chunk
        print("\n\n")

        chat_history.append({"role": "system", "content": ai_response})
