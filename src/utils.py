import re
import logging
from datetime import datetime
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def clean_text(text: str) -> str:
    """
    Clean the input text by removing extra whitespace, special characters, and fixing line breaks.
    Keeps alphanumeric characters, spaces, and basic punctuation.

    Args:
        text (str): The raw text to clean.

    Returns:
        str: The cleaned text.
    """
    if not text:
        return ""
    
    # Replace multiple newlines with a single space
    text = re.sub(r'\n+', ' ', text)
    
    # Remove special characters but keep basic punctuation (.,!?-')
    # This regex allows alphanumeric, spaces, and specified punctuation
    text = re.sub(r'[^a-zA-Z0-9\s.,!?-]', '', text)
    
    # Replace multiple spaces with a single space
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into chunks of approximately chunk_size characters, respecting sentence boundaries.
    Maintains an overlap between chunks.

    Args:
        text (str): The text to chunk.
        chunk_size (int): The target size for each chunk.
        overlap (int): The number of characters to overlap between chunks.

    Returns:
        List[str]: A list of text chunks.
    """
    if not text:
        return []

    # Simple sentence splitting based on punctuation
    # This splits on . ! ? followed by a space or end of string
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk = []
    current_length = 0
    
    for sentence in sentences:
        sentence_len = len(sentence)
        
        # If adding this sentence exceeds chunk_size and we have content, save the chunk
        if current_length + sentence_len > chunk_size and current_chunk:
            # Join current sentences to form the chunk
            chunk_str = " ".join(current_chunk)
            chunks.append(chunk_str)
            
            # Handle overlap
            # We want to keep the last few sentences that fit within the overlap size
            overlap_buffer = []
            overlap_len = 0
            for s in reversed(current_chunk):
                if overlap_len + len(s) < overlap:
                    overlap_buffer.insert(0, s)
                    overlap_len += len(s)
                else:
                    break
            
            current_chunk = overlap_buffer
            current_length = overlap_len
        
        current_chunk.append(sentence)
        current_length += sentence_len
    
    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(" ".join(current_chunk))
        
    return chunks

def extract_metadata(doc: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract metadata from a document dictionary.

    Args:
        doc (Dict[str, Any]): The document dictionary from DocumentLoader.

    Returns:
        Dict[str, Any]: A dictionary containing metadata.
    """
    content = doc.get('content', '')
    return {
        'filename': doc.get('filename', 'unknown'),
        'file_type': doc.get('file_type', 'unknown'),
        'date_processed': datetime.now().isoformat(),
        'word_count': len(content.split()) if content else 0
    }

def create_document_chunks(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Process a document: clean text, extract metadata, and create chunks.

    Args:
        doc (Dict[str, Any]): The raw document dictionary.

    Returns:
        List[Dict[str, Any]]: A list of dictionaries, each containing a text chunk and its metadata.
    """
    raw_content = doc.get('content', '')
    if not raw_content:
        logger.warning(f"Document {doc.get('filename')} has no content.")
        return []

    cleaned_content = clean_text(raw_content)
    metadata = extract_metadata(doc)
    text_chunks = chunk_text(cleaned_content)
    
    doc_chunks = []
    for i, chunk in enumerate(text_chunks):
        chunk_metadata = metadata.copy()
        chunk_metadata['chunk_index'] = i
        doc_chunks.append({
            'text': chunk,
            'metadata': chunk_metadata
        })
        
    logger.info(f"Created {len(doc_chunks)} chunks for {doc.get('filename')}")
    return doc_chunks
