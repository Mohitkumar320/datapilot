import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_sql(question: str, schema: str, history: list = None) -> str:
    history_text = ""
    if history:
        history_text = "\n\nPrevious questions and answers in this conversation:\n"
        for turn in history:
            history_text += f"Q: {turn['question']}\nSQL used: {turn['sql']}\n"

    prompt = f"""
You are a SQL expert. Given this database schema:
{schema}
{history_text}

Write a MySQL query to answer this new question:
{question}

If the question refers to a previous result (e.g. "those", "that", "the ones"),
use the previous SQL/context to understand what it refers to.

Return ONLY the SQL query, nothing else. No explanation, no markdown formatting.
"""
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[{"role": "user", "content": prompt}]
    )
    sql = response.choices[0].message.content.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql