from app.sql.executor import execute_sql

bad_sql = "SELECT * FROM this_table_does_not_exist;"
result = execute_sql(bad_sql)

print(result)