
from fastapi import FastAPI
from app.database import Base, engine
from app.routers.contact_routers import router as r1
from app.routers.public_grievance_routers import router as r2
from app.routers.webhooks import router as r3
from app.routers.user_routers import router as r4
from app.routers.rbac import router as r5
from fastapi.middleware.cors import CORSMiddleware
from app.settings.config import settings


Base.metadata.create_all(bind = engine)

app = FastAPI(
    title="Anand Nagar Website Backend API",
    version="1.0.0",
    description="Backend APIs for Anand Nagar Website"
)

FRONTEND_URL = settings.FRONTEND_URL.rstrip("/")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
     FRONTEND_URL
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {
        "message": "Anand Nagar Website Backend Running",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


app.include_router(router=r1, prefix='/contact', tags=["Contact Form"])
app.include_router(router=r2, prefix='/publicgrievance', tags=["Public Grievance Form"])
app.include_router(router=r3, prefix="/clerk", tags=["Webhooks"])
app.include_router(router=r4, prefix="/user", tags = ["Users"])
app.include_router(router=r5, prefix="/api", tags=["RBAC"])
