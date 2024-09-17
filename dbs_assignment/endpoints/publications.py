from fastapi import status, HTTPException, APIRouter
from sqlalchemy import or_
from ..models import Publication, Author, Category
from ..schemas import PublicationRequest, PublicationResponse
from ..database import SessionLocal

publications_router = APIRouter(tags=['publications_router'])

@publications_router.post("/publications", status_code=status.HTTP_201_CREATED, response_model=PublicationResponse)
async def publicationCreate(requested_publication: PublicationRequest):
    db = SessionLocal()
    db_item = db.query(Publication).filter(
            Publication.id == requested_publication.id).first()
    if db_item:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    if requested_publication.authors:
        existing_authors = db.query(Author).filter(or_(*(Author.name == author['name'] and Author.surname == author['surname'] for author in requested_publication.authors))).all()
        if len(existing_authors) < len(requested_publication.authors):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    if requested_publication.categories:
        existing_categories = db.query(Category).filter(or_(*(Category.name == category for category in requested_publication.categories))).all()
        if len(existing_categories) < len(requested_publication.categories):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    new_publication = Publication(
        id=requested_publication.id,
        title=requested_publication.title,
    )

    db.add(new_publication)
    db.commit()

    new_publication.authors = existing_authors
    new_publication.categories = existing_categories

    db.commit()

    authors = []
    if existing_authors:
        for author in existing_authors:
            authors.append({"name" : author.name, "surname" : author.surname})

    categories = []
    if existing_categories:
        for category in existing_categories:
            categories.append(category.name)

    result = {
        "id" : new_publication.id,
        "title" : new_publication.title,
        "authors" : authors,
        "categories" : categories,
        "created_at" : new_publication.created_at,
        "updated_at" : new_publication.updated_at
    }

    return result

@publications_router.get("/publications/{publication_id}", response_model=PublicationResponse)
async def publicationDetail(publication_id: str):
    db = SessionLocal()
    db_item = db.query(Publication).filter(Publication.id==publication_id).first()
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    authors = []
    if db_item.authors:
        for author in db_item.authors:
            authors.append({"name" : author.name, "surname" : author.surname})

    categories = []
    if db_item.categories:
        for category in db_item.categories:
            categories.append(category.name)

    result = {
        "id" : db_item.id,
        "title" : db_item.title,
        "authors" : authors,
        "categories" : categories,
        "created_at" : db_item.created_at,
        "updated_at" : db_item.updated_at
    }

    return result


@publications_router.delete("/publications/{publication_id}", status_code=status.HTTP_204_NO_CONTENT)
async def publicationDelete(publication_id: str):
    db = SessionLocal()
    db_item = db.query(Publication).filter(Publication.id==publication_id).first()

    if db_item is not None:
        db.delete(db_item)
        db.commit()

    return

@publications_router.patch("/publications/{publication_id}", response_model=PublicationResponse)
async def publicationUpdate(publication_id: str, publication_patch : PublicationRequest):
    db = SessionLocal()
    publication = db.query(Publication).filter(Publication.id==publication_id).first()
    if publication is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    existing_authors = existing_categories = []

    if publication_patch.authors:
        existing_authors = db.query(Author).filter(or_(*(Author.name == author['name'] and Author.surname == author['surname'] for author in publication_patch.authors))).all()
        if len(existing_authors) < len(publication_patch.authors):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    if publication_patch.categories:
        existing_categories = db.query(Category).filter(or_(*(Category.name == category for category in publication_patch.categories))).all()
        if len(existing_categories) < len(publication_patch.categories):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    publication.title = publication_patch.title
    publication.authors = existing_authors
    publication.categories = existing_categories

    authors = []
    if publication_patch.authors:
        for author in existing_authors:
            authors.append({"name" : author.name, "surname" : author.surname})

    categories = []
    if publication_patch.categories:
        for category in existing_categories:
            categories.append(category.name)

    db.commit()

    result = {
            "id" : publication_id,
            "title" : publication.title,
            "authors" : authors,
            "categories" : categories,
            "created_at" : publication.created_at,
            "updated_at" : publication.updated_at
        }

    return result
