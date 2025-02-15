from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
from typing import Optional
from functions.optimiseContribution import optimise_contribution
from functions.calculateAnnuity import calculate_annuity_payments
from functions.calculateNPV import calculate_npv
from functions.calcTargetIncome import calculate_inflation_adjusted_income

router = APIRouter()

class ContributionRequest(BaseModel):
    currentSavings: float
    yearsToRetire: int
    annualRateofReturn: float
    expenseRatio: float
    targetYearlyIncome: float
    yearsPostRetirement: int
    cpi : float
    savingsRoR: float

class Outputs(BaseModel):
    monthlyContribution: float

class AnnuityPayment(BaseModel):
    year: int
    amount: float



@router.post("/optimize_contribution", response_model=Outputs)
def optimize_contribution(request: ContributionRequest):
    try:
        # Assuming optimiseContribution.py has a function called `calculate_optimal_contribution`
        inflationAdjustedTargetIncome = calculate_inflation_adjusted_income(request.targetYearlyIncome,request.cpi,request.yearsPostRetirement)
        annuity = calculate_annuity_payments(inflationAdjustedTargetIncome, request.yearsPostRetirement, request.cpi)
        annuity_payments = [AnnuityPayment(**payment) for payment in annuity]


        npv = calculate_npv(annuity_payments, request.savingsRoR)
        realRateOfReturn = (((1+request.annualRateofReturn)/(1+request.cpi))-1)
        
        response = Outputs(
        monthlyContribution = optimise_contribution(request.currentSavings,request.yearsToRetire,realRateOfReturn, request.expenseRatio, npv))
        
        return response
    except ImportError:
        raise HTTPException(status_code=500, detail="Optimization module not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))