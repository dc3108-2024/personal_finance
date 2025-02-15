import string
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from scipy.optimize import minimize_scalar
import os
from dotenv import load_dotenv
import openai
from openai import OpenAI
import calcTargetIncome



import calculateAnnuity 
import calculateNPV
import calculateAccumulation 
#import optimalContribution

# Create the FastAPI app
app = FastAPI()

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
@app.post("/calculate-retirement-goals", response_model=Outputs)
async def calculate_retirement_goals(inputs: Inputs):
    # Placeholder: Parse inputs
    personal = inputs.personalSituation
    assumptions = inputs.assumptions
    
    # Calculate inflation adjusted target yearly income level @ retirement
    #targetYearlyInfAdjusted = personal.targetYearlyIncome*((1+assumptions.cpi)**(personal.yearstoRetire))

    targetYearlyInfAdjusted = calcTargetIncome.calculate_inflation_adjusted_income(personal.targetYearlyIncome,assumptions.cpi,personal.yearstoRetire)
    annuity_payments = []

    # Calculate inflation adjusted yearly income for each year for the rest of the retirement period
    #annuity_payments = calculateAnnuity.calculate_annuity_payments(targetYearlyInfAdjusted, personal.yearsPostRetirement, assumptions.cpi)

    # Calculate inflation adjusted yearly income for each year for the rest of the retirement period
    annuity_payments_dicts = calculateAnnuity.calculate_annuity_payments(targetYearlyInfAdjusted, personal.yearsPostRetirement, assumptions.cpi)

    # Convert dictionaries to AnnuityPayment objects
    annuity_payments = [AnnuityPayment(**payment) for payment in annuity_payments_dicts]


    # Calculate the NPV of the investment portfolio value at retirement
    npv = calculateNPV.calculate_npv(annuity_payments, assumptions.savingsRoR)

    # Optimise for the periodic contribution needed to reach this NPV


    #monthly_rate = (((1+assumptions.investmentRoR)/(1+assumptions.cpi))-1)/12

    #yearly_contribution = (monthly_contribution*12)

    realRateofReturn = (((1+assumptions.investmentRoR)/(1+assumptions.cpi))-1)

    print(realRateofReturn)

    def calculate_savings(monthly_contribution):
        total_savings = personal.currentInvestmentVal
        for year in range(1, personal.yearstoRetire + 1):
            total_savings = (total_savings*(1 + realRateofReturn - assumptions.expenseRatio))+(((monthly_contribution*12)/2)*(realRateofReturn - assumptions.expenseRatio))+(monthly_contribution*12)
        return total_savings

    # Objective function for optimization
    # Goal: Minimize the difference between total savings and target
    def objective_function(monthly_contribution):
        total_savings = calculate_savings(monthly_contribution)
        return abs(total_savings - npv)  # Minimize this difference

    result = minimize_scalar(objective_function, bounds=(0, 10000), method='bounded')

    monthly_contribution = result.x

    if monthly_contribution > personal.contributionAffordability:
        outcome = "No"
    else:
        outcome = "Yes"
    

    # Calculate yearly buildup towards reirement corpus during the accumulation period

    yearly_buildup = []

    yearly_buildup = calculateAccumulation.calculate_yearly_buildup(personal.currentInvestmentVal, assumptions.cpi, assumptions.investmentRoR, assumptions.expenseRatio, personal.yearstoRetire, monthly_contribution)



    # Generate a summary of the retirement plan using Open AI gpt-4o-mini model

    load_dotenv()

    # Retrieve API Key from Environment
    # Retrieve API Key from Environment
    #openai.api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    #client = OpenAI()

    system_content = f"""
      You are a retirement planner and you help people interpret and summarise retirement goals. 
    """
    diff = (monthly_contribution - personal.contributionAffordability)

    user_content = f"""
    Summarize the retirement plan in simple text in 110 words, without compromising on the details.
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
        #model="o3-mini",
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


