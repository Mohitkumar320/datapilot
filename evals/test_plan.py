from app.sql.schema import get_schema
from app.sql.generator import generate_plan

schema = get_schema()

question = "Give me total rentals per category along with a bar chart."
plan = generate_plan(question, schema)
print(plan)