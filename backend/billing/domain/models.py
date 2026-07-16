from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List
from enum import Enum

class SubscriptionStatus(Enum):
    TRIAL = "TRIAL"
    ACTIVE = "ACTIVE"
    PAST_DUE = "PAST_DUE"
    CANCELED = "CANCELED"
    PAUSED = "PAUSED"

class Currency(Enum):
    USD = "USD"
    TRY = "TRY"
    EUR = "EUR"

@dataclass(frozen=True)
class Money:
    amount: int # Stored in smallest unit (e.g. cents)
    currency: Currency

@dataclass(frozen=True)
class SubscriptionPlan:
    plan_id: str
    name: str
    price: Money
    billing_cycle: str # monthly, yearly
    features: List[str]

@dataclass(frozen=True)
class Subscription:
    id: str
    user_id: str
    plan: SubscriptionPlan
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    cancel_at_period_end: bool
