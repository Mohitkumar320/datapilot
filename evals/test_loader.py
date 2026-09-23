from app.pandas_tools.loader import load_csv, get_dataframe_schema

result = load_csv("data/samplesuperstore.csv")   
print("Success:", result["success"])

if result["success"]:
    df = result["data"]
    print(df.head())
    print("\n--- Schema ---")
    print(get_dataframe_schema(df))