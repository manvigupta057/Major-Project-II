class Config:
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    CHROMA_DB_DIR = "./chroma_db"
    COLLECTION_NAME = "healthcare_docs"
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50
    MAX_SEARCH_RESULTS = 100
    LLM_MODEL = "llama-3.1-8b-instant"
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