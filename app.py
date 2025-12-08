"""
Main application entry point for the AI-Powered Job Application Assistant.
This file initializes the Streamlit interface and orchestrates the application flow.
"""

import streamlit as st
import os
from dotenv import load_dotenv
import tempfile
from pathlib import Path

from src.document_loader import DocumentLoader
from src.utils import create_document_chunks
from src.rag_pipeline import RAGPipeline
from src.generation_chains import JobApplicationGenerator

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="AI Job Application Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    /* Increase base font size for all text */
    html, body, [class*="css"] {
        font-size: 18px !important;
    }
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #555;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        font-size: 18px !important;
    }
    /* Increase font size for all text inputs and text areas */
    .stTextInput input, .stTextArea textarea {
        font-size: 18px !important;
    }
    /* Increase font size for labels */
    label {
        font-size: 18px !important;
    }
    /* Increase font size for markdown content */
    .stMarkdown {
        font-size: 18px !important;
    }
    /* Increase font size for info/warning/error messages */
    .stAlert {
        font-size: 18px !important;
    }
    </style>
""", unsafe_allow_html=True)

# Check for valid API key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key or api_key.startswith("sk-your-") or api_key == "your_api_key_here":
    st.error("Please set a valid OPENAI_API_KEY in your .env file")
    st.info("Get your API key from: https://platform.openai.com/api-keys")
    st.markdown("""
    **Steps to fix:**
    1. Go to https://platform.openai.com/api-keys
    2. Create a new API key
    3. Open `job-assistant/.env` file
    4. Replace `sk-your-key-here` with your actual API key
    5. Restart the application
    """)
    st.stop()

# Initialize session state
def init_session_state():
    """Initialize session state variables."""
    if 'rag_pipeline' not in st.session_state:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            st.session_state.rag_pipeline = RAGPipeline(openai_api_key=api_key)
            st.session_state.generator = JobApplicationGenerator(
                rag_pipeline=st.session_state.rag_pipeline,
                openai_api_key=api_key
            )
        else:
            st.session_state.rag_pipeline = None
            st.session_state.generator = None
    
    if 'documents_indexed' not in st.session_state:
        st.session_state.documents_indexed = False
    
    if 'indexed_files' not in st.session_state:
        st.session_state.indexed_files = []
    
    # Initialize dark mode (default to dark)
    if 'dark_mode' not in st.session_state:
        st.session_state.dark_mode = True

init_session_state()

# Apply theme-based styling
def apply_theme():
    """Apply dark or light theme based on session state."""
    if st.session_state.dark_mode:
        # Dark mode colors - improved for better readability
        bg_color = "#1a1a2e"
        sidebar_bg = "#16213e"
        text_color = "#ffffff"  # Bright white for main text
        secondary_text = "#e0e0e0"  # Slightly dimmer for secondary text
        heading_color = "#ffffff"  # White for headings
        accent_color = "#0f3460"
        card_bg = "#2d3748"  # Dark card background
        border_color = "#533483"
        input_bg = "#2d3748"  # Dark input background
        input_text = "#ffffff"
        button_bg = "#2d3748"  # Dark button background
        button_text = "#ffffff"  # White text for dark buttons
        box_bg = "#2d3748"  # Dark background for boxes
    else:
        # Light mode colors
        bg_color = "#ffffff"
        sidebar_bg = "#f8f9fa"
        text_color = "#1a1a1a"
        secondary_text = "#333333"
        heading_color = "#1a1a1a"
        accent_color = "#e8eaf6"
        card_bg = "#f5f5f5"
        border_color = "#9c27b0"
        input_bg = "#ffffff"
        input_text = "#1a1a1a"
        button_bg = "#f8f9fa"
        button_text = "#1a1a1a"
        box_bg = "#ffffff"
    
    st.markdown(f"""
        <style>
        /* Base font size for all text */
        html, body, [class*="css"] {{
            font-size: 16px !important;
        }}
        
        /* Remove white space at top */
        .main .block-container {{
            padding-top: 2rem !important;
        }}
        
        /* Hide Streamlit header */
        header {{
            background-color: {bg_color} !important;
        }}
        
        header[data-testid="stHeader"] {{
            background-color: {bg_color} !important;
        }}
        
        /* Main toolbar */
        .stApp header {{
            background-color: {bg_color} !important;
        }}
        
        /* Top padding area */
        .main {{
            background-color: {bg_color} !important;
        }}
        
        /* Main app background */
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}
        
        /* All text elements */
        p, div, span, label {{
            color: {text_color} !important;
            font-size: 16px !important;
        }}
        
        /* Headings */
        h1, h2, h3, h4, h5, h6 {{
            color: {heading_color} !important;
            font-weight: 700 !important;
        }}
        
        h1 {{ font-size: 2rem !important; }}
        h2 {{ font-size: 1.5rem !important; }}
        h3 {{ font-size: 1.25rem !important; }}
        
        /* Sidebar styling */
        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg};
            padding-top: 2rem;
        }}
        
        [data-testid="stSidebar"] * {{
            color: {text_color} !important;
        }}
        
        [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {{
            color: {text_color} !important;
        }}
        
        /* Sidebar title */
        [data-testid="stSidebar"] h1 {{
            color: {heading_color} !important;
            font-size: 1.5rem !important;
            font-weight: 700 !important;
            padding: 0 1rem;
            margin-bottom: 0.5rem;
        }}
        
        /* Text inputs and text areas */
        .stTextInput input, .stTextArea textarea {{
            background-color: {input_bg} !important;
            color: {input_text} !important;
            font-size: 14px !important;
            border: 1px solid {border_color} !important;
        }}
        
        .stTextInput input::placeholder, .stTextArea textarea::placeholder {{
            color: {secondary_text} !important;
            opacity: 0.6;
        }}
        
        /* Labels */
        label {{
            font-size: 14px !important;
            font-weight: 600 !important;
            color: {text_color} !important;
        }}
        
        /* Markdown content */
        .stMarkdown {{
            font-size: 15px !important;
            color: {text_color} !important;
        }}
        
        /* Info/warning/error messages */
        .stAlert {{
            font-size: 14px !important;
        }}
        
        /* File uploader - dark background in dark mode */
        [data-testid="stFileUploader"] {{
            background-color: {box_bg} !important;
        }}
        
        [data-testid="stFileUploader"] section {{
            background-color: {box_bg} !important;
            border: 1px solid #4a5568 !important;  /* Solid gray border instead of dashed purple */
        }}
        
        [data-testid="stFileUploader"] label {{
            color: {text_color} !important;
        }}
        
        [data-testid="stFileUploader"] small {{
            color: {secondary_text} !important;
        }}
        
        /* File uploader drag and drop area */
        [data-testid="stFileUploadDropzone"] {{
            background-color: {box_bg} !important;
            border: 1px solid #4a5568 !important;  /* Solid gray border */
        }}
        
        /* Browse Files button inside file uploader */
        [data-testid="stFileUploader"] button {{
            background-color: {button_bg} !important;
            color: {button_text} !important;
            border: 1px solid #4a5568 !important;  /* Gray border instead of purple */
            font-size: 16px !important;
            outline: none !important;  /* Remove outline */
        }}
        
        [data-testid="stFileUploader"] button:hover {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
            color: white !important;
            border: 1px solid transparent !important;
        }}
        
        [data-testid="stFileUploader"] button:focus {{
            outline: none !important;  /* Remove focus outline */
            box-shadow: none !important;
        }}
        
        /* All white boxes/containers */
        .element-container {{
            background-color: transparent !important;
        }}
        
        /* Form containers */
        [data-testid="stForm"] {{
            background-color: transparent !important;
        }}
        
        /* Column containers */
        [data-testid="column"] {{
            background-color: transparent !important;
        }}
        
        /* Navigation radio buttons - make them look like modern nav items */
        [data-testid="stSidebar"] .stRadio > label {{
            display: none;
        }}
        
        [data-testid="stSidebar"] .stRadio > div {{
            gap: 0.5rem;
        }}
        
        [data-testid="stSidebar"] .stRadio > div > label {{
            background-color: transparent;
            border-radius: 8px;
            padding: 0.75rem 1rem;
            margin: 0.25rem 0;
            cursor: pointer;
            transition: all 0.3s ease;
            border: none;
            color: {text_color} !important;
            font-size: 15px !important;
            display: flex;
            align-items: center;
        }}
        
        [data-testid="stSidebar"] .stRadio > div > label:hover {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
            transform: translateX(5px);
        }}
        
        [data-testid="stSidebar"] .stRadio > div > label[data-baseweb="radio"] > div:first-child {{
            display: none;
        }}
        
        /* Active navigation item */
        [data-testid="stSidebar"] .stRadio > div > label > div[data-checked="true"] {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
        }}
        
        /* Buttons - Fix text color for readability */
        .stButton > button {{
            font-size: 14px !important;
            font-weight: 600 !important;
            padding: 0.6rem 1.2rem !important;
            outline: none !important;
        }}
        
        .stButton > button:focus {{
            outline: none !important;
            box-shadow: none !important;
        }}
        
        /* Primary buttons (with colored background) */
        .stButton > button[kind="primary"] {{
            color: white !important;
            background-color: #dc3545 !important;
            border: 1px solid #dc3545 !important;
        }}
        
        /* Secondary buttons (default - dark background in dark mode) */
        .stButton > button[kind="secondary"] {{
            color: {button_text} !important;
            background-color: {button_bg} !important;
            border: 1px solid #4a5568 !important;  /* Gray border instead of purple */
        }}
        
        /* Default buttons */
        .stButton > button:not([kind]) {{
            color: {button_text} !important;
            background-color: {button_bg} !important;
            border: 1px solid #4a5568 !important;  /* Gray border instead of purple */
        }}
        
        /* Download buttons */
        .stDownloadButton > button {{
            color: {button_text} !important;
            background-color: {button_bg} !important;
            border: 1px solid #4a5568 !important;  /* Gray border instead of purple */
            font-size: 14px !important;
            outline: none !important;
        }}
        
        .stDownloadButton > button:focus {{
            outline: none !important;
            box-shadow: none !important;
        }}
        
        /* Form submit button */
        button[type="submit"] {{
            color: white !important;
        }}
        
        /* Theme toggle button styling */
        .theme-toggle {{
            position: fixed;
            bottom: 2rem;
            left: 1rem;
            z-index: 999;
        }}
        
        .theme-toggle button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
            border: none;
            border-radius: 50px;
            padding: 0.75rem 1.5rem;
            font-size: 18px !important;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            transition: all 0.3s ease;
        }}
        
        .theme-toggle button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }}
        </style>
    """, unsafe_allow_html=True)

apply_theme()

# Sidebar navigation
with st.sidebar:
    st.title("Job Application Assistant")
    st.markdown("---")
    
    # Navigation menu
    page = st.radio(
        "Navigation",
        ["Setup Documents", "Generate Materials"],
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Theme toggle button
    theme_icon = "" if st.session_state.dark_mode else ""
    theme_text = "Light Mode" if st.session_state.dark_mode else "Dark Mode"
    
    if st.button(f"{theme_icon} {theme_text}", key="theme_toggle", use_container_width=True):
        st.session_state.dark_mode = not st.session_state.dark_mode
        st.rerun()


# Clean up page names for logic
page = page.replace("📄 ", "").replace("✨ ", "").replace("ℹ️ ", "")

# Check for API key
if not os.getenv("OPENAI_API_KEY"):
    st.error("OpenAI API key not found! Please add OPENAI_API_KEY to your .env file.")
    st.stop()

# Page 1: Setup Documents
if page == "Setup Documents":
    st.markdown('<p class="main-header">Setup Your Documents</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Upload your resume, portfolio, or background documents to create a personalized knowledge base.</p>', unsafe_allow_html=True)
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Upload Documents (PDF, DOCX, TXT)",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True,
        help="Upload your resume, cover letters, project descriptions, or any relevant documents."
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("Process and Index Documents", type="primary"):
            if not uploaded_files:
                st.warning("Please upload at least one document.")
            else:
                with st.spinner("Processing documents..."):
                    try:
                        # Create temporary directory for uploaded files
                        temp_dir = tempfile.mkdtemp()
                        loader = DocumentLoader(temp_dir)
                        
                        # Save uploaded files
                        for uploaded_file in uploaded_files:
                            file_path = os.path.join(temp_dir, uploaded_file.name)
                            with open(file_path, 'wb') as f:
                                f.write(uploaded_file.getbuffer())
                        
                        # Load and process documents
                        documents = loader.load_all_documents()
                        
                        if not documents:
                            st.error("No documents could be loaded. Please check your files.")
                        else:
                            # Create chunks
                            all_chunks = []
                            for doc in documents:
                                chunks = create_document_chunks(doc)
                                all_chunks.extend(chunks)
                            
                            # Add to RAG pipeline
                            st.session_state.rag_pipeline.add_documents(all_chunks)
                            
                            # Update session state
                            st.session_state.documents_indexed = True
                            st.session_state.indexed_files = [f.name for f in uploaded_files]
                            
                            st.success(f"Successfully indexed {len(all_chunks)} chunks from {len(documents)} documents!")
                            
                    except Exception as e:
                        st.error(f"Error processing documents: {str(e)}")
    
    with col2:
        if st.button("Reset Vector Store", type="secondary"):
            if st.session_state.rag_pipeline:
                st.session_state.rag_pipeline.reset_vectorstore()
                st.session_state.documents_indexed = False
                st.session_state.indexed_files = []
                st.success("Vector store reset successfully!")
    
    # Display indexed documents
    st.markdown("---")
    st.subheader("Indexed Documents")
    
    if st.session_state.documents_indexed and st.session_state.indexed_files:
        st.write(f"**{len(st.session_state.indexed_files)} documents indexed:**")
        for filename in st.session_state.indexed_files:
            st.write(f"✓ {filename}")
    else:
        st.info("No documents indexed yet. Upload and process documents to get started.")

# Page 2: Generate Materials
elif page == "Generate Materials":
    st.markdown('<p class="main-header">Generate Application Materials</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Create tailored resumes, cover letters, and more based on job descriptions.</p>', unsafe_allow_html=True)
    
    # Check if documents are indexed
    if not st.session_state.documents_indexed:
        st.warning("No documents indexed yet. Please go to 'Setup Documents' to upload your background information first.")
        st.stop()
    
    # Input form
    with st.form("job_details_form"):
        st.subheader("Job Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Company Name *", placeholder="e.g., Google")
            role_title = st.text_input("Role Title *", placeholder="e.g., Senior Software Engineer")
        
        with col2:
            candidate_name = st.text_input("Your Name *", placeholder="e.g., John Doe")
            resume_content = st.text_area(
                "Your Current Resume (for ATS Analysis)",
                placeholder="Paste your current resume text here...",
                height=100,
                help="This is used for ATS analysis to compare against the job description."
            )
        
        job_description = st.text_area(
            "Job Description *",
            placeholder="Paste the complete job description here...",
            height=300,
            help="Include the full job posting with requirements, responsibilities, and qualifications."
        )
        
        submit_button = st.form_submit_button("Generate All Materials", type="primary")
    
    # Generate materials
    if submit_button:
        if not all([job_description, company_name, role_title, candidate_name]):
            st.error("Please fill in all required fields (marked with *).")
        else:
            with st.spinner("Generating your application materials... This may take a minute."):
                try:
                    # Use placeholder resume if not provided
                    if not resume_content:
                        resume_content = "Resume content not provided for ATS analysis."
                    
                    # Generate all materials
                    results = st.session_state.generator.generate_all(
                        job_description=job_description,
                        company_name=company_name,
                        role_title=role_title,
                        candidate_name=candidate_name,
                        resume_content=resume_content
                    )
                    
                    st.success("All materials generated successfully!")
                    
                    # Display results in tabs
                    tab1, tab2, tab3, tab4 = st.tabs([
                        "Resume Bullets",
                        "Cover Letter",
                        "ATS Analysis",
                        "LinkedIn Message"
                    ])

                    # Store results in session state for regeneration
                    if 'generated_results' not in st.session_state:
                        st.session_state.generated_results = {}
                    st.session_state.generated_results = results
                    st.session_state.job_details = {
                        'job_description': job_description,
                        'company_name': company_name,
                        'role_title': role_title,
                        'candidate_name': candidate_name,
                        'resume_content': resume_content
                    }

                except Exception as e:
                    st.error(f"Error generating materials: {str(e)}")
                    st.exception(e)

    # Display results if they exist
    if 'generated_results' in st.session_state and st.session_state.generated_results:
        results = st.session_state.generated_results

        # Helper functions for downloads
        def create_docx_download(content, filename):
            """Create a DOCX file for download"""
            from docx import Document
            from io import BytesIO

            doc = Document()
            for line in content.split('\n'):
                if line.strip():
                    doc.add_paragraph(line)

            bio = BytesIO()
            doc.save(bio)
            bio.seek(0)
            return bio

        def create_txt_download(content):
            """Create a TXT file for download"""
            return content.encode()

        # Custom CSS for better styling
        st.markdown("""
            <style>
            .generated-content {
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                border-left: 4px solid #1f77b4;
                margin: 10px 0;
                font-size: 18px;
            }
            .bullet-point {
                font-size: 1.2rem;
                line-height: 2;
                margin: 12px 0;
                padding-left: 10px;
            }
            .section-header {
                color: #1f77b4;
                font-size: 1.8rem;
                font-weight: 600;
                margin-top: 10px;
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### Generated Materials")

        # Display results in tabs
        tab1, tab2, tab3, tab4 = st.tabs([
            "Resume Bullets",
            "Cover Letter",
            "ATS Analysis",
            "LinkedIn Message"
        ])

        with tab1:
            st.markdown('<p class="section-header">Resume Bullet Points</p>', unsafe_allow_html=True)

            # Display bullets with better formatting
            st.markdown('<div class="generated-content">', unsafe_allow_html=True)
            bullets = results['resume_bullets'].split('\n')
            for bullet in bullets:
                if bullet.strip():
                    st.markdown(f'<div class="bullet-point">{bullet}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Download buttons
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                st.download_button(
                    label="Download TXT",
                    data=create_txt_download(results['resume_bullets']),
                    file_name="resume_bullets.txt",
                    mime="text/plain"
                )
            with col2:
                if st.button("Regenerate", key="regen_bullets"):
                    with st.spinner("Regenerating bullets..."):
                        try:
                            new_bullets = st.session_state.generator.generate_resume_bullets(
                                st.session_state.job_details['job_description'],
                                st.session_state.job_details['candidate_name']
                            )
                            st.session_state.generated_results['resume_bullets'] = new_bullets
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

        with tab2:
            st.markdown('<p class="section-header">Cover Letter</p>', unsafe_allow_html=True)

            # Display cover letter
            st.markdown('<div class="generated-content">', unsafe_allow_html=True)
            paragraphs = results['cover_letter'].split('\n\n')
            for para in paragraphs:
                if para.strip():
                    st.markdown(f'<p style="line-height: 1.8; margin: 15px 0;">{para}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Download buttons
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                st.download_button(
                    label="Download DOCX",
                    data=create_docx_download(results['cover_letter'], "cover_letter.docx"),
                    file_name="cover_letter.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            with col2:
                if st.button("Regenerate", key="regen_cover"):
                    with st.spinner("Regenerating cover letter..."):
                        try:
                            new_cover = st.session_state.generator.generate_cover_letter(
                                st.session_state.job_details['job_description'],
                                st.session_state.job_details['company_name'],
                                st.session_state.job_details['role_title']
                            )
                            st.session_state.generated_results['cover_letter'] = new_cover
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

        with tab3:
            st.markdown('<p class="section-header">ATS Analysis Report</p>', unsafe_allow_html=True)

            # Display ATS analysis
            st.markdown(results['ats_analysis'])

            # Download button
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                st.download_button(
                    label="Download TXT",
                    data=create_txt_download(results['ats_analysis']),
                    file_name="ats_analysis.txt",
                    mime="text/plain"
                )
            with col2:
                if st.button("Regenerate", key="regen_ats"):
                    with st.spinner("Regenerating ATS analysis..."):
                        try:
                            new_ats = st.session_state.generator.generate_ats_analysis(
                                st.session_state.job_details['job_description'],
                                st.session_state.job_details['resume_content']
                            )
                            st.session_state.generated_results['ats_analysis'] = new_ats
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

        with tab4:
            st.markdown('<p class="section-header">LinkedIn Message</p>', unsafe_allow_html=True)

            # Display LinkedIn message
            st.markdown('<div class="generated-content">', unsafe_allow_html=True)
            st.markdown(f'<p style="line-height: 1.8;">{results["linkedin_message"]}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Download buttons
            col1, col2, col3 = st.columns([1, 1, 2])
            with col1:
                st.download_button(
                    label="Download TXT",
                    data=create_txt_download(results['linkedin_message']),
                    file_name="linkedin_message.txt",
                    mime="text/plain"
                )
            with col2:
                if st.button("Regenerate", key="regen_linkedin"):
                    with st.spinner("Regenerating LinkedIn message..."):
                        try:
                            new_linkedin = st.session_state.generator.generate_linkedin_message(
                                st.session_state.job_details['job_description'],
                                st.session_state.job_details['company_name'],
                                st.session_state.job_details['role_title']
                            )
                            st.session_state.generated_results['linkedin_message'] = new_linkedin
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
