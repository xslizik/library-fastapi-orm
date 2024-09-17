from fastapi import status, HTTPException, APIRouter
from ..models import Instance, Publication
from ..schemas import InstanceRequest, InstanceResponse
from ..database import SessionLocal

instances_router = APIRouter(tags=['instances_router'])

@instances_router.post("/instances", response_model=InstanceResponse, status_code=status.HTTP_201_CREATED)
async def instanceCreate(new_instance: InstanceRequest):
    db = SessionLocal()
    db_item = db.query(Publication).filter(Publication.id == new_instance.publication_id).first()
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    db_item = db.query(Instance).filter(Instance.id == new_instance.id).first()
    if db_item is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT)

    instance = Instance(
        id=new_instance.id,
        type=new_instance.type,
        publisher=new_instance.publisher,
        year=new_instance.year,
        status=new_instance.status,
        publication_id=new_instance.publication_id
    )

    db.add(instance)
    db.commit()

    if instance.created_at:
       return instance
    else:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@instances_router.get("/instances/{instance_id}", response_model=InstanceResponse)
async def instanceDetail(instance_id: str):
    db = SessionLocal()
    db_item = db.query(Instance).filter(Instance.id==instance_id).first()
    if db_item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return db_item

@instances_router.delete("/instances/{instance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def instanceDelete(instance_id: str):
    db = SessionLocal()
    db_item = db.query(Instance).filter(Instance.id==instance_id).first()

    if db_item is not None:
        db.delete(db_item)
        db.commit()

    return

@instances_router.patch("/instances/{instance_id}", response_model=InstanceResponse)
async def instanceUpdate(instance_id: str, instance_patch : InstanceRequest):
    db = SessionLocal()
    instance = db.query(Instance).filter(Instance.id==instance_id).first()
    if instance is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if instance_patch.publication_id:
        db_item = db.query(Publication).filter(Publication.id==instance_patch.publication_id).first()
        if db_item is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    if instance_patch.type:
        instance.type = instance_patch.type
    if instance_patch.publisher:
        instance.publisher = instance_patch.publisher
    if instance_patch.year:
        instance.year = instance_patch.year
    if instance_patch.status:
        instance.status = instance_patch.status
    if instance_patch.publication_id:
        instance.publication_id = instance_patch.publication_id

    db.commit()

    if instance.created_at:
       return instance
    else:
      raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
