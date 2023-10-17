import os
import requests
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI

PACKAGE_DIR = os.path.dirname(__file__)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

def load_embedding_model(embedding_model_id="BAAI/bge-small-en-v1.5", use_openai=True):
    if use_openai: 
        if 'OPENAI_API_KEY' not in os.environ:
            raise ValueError("The environment variable 'OPENAI_API_KEY' is not set. Please set it to continue. i.e. export OPENAI_API_KEY=<openai_api_key>")
        return OpenAIEmbeddings(
            openai_api_base="https://mirageml--creative-embed-text-amankishore-dev.modal.run"
        )
    from langchain.embeddings import HuggingFaceBgeEmbeddings

    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}
    model_dir = os.path.join(PACKAGE_DIR, 'models', embedding_model_id)
    os.makedirs(model_dir, exist_ok=True)
    print("Saving embedding model to:", model_dir)
    embeddings = HuggingFaceBgeEmbeddings(
        model_name=embedding_model_id,
        cache_folder=model_dir,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    return embeddings

def load_llm(llm_model_id="HuggingFaceH4/zephyr-7b-alpha", use_openai=True, **kwargs):
    if use_openai: 
        if 'OPENAI_API_KEY' not in os.environ:
            raise ValueError("The environment variable 'OPENAI_API_KEY' is not set. Please set it to continue. i.e. export OPENAI_API_KEY=<openai_api_key>")
        return ChatOpenAI()
    from langchain.llms import HuggingFacePipeline

    model_dir = os.path.join(PACKAGE_DIR, 'models', llm_model_id)
    print("Saving LLM model to:", model_dir)
    os.makedirs(model_dir, exist_ok=True)
    llm = HuggingFacePipeline.from_model_id(
        model_id=llm_model_id,
        task="text-generation",
        model_kwargs={"temperature": 0, "do_sample": True, "max_length": 256},
        cache_dir=model_dir
    )
    return llm


def get_embedding(text_list):
    response = requests.post('https://mirageml--creative-embed-text-amankishore-dev.modal.run', json={'text_list': text_list})
    response.raise_for_status()  # Raise an exception if the request failed
    return response.json()['embedding']

def llm_call(messages, stream=False):
    json_data = {
        "messages": messages,
        "stream": stream
    }
    return requests.post('https://mirageml--creative-gpt-amankishore-dev.modal.run', json=json_data, stream=stream)
