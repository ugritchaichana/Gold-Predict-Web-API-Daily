from fastapi import FastAPI
from . import endpoints  # Changed from "from api import endpoints"
from fastapi.middleware.cors import CORSMiddleware

# Configure FastAPI app with both documentation options
app = FastAPI(
    title="Gold Price Prediction API",
    description="""
        /add-current-data?data=goldth
        /add-current-data?data=goldus
        /add-current-data?data=currency
    
    """,
    version="1.0.0",
    docs_url=None,         # Disable Swagger UI
    redoc_url=None,        # Disable ReDoc
    openapi_tags=[
        {
            "name": "Gold and Currency Data",
            "description": "Operations to fetch and store gold prices and currency exchange rates"
        }
    ],
    contact={
        "name": "Gold Price Prediction Team",
        "url": "https://github.com/yourusername/Gold-Predict-Web-API-Daily",
    },
    license_info={
        "name": "Private",
    },
)

# Configure CORS for API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(endpoints.router, prefix="")

# Create a new endpoint for the original root functionality at a different path
@app.get("/routes", tags=["Routes"], summary="List all application routes")
def routes():
    """
    Shows all available routes in this API for quick reference.
    """
    return {"routes": [
        "/add-current-data?data=goldus",
        "/add-current-data?data=goldth",
        "/add-current-data?data=currency"
    ]}