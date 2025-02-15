# routers/__init__.py
from .accumulation import router as accumulation_router
from .annuity import router as annuity_router
from .npv import router as npv_router
from .retirement import router as retirement_router

# Expose them as a list for easy inclusion in FastAPI
all_routers = [
    (accumulation_router, "/accumulation", ["Accumulation"]),
    (annuity_router, "/annuity", ["Annuity"]),
    (npv_router, "/npv", ["NPV"]),
    (retirement_router, "/retirement", ["Retirement"])
]