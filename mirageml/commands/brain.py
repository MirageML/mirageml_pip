from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI


def load_embedding_model(use_openai=False):
    if use_openai: return OpenAIEmbeddings()
    from langchain.embeddings import HuggingFaceBgeEmbeddings

    model_name = "BAAI/bge-small-en-v1.5"
    model_kwargs = {'device': 'cpu'}
    encode_kwargs = {'normalize_embeddings': False}
    embeddings = HuggingFaceBgeEmbeddings(
        model_name=model_name,
        model_kwargs=model_kwargs,
        encode_kwargs=encode_kwargs
    )
    return embeddings

def load_llm(use_openai=False):
    if use_openai: return ChatOpenAI()
    from langchain.llms import HuggingFacePipeline

    llm = HuggingFacePipeline.from_model_id(
        model_id="HuggingFaceH4/zephyr-7b-alpha",
        task="text-generation",
        model_kwargs={"temperature": 0, "max_length": 256},
    )
    return llm

