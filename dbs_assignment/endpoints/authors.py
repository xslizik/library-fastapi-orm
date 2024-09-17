from fastapi import status, HTTPException, APIRouter
from sqlalchemy import or_, and_
from ..models import Author
from ..schemas import AuthorRequest, AuthorResponse, AuthorPatch
from ..database import SessionLocal

authors_router = APIRouter(tags=['authors_router'])

@authors_router.post("/authors", response_model=AuthorResponse, status_code=status.HTTP_201_CREATED)
async def authorCreate(new_author: AuthorRequest):
    db = SessionLocal()
    db_item = db.query(Author).filter(
        or_(
            and_(
                Author.name == new_author.name,
                Author.surname == new_author.surname),
            Author.id == new_author.id)).first()
    if db_item is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    author = Author(
        id=new_author.id,
        name=new_author.name,
        surname=new_author.surname
    )

    db.add(author)
    db.commit()

    if author.name:
       return author
    else:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@authors_router.get("/authors/{author_id}", response_model=AuthorResponse)
async def authorDetail(author_id: str):
    db = SessionLocal()
    db_item = db.query(Author).filter(Author.id==author_id).first()
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return db_item

@authors_router.delete("/authors/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
async def authorDelete(author_id: str):
    db = SessionLocal()
    db_item = db.query(Author).filter(Author.id==author_id).first()

    if db_item is not None:
        db.delete(db_item)
        db.commit()

    return

@authors_router.patch("/authors/{author_id}", response_model=AuthorResponse)
async def authorUpdate(author_id: str, author_patch : AuthorPatch):
    db = SessionLocal()
    author = db.query(Author).filter(Author.id==author_id).first()
    if author is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if author_patch.name:
        author.name = author_patch.name
    if author_patch.surname:
        author.surname = author_patch.surname
    db.commit()

    if author.name:
       return author
    else:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
