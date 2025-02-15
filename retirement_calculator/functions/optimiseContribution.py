from scipy.optimize import minimize_scalar

# Function that calculates total savings
def calculate_savings(monthly_contribution, current_savings, years_to_retirement, annual_return_rate, expense_ratio):
    total_savings = current_savings
    for year in range(1, years_to_retirement + 1):
        total_savings = (total_savings * (1 + annual_return_rate - expense_ratio)) + (((monthly_contribution * 12) / 2) * (annual_return_rate - expense_ratio)) + (monthly_contribution * 12)
    return total_savings

# Objective function for optimization
def objective_function(monthly_contribution, current_savings, years_to_retirement, annual_return_rate, expense_ratio, desired_savings):
    total_savings = calculate_savings(monthly_contribution, current_savings, years_to_retirement, annual_return_rate, expense_ratio)
    return abs(total_savings - desired_savings)

# Function to optimize monthly contribution
def optimise_contribution(current_savings, years_to_retirement, annual_return_rate, expense_ratio, desired_savings):
    result = minimize_scalar(objective_function, bounds=(0, 10000), method='bounded', args=(current_savings, years_to_retirement, annual_return_rate, expense_ratio, desired_savings))
    return result.x