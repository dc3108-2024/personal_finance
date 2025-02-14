import string
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import calculateAnnuity
import calcTargetIncome


app = FastAPI()

class AnnuityRequest(BaseModel):
    targetYearlyIncome: float
    yearsPostRetirement: int
    cpi: float

class AnnuityPayment(BaseModel):
    year: int
    amount: float

class Outputs(BaseModel):
    annuityPayments: Optional[List[AnnuityPayment]]

@app.post("/calculate_annuity", response_model=Outputs)
async def calculate_annuity_endpoint(request: AnnuityRequest):
    #try:
        inflationAdjustedTargetIncome = calcTargetIncome.calculate_inflation_adjusted_income(request.targetYearlyIncome,request.cpi,request.yearsPostRetirement)
        annuity = calculateAnnuity.calculate_annuity_payments(inflationAdjustedTargetIncome, request.yearsPostRetirement, request.cpi)
        response = Outputs(
        annuityPayments = annuity
     )
        return response
    #except Exception as e:
    #    raise HTTPException(status_code=400, detail=str(e))

#if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port=8000)