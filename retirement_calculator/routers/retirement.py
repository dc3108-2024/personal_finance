import string
from fastapi import FastAPI, HTTPException, APIRouter 
from pydantic import BaseModel
from typing import List, Optional
from scipy.optimize import minimize_scalar
import os
from dotenv import load_dotenv
import openai
from openai import OpenAI
from functions.calcTargetIncome import calculate_inflation_adjusted_income
from functions.optimiseContribution import optimise_contribution



from functions.calculateAnnuity import calculate_annuity_payments 
from functions.calculateNPV import calculate_npv
from functions.calculateAccumulation import calculate_yearly_buildup


router = APIRouter()

# Define input schema
class PersonalSituation(BaseModel):
    currentInvestmentVal: float
    yearstoRetire: int
    yearsPostRetirement: int
    targetYearlyIncome: float
    contributionAffordability: float

class Assumptions(BaseModel):
    cpi: float
    expenseRatio: float
    investmentRoR: float
    savingsRoR: float

class Inputs(BaseModel):
    personalSituation: PersonalSituation
    assumptions: Assumptions

class AnnuityPayment(BaseModel):
    year: int
    amount: float

class AccumulationPeriod(BaseModel):
    year: int
    investedPrincipal: float
    totalBalanceAfterExpenses : float
    returnNetofExpenses : float

class Outputs(BaseModel):
    retirementPlanSummary : str
    periodicContributionNeeded: float
    accumulationPeriod: Optional[List[AccumulationPeriod]]
    investmentValueAtRetirement: float
    annuityPayments: Optional[List[AnnuityPayment]]
    

# API endpoint
@router.post("/calculate-retirement-goals", response_model=Outputs)
async def calculate_retirement_goals(inputs: Inputs):
    # Placeholder: Parse inputs
    personal = inputs.personalSituation
    assumptions = inputs.assumptions
    
    # Calculate inflation adjusted target yearly income level @ retirement
    

    targetYearlyInfAdjusted = calculate_inflation_adjusted_income(personal.targetYearlyIncome,assumptions.cpi,personal.yearstoRetire)
    annuity_payments = []

    # Calculate inflation adjusted yearly income for each year for the rest of the retirement period
    

    # Calculate inflation adjusted yearly income for each year for the rest of the retirement period
    annuity_payments_dicts = calculate_annuity_payments(targetYearlyInfAdjusted, personal.yearsPostRetirement, assumptions.cpi)

    # Convert dictionaries to AnnuityPayment objects
    annuity_payments = [AnnuityPayment(**payment) for payment in annuity_payments_dicts]


    # Calculate the NPV of the investment portfolio value at retirement
    npv = calculate_npv(annuity_payments, assumptions.savingsRoR)

    # Optimise for the periodic contribution needed to reach this NPV

    realRateofReturn = (((1+assumptions.investmentRoR)/(1+assumptions.cpi))-1)
    result = optimise_contribution(personal.currentInvestmentVal, personal.yearstoRetire, realRateofReturn, assumptions.expenseRatio, npv)
    
    monthly_contribution = result

    if monthly_contribution > personal.contributionAffordability:
        outcome = "No"
    else:
        outcome = "Yes"
    

    # Calculate yearly buildup towards reirement corpus during the accumulation period

    yearly_buildup = []

    yearly_buildup = calculate_yearly_buildup(personal.currentInvestmentVal, assumptions.cpi, assumptions.investmentRoR, assumptions.expenseRatio, personal.yearstoRetire, monthly_contribution)



    # Generate a summary of the retirement plan using Open AI gpt-4o-mini model

    load_dotenv()

    # Retrieve API Key from Environment
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


    system_content = f"""
      You are a retirement planner and you help people interpret and summarise retirement goals. 
    """
    diff = (monthly_contribution - personal.contributionAffordability)

    user_content = f"""
    Summarize the retirement plan in simple text in 90 words, without compromising on the details.
    First start with what they need to do to meet their goal and then give them the summary of the plan
    then comment on whether they can afford the monthly contribution.
    Sound very friendly and professional.
    Inputs:
    - Current investment value: {personal.currentInvestmentVal}
    - Years to retire: {personal.yearstoRetire}
    - Years post retirement: {personal.yearsPostRetirement}
    - Target yearly income post retirement: {personal.targetYearlyIncome}
    Assumptions:
    - Fund expense ratio: {assumptions.expenseRatio}
    - Rate of return on investment: {assumptions.investmentRoR}
    - Interest on savings post retirement: {assumptions.savingsRoR}
    - CPI: {assumptions.cpi}
    Calculations:
    - Calculated Monthly contribution need to meet goal: {monthly_contribution}
    - Target savings: {npv}
    - Accumulation period: {yearly_buildup}
    - Annuity payments: {annuity_payments}
    - User's contribution affordability: {personal.contributionAffordability}
    - you need to compare the monthly contribution with the user's contribution affordability
    if {diff} is greater than 0,
        tell the user they cannot afford the monthly contribution
    otherwise,
        tell the user they can afford the monthly contribution
    or if {diff} is really small, tell the user that your contribution affordability just marginally falls short, etc.
    """

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ],
        temperature=0.7
    )
    
    response = Outputs(
         retirementPlanSummary = str(completion.choices[0].message.content),
         periodicContributionNeeded = monthly_contribution,
         accumulationPeriod = yearly_buildup,
         investmentValueAtRetirement = npv,
         annuityPayments = annuity_payments
     )

    def format_currency(value):
        return f"${value:,.2f}"

    
    return response

# Run the app using: uvicorn filename:app --reload


