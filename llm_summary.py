import streamlit as st
from openai import OpenAI
from typing import Any

client = OpenAI(api_key=st.secrets["openai"]["api_key"])

def summarize_issues(requests_with_issues):
    if not requests_with_issues:
        return "No significant performance or reliability issues detected."

    all_messages = []
    for req in requests_with_issues:
        url = req.get('url', '')
        issues = req.get('issues', [])
        if issues:
            issue_texts = [f"{i['message']}" for i in issues]
            all_messages.append(f"Request: {url}\n" + "\n".join(issue_texts))

    prompt = (
        "You are a performance analyst. Summarize the following request-level issues "
        "from a HAR file into a short, readable explanation that highlights common patterns, "
        "potential root causes, and what to look at. Use concise technical language:\n\n"
        + "\n\n".join(all_messages)
    )

    messages: Any = [
        {"role": "system", "content": "You are a helpful AI network performance analyst."},
        {"role": "user", "content": prompt}
    ]

    model_choice = st.selectbox("Choose GPT Model", ["gpt-3.5-turbo", "gpt-4"], index=0)

    try:
        response = client.chat.completions.create(
            model=model_choice,
            messages=messages,
            max_tokens=300,
            temperature=0.3
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"⚠️ GPT summary failed: {e}"
