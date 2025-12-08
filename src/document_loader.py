import os
import logging
from typing import List, Dict, Any, Optional
import pypdf
import docx

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DocumentLoader:
    """
    A class to load and extract text from various document formats (PDF, DOCX, TXT).
    """

    def __init__(self, data_folder: str):
        """
        Initialize the DocumentLoader with the path to the data folder.

        Args:
            data_folder (str): Path to the directory containing documents.
        """
        self.data_folder = data_folder
        if not os.path.exists(data_folder):
            logger.warning(f"Data folder '{data_folder}' does not exist.")

    def load_pdf(self, file_path: str) -> str:
        """
        Extract text from a PDF file.

        Args:
            file_path (str): Path to the PDF file.

        Returns:
            str: Extracted text content.
        """
        try:
            text = ""
            with open(file_path, 'rb') as file:
                reader = pypdf.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            logger.error(f"Error loading PDF '{file_path}': {e}")
            return ""

    def load_docx(self, file_path: str) -> str:
        """
        Extract text from a DOCX file.

        Args:
            file_path (str): Path to the DOCX file.

        Returns:
            str: Extracted text content.
        """
        try:
            doc = docx.Document(file_path)
            text = []
            for paragraph in doc.paragraphs:
                text.append(paragraph.text)
            return "\n".join(text).strip()
        except Exception as e:
            logger.error(f"Error loading DOCX '{file_path}': {e}")
            return ""

    def load_txt(self, file_path: str) -> str:
        """
        Read plain text from a TXT file.

        Args:
            file_path (str): Path to the TXT file.

        Returns:
            str: File content.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read().strip()
        except Exception as e:
            logger.error(f"Error loading TXT '{file_path}': {e}")
            return ""

    def load_document(self, file_path: str) -> Dict[str, Any]:
        """
        Auto-detect format and load document.

        Args:
            file_path (str): Path to the document file.

        Returns:
            dict: Dictionary with 'content', 'filename', and 'file_type'.
                  Returns empty content if loading fails or format is unsupported.
        """
        filename = os.path.basename(file_path)
        file_ext = os.path.splitext(filename)[1].lower()
        content = ""

        if file_ext == '.pdf':
            content = self.load_pdf(file_path)
        elif file_ext == '.docx':
            content = self.load_docx(file_path)
        elif file_ext == '.txt':
            content = self.load_txt(file_path)
        else:
            logger.warning(f"Unsupported file format: {filename}")
            return {'content': "", 'filename': filename, 'file_type': 'unknown'}

        return {
            'content': content,
            'filename': filename,
            'file_type': file_ext[1:]  # remove the dot
        }

    def load_all_documents(self) -> List[Dict[str, Any]]:
        """
        Load all supported documents from the data folder.

        Returns:
            list[dict]: List of dictionaries containing document data.
        """
        documents = []
        if not os.path.exists(self.data_folder):
            logger.error(f"Data folder '{self.data_folder}' not found.")
            return documents

        for filename in os.listdir(self.data_folder):
            file_path = os.path.join(self.data_folder, filename)
            if os.path.isfile(file_path):
                # Check if it's a supported format before trying to load
                if filename.lower().endswith(('.pdf', '.docx', '.txt')):
                    doc_data = self.load_document(file_path)
                    if doc_data['content']: # Only add if content was successfully extracted
                        documents.append(doc_data)
        
        logger.info(f"Loaded {len(documents)} documents from '{self.data_folder}'.")
        return documents
