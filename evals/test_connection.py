import os
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

conn = mysql.connector.connect(
    host="127.0.0.1",
    port=3306,
    user="root",
    password=os.getenv("MYSQL_PASSWORD"),
    database="sakila"
)

cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM customer;")
result = cursor.fetchone()

print("Number of customers in sakila:", result[0])

cursor.close()
conn.close()