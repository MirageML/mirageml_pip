RAG_TEMPLATE = """Answer the question based only on the following context, if the context isn't relevant answer without it. If the context is relevant, mention which sources you used.:
{context}

Sources:
{sources}

Question: {question}
"""