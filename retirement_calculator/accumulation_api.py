from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import calculateAccumulation
from typing import List, Optional

app = FastAPI()

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

@app.post("/calculate_accumulation")
def calculate_accumulation_endpoint(request: AccumulationRequest):
    #try:
        result = calculateAccumulation.calculate_yearly_buildup(
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