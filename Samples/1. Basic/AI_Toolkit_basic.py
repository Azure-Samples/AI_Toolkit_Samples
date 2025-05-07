from openai import OpenAI
 
client = OpenAI(
    base_url="http://127.0.0.1:5272/v1/",
    api_key="xyz" # required by API but not used
)
 
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user","content": "What is the capital of India?",
        }
    ],
    model="Phi-3-mini-128k-cuda-int4-onnx",
)
 
print(chat_completion.choices[0].message.content)