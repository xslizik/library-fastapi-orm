from fastapi import status, HTTPException, APIRouter
from ..models import User
from ..schemas import UserRequest, UserResponse, UserPatch
from ..database import SessionLocal
from datetime import timezone

users_router = APIRouter(tags=['users_router'])

@users_router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def userCreate(new_user: UserRequest):
    db = SessionLocal()

    db_item = db.query(User).filter(User.id == new_user.id).first()
    if db_item is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)
    db_item = db.query(User).filter(User.email == new_user.email).first()
    if db_item is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    new_user = User(
        id=new_user.id,
        name=new_user.name,
        surname=new_user.surname,
        email=new_user.email,
        birth_date=new_user.birth_date,
        personal_identificator=new_user.personal_identificator
    )

    db.add(new_user)
    db.commit()

    if new_user.created_at:
       return new_user
    else:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@users_router.get("/users/{user_id}")
async def userDetail(user_id: str):
    db = SessionLocal()
    db_item = db.query(User).filter(User.id==user_id).first()
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    birth = db_item.birth_date.astimezone(timezone.utc).strftime('%Y-%m-%d')

    result = {
        "id" : db_item.id,
        "name" : db_item.name,
        "surname" : db_item.surname,
        "email" : db_item.email,
        "birth_date" : birth,
        "personal_identificator" : db_item.personal_identificator,
        "created_at" : db_item.created_at,
        "updated_at" : db_item.updated_at
    }

    if db_item.rentals:
        rentals = []
        for rental in db_item.rentals:
            a = {
                "duration" : rental.duration,
                "id" : rental.id,
                "publication_instance_id" : rental.publication_instance_id,
                "status" : rental.status,
                "user_id" : rental.user_id
            }
            rentals.append(a)
        result["rentals"] = rentals

    if db_item.reservations:
        reservations = []
        for reservation in db_item.reservations:
            b = {
                "id" : reservation.id,
                "publication_id" : reservation.publication_id,
                "user_id" : reservation.user_id,
            }
            reservations.append(b)
        result["reservations"] = reservations

    return result

@users_router.patch("/users/{user_id}")
async def userUpdate(user_id: str, user_patch : UserPatch):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    db_item = db.query(User).filter(User.email==user_patch.email).first()
    if db_item is not None and user_id != db_item.id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    if user_patch.name:
        user.name = user_patch.name
    if user_patch.surname:
        user.surname = user_patch.surname
    if user_patch.email:
        user.email = user_patch.email
    if user_patch.birth_date:
        user.birth_date = user_patch.birth_date
    if user_patch.personal_identificator:
        user.personal_identificator = user_patch.personal_identificator

    db.commit()

    birth = user.birth_date.astimezone(timezone.utc).strftime('%Y-%m-%d')

    result = {
        "id" : user.id,
        "name" : user.name,
        "surname" : user.surname,
        "email" : user.email,
        "birth_date" : birth,
        "personal_identificator" : user.personal_identificator,
    }

    return result
