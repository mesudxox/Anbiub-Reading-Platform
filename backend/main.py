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


model.Base.metadata.create_all(bind=engine)

app=FastAPI(title="Anbibu Reading Platform")
app.add_middleware(CORSMiddleware, 
                   allow_origins=["*"],
                   allow_methods=["*"]
                   )

@app.get("/books")
def list_of_books(db: Session = Depends(get_db)):
    books = db.query(model.Book).all()
    return books

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
    book = db.query(model.Book).filter(model.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    try:
        
        result = extract_text(book.file_path, start_page=skip, end_page=skip + limit)
        
        return {
            "title": book.title,
            "page_range": f"Showing pages {skip} to {skip + limit}",
            "text": result["content"],      
            "word_map": result["word_map"], 
            "total_pages": result["total_pages"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)



