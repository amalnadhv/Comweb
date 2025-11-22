from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pymssql
import os

app = FastAPI()

# Allow Netlify/mobile
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables (Render)
DB_SERVER = os.getenv("DB_SERVER", "BSERVER\\PBSERVER")
DB_USER = os.getenv("DB_USER", "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "SVVsvv@999")
DB_NAME = os.getenv("DB_NAME", "COM_JSF")

def get_connection():
    return pymssql.connect(
        server=DB_SERVER,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

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
