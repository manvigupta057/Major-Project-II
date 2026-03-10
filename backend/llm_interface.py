from langchain_ollama import OllamaLLM
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from config import Config
import os

class LLMInterface:
    def __init__(self, model_name: str = None, provider: str = "ollama"):
        if model_name:
            self.model_name = model_name
        elif hasattr(Config, 'LLM_MODEL'):
            self.model_name = Config.LLM_MODEL
        else:
            self.model_name = "llama3"
        
        temperature = 0.0
        if hasattr(Config, 'LLM_TEMPERATURE'):
            temperature = Config.LLM_TEMPERATURE
        
        if provider == "groq":
            from dotenv import load_dotenv
            load_dotenv()
            
            api_key = os.environ.get("GROQ_API_KEY")
            if not api_key:
                print("WARNING: GROQ_API_KEY not found in environment variables. Groq provider will fail if used.")
            
            self.llm = ChatGroq(model=self.model_name, temperature=temperature, groq_api_key=api_key)
        else:
            self.llm = OllamaLLM(model=self.model_name, temperature=temperature)
        
        template = """Answer the question based only on the following context:
        {context}
        
        Question: {question}
        """
        if hasattr(Config, 'PROMPT_TEMPLATE'):
            template = Config.PROMPT_TEMPLATE

        self.prompt = ChatPromptTemplate.from_template(template)

    def generate_answer(self, query: str, context: str) -> str:
        chain = self.prompt | self.llm
        response = chain.invoke({"context": context, "question": query})
        
        if hasattr(response, 'content'):
            return response.content
        
        return response
