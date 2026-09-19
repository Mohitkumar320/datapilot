import os
from dotenv import load_dotenv
import mysql.connector
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

schema = """
Tables in sakila database include: actor, film, customer, rental, payment,
category, store, address, city, country, staff, inventory, language,
film_actor, film_category.
"""

questions = [
    "List all customers whose first name is 'MARY'.",
    "Find the 5 longest films by length.",
    "Get the titles of all films in the 'Comedy' category.",
    "Which actor has appeared in the most films?",
    "List customer names along with the film titles they've rented.",
    "Total revenue collected by each store.",
    "Find customers who have never rented a film.",
    "Find the top 3 most rented film categories by total rental count.",
    "Show me the best customers.",
    "Find categories that have more than 50 films.",
    "How many rentals happened in May 2005?",
    "List films that have never been rented."
]

models = ["qwen/qwen3.8-27b", "openai/gpt-oss-120b"]

def run_sql(sql):
    conn = mysql.connector.connect(
        host="127.0.0.1", port=3306, user="root",
        password=os.getenv("MYSQL_PASSWORD"), database="sakila"
    )
    cursor = conn.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

results_log = []

for i, question in enumerate(questions, start=1):
    results_log.append(f"\n## Question {i}: {question}\n")
    for model in models:
        prompt = f"""
You are a SQL expert. Given this database schema:
{schema}

Write a MySQL query to answer this question:
{question}

Return ONLY the SQL query, nothing else. No explanation, no markdown formatting.
"""
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}]
            )
            sql = response.choices[0].message.content.strip()
            sql = sql.replace("```sql", "").replace("```", "").strip()

            try:
                rows = run_sql(sql)
                result_text = "\n".join(str(r) for r in rows[:10])
                if len(rows) > 10:
                    result_text += f"\n... ({len(rows)} total rows)"
            except Exception as db_err:
                result_text = f"SQL EXECUTION ERROR: {db_err}"

            results_log.append(f"**{model}**\nSQL:\n```\n{sql}\n```\nResult:\n```\n{result_text}\n```\n")

        except Exception as api_err:
            results_log.append(f"**{model}**: API ERROR: {api_err}\n")

with open("evals/results.md", "w", encoding="utf-8") as f:
    f.write("# Model Comparison Results\n" + "\n".join(results_log))

print("Done. Results saved to evals/results.md")