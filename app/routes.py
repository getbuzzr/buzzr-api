from fastapi import APIRouter

from routers import users, departments, favorites, addresses, products, categories, orders, admin, addresses, search

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


@api_router.get("/")
async def health_check():
    return {"message": "success"}
