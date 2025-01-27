import streamlit as st
import base64
from openai import OpenAI

client = OpenAI(
  base_url="http://127.0.0.1:5272/v1/",
  api_key="xyz" # required by API but not used
)

st.title('Recipe Generator 🍔')
st.write('This is a simple recipe generator application.Upload images of the Ingridients and get the recipe by Chef GenAI! 🧑‍🍳')
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
  st.image(uploaded_file, width=300)

preference = st.sidebar.selectbox(
    "Choose your preference",
    ("Vegetarian", "Non-Vegetarian")
)

cuisine = st.sidebar.selectbox(
  "Select for Cuisine",
  ("Indian","Chinese","French","Thai","Italian","Mexican","Japanese","American","Greek","Spanish")
)


def encode_image(uploaded_file):
  """Encodes a Streamlit uploaded file into base64 format"""
  if uploaded_file is not None:
    content = uploaded_file.read()
    return base64.b64encode(content).decode("utf-8")
  else:
    return None

base64_image = encode_image(uploaded_file)

if st.button("Ask Chef GenAI!"):
  if base64_image:
    response = client.chat.completions.create(
    model="Phi-3-vision-128k-cpu-int4-rtn-block-32-acc-level-4-onnx",
    messages=[
      {
        "role": "user",
        "content": [
          {
            "type": "text",
            "text": f"STRICTLY use the ingredients in the image to generate a {preference} recipe and {cuisine} cuisine.",
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
else:
  st.write("Please upload an image with any number of ingridients and instantly get a recipe.")


