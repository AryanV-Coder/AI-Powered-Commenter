import json
import requests
import base64
from io import BytesIO
from PIL import Image

# Convert image to base64
def encode_image(image):
    if image.mode == "RGBA":
        image = image.convert("RGB")  # Convert RGBA to RGB
    
    buffered = BytesIO()
    image.save(buffered, format="JPEG")  
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

# Convert Google Drive image URL to base64
def google_drive_to_base64(drive_url):
    try:
        # Extract the file ID from the Google Drive link
        if "id=" in drive_url:
            file_id = drive_url.split("id=")[-1]
        elif "/file/d/" in drive_url:
            file_id = drive_url.split("/file/d/")[1].split("/")[0]
        else:
            print(f"⚠️ Invalid Google Drive URL format: {drive_url}")
            return None

        # Generate a direct image link
        direct_url = f"https://drive.google.com/thumbnail?id={file_id}&sz=w1000"  # Thumbnail view

        # Download the image
        response = requests.get(direct_url, stream=True)
        if response.status_code == 200:
            image = Image.open(BytesIO(response.content))
            return encode_image(image)  # Convert to base64
        else:
            print(f"❌ Failed to download image {drive_url}: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error processing image {drive_url}: {e}")
        return None

# Load JSON
with open('fineTuning/shayari.json', 'r') as file:
    raw_data = json.load(file)

# Convert all Google Drive URLs to base64
for item in raw_data:
    if "parts" in item:
        for part in item["parts"]:
            if "mime_type" in part and part["mime_type"] == "image/jpeg":
                if part["data"].startswith("http"):  # If it's a URL, convert it
                    base64_img = google_drive_to_base64(part["data"])
                    if base64_img:
                        part["data"] = base64_img  # Replace URL with base64

# Save the updated JSON
with open('fineTuning/shayari.json', 'w') as file:
    json.dump(raw_data, file, indent=4)

print("✅ Google Drive images converted to base64 successfully!")
