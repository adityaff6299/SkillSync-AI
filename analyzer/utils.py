import PyPDF2
import re
import os
import numpy as np


_READER = None

def get_ocr_reader():
    
    global _READER
    if _READER is None:
        import easyocr
        print("--- Loading AI OCR Engine (One-time load) ---")
        
        _READER = easyocr.Reader(['en'], gpu=False)
    return _READER

def get_pdf_text(file_path):
   
    text = ""
    try:
        
        with open(file_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                content = page.extract_text()
                if content:
                    text += content
        
        
        if not text.strip():
            from pdf2image import convert_from_path
            print(">>> Image-PDF detected. Converting to images for OCR...")
            
            
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
   
    if not text or not isinstance(text, str):
        return []

    
    SKILL_LOOKUP = [
        'Python', 'Django', 'Java', 'C++', 'C', 'HTML', 'CSS', 
        'JavaScript', 'SQL', 'Machine Learning', 'Data Science', 
        'React', 'Node.js', 'Angular', 'AWS', 'Docker', 'Git'
    ]
    
    found = []
    text_clean = text.lower()
    
    
    for skill in SKILL_LOOKUP:
        if skill.lower() in text_clean:
            found.append(skill)
            
    
    if 'pyth0n' in text_clean or 'pytn' in text_clean:
        found.append('Python')
    if 'dj4ngo' in text_clean or 'djng' in text_clean:
        found.append('Django')
            
    
    found = list(set(found)) 
    if not found and len(text_clean.strip()) > 0:
        
        first_word = text_clean.replace(',', ' ').split()[0]
        return [first_word.capitalize()]
        
    return found