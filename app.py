from flask import Flask, render_template, request
import requests
import json
import os
import logging

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_URL = os.getenv("OPENAI_URL")
DEFAULT_SIZE = os.getenv("DEFAULT_SIZE")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def generate_image(description, n=1):
    url = OPENAI_URL
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json',
    }
    data = {
        "prompt": description,
        "n": n,
        "size": DEFAULT_SIZE
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
        logger.info(f"Images requested: {n}")
        logger.info(f"API Response: {response.text}")
        
        data = response.json().get('data', [])
        image_urls = [item.get('url', None) for item in data if item.get('url')]
        
        return image_urls

    except requests.HTTPError as http_err:
        logger.error(f"HTTP error occurred: {http_err}")
    except Exception as err:
        logger.error(f"Other error occurred: {err}")
    return []

@app.route("/", methods=["POST"])
def generate_and_display_image():
    if request.method == "POST":
        description = request.form.get("description")
        n = int(request.form.get("num_images", 1))
        if description:
            image_urls = generate_image(description, n)
            logger.info(f"Generated image URLs: {image_urls}")
            return render_template("index.html", image_urls=image_urls, description=description)

    return render_template("index.html", image_urls=None, description=None)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
