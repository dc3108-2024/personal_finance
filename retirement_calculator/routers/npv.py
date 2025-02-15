import string
from fastapi import FastAPI, HTTPException, APIRouter 
from pydantic import BaseModel
from typing import List, Optional
from functions.calculateNPV import calculate_npv

router = APIRouter()


class Cash_Flow(BaseModel):
    year: int
    amount: float
    

class NPVRequest(BaseModel):
    annuity_payments: Optional[List[Cash_Flow]]
    rate: float

class Outputs(BaseModel):
    npv: float

@router.post("/calculate-npv", response_model = Outputs)
def calculate_npv_endpoint(request: NPVRequest):
    npv = calculate_npv(request.annuity_payments, request.rate)
    return Outputs(npv = npv)

#if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port=8000)