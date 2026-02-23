from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)

def get_driver():
    options = Options()
    options.binary_location = "/usr/bin/google-chrome"
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def get_first_google_image(query: str):
    driver = get_driver()
    src = None

    try:
        search_url = f"https://www.google.com/search?tbm=isch&q={query}"
        driver.get(search_url)

        time.sleep(2)

        # Skip logo images, get real image results
        images = driver.find_elements(By.CSS_SELECTOR, "img")

        for img in images:
            candidate = img.get_attribute("src")
            if candidate and candidate.startswith("http"):
                src = candidate
                break

    except Exception:
        src = None

    finally:
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
