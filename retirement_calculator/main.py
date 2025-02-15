# main.py
from fastapi import FastAPI
from routers.accumulation import router as accumulation_router
from routers.annuity import router as annuity_router 
from routers.npv import router as npv_router
from routers.retirement import router as retirement_router
from routers.contribution import router as contribution_router 

app = FastAPI()

# Include Routers
app.include_router(accumulation_router, prefix="/accumulation", tags=["Accumulation"])
app.include_router(annuity_router, prefix="/annuity", tags=["Annuity"])
app.include_router(npv_router, prefix="/npv", tags=["NPV"])
app.include_router(contribution_router, prefix="/contribution", tags=["ContributuonNeeded"])
app.include_router(retirement_router, prefix="/retirement", tags=["Retirement"])


@app.get("/")
def read_root():
    return {"message": "Welcome to the Retirement Planner API!"}
