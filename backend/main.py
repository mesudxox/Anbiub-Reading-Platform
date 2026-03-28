from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from book_db import engine, get_db, SessionLocal
from sqlalchemy.orm import Session
import model
from fastapi import UploadFile, File, Depends
import os
import uuid
import shutil
from extract import extract_text
import re
from translation import translate_to_amharic

model.Base.metadata.create_all(bind=engine)

app=FastAPI(title="Anbibu Reading Platform")
app.add_middleware(CORSMiddleware, 
                   allow_origins=["*"],
                   allow_methods=["*"]
                   )

@app.get("/books")
def list_of_books(db: Session = Depends(get_db)):
    try:
        books = db.query(model.Book).all()
        return books
    except Exception as e:
        print(f"❌ DATABASE ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/books/{book_id}")
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(model.Book).filter(model.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book
@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(model.Book).filter(model.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if os.path.exists(book.file_path):
        os.remove(book.file_path)
    db.delete(book)
    db.commit()
    return {"message": "Book deleted successfully"}

@app.post("/upload")
async def upload_book(
    title: str, 
    description: str, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    os.makedirs("upload", exist_ok=True)
    
   
    safe_title = "".join(x for x in title if x.isalnum() or x in "._- ")
    file_name = f"{str(uuid.uuid4())}_{safe_title}.pdf"
    file_path = os.path.join("upload", file_name)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    new_book = model.Book(title=title, file_path=file_path, description=description)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
        
    return {"message": "Book uploaded successfully", "book_id": new_book.id}

@app.get("/books/{book_id}/extract")
def extract_book_text(
    book_id: int, 
    skip: int = 0,    
    limit: int = 5,   
    db: Session = Depends(get_db)
):
    # 1. Fetch from DB
    book = db.query(model.Book).filter(model.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # 2. Safety Check (Is the file actually on the disk?)
    if not os.path.exists(book.file_path):
        print(f"❌ FILE NOT FOUND AT: {os.path.abspath(book.file_path)}")
        raise HTTPException(status_code=500, detail=f"PDF file missing at {book.file_path}")

    # 3. Processing (Notice 'try' is NOT inside the 'if' anymore)
    try:
        print(f"📄 Extracting pages {skip} to {skip + limit}...")
        result = extract_text(book.file_path, start_page=skip, end_page=skip + limit)
        
        # Clean the text
        clean_text = result["content"].replace(book.title, "")
        cleaned_content = re.sub(r'[ \t]+', ' ', clean_text).strip()

        print("🧠 Calling Gemini for translation and dictionary...")
        # ai_response = {"full_translation": "...", "word_map": {...}}
        ai_response = translate_to_amharic(cleaned_content)

        # 4. Final Return
        return {
            "title": book.title,
            "original_text": cleaned_content,
            "full_translation": ai_response.get("full_translation"),
            "word_dictionary": ai_response.get("word_map"),
            "coordinate_map": result["word_map"],
            "total_pages": result["total_pages"],
            "page_range": f"{skip + 1} - {skip + limit}"
        }

    except Exception as e:
        print(f"🔥 EXTRACTION/TRANSLATION ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Anbibu Error: {str(e)}")

    # try:
    #     print(f"📄 Extracting pages {skip} to {skip + limit}...")
    #     result = extract_text(book.file_path, start_page=skip, end_page=skip + limit)
        
    #     clean_text = result["content"].replace(book.title, "")
    #     cleaned_content = re.sub(r'[ \t]+', ' ', clean_text).strip()

    #     print("🧠 Calling Gemini for Amharic translation...")
    #     amharic_text = translate_to_amharic(cleaned_content)

    #     return {
    #         "title": book.title,
    #         "original_text": cleaned_content,
    #         "translated_text": amharic_text, 
    #         "word_map": result["word_map"],
    #         "total_pages": result["total_pages"],
    #         "page_range": f"{skip + 1} - {skip + limit}"
    #     }
    
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)



