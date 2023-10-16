import os
from operator import itemgetter

from .brain import load_embedding_model, load_llm

from langchain.prompts import ChatPromptTemplate
from langchain.prompts.prompt import PromptTemplate
from langchain.schema.output_parser import StrOutputParser
from langchain.schema.runnable import RunnablePassthrough
from langchain.schema.runnable import RunnableMap
from langchain.schema import Document, format_document
from langchain.vectorstores import Qdrant
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory



os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_API_KEY"] = "ls__3c2ab9d78f454ee7a82f44d803e02e75"
os.environ["LANGCHAIN_PROJECT"] = "mirage-cli"


DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")
def _combine_documents(docs, document_prompt = DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n"):
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)


def rag_question(db_name=None):
    if 'OPENAI_API_KEY' not in os.environ:
        raise ValueError("The environment variable 'OPENAI_API_KEY' is not set. Please set it to continue. i.e. export OPENAI_API_KEY=<openai_api_key>")

    documents = [Document(page_content="harrison worked at kensho", metadata={"source": 1})]
    vectorstore = Qdrant.from_documents(
        documents, 
        embedding=load_embedding_model(),
        location=":memory:"
    )
    retriever = vectorstore.as_retriever()
    memory = ConversationBufferMemory(return_messages=True, output_key="answer", input_key="question")

    _template = """Given the following conversation and a follow up question, rephrase the follow up question to be a standalone question, in its original language.

    Chat History:
    {chat_history}
    Follow Up Input: {question}
    Standalone question:"""
    CONDENSE_QUESTION_PROMPT = PromptTemplate.from_template(_template)

    template = """Answer the question based only on the following context:
    {context}

    Question: {question}
    """
    ANSWER_PROMPT = ChatPromptTemplate.from_template(template)
    
    _inputs = RunnableMap(
        standalone_question=RunnablePassthrough.assign(
            chat_history=lambda x: memory.buffer_as_str
        ) | CONDENSE_QUESTION_PROMPT | load_llm | StrOutputParser(),
    )
    # Now we retrieve the documents
    retrieved_documents = {
        "docs": itemgetter("standalone_question") | retriever,
        "question": lambda x: x["standalone_question"]
    }
    # Now we construct the inputs for the final prompt
    final_inputs = RunnableMap(
        context=RunnablePassthrough.assign(
            chat_history=lambda x: _combine_documents(x["docs"])
        ),
        question=itemgetter("question")
    )
    
    final_inputs = {
        "context": lambda x: _combine_documents(x["docs"]),
        "question": itemgetter("question")
    }
    # And finally, we do the part that returns the answers
    answer = {
        "answer": final_inputs | ANSWER_PROMPT | load_llm,
        "docs": itemgetter("docs"),
    }
    # And now we put it all together!
    final_chain = _inputs | retrieved_documents | answer
    
    print("Starting chat. Type 'exit' to end the chat.")
    chat_history = []
    while True:
        user_input = input("Chat with Mirage: ")
        if user_input.lower() == 'exit':
            break

        inputs = {
            "question": user_input,
        }

        ai_reponse = ""
        for s in final_chain.stream(inputs):
            if "docs" in s:
                documents = s["docs"]        
            else: 
                print(s["answer"].content, end="", flush=True)
                ai_reponse += s["answer"].content
        print("\n\n")
        if documents:
            sources = "\n".join([str(x.metadata["source"]) for x in documents])
            print("Relevant Sources:\n" + sources + "\n\n")
        memory.save_context(inputs, {"answer": ai_reponse})

