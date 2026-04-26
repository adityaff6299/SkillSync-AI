import PyPDF2
import re
import os
import numpy as np

# Global variable to hold the OCR engine so it only loads once
_READER = None

def get_ocr_reader():
    """Initializes EasyOCR only when an image-PDF is uploaded to save RAM."""
    global _READER
    if _READER is None:
        import easyocr
        print("--- Loading AI OCR Engine (One-time load) ---")
        # Set gpu=True if you have a dedicated graphics card and CUDA installed
        _READER = easyocr.Reader(['en'], gpu=False)
    return _READER

def get_pdf_text(file_path):
    """
    Extracts text from a PDF. 
    Try 1: Standard text layer (Fast).
    Try 2: OCR for image-based PDFs (Deep Scan).
    """
    text = ""
    try:
        # 1. Try standard text extraction
        with open(file_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                content = page.extract_text()
                if content:
                    text += content
        
        # 2. OCR Fallback (If the PDF is just an image)
        if not text.strip():
            from pdf2image import convert_from_path
            print(">>> Image-PDF detected. Converting to images for OCR...")
            
            # Note: Ensure Poppler is installed on your system
            images = convert_from_path(file_path)
            reader = get_ocr_reader()
            
            for i, img in enumerate(images):
                print(f">>> Scanning Page {i+1}...")
                img_np = np.array(img)
                results = reader.readtext(img_np, detail=0)
                text += " ".join(results)
                
            print(f"--- DEBUG: OCR EXTRACTED TEXT --- \n{text[:200]}...\n--------------------------------")

    except Exception as e:
        print(f"CRITICAL EXTRACTION ERROR: {e}")
        
    return text

def extract_skills(text):
    """
    Scans text for skills using a greedy approach. 
    If known skills aren't found, it falls back to the raw input.
    """
    if not text or not isinstance(text, str):
        return []

    # Aggressive list of core skills to check
    SKILL_LOOKUP = [
        'Python', 'Django', 'Java', 'C++', 'C', 'HTML', 'CSS', 
        'JavaScript', 'SQL', 'Machine Learning', 'Data Science', 
        'React', 'Node.js', 'Angular', 'AWS', 'Docker', 'Git'
    ]
    
    found = []
    text_clean = text.lower()
    
    # 1. Check if the skill name exists anywhere in the text
    for skill in SKILL_LOOKUP:
        if skill.lower() in text_clean:
            found.append(skill)
            
    # 2. Specific Fuzzy Checks for common OCR/Typing mistakes
    if 'pyth0n' in text_clean or 'pytn' in text_clean:
        found.append('Python')
    if 'dj4ngo' in text_clean or 'djng' in text_clean:
        found.append('Django')
            
    # 3. THE ULTIMATE FALLBACK
    # If we found nothing, but the user definitely typed *something*, 
    # just grab the first valid word so the search engine doesn't crash.
    found = list(set(found)) # Remove duplicates
    
    if not found and len(text_clean.strip()) > 0:
        # Split by commas or spaces and grab the first chunk
        first_word = text_clean.replace(',', ' ').split()[0]
        return [first_word.capitalize()]
        
    return found