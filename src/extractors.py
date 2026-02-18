import io
from docx import Document
import pandas as pd
from PyPDF2 import PdfReader


def extract_text(filename: str, file_content: bytes) -> str:
    """Extract text from TXT, DOCX, PDF, or XLSX files"""
    
    if filename.endswith('.txt'):
        try:
            return file_content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                return file_content.decode('latin-1')
            except:
                return file_content.decode('utf-8', errors='ignore')
    
    elif filename.endswith('.pdf'):
        pdf_reader = PdfReader(io.BytesIO(file_content))
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text() + '\n'
        return text
    
    elif filename.endswith('.docx'):
        doc = Document(io.BytesIO(file_content))
        text = '\n'.join([para.text for para in doc.paragraphs])
        return text
    
    elif filename.endswith('.xlsx'):
        df = pd.read_excel(io.BytesIO(file_content))
        text = df.to_string()
        return text
    
    else:
        raise ValueError("Formato de archivo no soportado. Soportados: .txt, .pdf, .docx, .xlsx")