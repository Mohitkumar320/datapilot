from app.sql.generator import generate_sql

schema = """
Tables in sakila database include: actor, film, customer, rental, payment,
category, store, address, city, country, staff, inventory, language,
film_actor, film_category.
"""

question = "List all customers whose first name is 'MARY'."

sql = generate_sql(question, schema)
print("Generated SQL:\n", sql)