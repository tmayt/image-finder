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

        images = driver.find_elements(By.CSS_SELECTOR, "img")
        for img in images:
            width = driver.execute_script("return arguments[0].naturalWidth;", img)
            if width and width > 200:
                candidate = img.get_attribute("src") or img.get_attribute("data-src")
                if candidate and candidate.startswith("http"):
                    src = candidate
                    break
    except Exception as e:
        print("Error in Google search:", e)
        src = None
    finally:
        driver.quit()
    return src

def get_first_upc_item(query: str):
    driver = get_driver()
    upc, image = None, None
    try:
        search_url = f"https://www.upcitemdb.com/query?s={query}&type=2"
        driver.get(search_url)
        time.sleep(2)  # wait for page to load

        # Find the container div
        container = driver.find_element(By.CSS_SELECTOR, "div.upclist.col-xs-12")
        first_li = container.find_element(By.CSS_SELECTOR, "ul > li")

        # UPC number
        upc_el = first_li.find_element(By.CSS_SELECTOR, "div.rImage > a")
        upc = upc_el.text.strip()

        # Product image
        img_el = first_li.find_element(By.CSS_SELECTOR, "a.img_prod > img")
        image = img_el.get_attribute("src")

    except Exception as e:
        print("Error in UPC search:", e)
        upc, image = None, None
    finally:
        driver.quit()

    return upc, image

@app.route("/search/google", methods=["GET"])
def search_image_google():
    query = request.args.get("q", "")
    if not query:
        return jsonify({"error": "missing query parameter q"}), 400

    google_image = get_first_google_image(query)

    return jsonify({
        "query": query,
        "google_image": google_image,
        "upc": '',
        "upc_image": ''
    })

@app.route("/search/upc", methods=["GET"])
def search_image_upc():
    query = request.args.get("q", "")
    if not query:
        return jsonify({"error": "missing query parameter q"}), 400

    upc, upc_image = get_first_upc_item(query)

    return jsonify({
        "query": query,
        "google_image": '',
        "upc": upc,
        "upc_image": upc_image
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)