from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import pyodbc

app = FastAPI()

# Allow requests from anywhere (Netlify/mobile)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["https://leafy-blini-990d44.netlify.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_connection():
    return pyodbc.connect(
        "Driver={ODBC Driver 17 for SQL Server};"
        "Server=BSERVER\\PBSERVER;"
        "Database=COM_JSF;"
        "UID=sa;"
        "PWD=SVVsvv@999;"
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

        # Return JSON explicitly to avoid ngrok HTML issues
        return JSONResponse(
            content={
                "sales": float(sales),
                "sales_return": float(sales_return),
                "actual_sales": actual_sales
            }
        )

    except Exception as e:
        # Catch errors and return JSON error response
        return JSONResponse(
            content={"error": str(e)},
            status_code=500
        )
