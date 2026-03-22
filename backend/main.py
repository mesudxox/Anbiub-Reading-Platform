from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from book_db import engine
import model

model.Base.metadata.create_all(bind=engine)

app=FastAPI(title="Anbibu Reading Platform")
app.add_middleware(CORSMiddleware, 
                   allow_origins=["*"],
                   allow_methods=["*"]
                   )

@app.get("/")
def display():
    return "we have created a container"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)



