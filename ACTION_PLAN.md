# Healthcare Chatbot (RAG): Action Plan

| Sr. No. | Technical Requirement / Feature | Blockers | Resources / Technologies | Estimated Time |
| :--- | :--- | :--- | :--- | :--- |
| 1 | Relevant medical dataset selection and integration | Finding dataset containing diseases, symptoms and remedies | Kaggle datasets, Pandas, NumPy | 3 hrs |
| 2 | Dataset preprocessing and cleaning | Inconsistent or missing data in dataset | Pandas, Python | 2 hrs |
| 3 | Embedding generation for dataset | Large dataset may increase processing time | Sentence-Transformers | 3 hrs |
| 4 | Vector database setup for semantic search | Efficient storage and retrieval of embeddings | ChromaDB | 2 hrs |
| 5 | RAG-based query processing | Ensuring accurate responses without hallucination | LangChain, Groq LLM | 4 hrs |
| 6 | Follow-up question generation based on user query | Maintaining conversational context | Groq API | 3 hrs |
| 7 | Remedy recommendation system | Dataset may not contain complete remedies | Dataset + Groq LLM reasoning | 3 hrs |
| 8 | Nearby clinic suggestion | Accessing user location and API usage limits | Google Maps / Google Places API | 3 hrs |
| 9 | Medication confirmation flow | User may give incomplete information | Conversational prompts via LLM | 2 hrs |
| 10 | Receipt upload support | Handling image uploads and formats | FastAPI File Upload | 2 hrs |
| 11 | OCR-based receipt text extraction | Low image quality or handwritten prescriptions | EasyOCR, OpenCV, Tesseract | 4 hrs |
| 12 | Follow-up remedy suggestions based on receipt | Correct interpretation of extracted medicine data | Groq LLM | 3 hrs |
| 13 | Chat interface for interaction | Real-time message updates and UI responsiveness | React, Tailwind CSS | 3 hrs |
| 14 | File upload UI for prescription images | Handling large image uploads | React, Axios | 2 hrs |
| **Total** | | | | **41 hrs** |
