from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
import uvicorn
from functions.calculateAccumulation import calculate_yearly_buildup
from typing import List, Optional


router = APIRouter()

class AccumulationRequest(BaseModel):
    initialInvestment: float
    cpi: float
    rateofReturn: float
    expenseRatio: float
    yearstoRetire : int
    monthlyContribution : float

class Accumulation(BaseModel):
    year: int 
    investedPrincipal: float
    totalBalanceAfterExpenses : float
    returnNetofExpenses : float


class Outputs(BaseModel):
    yearlyBuildup: Optional[List[Accumulation]]

@router.post("/calculate_accumulation", response_model = Outputs)
def calculate_accumulation_endpoint(request: AccumulationRequest):
    #try:
        result = calculate_yearly_buildup(
            request.initialInvestment,
            request.cpi,
            request.rateofReturn,
            request.expenseRatio,
            request.yearstoRetire,
            request.monthlyContribution
        )
        response = Outputs(
        yearlyBuildup = result)
        return response
    #except Exception as e:
    #   raise HTTPException(status_code=400, detail=str(e))

#if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port=8000)