import httpx
import os
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://www.virustotal.com/api/v3"

def _get_headers():
    VT_API_KEY = os.getenv("VT_API_KEY", "")
    if not VT_API_KEY:
        raise ValueError("VT_API_KEY is not set in environment or .env file.")
    return {
        "x-apikey": VT_API_KEY,
        "accept": "application/json"
    }

async def fetch_vt_data(identifier: str, type: str):
    """
    type: 'domain', 'ip', 'hash'
    """
    endpoint = ""
    if type == "domain":
        endpoint = f"/domains/{identifier}"
    elif type == "ip":
        endpoint = f"/ip_addresses/{identifier}"
    elif type == "hash":
        endpoint = f"/files/{identifier}"
    else:
        raise ValueError(f"Unknown type: {type}")

    url = f"{BASE_URL}{endpoint}"
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=_get_headers())
        except ValueError as e:
            raise HTTPException(status_code=500, detail=str(e))
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Request error: {str(e)}")
            
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            raise HTTPException(status_code=429, detail="VirusTotal API Rate Limit Exceeded.")
        elif response.status_code == 404:
            raise HTTPException(status_code=404, detail="Resource not found on VirusTotal.")
        else:
            raise HTTPException(status_code=response.status_code, detail=f"Error fetching from VirusTotal: {response.text}")
