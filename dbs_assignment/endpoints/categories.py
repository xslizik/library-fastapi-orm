from fastapi import status, HTTPException, APIRouter
from sqlalchemy import or_
from ..models import Category
from ..schemas import CategoryRequest, CategoryResponse
from ..database import SessionLocal

categories_router = APIRouter(tags=['categories_router'])

@categories_router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def categoryCreate(new_category: CategoryRequest):
    db = SessionLocal()
    db_item = db.query(Category).filter(
        or_(
        Category.name == new_category.name,
        Category.id == new_category.id)).first()
    if db_item is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    category = Category(
        id=new_category.id,
        name=new_category.name
    )

    db.add(category)
    db.commit()

    if category.created_at:
       return category
    else:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@categories_router.get("/categories/{category_id}", response_model=CategoryResponse)
async def categoryDetail(category_id: str):
    db = SessionLocal()
    db_item = db.query(Category).filter(Category.id==category_id).first()
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return db_item

@categories_router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def categoryDelete(category_id: str):
    db = SessionLocal()
    db_item = db.query(Category).filter(Category.id==category_id).first()

    if db_item is not None:
        db.delete(db_item)
        db.commit()

    return

@categories_router.patch("/categories/{category_id}", response_model=CategoryResponse)
async def categoryUpdate(category_id: str, category_patch : CategoryRequest):
    db = SessionLocal()
    db_item = db.query(Category).filter(Category.name==category_patch.name).first()
    if db_item is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    db_item = db.query(Category).filter(Category.id==category_id).first()
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    db_item.name = category_patch.name
    db.commit()

    if db_item.created_at:
       return db_item
    else:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
