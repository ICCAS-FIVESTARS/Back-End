from fastapi import FastAPI
from app.api.analyze_router import router as analyze_router

app = FastAPI()

app.include_router(analyze_router.router, prefix="/analyze") 

# FastAPI app entrypoint