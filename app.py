# streamlit run app.py
import streamlit as st
import google.generativeai as genai
from  PIL import Image
import time
import json
import base64
from gtts import gTTS
from io import BytesIO

st.title("AI Powered Commenter")
mood = ["Good & Funny Comments","Roasting","Shayari"]
option = st.selectbox("Select a Mood:", mood)

genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash-lite")

if (option == mood[0]):
    with open('fineTuning/funny.json','r') as file:
        data = json.load(file)  # Load JSON into a Python dictionary
elif (option == mood[1]):
    with open('fineTuning/roasting.json','r') as file:
        data = json.load(file)  # Load JSON into a Python dictionary
elif (option == mood[2]):
    with open('fineTuning/shayari.json','r') as file:
        data = json.load(file)  # Load JSON into a Python dictionary

# Convert image to base64
def encode_image(image):
    if image.mode == "RGBA":
        image = image.convert("RGB")  # Convert RGBA to RGB

    buffered = BytesIO()
    image.save(buffered, format="JPEG")  
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# Text you want to convert to speech
text = "Please capture or upload image"
def aiResponse(data):
    global text
    response = model.generate_content(data,stream=True)
    response.resolve() # Ensure the response is fully generated
    text = response.text
    for word in response.text.split():
        yield word + " "
        time.sleep(0.02)


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

# Convert to speech (TTS)
tts = gTTS(text, lang='hi')

# Save to in-memory buffer instead of file
audio_buffer = BytesIO()
tts.write_to_fp(audio_buffer)

# Rewind the buffer to the beginning
audio_buffer.seek(0)

# Play in Streamlit
st.audio(audio_buffer, format='audio/mp3', autoplay = False)