from fastapi import APIRouter, Query, HTTPException, status
import requests
from datetime import datetime
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

# Define response models for better documentation
class RouteInfo(BaseModel):
    routes: List[str]
    
class GoldDataResponse(BaseModel):
    status: str
    requests_data: Optional[Dict[str, Any]] = None
    form_data: Optional[Dict[str, Any]] = None
    latest_date_data_db: Optional[str] = None
    response: Optional[Dict[str, Any]] = None
    
class CurrencyDataResponse(BaseModel):
    status: str
    new_data: Optional[Dict[str, Any]] = None
    latest_date_data_db: Optional[str] = None

router = APIRouter(
    tags=["Gold and Currency Data"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=RouteInfo, summary="List Available API Routes")
def list_routes():
    """
    Returns a list of available API routes for the gold price prediction service.
    """
    return {
        "routes": [
            "/add-current-data?data=goldus",
            "/add-current-data?data=goldth",
            "/add-current-data?data=currency"
        ]
    }

@router.get("/add-current-data", 
            response_model=Dict[str, Any],
            summary="Fetch and Add Current Gold or Currency Data",
            description="Fetches the latest gold or currency data and adds it to the database if it's newer than existing data.")
def add_current_data(
    data: str = Query(
        ..., 
        description="Type of data to fetch", 
        example="goldus",
        enum=["goldus", "goldth", "currency"]
    )
):
    """
    Fetches the latest gold or currency data and adds it to the database if the data is newer than what already exists.
    
    Parameters:
    - **data**: Type of data to fetch. Options: 
        - `goldus` - Gold prices from US markets
        - `goldth` - Gold prices from Thai markets
        - `currency` - USD to THB currency exchange rate
    
    Returns:
    - If new data is added: Status message and the newly added data
    - If no new data: Status message and the latest data in the database
    """
    try:
        # ==================== START GOLD TH ====================
        if data == "goldth":
            url_addgold_th = "https://34.117.31.73.nip.io/finnomenaGold/create-gold-data/"
            latest_date_data_db = requests.get("https://34.117.31.73.nip.io/finnomenaGold/get-gold-data/?db_choice=0&cache=False&frame=1d", verify=False).json()["data"][-1]["date"]
            response = requests.get("https://www.finnomena.com/fn3/api/gold/trader/history/graph?period=5D&sampling=0&startTimeframe=")
            data = response.json()["data"]
            latest_data = data[-1] if data else {}
            new_date = datetime.strptime(latest_data["createdAt"], "%Y-%m-%dT%H:%M:%SZ").strftime("%d-%m-%y")
            form_data = {
                "db_choice": "0",
                "data": [{
                    "created_at": latest_data["createdAt"],
                    "created_time": latest_data["createdTime"],
                    "price": latest_data["barBuyPrice"],
                    "bar_sell_price": latest_data["barSellPrice"],
                    "bar_price_change": latest_data["barPriceChange"],
                    "ornament_buy_price": latest_data["ornamentBuyPrice"],
                    "ornament_sell_price": latest_data["ornamentSellPrice"],
                    "timestamp": latest_data["timestamp"],
                    "date": new_date,
                }]
            }
            if new_date > latest_date_data_db:
                requests_data = requests.post(url_addgold_th, json=form_data, verify=False).json()
                return {"status": "New data added success", "requests_data" : requests_data}
            else:
                return {"status": "No new data added", "latest_date_data_db": latest_date_data_db, "response": latest_data}
        # ==================== ENDED GOLD TH ====================

        # ==================== START GOLD US ====================
        elif data == "goldus":
            url_addgold_us = "https://34.117.31.73.nip.io/finnomenaGold/create-gold-data/" 
            latest_date_data_db = requests.get("https://34.117.31.73.nip.io/finnomenaGold/get-gold-data/?db_choice=1&cache=False&frame=7d", verify=False).json()["data"][-1]["date"]
            response = requests.get("https://www.finnomena.com/fn3/api/polygon/gold/spot/v2/aggs/ticker/C%3AXAUUSD/range/1/day/2025-03-02/2025-03-09").json()["data"]["results"][-1]
            form_data = {
                "db_choice": "1",
                "data": [{
                    "date": datetime.utcfromtimestamp(response["t"] / 1000).strftime("%d-%m-%y"),
                    "close_price": response["c"],
                    "volume_weight_avg": response["vw"],
                    "timestamp": response["t"],
                    "high_price": response["h"],
                    "low_price": response["l"],
                    "price": response["o"],
                    "volume": response["v"],
                    "num_transactions": response["n"],
                    "created_at": datetime.utcfromtimestamp(response["t"] / 1000).strftime("%Y-%m-%dT%H:%M:%SZ")
                }]
            }
            if latest_date_data_db < form_data["data"][0]["date"]:
                requests_data = requests.post(url_addgold_us, json=form_data, verify=False).json()
                return {"status": "New data added success", "requests_data": requests_data, "form_data": form_data}
            else:
                return {"status": "No new data added", "latest_date_data_db": latest_date_data_db, "response": response}    
        # ==================== ENDED GOLD US ====================

        # ==================== START CURRENCY ====================
        elif data == "currency": 
            currency_api = requests.get("https://www.alphavantage.co/query?function=FX_DAILY&from_symbol=USD&to_symbol=THB&apikey=51701afb48513dc95e52d7d4").json()
            currency_latest_db = requests.get("https://34.117.31.73.nip.io/currency/get/?frame=1d&cache=False", verify=False).json()["data"][-1]["date"]
            latest_date = list(currency_api["Time Series FX (Daily)"].keys())[0]
            if latest_date == currency_latest_db or latest_date < currency_latest_db:
                return {"status": "No new data added", "latest_date_data_db": currency_latest_db}
            elif currency_latest_db < latest_date:
                latest_data = currency_api["Time Series FX (Daily)"][latest_date]
                form_data = {
                    "date": latest_date,
                    "price": latest_data["4. close"],
                    "open": latest_data["1. open"],
                    "high": latest_data["2. high"],
                    "low": latest_data["3. low"],
                    "percent": (float(latest_data["4. close"]) - float(currency_api["Time Series FX (Daily)"][list(currency_api["Time Series FX (Daily)"].keys())[1]]["4. close"])) / float(currency_api["Time Series FX (Daily)"][list(currency_api["Time Series FX (Daily)"].keys())[1]]["4. close"]) * 100,
                    "diff": float(latest_data["4. close"]) - float(currency_api["Time Series FX (Daily)"][list(currency_api["Time Series FX (Daily)"].keys())[1]]["4. close"])
                }
                requests.post("https://34.117.31.73.nip.io/currency/add-crrencyth/", json=form_data, verify=False).json()
                return {
                    "status": "New data added success",
                    "new_data": requests.get("https://34.117.31.73.nip.io/currency/get/?frame=1d&cache=False", verify=False).json()["data"][-1]
                }
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid data parameter: {data}. Must be one of: 'goldus', 'goldth', 'currency'"
            )
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Request error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")