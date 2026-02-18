
from fastapi import APIRouter

router = APIRouter()

@router.get("/agent")
def agent_info():
    return {
        "name": "China West Connector AI",
        "description": "AI advisor for China business, manufacturing sourcing, energy projects, and investment partnerships.",
        "website": "https://www.chinawestconnector.com",
        "api_endpoint": "https://asset-manager--888nv666.replit.app/respond",
        "contact": "info@chinawestconnector.com",
        "tags": [
            "China sourcing",
            "FDI China",
            "manufacturing China",
            "energy projects",
            "China partnerships"
        ]
    }


