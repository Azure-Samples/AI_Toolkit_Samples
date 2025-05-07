import streamlit as st
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:5272/v1/",
    api_key="xyz" # required by API but not used
)

st.title("Chat with Phi-3")
query = st.chat_input("Enter query:")

if query:
    with st.chat_message("user"):
        st.write(query)

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "user","content": "You are a helpful assistant and provides structured answers."},
            {"role": "user", "content": query}
        ],
        model="Phi-3-mini-128k-cuda-int4-onnx",
    )
    with st.chat_message("assistant"):
        st.write(chat_completion.choices[0].message.content)

