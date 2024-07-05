# NotifyMe/constants.py
from enum import Enum

class Plans(Enum):
  BASIC_PLAN="BASIC"
  REGULAR_PLAN= "REGULAR"
  STANDARD_PLAN= "STANDARD"
  PREMIUM_PLAN= "PREMIUM"



class PlansDuration(Enum):
  BASIC = 30,
  REGULAR = 90,
  STANDARD = 180,
  PREMIUM = 365





