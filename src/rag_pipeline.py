import os
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.utils import embedding_functions
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RAGPipeline:
    """
    A class to handle the RAG pipeline: embeddings, vector storage, and semantic search.
    """

    def __init__(self, openai_api_key: str, chroma_client: Optional[chromadb.ClientAPI] = None, collection_name: str = "job_assistant"):
        """
        Initialize the RAGPipeline.

        Args:
            openai_api_key (str): OpenAI API Key.
            chroma_client (chromadb.ClientAPI, optional): ChromaDB client. Defaults to None (creates a new PersistentClient).
            collection_name (str): Name of the ChromaDB collection.
        """
        self.openai_api_key = openai_api_key
        if not self.openai_api_key:
            logger.warning("OpenAI API Key is missing. Embeddings will fail.")
        
        self.collection_name = collection_name
        
        if chroma_client:
            self.client = chroma_client
        else:
            # Default to a persistent client in the data directory
            # Use path relative to this file to ensure consistency regardless of CWD
            from pathlib import Path
            current_dir = Path(__file__).parent.absolute()
            project_root = current_dir.parent
            data_path = str(project_root / "data" / "chroma_db")
            
            logger.info(f"Using ChromaDB path: {data_path}")
            self.client = chromadb.PersistentClient(path=data_path)
            
        self.embedding_model = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=self.openai_api_key
        )
        
        self.collection = None
        self.setup_vectorstore()

    def setup_vectorstore(self) -> None:
        """
        Create or load the ChromaDB collection.
        """
        try:
            # We use the OpenAI embedding function for Chroma to handle embeddings automatically if we pass it
            # But the requirement asks for create_embeddings method, so we might handle it manually or use the function.
            # To strictly follow "create_embeddings" method requirement, we will generate embeddings there and pass to add.
            # However, Chroma's get_or_create_collection can take an embedding function.
            # Let's stick to manual embedding generation to satisfy the specific method requirement clearly.
            
            self.collection = self.client.get_or_create_collection(name=self.collection_name)
            logger.info(f"Vector store collection '{self.collection_name}' ready.")
        except Exception as e:
            logger.error(f"Failed to setup vector store: {e}")

    def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts using OpenAI.

        Args:
            texts (List[str]): List of text strings.

        Returns:
            List[List[float]]: List of embedding vectors.
        """
        try:
            if not texts:
                return []
            return self.embedding_model.embed_documents(texts)
        except Exception as e:
            logger.error(f"Failed to create embeddings: {e}")
            return []

    def add_documents(self, chunks: List[Dict[str, Any]]) -> None:
        """
        Add document chunks to the vector store.

        Args:
            chunks (List[Dict[str, Any]]): List of document chunks with 'text' and 'metadata'.
        """
        if not chunks:
            logger.warning("No chunks to add.")
            return

        try:
            texts = [chunk['text'] for chunk in chunks]
            metadatas = [chunk['metadata'] for chunk in chunks]
            ids = [f"{chunk['metadata']['filename']}_{chunk['metadata']['chunk_index']}" for chunk in chunks]
            
            # Generate embeddings
            embeddings = self.create_embeddings(texts)
            
            if not embeddings:
                logger.error("Failed to generate embeddings. Aborting add_documents.")
                return

            self.collection.upsert(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Added/Updated {len(chunks)} chunks in collection '{self.collection_name}'.")
        except Exception as e:
            logger.error(f"Failed to add documents to vector store: {e}")

    def search_similar(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for similar documents using the query.

        Args:
            query (str): The search query.
            n_results (int): Number of results to return.

        Returns:
            List[Dict[str, Any]]: List of results with metadata and distance.
        """
        try:
            query_embedding = self.embedding_model.embed_query(query)
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results['ids']:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        'id': results['ids'][0][i],
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if results['distances'] else None
                    })
            
            return formatted_results
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def reset_vectorstore(self) -> None:
        """
        Delete and recreate the collection.
        """
        try:
            try:
                self.client.delete_collection(self.collection_name)
                logger.info(f"Collection '{self.collection_name}' deleted.")
            except ValueError:
                # Collection might not exist, which is fine
                logger.info(f"Collection '{self.collection_name}' did not exist, skipping delete.")
            except Exception as e:
                logger.warning(f"Error deleting collection: {e}. Attempting to recreate anyway.")
            
            self.setup_vectorstore()
            logger.info(f"Collection '{self.collection_name}' reset successfully.")
        except Exception as e:
            logger.error(f"Failed to reset vector store: {e}")

    def get_collection_count(self) -> int:
        """
        Get the number of documents in the collection.
        
        Returns:
            int: Number of items in the collection.
        """
        try:
            if self.collection:
                return self.collection.count()
            return 0
        except Exception as e:
            logger.error(f"Failed to get collection count: {e}")
            return 0
