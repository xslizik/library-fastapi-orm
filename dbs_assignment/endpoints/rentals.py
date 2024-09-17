from fastapi import status, HTTPException, APIRouter
from ..models import Rental, User, Publication, Reservation
from ..schemas import RentalRequest, RentalResponse, RentalPatch
from ..database import SessionLocal

rentals_router = APIRouter(tags=['rentals_router'])

@rentals_router.post("/rentals", response_model=RentalResponse, status_code=status.HTTP_201_CREATED)
async def rentalCreate(new_rental: RentalRequest):
    db = SessionLocal()
    db_item = db.query(Rental).filter(Rental.id == new_rental.id).first()
    if db_item is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    user = db.query(User).filter(User.id == new_rental.user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    publication = db.query(Publication).filter(Publication.id == new_rental.publication_id).first()
    if publication is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    available_instance = None
    if publication.instances:
        for instance in publication.instances:
            if instance.status == "available":
                available_instance = instance
                break

    if not available_instance:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    reservation = db.query(Reservation).filter(Reservation.publication_id == new_rental.publication_id).order_by(
        Reservation.created_at.asc()).first()

    if reservation is not None:
        if reservation.user_id != new_rental.user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    rental = Rental(
        id=new_rental.id,
        user_id=new_rental.user_id,
        publication_instance_id=available_instance.id,
        duration=new_rental.duration
    )

    available_instance.status = "reserved"

    db.add(rental)
    db.commit()

    if rental.start_date:
       return rental
    else:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@rentals_router.get("/rentals/{rental_id}", response_model=RentalResponse)
async def rentalDetail(rental_id: str):
    db = SessionLocal()
    db_item = db.query(Rental).filter(Rental.id==rental_id).first()
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return db_item

@rentals_router.patch("/rentals/{rental_id}", response_model=RentalResponse)
async def rentalUpdate(rental_id: str, rental_patch : RentalPatch):
    db = SessionLocal()
    rental = db.query(Rental).filter(Rental.id==rental_id).first()
    if rental is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    rental.duration = rental_patch.duration
    db.commit()

    if rental.start_date:
       return rental
    else:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
