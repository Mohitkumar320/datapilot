import os
from dotenv import load_dotenv
import mysql.connector
import pandas as pd
from decimal import Decimal

load_dotenv()

def execute_sql(sql: str):
    try:
        conn = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password=os.getenv("MYSQL_PASSWORD"),
            database="sakila"
        )
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        cursor.close()
        conn.close()

        df = pd.DataFrame(rows, columns=columns)

        for col in df.columns:
            if df[col].apply(lambda x: isinstance(x, Decimal)).any():
                df[col] = df[col].astype(float)

        return {"success": True, "data": df, "error": None}
    except mysql.connector.Error as e:
        return {"success": False, "data": None, "error": str(e)}