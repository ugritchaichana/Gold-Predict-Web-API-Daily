import sys
import uvicorn
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent / 'app'))

from app.main import app

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
    # uvicorn.run(app, host="0.0.0.0", port=8000)