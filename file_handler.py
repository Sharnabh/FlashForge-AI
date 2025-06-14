import PyPDF2
import docx
import io
from typing import Optional, Tuple

class FileHandler:
    """Handles file processing for different formats"""
    
    @staticmethod
    def extract_text_from_pdf(file_content: bytes) -> str:
        """Extract text from PDF file"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    @staticmethod
    def extract_text_from_docx(file_content: bytes) -> str:
        """Extract text from DOCX file"""
        try:
            doc = docx.Document(io.BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")
    
    @staticmethod
    def extract_text_from_txt(file_content: bytes) -> str:
        """Extract text from TXT file"""
        try:
            return file_content.decode('utf-8').strip()
        except UnicodeDecodeError:
            try:
                return file_content.decode('latin-1').strip()
            except Exception as e:
                raise Exception(f"Error reading TXT file: {str(e)}")
    
    @staticmethod
    def process_uploaded_file(uploaded_file) -> Tuple[str, str]:
        """Process uploaded file and return filename and content"""
        if uploaded_file is None:
            return "", ""
        
        filename = uploaded_file.name
        file_content = uploaded_file.read()
        
        if filename.lower().endswith('.pdf'):
            content = FileHandler.extract_text_from_pdf(file_content)
        elif filename.lower().endswith('.docx'):
            content = FileHandler.extract_text_from_docx(file_content)
        elif filename.lower().endswith('.txt'):
            content = FileHandler.extract_text_from_txt(file_content)
        else:
            raise Exception("Unsupported file format. Please upload PDF, DOCX, or TXT files.")
        
        return filename, content
