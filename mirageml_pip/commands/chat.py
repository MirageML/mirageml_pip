import requests 
ENDPOINT_URL = "https://mirageml--creative-assistant.modal.run/"

def chat():
    print("Starting chat. Type 'exit' to end the chat.")
    while True:
        user_input = input("Chat with Mirage: ")
        if user_input.lower() == 'exit':
            break

        json_data = {
            "user_input": user_input
        }

        response = requests.post(ENDPOINT_URL, json=json_data, stream=True)
        for chunk in response.iter_content(1024):
            if chunk:
                decoded_chunk = chunk.decode('utf-8')
                print(decoded_chunk, end='', flush=True)
        print("\n")
