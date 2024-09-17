from fastapi import status, HTTPException, APIRouter
from ..models import Reservation, User, Publication
from ..schemas import ReservationRequest, ReservationResponse
from ..database import SessionLocal

reservations_router = APIRouter(tags=['reservations_router'])

@reservations_router.post("/reservations", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED)
async def reservationCreate(new_reservation: ReservationRequest):
    db = SessionLocal()
    db_item = db.query(Reservation).filter(Reservation.id == new_reservation.id).first()
    if db_item is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    db_item = db.query(User).filter(User.id == new_reservation.user_id).first()
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    publication = db.query(Publication).filter(Publication.id == new_reservation.publication_id).first()
    if publication is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    available = False
    if publication.instances:
        for instance in publication.instances:
            if instance.status == "available":
                available = True

    if available:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    reservation = Reservation(
        id=new_reservation.id,
        user_id=new_reservation.user_id,
        publication_id=new_reservation.publication_id,
    )

    db.add(reservation)
    db.commit()

    if reservation.created_at:
       return reservation
    else:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@reservations_router.get("/reservations/{reservation_id}", response_model=ReservationResponse)
async def reservationDetail(reservation_id: str):
    db = SessionLocal()
    db_item = db.query(Reservation).filter(Reservation.id==reservation_id).first()
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return db_item

@reservations_router.delete("/reservations/{reservation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def reservationDelete(reservation_id: str):
    db = SessionLocal()
    db_item = db.query(Reservation).filter(Reservation.id==reservation_id).first()

    if db_item is not None:
        db.delete(db_item)
        db.commit()

    return
