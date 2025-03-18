# Tutorial for creating baseline RAG chatbot using AI Toolkit and Streamlit

# Importing required libraries
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

# Initializing the required components for RAG
embeddings = SentenceTransformerEmbeddings(model_name='all-MiniLM-L6-v2')

model = ChatOpenAI(
    base_url="http://127.0.0.1:5272/v1/",
    api_key="ai-toolkit",
    model="Phi-3-mini-128k-directml-int4-awq-block-128-onnx",
    temperature=0.7
)

# Loading the knowledge base
load_db = Chroma(persist_directory='./ai-toolkit', embedding_function=embeddings)
retriever = load_db.as_retriever(search_kwargs={'k': 3})

# Defining the template
template = """ You are a specialized AI assistant for the Microsoft Visual Studio Code AI Toolkit.\n
    Your responses should be strictly relevant to this product and the user's query. \n
    Avoid providing information that is not directly related to the toolkit.
    Maintain a professional tone and ensure your responses are accurate and helpful.
    Strictly adhere to the user's question and provide relevant information. 
    If you do not know the answer then respond "I dont know".Do not refer to your knowledge base.
    {context}
    Question:
    {question}
"""

# Defining the pipeline
prompt = ChatPromptTemplate.from_template(template)
output_parser = StrOutputParser()

# Defining the pipeline
setup_and_retrieval = RunnableParallel(
    {"context": retriever, "question": RunnablePassthrough()}
)
chain = setup_and_retrieval | prompt | model | output_parser

# Streamlit app
st.title("AI Toolkit Chatbot")
st.write("Ask me anything about the Microsoft Visual Studio Code AI Toolkit.")

# user session
if 'messages' not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if user_input := st.chat_input("Your question:"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    response = chain.invoke(user_input)
    st.session_state.messages.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)