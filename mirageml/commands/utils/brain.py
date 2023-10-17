import os
import requests
from sentence_transformers import SentenceTransformer

PACKAGE_DIR = os.path.dirname(__file__)
os.environ['TRANSFORMERS_CACHE'] = os.path.join(PACKAGE_DIR, 'models')

def local_get_embedding(text_list, embedding_model_id="BAAI/bge-small-en-v1.5"):
    model_dir = os.path.join(PACKAGE_DIR, 'models', embedding_model_id)
    if not os.path.exists(model_dir):
        os.makedirs(model_dir, exist_ok=True)   
        print("Downloading model to:", model_dir)
        print("This will take a few minutes and only happen once!")
    model = SentenceTransformer(
        embedding_model_id, 
        cache_folder=model_dir
        )
    embeddings = model.encode(text_list, normalize_embeddings=False)
    
    # Convert the embeddings to a list
    embeddings = embeddings.tolist()
    return embeddings

def local_llm_call(messages, llm_model_id="princeton-nlp/Sheared-LLaMA-1.3B", stream=False):
    from transformers import AutoModelForCausalLM, AutoTokenizer, TextStreamer
    model_dir = os.path.join(PACKAGE_DIR, 'models', llm_model_id)
    if not os.path.exists(model_dir):
        os.makedirs(model_dir, exist_ok=True)
        print("Downloading model to:", model_dir)
        print("This will take a few minutes and only happen once!")
    tok = AutoTokenizer.from_pretrained(llm_model_id, cache_dir=model_dir)
    model = AutoModelForCausalLM.from_pretrained(llm_model_id, cache_dir=model_dir)

    chat_template = tok.apply_chat_template(messages, tokenize=False, add_special_tokens=False)
    inputs = tok(chat_template, return_tensors="pt")
    
    if stream: 
        streamer = TextStreamer(tok)
        return model.generate(**inputs, streamer=streamer, max_new_tokens=2048)
    else:
        outputs = model.generate(**inputs, max_new_tokens=2048)
        return tok.batch_decode(outputs, skip_special_tokens=True)

def get_embedding(text_list, model="BAAI/bge-small-en-v1.5", local=False):
    if local: return local_get_embedding(text_list, embedding_model_id=model)
    response = requests.post('https://mirageml--brain-embed-text.modal.run', json={'text_list': text_list})
    response.raise_for_status()  # Raise an exception if the request failed
    return response.json()['embedding']

def llm_call(messages, model="gpt-3.5-turbo", stream=False, local=False):
    if local: return local_llm_call(messages, stream=stream)
    json_data = {
        "model": model,
        "messages": messages,
        "stream": stream
    }
    return requests.post('https://mirageml--brain-gpt.modal.run', json=json_data, stream=stream)
