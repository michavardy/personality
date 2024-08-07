from langchain.vectorstores.chroma import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from pathlib import Path
from typing import Callable
import shutil
from langchain_core.documents.base import Document


class VectorStoreError(Exception):
    pass

class ChromaVectorStore:
    _open_ai_embeddings = OpenAIEmbeddings()
    _db_path = "chroma_db"
    _k = 5
    def __init__(self, db_path = None, embeddings = None, k=None, overwrite=False):
        self._vector_store = None
        self.db_path = db_path
        self.embeddings = embeddings
        self.k = k
        if not self.embeddings:
            self.embeddings = self._open_ai_embeddings
        if not self.db_path:
            self.db_path = self._db_path
        if not self.k:
            self.k = self._k
        if overwrite == True:
            if self.is_vector_store_exists():
                self.delete_vector_store()
    @property
    def vector_store(self) -> Chroma:
        if self._vector_store is None:
            self._vector_store = self.get_vector_store()
        return self._vector_store
    def is_vector_store_exists(self) -> bool:
        if Path(self.db_path).exists():
            return True
        return False
    def get_vector_store(self) -> Chroma:
        if self.is_vector_store_exists():
            return Chroma(persist_directory=self.db_path, embedding_function=self.embeddings)
        raise VectorStoreError(f"The specified database path '{self.db_path}' does not exist.")
    def delete_vector_store(self) -> None:
        if not self.is_vector_store_exists():
             raise VectorStoreError(f"The specified database path '{self.db_path}' does not exist.")
        shutil.rmtree(self.db_path)
    def get_chunks(self, content:str, seperator:str='\n', chunk_size:int = 300, chunk_overlap:int = 100, length_function: Callable = len)-> list[str]:
        text_splitter = CharacterTextSplitter(
            separator=seperator, 
            chunk_size=chunk_size, 
            chunk_overlap=chunk_overlap, 
            length_function=length_function
            )
        return text_splitter.split_text(content)
    def load_chunk_into_vector_store(self, chunks: list[str]) -> None:
        vector_store = Chroma.from_texts(chunks, self.embeddings, persist_directory=self.db_path)
        vector_store.persist()
        self._vector_store = vector_store
    def extract_from_vector_store(self, prompt: str, k: int = None) -> list[Document]:
        if not k:
            k = self.k
        return self.vector_store.similarity_search(query=prompt, k=k)
    def extract_from_vector_store_with_score(self, prompt: str, k: int = None) -> list[tuple[Document, float]]:
        if not k:
            k = self.k
        return self.vector_store.similarity_search_with_score(query=prompt, k=k)
    def extract_from_vector_store_using_max_margina_relevance(self, prompt: str, k:int = None, lambda_mult: float = 0.5) -> list[Document]:
        if not k:
            k = self.k
        return self.vector_store.max_marginal_relevance_search_by_vector(query=prompt, k=k, lambda_mult=lambda_mult)