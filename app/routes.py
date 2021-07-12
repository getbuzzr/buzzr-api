from fastapi import APIRouter
import json
from routers import users, departments, favorites, addresses, products, categories, orders, admin, addresses, search, riders, coupons, tags, recipes
from utils import get_parameter_from_ssm
from caching import redis_client, REDIS_TTL
from schemas.OpeningHoursSchema import OpeningHoursSchemaOut
api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(
    departments.router, prefix="/departments", tags=["departments"])
api_router.include_router(
    favorites.router, prefix="/favorites", tags=["favorites"])
api_router.include_router(
    categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(
    products.router, prefix="/products", tags=["products"])
api_router.include_router(
    orders.router, prefix="/orders", tags=["orders"])
api_router.include_router(
    admin.router, prefix="/admin", tags=["admin"])
api_router.include_router(
    addresses.router, prefix="/addresses", tags=["addresses"])
api_router.include_router(
    search.router, prefix="/search", tags=["search"])
api_router.include_router(
    riders.router, prefix="/riders", tags=["riders"])
api_router.include_router(
    coupons.router, prefix="/coupons", tags=["coupons"])
api_router.include_router(
    tags.router, prefix="/tags", tags=["tags"])
api_router.include_router(
    recipes.router, prefix="/recipes", tags=["recipes"])

@api_router.get("/")
async def health_check():
    return {"message": "success"}


@api_router.get("/opening_hours",response_model=OpeningHoursSchemaOut)
def get_opening_hours():
    try:
        opening_hours = json.loads(
            redis_client.get(f"opening_hours").decode("utf-8"))
    except:
        opening_hours = json.loads(get_parameter_from_ssm("opening_hours"))
        redis_client.set(
            "opening_hours", json.dumps(opening_hours), 3600)
    return opening_hours
