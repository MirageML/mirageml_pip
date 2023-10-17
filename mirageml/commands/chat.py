import requests 
from .utils.brain import llm_call

def chat(model="gpt-3.5-turbo"):
    chat_history = [{"role": "system", "content": "You are a helpful assistant."}]
    print("Starting chat. Type 'exit' to end the chat.")
    while True:
        user_input = input("Chat with Mirage: ")
        if user_input.lower() == 'exit':
            break

        chat_history.append({"role": "user", "content": user_input})
        response = llm_call(chat_history, model=model, stream=True)

        ai_response = ""
        for chunk in response.iter_content(1024):
            if chunk:
                decoded_chunk = chunk.decode('utf-8')
                print(decoded_chunk, end='', flush=True)
                ai_response += decoded_chunk
        print("\n")

        chat_history.append({"role": "system", "content": ai_response})
