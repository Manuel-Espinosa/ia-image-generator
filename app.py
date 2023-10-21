from flask import Flask, render_template, request
import requests
import json
import os
import logging
import openai

app = Flask(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_URL = os.getenv("OPENAI_URL")
DEFAULT_SIZE = os.getenv("DEFAULT_SIZE")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def send_question_using_description(description):
    if not description:
        return {'error': 'Description is required'}
    if not openai.api_key:
        logger.error('OpenAI API key is missing or not configured')
        return {'error': 'OpenAI API key is not configured'}

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": description}
            ]     
        )
        logger.info(f"Raw API Response: {response.choices}")  # Logging the entire raw response
        answer = response.choices[0].message['content']
        return {'answer': answer}

    except Exception as e:
        logger.error(f'Error: {str(e)}')
        return {'error': str(e)}


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
        logger.info(f"Requested URL: {url}")
        logger.info(f"Request Headers: {headers}")
        logger.info(f"Request Data: {data}")
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()
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
            response_data = send_question_using_description(description)
            answer = response_data.get('answer', '')
            return render_template("index.html", image_urls=image_urls, description=description, answer=answer)


    return render_template("index.html", image_urls=None, description=None)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
