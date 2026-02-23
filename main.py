from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

app = Flask(__name__)

def get_first_google_image(query: str):
    # Prepare headless Chrome
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")

    driver = webdriver.Chrome(options=options)

    # Format URL for Google Images
    search_url = f"https://www.google.com/search?tbm=isch&q={query}"
    driver.get(search_url)
    
    time.sleep(2)  # wait for images to load

    # Find first image
    try:
        img = driver.find_element(By.CSS_SELECTOR, "img")
        src = img.get_attribute("src")

    except Exception as e:
        src = None

    driver.quit()
    return src

@app.route("/search", methods=["GET"])
def search_image():
    query = request.args.get("q", "")
    if not query:
        return jsonify({"error": "missing query parameter q"}), 400

    first_image = get_first_google_image(query)
    return jsonify({"query": query, "image": first_image})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
