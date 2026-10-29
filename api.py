import os
from pathlib import Path
from secrets import compare_digest

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import APIKeyHeader

# Load settings from the file next to this script
load_dotenv(Path(__file__).with_name(".env"))

api_key = os.getenv("API_KEY")

if not api_key:
    raise RuntimeError("API_KEY is missing from .env")

app = FastAPI(
    title="CIDFF Project API",
    description="Access to territorial indicators and recorded state funding.",
    version="1.0"
)

# Read the access key from the request header
key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def check_api_key(key: str | None = Depends(key_header)):
    if key is None or not compare_digest(key.encode(), api_key.encode()):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid API key",
            headers={"WWW-Authenticate": "APIKey"}
        )


@app.get("/")
def home():
    return {"message": "CIDFF Project API is running"}


@app.get("/protected-check", dependencies=[Depends(check_api_key)])
def protected_check():
    return {"message": "Access granted"}


from sqlalchemy import URL, create_engine

# Build the database connection from local settings
database_url = URL.create(
    "mysql+pymysql",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=3306,
    database=os.getenv("DB_NAME"),
    query={"charset": "utf8mb4"}
)

engine = create_engine(database_url, pool_pre_ping=True)


from fastapi import Query
from sqlalchemy import text

# Return recorded state payments by department for one year
@app.get("/funding-summary", dependencies=[Depends(check_api_key)])
def funding_summary(year: int = Query(default=2024, ge=2020, le=2024)):
    query = text("""
        SELECT
            department_code,
            COUNT(*) AS record_count,
            SUM(amount) AS total_amount
        FROM funding_payments
        WHERE year = :year
        GROUP BY department_code
        ORDER BY department_code
    """)

    with engine.connect() as connection:
        results = connection.execute(query, {"year": year})
        return [dict(row) for row in results.mappings()]








