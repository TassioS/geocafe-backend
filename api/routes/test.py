from fastapi import APIRouter
test_router = APIRouter()

@test_router.get("/")
async def home():
    return Response(status_code=200, content="Teste funcionando")