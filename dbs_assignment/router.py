from fastapi import APIRouter

from dbs_assignment.endpoints.categories import categories_router
from dbs_assignment.endpoints.authors import authors_router
from dbs_assignment.endpoints.publications import publications_router
from dbs_assignment.endpoints.instances import instances_router
from dbs_assignment.endpoints.users import users_router
from dbs_assignment.endpoints.cards import cards_router
from dbs_assignment.endpoints.rentals import rentals_router
from dbs_assignment.endpoints.reservations import reservations_router

router = APIRouter()

router.include_router(categories_router, tags=["categories_router"])
router.include_router(authors_router, tags=["authors_router"])
router.include_router(publications_router, tags=["publications_router"])
router.include_router(instances_router, tags=["instances_router"])
router.include_router(users_router, tags=["users_router"])
router.include_router(cards_router, tags=["cards_router"])
router.include_router(rentals_router, tags=["rentals_router"])
router.include_router(reservations_router, tags=["reservations_router"])