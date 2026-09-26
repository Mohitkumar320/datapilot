import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langsmith import traceable

load_dotenv()
llm = ChatGroq(model="openai/gpt-oss-120b", api_key=os.getenv("GROQ_API_KEY"))


@traceable
def generate_summary(question: str, history: list) -> str:
    if not history:
        return "There's nothing to summarize yet — ask a data question first."

    findings_text = ""
    for i, turn in enumerate(history, start=1):
        findings_text += f"\nFinding {i} — Question: {turn['question']}\n"
        if turn.get("data") is not None:
            findings_text += f"Result:\n{turn['data'].to_string(index=False)}\n"
        else:
            findings_text += "Result: no data (this question failed or produced nothing)\n"

    prompt = f"""
You are a data analysis assistant. The user has asked several questions about a dataset during this session, and now wants a summary of everything found so far.

Here are all the findings from this session:
{findings_text}

The user's request: {question}

Write a clear, concise narrative summary of the key findings above. Highlight the most important numbers and any patterns worth noting. Do not repeat every single row of every table — synthesize the key takeaways in plain language. Keep it to a few short paragraphs.

Do not attempt to generate, describe, or embed any chart, image, or visualization yourself (no image data, no markdown images, no code blocks for plotting) — a chart is created separately by the system if needed. Focus only on the written narrative.
"""
    response = llm.invoke(prompt)
    return response.content.strip()

if __name__ == "__main__":
    import pandas as pd
    fake_history = [
        {"question": "average Profit by Sub-Category", "data": pd.DataFrame({"Sub-Category": ["Chairs", "Tables"], "Profit": [43.1, -55.3]})},
        {"question": "highest Sales region for Consumer segment", "data": pd.DataFrame({"Region": ["West"], "Sales": [158000]})}
    ]
    summary = generate_summary("summarize everything we found", fake_history)
    print(summary)