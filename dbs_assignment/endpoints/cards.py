from fastapi import status, HTTPException, APIRouter
from ..models import Card, User
from ..schemas import CardRequest, CardResponse, CardPatch
from ..database import SessionLocal

cards_router = APIRouter(tags=['cards_router'])

@cards_router.post("/cards", response_model=CardResponse, status_code=status.HTTP_201_CREATED)
async def cardCreate(new_card: CardRequest):
    db = SessionLocal()
    db_item = db.query(User).filter(User.id == new_card.user_id).first()
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)

    db_item = db.query(Card).filter(Card.user_id == new_card.user_id).first()
    if db_item is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    card = Card(
        id=new_card.id,
        user_id=new_card.user_id,
        magstripe=new_card.magstripe,
        status=new_card.status
    )

    db.add(card)
    db.commit()

    if card.created_at:
       return card
    else:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@cards_router.get("/cards/{card_id}", response_model=CardResponse)
async def cardDetail(card_id: str):
    db = SessionLocal()
    db_item = db.query(Card).filter(Card.id==card_id).first()
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if db_item.created_at:
       return db_item
    else:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@cards_router.delete("/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cardDelete(card_id: str):
    db = SessionLocal()
    db_item = db.query(Card).filter(Card.id==card_id).first()
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if db_item is not None:
        db.delete(db_item)
        db.commit()

    return

@cards_router.patch("/cards/{card_id}", response_model=CardResponse)
async def cardUpdate(card_id: str, card_patch : CardPatch):
    db = SessionLocal()
    card = db.query(Card).filter(Card.id == card_id).first()
    if card is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if card_patch.user_id:
        db_item = db.query(User).filter(User.id==card_patch.user_id).first()
        if db_item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    db_item = db.query(Card).filter(Card.user_id == card_patch.user_id).first()
    if db_item is not None and card_id != db_item.id:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    if card_patch.status:
        card.status = card_patch.status
    if card_patch.user_id:
        card.user_id = card_patch.user_id
    db.commit()

    if card.created_at:
       return card
    else:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
