# streamlit run app.py
import streamlit as st
import google.generativeai as genai
from  PIL import Image
import time
import json
import base64
from io import BytesIO




genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash-lite")

with open('data.json','r') as file:
    data = json.load(file)  # Load JSON into a Python dictionary

# Convert image to base64
def encode_image(image):
    if image.mode == "RGBA":
        image = image.convert("RGB")  # Convert RGBA to RGB

    buffered = BytesIO()
    image.save(buffered, format="JPEG")  
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def aiResponse(data):
    response = model.generate_content(data,stream=True)
    response.resolve() # Ensure the response is fully generated

    for word in response.text.split():
        yield word + " "
        time.sleep(0.02)

st.title("AI Powered Commenter")

enable = st.checkbox("Enable camera")
capture = st.camera_input(label="Take a picture", disabled=not enable)
uploaded_image = st.file_uploader("Choose an image")

if capture :
    image = Image.open(capture)
    base64_image = encode_image(image)
    prompt = [
                {
                    "role": "user",
                    "parts": [
                        {
                            "mime_type": "image/jpeg",
                            "data": base64_image
                        }
                    ]
                }
            ]
    data = data + prompt
    st.write_stream(aiResponse(data))

if uploaded_image :
    image = Image.open(uploaded_image)
    st.image(image)
    base64_image = encode_image(image)
    prompt = [
                {
                    "role": "user",
                    "parts": [
                        {
                            "mime_type": "image/jpeg",
                            "data": base64_image
                        }
                    ]
                }
            ]
    data = data + prompt
    st.write_stream(aiResponse(data))