import os
from .utils.brain import get_embedding, llm_call
from .utils.vectordb import get_qdrant_db
from .add_source import add_local_source


def rag_chat(sources: list = None, model: str = "gpt-3.5-turbo"):
    if not sources:
        print("Please specify at least 1 source! Use `mirageml list sources` to see available sources.")
        return
    
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

    # chat_history = [
    #     {"role": "system", "content": "You are a helpful assistant."},
    # ]
    print("Starting chat. Type 'exit' to end the chat.")
    user_input = input(f"Chat with Mirage ({', '.join(sources)}): ")

    hits = []
    print("Searching through sources...")
    for source_name in sources:
        hits.extend(qdrant_client.search(
            collection_name=source_name,
            query_vector=get_embedding([user_input])[0],
            limit=5
        ))

    sorted_hits = sorted(hits, key=lambda x: x.score, reverse=True)[:10]

    breakpoint()

    sources = "\n".join([str(x.payload["source"]) for x in sorted_hits])
    context = "\n\n".join([str(x.payload["source"]) + ": " + x.payload["data"] for x in sorted_hits])

    chat_history = [
        {"role": "system", "content": "You are a helpful assistant that responds to questions concisely with the given context in the following format:\n{answer}\n\nSources:\n{sources}"},
        {"role": "user", "content": template.format(context=context, question=user_input, sources=sources)}
    ]
        
    print("Found relevant sources! Answering question...\n")
    response = llm_call(chat_history, model=model, stream=True)

    ai_response = ""
    for chunk in response.iter_content(1024):
        if chunk:
            decoded_chunk = chunk.decode('utf-8')
            print(decoded_chunk, end='', flush=True)
            ai_response += decoded_chunk
    print("\n\n")

    # if sources:
    #     print("Relevant Sources:\n" + sources + "\n\n")

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
        response = llm_call(chat_history, model=model, stream=True)

        ai_response = ""
        for chunk in response.iter_content(1024):
            if chunk:
                decoded_chunk = chunk.decode('utf-8')
                print(decoded_chunk, end='', flush=True)
                ai_response += decoded_chunk
        print("\n\n")

        chat_history.append({"role": "system", "content": ai_response})
