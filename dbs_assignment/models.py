import uuid
import random
from datetime import timedelta
from typing import List
from sqlalchemy import DateTime, String, ForeignKey, Table, Integer
from sqlalchemy.sql import func
from sqlalchemy.sql.schema import Column
from sqlalchemy.orm import relationship
from .database import Base, engine
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

card_statuses = ['active', 'expired', 'inactive']
CardStatusEnum = ENUM(*card_statuses, name='card_status', create_type=False)
CardStatusEnum.create(bind=engine, checkfirst=True)

instance_types = ['physical', 'ebook', 'audiobook']
InstanceTypeEnum = ENUM(*instance_types, name='instance_type', create_type=False)
InstanceTypeEnum.create(bind=engine, checkfirst=True)

instance_statuses = [ 'available', 'reserved' ]
InstanceStatusEnum = ENUM(*instance_statuses, name='instance_status', create_type=False)
InstanceStatusEnum.create(bind=engine, checkfirst=True)

rental_statuses = [ 'active', 'returned', 'overdue' ]
RentalStatusEnum = ENUM(*rental_statuses, name='rental_status', create_type=False)
RentalStatusEnum.create(bind=engine, checkfirst=True)

random.seed(12345)

class Entity():
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

class User(Base, Entity):
    __tablename__ = 'users'
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    birth_date = Column(DateTime(timezone=True), nullable=False)
    personal_identificator = Column(String, nullable=False)

    # USER CAN HAVE MANY CARDS
    cards : Mapped[List["Card"]] = relationship()
    # USER CAN HAVE MANY RENTALS
    rentals : Mapped[List["Rental"]] = relationship()
    # USER CAN HAVE MANY RESERVATIONS
    reservations : Mapped[List["Reservation"]] = relationship()

class Card(Base, Entity):
    __tablename__ = 'cards'
    user_id : Mapped[str] = mapped_column(ForeignKey("users.id"))
    magstripe = Column(String(length=20), nullable=False)
    status = Column(CardStatusEnum, nullable=False)

publications_authors = Table('publications_authors', Base.metadata,
    Column('publication_id', String, ForeignKey('publications.id')),
    Column('author_id', String, ForeignKey('authors.id'))
)
publications_categories = Table('publications_categories', Base.metadata,
    Column('publication_id', String, ForeignKey('publications.id')),
    Column('category_id', String, ForeignKey('categories.id'))
)

class Publication(Base, Entity):
    __tablename__ = 'publications'
    title = Column(String, nullable=False)

    # MANY PUBLICATIONS CAN HAVE MANY AUTHORS
    authors : Mapped[List["Author"]] = relationship(secondary=publications_authors)
    # MANY PUBLICATIONS CAN HAVE MANY CATEGORIES"
    categories: Mapped[List["Category"]] = relationship(secondary=publications_categories)

    # PUBLICATION CAN HAVE MANY INSTANCES
    instances : Mapped[List["Instance"]] = relationship(cascade="delete, delete-orphan")

    # PUBLICATION CAN HAVE MANY RESERVATIONS
    reservations : Mapped[List["Reservation"]] = relationship(cascade="delete, delete-orphan")

class Category(Base, Entity):
    __tablename__ = 'categories'
    name = Column(String, nullable=False)

    publications: Mapped[List["Publication"]] = relationship(secondary=publications_categories, back_populates="categories")

class Author(Base, Entity):
    __tablename__ = 'authors'
    name = Column(String, nullable=False)
    surname = Column(String, nullable=False)

    publications: Mapped[List["Publication"]] = relationship(secondary=publications_authors, back_populates="authors")

class Instance(Base, Entity):
    __tablename__ = 'instances'
    type = Column(InstanceTypeEnum, nullable=False)
    publisher = Column(String, nullable=False)
    year = Column(Integer, nullable=False)
    status = Column(InstanceStatusEnum, nullable=False)

    publication_id : Mapped[str] = mapped_column(ForeignKey("publications.id"))

    # INSTANCE CAN HAVE MANY RENTAL
    rental: Mapped["Rental"] = relationship(cascade="delete, delete-orphan")

class Rental(Base):
    __tablename__ = 'rentals'
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id : Mapped[String] = mapped_column(ForeignKey("users.id"))
    publication_instance_id : Mapped[String] = mapped_column(ForeignKey("instances.id"))
    duration = Column(Integer, nullable=False)
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True))
    status = Column(RentalStatusEnum, default='active', nullable=False)

    @property
    def end_date(self):
        return self.start_date + timedelta(days=self.duration)

class Reservation(Base):
    __tablename__ = 'reservations'
    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: str(uuid.uuid4()))

    user_id : Mapped[String] = mapped_column(ForeignKey("users.id"))
    publication_id : Mapped[String] = mapped_column(ForeignKey("publications.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
