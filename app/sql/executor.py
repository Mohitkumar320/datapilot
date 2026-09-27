import os
from dotenv import load_dotenv
import mysql.connector
import pandas as pd
from decimal import Decimal

load_dotenv()

def execute_sql(sql: str, db_config: dict):
    try:
        conn = mysql.connector.connect(
            host=db_config["host"],
            port=db_config["port"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"]
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