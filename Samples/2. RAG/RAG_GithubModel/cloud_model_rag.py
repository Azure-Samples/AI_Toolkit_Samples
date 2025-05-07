from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from dotenv import load_dotenv
import os
from langchain_openai import OpenAIEmbeddings
load_dotenv()
token = os.getenv('GITHUB_TOKEN')
endpoint = "https://models.inference.ai.azure.com"
model_name = "text-embedding-3-small"

#embeddings=SentenceTransformerEmbeddings(model_name='all-MiniLM-L6-v2')

embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
    base_url=endpoint,
    api_key=token,
)

model=ChatOpenAI(
    base_url="http://127.0.0.1:5272/v1/",
    api_key="ai-toolkit",
    model="Phi-3-mini-128k-directml-int4-awq-block-128-onnx",
    temperature=0.7
)

load_db=Chroma(persist_directory='./ai-toolkit',embedding_function=embeddings)
retriever=load_db.as_retriever(search_kwargs={'k':3})

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

prompt = ChatPromptTemplate.from_template(template)
output_parser = StrOutputParser()

#RunnableParallel object is created to run multiple tasks in parallel

setup_and_retrieval = RunnableParallel(
    {"context": retriever, "question": RunnablePassthrough()}
)

#Represents the entire processing pipeline, where each component processes the input and passes the result to the next component.
chain = setup_and_retrieval | prompt | model | output_parser
query=input("Enter your query:")
resp=chain.invoke(query)
print(resp)