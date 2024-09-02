from fastapi import FastAPI
from contextlib import asynccontextmanager
import os
from file_upload import rout


path=os.getcwd()

@asynccontextmanager
async def lifespan_start(app:FastAPI):
    path1=os.path.join(path,'temp')
    if not os.path.exists(path1):
        os.mkdir(path1)
    print("App started")
    
    yield
    
    print("App shutdown")
app=FastAPI(lifespan=lifespan_start)
app.include_router(rout)
