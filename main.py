from fastapi import FastAPI
from fastapi import Response
from fastapi.middleware.cors import CORSMiddleware

from api.routes.field import field_router
from api.routes.map import map_router
from api.routes.note import note_router
from api.routes.user import user_router

app = FastAPI(title="Tortoise ORM FastAPI example")
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user_router, prefix='/user')
app.include_router(field_router, prefix='/field')
app.include_router(map_router, prefix='/map')
app.include_router(note_router, prefix='/note')


@app.get("/")
async def home():
    return Response(status_code=200, content="Backend service up.")
