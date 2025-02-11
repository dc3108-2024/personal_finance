import numpy as np
import numpy_financial as npf

def calculate_npv(annuity_list, discount_rate):
    """
    Calculates the Net Present Value (NPV) of annuity payments using NumPy.

    :param annuity_list: List of dictionaries with "amount" as annuity payments.
    :param discount_rate: Post-retirement rate of return (savingsRoR).
    :return: Present value of all annuity payments.
    """
    # Extract the annuity amounts into a NumPy array
    cash_flows = np.array([payment["amount"] for payment in annuity_list])

    # Use np.npv() to calculate the present value of all future cash flows
    npv = npf.npv(discount_rate, cash_flows)

    return npv


