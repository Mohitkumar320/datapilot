import os
from dotenv import load_dotenv
import mysql.connector

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
        cursor.close()
        conn.close()
        return {"success": True, "data": rows, "error": None}
    except mysql.connector.Error as e:
        return {"success": False, "data": None, "error": str(e)}