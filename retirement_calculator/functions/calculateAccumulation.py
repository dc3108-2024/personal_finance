def calculate_yearly_buildup(initialInvestment, cpi, rateofReturn, expenseRatio, yearstoRetire, monthlyContribution):
    """
    Calculates annuity payments for each year of retirement, adjusting for inflation.
    
    :param target_monthly_income: Desired monthly income in the first year of retirement.
    :param years_post_retirement: Number of years the annuity will be paid.
    :param cpi: Annual inflation rate (Consumer Price Index).
    :return: List of annuity payments year by year.
    """
    yearly_buildup = []

    total_savings = initialInvestment

    realRateofReturn = (((1+rateofReturn)/(1+cpi))-1)

    for year in range(1, yearstoRetire + 1):

        initialBalance = total_savings
        totalSavings =  (total_savings*(1 + realRateofReturn - expenseRatio))
        totalBalanceAfterExpenses = totalSavings + (((monthlyContribution*12)/2)*(realRateofReturn - expenseRatio)) + (monthlyContribution*12)
        returnNetofExpenses = totalBalanceAfterExpenses - initialBalance
        # Store the result as a dictionary (or tuple)
        yearly_buildup.append({"year": year, "investedPrincipal": initialBalance, "totalBalanceAfterExpenses" : totalBalanceAfterExpenses, "returnNetofExpenses" :returnNetofExpenses})
        total_savings = totalBalanceAfterExpenses
    
    return yearly_buildup