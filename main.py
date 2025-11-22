from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pyodbc
import os

app = FastAPI()

# Allow requests from anywhere (Netlify/mobile)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["https://leafy-blini-990d44.netlify.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# SQL Server connection settings
# -------------------------------
SERVER = os.getenv("DB_SERVER", "BSERVER")  # e.g., your_server.database.windows.net
DATABASE = os.getenv("DB_NAME", "COM_JSF")
USERNAME = os.getenv("DB_USER", "sa")
PASSWORD = os.getenv("DB_PASSWORD", "SVVsvv@999")
PORT = os.getenv("DB_PORT", 1433)

# Connection string using FreeTDS driver
def get_connection():
    return pyodbc.connect(
        f"DRIVER=FreeTDS;"
        f"SERVER={SERVER};"
        f"PORT={PORT};"
        f"DATABASE={DATABASE};"
        f"UID={USERNAME};"
        f"PWD={PASSWORD};"
        "TDS_Version=8.0;"
    )

# -------------------------------
# API endpoint
# -------------------------------
@app.get("/sales_today")
def get_sales_today():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        # Total sales (type 'C')
        cursor.execute("""
            SELECT SUM(ISNULL(amount,0)) AS sales
            FROM astran
            WHERE LEFT(account,4) BETWEEN '4000' AND '4999'
              AND type='C'
              AND CONVERT(date,jvdate)=CONVERT(date,GETDATE())
        """)
        sales = cursor.fetchone()[0] or 0

        # Total sales return (type 'D')
        cursor.execute("""
            SELECT SUM(ISNULL(amount,0)) AS salesReturn
            FROM astran
            WHERE LEFT(account,4) BETWEEN '4000' AND '4999'
              AND type='D'
              AND CONVERT(date,jvdate)=CONVERT(date,GETDATE())
        """)
        sales_return = cursor.fetchone()[0] or 0

        conn.close()

        actual_sales = float(sales) - float(sales_return)

        return JSONResponse(
            content={
                "sales": float(sales),
                "sales_return": float(sales_return),
                "actual_sales": actual_sales
            }
        )

    except Exception as e:
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )
