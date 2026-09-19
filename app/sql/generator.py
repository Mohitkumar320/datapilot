import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_sql(question: str, schema: str) -> str:
    prompt = f"""
You are a SQL expert. Given this database schema:
{schema}

Write a MySQL query to answer this question:
{question}

Return ONLY the SQL query, nothing else. No explanation, no markdown formatting.
"""
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}]
    )
    sql = response.choices[0].message.content.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql