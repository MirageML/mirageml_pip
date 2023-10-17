import os
from .utils.brain import load_embedding_model, load_llm, get_embedding, llm_call
from .utils.vectordb import get_qdrant_db, create_qdrant_db
from .add_source import add_local_source


def rag_chat(collections: list = None):
    if not collections:
        print("Please specify at least 1 source! Use `mirageml list sources` to see available sources.")
        return
    
    if "local" in collections:
        collections.remove("local")
        collections.append(add_local_source())
    
    # collection_name = "test"
    # data = ["harrison worked at kensho"]
    # metadata = [{"data": "harrison worked at kensho", "source": 1}]

    # qdrant_client = create_qdrant_db(data, metadata, collection_name=collection_name)
    qdrant_client = get_qdrant_db()

    template = """Answer the question based only on the following context, if the context isn't relevant answer without it. If the context is relevant, mention which sources you used.:
    {context}

    Chat History:
    {chat_history}

    Sources:
    {sources}

    Question: {question}
    """

    chat_history = [
        {"role": "system", "content": "You are a helpful assistant."},
    ]
    print("Starting chat. Type 'exit' to end the chat.")
    while True:
        user_input = input("Chat with Mirage: ")
        if user_input.lower() == 'exit':
            break

        hits = []
        print("Searching through sources...")
        for collection_name in collections:
            hits.extend(qdrant_client.search(
                collection_name=collection_name,
                query_vector=get_embedding([user_input])[0],
                limit=10
            ))

        sorted_hits = sorted(hits, key=lambda x: x.score, reverse=True)[:10]

        sources = "\n".join([str(x.payload["source"]) for x in sorted_hits])
        context = "\n\n".join([str(x.payload["source"]) + ": " + x.payload["data"] for x in sorted_hits])

        messages = [
            {"role": "system", "content": "You are a helpful assistant that responds to questions concisely with the given context in the following format:\n{answer}\n\nSources:\n{sources}"},
            {"role": "user", "content": template.format(chat_history=chat_history, context=context, question=user_input, sources=sources)}
        ]
        
        print("Found relevant sources! Answering question...\n")
        response = llm_call(messages, stream=True)

        ai_response = ""
        for chunk in response.iter_content(1024):
            if chunk:
                decoded_chunk = chunk.decode('utf-8')
                print(decoded_chunk, end='', flush=True)
                ai_response += decoded_chunk
        print("\n\n")

        # if sources:
        #     print("Relevant Sources:\n" + sources + "\n\n")

        chat_history.append({"role": "user", "content": user_input})
        chat_history.append({"role": "system", "content": ai_response})

