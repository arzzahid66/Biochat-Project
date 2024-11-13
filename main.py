from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi.responses import JSONResponse
from app.api.router import api_router
from starlette.staticfiles import StaticFiles


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
    )

app.include_router(api_router, prefix="/api")

# welcome message
@app.get("/")
def start_app():
    return JSONResponse(content={"message":"Welcome to the Biochat Bot"})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9090)