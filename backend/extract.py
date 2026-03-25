import fitz
from fastapi import HTTPException
import fitz

def extract_text(file_path: str, start_page: int, end_page: int):
    full_text = ""
    word_map = [] 
    with fitz.open(file_path) as doc:
        total_pages = len(doc)
        actual_end = min(end_page, total_pages)
        
        for page_num in range(start_page, actual_end):
            page = doc[page_num]
            
            full_text += page.get_text("text")
            
          
            words = page.get_text("words")
            
            for w in words:
                word_map.append({
                    "text": w[4],
                    "bbox": [w[0], w[1], w[2], w[3]], 
                    "page": page_num
                })
            
    return {
        "content": full_text, 
        "word_map": word_map, 
        "total_pages": total_pages
    }