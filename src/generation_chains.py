"""
Module for the generation pipeline.
Orchestrates RAG retrieval and LLM generation for job application materials.
"""

import logging
from typing import Dict, List, Any
from langchain_openai import ChatOpenAI
from .prompt_templates import get_prompt
from .rag_pipeline import RAGPipeline

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JobApplicationGenerator:
    """
    A class to generate job application materials using RAG and LLM.
    """

    def __init__(self, rag_pipeline: RAGPipeline, openai_api_key: str, model: str = "gpt-3.5-turbo"):
        """
        Initialize the JobApplicationGenerator.

        Args:
            rag_pipeline (RAGPipeline): The RAG pipeline instance for context retrieval.
            openai_api_key (str): OpenAI API key.
            model (str): The ChatGPT model to use (default: gpt-3.5-turbo).
        """
        self.rag_pipeline = rag_pipeline
        self.llm = ChatOpenAI(
            model=model,
            temperature=0.7,
            openai_api_key=openai_api_key
        )
        logger.info(f"JobApplicationGenerator initialized with model: {model}")

    def _retrieve_context(self, query: str, n_results: int = 3) -> str:
        """
        Retrieve relevant context from the RAG pipeline.

        Args:
            query (str): The query string.
            n_results (int): Number of results to retrieve.

        Returns:
            str: Concatenated context from retrieved chunks.
        """
        try:
            results = self.rag_pipeline.search_similar(query, n_results=n_results)
            if not results:
                logger.warning("No context retrieved from RAG pipeline.")
                return "No relevant background information available."
            
            context_parts = [result['text'] for result in results]
            return "\n\n".join(context_parts)
        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return "Error retrieving background information."

    def generate_resume_bullets(self, job_description: str, candidate_name: str) -> str:
        """
        Generate tailored resume bullet points.

        Args:
            job_description (str): The job description.
            candidate_name (str): The candidate's name.

        Returns:
            str: Generated resume bullet points.
        """
        try:
            logger.info("Generating resume bullets...")
            
            # Retrieve relevant context
            context = self._retrieve_context(job_description, n_results=5)
            
            # Format prompt
            prompt = get_prompt(
                "resume_bullets",
                job_description=job_description,
                context=context,
                name=candidate_name
            )
            
            # Generate with LLM
            response = self.llm.invoke(prompt)
            result = response.content
            
            logger.info("Resume bullets generated successfully.")
            return result
        except Exception as e:
            logger.error(f"Error generating resume bullets: {e}")
            return f"Error: {str(e)}"

    def generate_cover_letter(self, job_description: str, company_name: str, role_title: str) -> str:
        """
        Generate a personalized cover letter.

        Args:
            job_description (str): The job description.
            company_name (str): The company name.
            role_title (str): The role title.

        Returns:
            str: Generated cover letter.
        """
        try:
            logger.info("Generating cover letter...")
            
            # Retrieve relevant context
            context = self._retrieve_context(job_description, n_results=5)
            
            # Format prompt
            prompt = get_prompt(
                "cover_letter",
                job_description=job_description,
                company_name=company_name,
                role_title=role_title,
                context=context
            )
            
            # Generate with LLM
            response = self.llm.invoke(prompt)
            result = response.content
            
            logger.info("Cover letter generated successfully.")
            return result
        except Exception as e:
            logger.error(f"Error generating cover letter: {e}")
            return f"Error: {str(e)}"

    def generate_ats_analysis(self, job_description: str, resume_content: str = "") -> str:
        """
        Generate ATS analysis comparing resume to job description.

        Args:
            job_description (str): The job description.
            resume_content (str): The candidate's resume content (optional).

        Returns:
            str: ATS analysis report.
        """
        try:
            logger.info("Generating ATS analysis...")
            
            # If no resume content provided, retrieve from RAG pipeline
            if not resume_content or resume_content.strip() == "" or resume_content == "Resume content not provided for ATS analysis.":
                logger.info("No resume content provided, retrieving from RAG pipeline...")
                # Retrieve comprehensive context from uploaded documents
                resume_content = self._retrieve_context(
                    "resume work experience projects skills education background", 
                    n_results=10  # Get more chunks to build complete resume picture
                )
                logger.info(f"Retrieved resume content from RAG pipeline: {len(resume_content)} characters")
            
            # Format prompt
            prompt = get_prompt(
                "ats_analysis",
                job_description=job_description,
                resume_content=resume_content
            )
            
            # Generate with LLM
            response = self.llm.invoke(prompt)
            result = response.content
            
            logger.info("ATS analysis generated successfully.")
            return result
        except Exception as e:
            logger.error(f"Error generating ATS analysis: {e}")
            return f"Error: {str(e)}"

    def generate_linkedin_message(self, job_description: str, company_name: str, role_title: str) -> str:
        """
        Generate a personalized LinkedIn message.

        Args:
            job_description (str): The job description.
            company_name (str): The company name.
            role_title (str): The role title.

        Returns:
            str: Generated LinkedIn message.
        """
        try:
            logger.info("Generating LinkedIn message...")
            
            # Retrieve one key achievement
            results = self.rag_pipeline.search_similar(job_description, n_results=1)
            achievement = results[0]['text'] if results else "relevant experience in the field"
            
            # Format prompt
            prompt = get_prompt(
                "linkedin_message",
                job_description=job_description,
                company_name=company_name,
                role_title=role_title,
                achievement=achievement
            )
            
            # Generate with LLM
            response = self.llm.invoke(prompt)
            result = response.content
            
            logger.info("LinkedIn message generated successfully.")
            return result
        except Exception as e:
            logger.error(f"Error generating LinkedIn message: {e}")
            return f"Error: {str(e)}"

    def generate_all(
        self,
        job_description: str,
        company_name: str,
        role_title: str,
        candidate_name: str,
        resume_content: str
    ) -> Dict[str, str]:
        """
        Generate all job application materials.

        Args:
            job_description (str): The job description.
            company_name (str): The company name.
            role_title (str): The role title.
            candidate_name (str): The candidate's name.
            resume_content (str): The candidate's resume content.

        Returns:
            Dict[str, str]: Dictionary with all generated outputs.
        """
        logger.info("Generating all job application materials...")
        
        return {
            "resume_bullets": self.generate_resume_bullets(job_description, candidate_name),
            "cover_letter": self.generate_cover_letter(job_description, company_name, role_title),
            "ats_analysis": self.generate_ats_analysis(job_description, resume_content),
            "linkedin_message": self.generate_linkedin_message(job_description, company_name, role_title)
        }
