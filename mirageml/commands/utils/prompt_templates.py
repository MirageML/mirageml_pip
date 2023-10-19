RAG_TEMPLATE = """Answer the question based on the following context. If the context is relevant, mention which sources you used:
{context}

Sources:
{sources}

Question: {question}
"""

CHAT_TEMPLATE = """Answer the question using the following context:
{context}

Question: {question}
"""