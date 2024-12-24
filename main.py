from fastapi import FastAPI
from process import process_router
from rec import rec_router

app = FastAPI()
app.include_router(process_router)
app.include_router(rec_router)