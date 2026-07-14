from fastapi import APIRouter, Depends
from backend.admin.security.authorization import requires_permission

router = APIRouter()

@router.get("/kpis")
def get_dashboard_kpis(admin: dict = Depends(requires_permission("dashboard.view"))):
    # Mock aggregated KPIs. In a real scenario, this aggregates from user count, payments, etc.
    return {
        "success": True,
        "data": {
            "dau": 1250,
            "wau": 8400,
            "mau": 24000,
            "mrr": 5400.0,
            "premium_users": 540,
            "ai_cost_today": 12.50
        }
    }
