import streamlit as st
import base64
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:5272/v1/",
    api_key="xyz" # required by API but not used
)

st.title('Image Analyser Application')
st.write('This is a simple Image Translator Application that uses the Phi-3 Vision model to analyse the image.')
uploaded_file = st.file_uploader("Choose a file")


def encode_image(uploaded_file):
    with open(uploaded_file, "rb") as uploaded_file:
        return base64.b64encode(uploaded_file.read()).decode("utf-8")
    
base64_image = encode_image(uploaded_file)

response = client.chat.completions.create(
    model="Phi-3-vision-128k-cpu-int4-rtn-block-32-acc-level-4-onnx",
    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Analyse the following image and describe the image to the user",
                },
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ],
        }
    ],
)
print(response.choices[0].message.content)
st.write(response.choices[0].message.content)