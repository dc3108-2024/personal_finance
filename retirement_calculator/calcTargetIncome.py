def calculate_inflation_adjusted_income(targetYearlyIncome, cpi, yearsToRetire):
    """
    Calculate inflation adjusted target yearly income level at retirement.

    Parameters:
    personal (object): An object containing personal financial details.
    assumptions (object): An object containing financial assumptions.

    Returns:
    float: Inflation adjusted target yearly income level at retirement.
    """
    target_yearly_inf_adjusted = targetYearlyIncome * ((1 + cpi) ** yearsToRetire)
    return target_yearly_inf_adjusted