import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

def get_schema(database: str = "sakila") -> str:
    conn = mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password=os.getenv("MYSQL_PASSWORD"),
        database=database
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
        FROM information_schema.columns
        WHERE TABLE_SCHEMA = %s
        ORDER BY TABLE_NAME, ORDINAL_POSITION
    """, (database,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    schema_text = ""
    current_table = None
    for table_name, column_name, data_type in rows:
        if table_name != current_table:
            schema_text += f"\nTable {table_name}:\n"
            current_table = table_name
        schema_text += f"  - {column_name} ({data_type})\n"

    return schema_text