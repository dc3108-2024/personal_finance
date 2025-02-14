import string
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import calculateNPV

app = FastAPI()


class Cash_Flow(BaseModel):
    year: int
    amount: float
    

class NPVRequest(BaseModel):
    annuity_payments: Optional[List[Cash_Flow]]
    rate: float

class Outputs(BaseModel):
    npv: float

@app.post("/calculate-npv")
def calculate_npv(request: NPVRequest):
    npv = calculateNPV.calculate_npv(request.annuity_payments, request.rate)
    return Outputs(npv = npv)

#if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port=8000)