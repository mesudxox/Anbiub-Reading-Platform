from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from book_db import engine, get_db, SessionLocal
from sqlalchemy.orm import Session
import model
from fastapi import UploadFile, File, Depends
import os
import uuid
import shutil


model.Base.metadata.create_all(bind=engine)

app=FastAPI(title="Anbibu Reading Platform")
app.add_middleware(CORSMiddleware, 
                   allow_origins=["*"],
                   allow_methods=["*"]
                   )

@app.get("/")
def display():
    return "we have created a container"

@app.post("/upload")
async def upload_book(
    title: str, 
    description: str, 
    file: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    # 1. Ensure directory exists
    os.makedirs("upload", exist_ok=True)
    
    # 2. Generate a safe, string-based filename
    # We use .replace to make sure the title doesn't have weird characters
    safe_title = "".join(x for x in title if x.isalnum() or x in "._- ")
    file_name = f"{str(uuid.uuid4())}_{safe_title}.pdf"
    file_path = os.path.join("upload", file_name)
    
    # 3. Save the file using shutil (The 'Advanced' way)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 4. Save to Database
    new_book = model.Book(title=title, file_path=file_path, description=description)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    
    # NOTE: NO db.close() here! Depends(get_db) handles it.
    
    return {"message": "Book uploaded successfully", "book_id": new_book.id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)



