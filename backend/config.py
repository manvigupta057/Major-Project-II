class Config:
    EMBEDDING_MODEL = "mxbai-embed-large"
    CHROMA_DB_DIR = "./chroma_db"
    COLLECTION_NAME = "rag_documents"
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    MAX_SEARCH_RESULTS = 100
    LLM_MODEL = "llama3.2:1b"
    LLM_TEMPERATURE = 0.0
    
    PROMPT_TEMPLATE = """You are a strictly helpful assistant. Use ONLY the following pieces of context to answer the question at the end.
    
    Rules:
    1. Do NOT use any outside knowledge.
    2. Use the provided context to answer the question.
    3. You can infer structural information (like column names) from the data provided.
    
    Context:
    {context}
    
    Question: {question}
    
    Answer:"""