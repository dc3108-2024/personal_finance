import string
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from scipy.optimize import minimize_scalar
import os
from dotenv import load_dotenv
import openai
from openai import OpenAI



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
def calculate_retirement_goals(inputs: Inputs):
    # Placeholder: Parse inputs
    personal = inputs.personalSituation
    assumptions = inputs.assumptions
    
    # Calculate inflation adjusted target yearly income level @ retirement
    targetYearlyInfAdjusted = personal.targetYearlyIncome*((1+assumptions.cpi)**(personal.yearstoRetire))

    annuity_payments = []

    # Calculate inflation adjusted yearly income for each year for the rest of the retirement period
    annuity_payments = calculateAnnuity.calculate_annuity_payments(targetYearlyInfAdjusted, personal.yearsPostRetirement, assumptions.cpi)

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

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_content},
            {
                "role": "user",
                "content": f"""Help summarise the retirement plan in plain text and within 150 words, given the following inputs from user
                current value of investment : {personal.currentInvestmentVal},
                years to retire : {personal.yearstoRetire},
                years post retirement : {personal.yearsPostRetirement},
                target yearly income post retirement : {personal.targetYearlyIncome}
                and the following assumptions the user has made namely,
                fund expense ratio: {assumptions.expenseRatio},
                assumed rate of return on investment : {assumptions.investmentRoR},
                assumed interest on savings post retirement : {assumptions.savingsRoR},
                cpi : {assumptions.cpi}

                The above parameters requires them to:
                make a monthly contribution of : {monthly_contribution},
                which will allow them to have a target savings of {npv}
                that will allow them to reach the target yearly income level factoring in inflation
                note the following and you can make creative reference to the below in the summary plan:
                1. the accumulation period particulars are captured in {yearly_buildup}
                2. the annuity payments post retirement are captured in {annuity_payments}

                While being a little creative is good,  don't change the inputs and the calculated values in the plan.
                Organise the reponse in logical paragraphs please.
                Sound like a seasoned financial advisor while appealing to laypersons in finance.
                
                """
            },
        ],
        temperature=0.5
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

    # Modify your response
    #response = Outputs(
    #    retirementPlanSummary=str(completion.choices[0].message.content),
    #    periodicContributionNeeded=format_currency(monthly_contribution),
    #    accumulationPeriod=[
    #        {
    #            "year": p["year"],
    #            "investedPrincipal": format_currency(p["investedPrincipal"]),
    #            "totalBalanceAfterExpenses": format_currency(p["totalBalanceAfterExpenses"]),
    #            "returnNetofExpenses": format_currency(p["returnNetofExpenses"])
    #        }
    #        for p in yearly_buildup
    #    ],
    #    investmentValueAtRetirement=format_currency(npv),
    #    annuityPayments=[
    #        {"year": p["year"], "amount": format_currency(p["amount"])} for p in annuity_payments
    #    ]
    #)

    return response

# Run the app using: uvicorn filename:app --reload


