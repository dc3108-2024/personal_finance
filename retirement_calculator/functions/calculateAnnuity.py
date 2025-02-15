def calculate_annuity_payments(target_yearly_income, years_post_retirement, cpi):
    """
    Calculates annuity payments for each year of retirement, adjusting for inflation.
    
    :param target_monthly_income: Desired monthly income in the first year of retirement.
    :param years_post_retirement: Number of years the annuity will be paid.
    :param cpi: Annual inflation rate (Consumer Price Index).
    :return: List of annuity payments year by year.
    """
    annuity_payments = []

    for year in range(1, years_post_retirement + 1):
        # Calculate the adjusted annual annuity payment for the given year
        adjusted_payment = target_yearly_income * ((1 + cpi) ** (year - 1))
        
        # Store the result as a dictionary (or tuple)
        annuity_payments.append({"year": year, "amount": adjusted_payment})
    
    return annuity_payments