from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from app.config import settings

class EmbeddingService:
    def __init__(self):
        self.embedding=GoogleGenerativeAIEmbeddings(
            google_api_key=settings.GOOGLE_API_KEY,
            model_name=settings.EMBEDDING_MODEL
        )
        self.text_splitter=RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            lenght_function=len,
            is_separator_regex=False
        )
    
    def split_text(self, text:str) -> List[str]:
        return self.text_splitter.split_text(text)
    
    def embed_text(self,text:str) -> List[float]:
        if not text or not text.strip():
            raise ValueError("Cannot embed empty text")
        return self.embedding.embed_query(text)
    
    def embed_texts(self,texts:List[str]) -> List[List[float]]:
        if not texts:
            raise ValueError("Cannot embed empty list of texts")
        return self.embedding.embed_documents(texts )