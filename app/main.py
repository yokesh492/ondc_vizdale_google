from fastapi import FastAPI
from app.api.routes import router as api_router
from app.api.auth import router
from fastapi.middleware.cors import CORSMiddleware
import os 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT",8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
