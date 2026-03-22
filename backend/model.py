from sqlalchemy import Integer, String, Column
from book_db import Base

class Book(Base):
    __tablename__="books"
    id=Column(Integer, primary_key=True, index=True)
    title=Column(String(500), index=True)
    file_path=Column(String(500))
    description=Column(String(500))