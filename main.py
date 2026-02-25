from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

app = Flask(__name__)

# ----------------- Selenium Driver -----------------
def create_driver():
    """Initialize and return a headless Chrome driver."""
    options = Options()
    options.binary_location = "/usr/bin/google-chrome"
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-infobars")
    options.add_argument("--disable-extensions")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

# ----------------- Helper Functions -----------------
def find_first_image(driver, url, min_width=200, selector="img"):
    """Navigate to a URL and return the first image URL that meets width criteria."""
    try:
        driver.get(url)
        time.sleep(2)  # for production, replace with WebDriverWait
        images = driver.find_elements(By.CSS_SELECTOR, selector)
        for img in images:
            width = driver.execute_script("return arguments[0].naturalWidth;", img)
            if width and width > min_width:
                src = img.get_attribute("src") or img.get_attribute("data-src")
                if src and src.startswith("http"):
                    return src
    except Exception as e:
        print("Error fetching image:", e)
    return None

def get_upc_item(driver, query):
    """Return UPC code and image from upcitemdb for a query."""
    try:
        driver.get(f"https://www.upcitemdb.com/query?s={query}&type=2")
        time.sleep(2)
        container = driver.find_element(By.CSS_SELECTOR, "div.upclist.col-xs-12")
        first_li = container.find_element(By.CSS_SELECTOR, "ul > li")
        upc = first_li.find_element(By.CSS_SELECTOR, "div.rImage > a").text.strip()
        image = first_li.find_element(By.CSS_SELECTOR, "a.img_prod > img").get_attribute("src")
        return upc, image
    except Exception as e:
        print("Error fetching UPC:", e)
        return None, None

def search_google_image(query):
    driver = create_driver()
    try:
        return find_first_image(driver, f"https://www.google.com/search?tbm=isch&q={query}")
    finally:
        driver.quit()

def search_bing_image(query):
    driver = create_driver()
    try:
        return find_first_image(driver, f"https://www.bing.com/images/search?q={query}&first=1")
    finally:
        driver.quit()

def search_upc(query):
    driver = create_driver()
    try:
        return get_upc_item(driver, query)
    finally:
        driver.quit()

# ----------------- Flask Route -----------------
@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "").strip()
    source = request.args.get("source", "google").lower()

    if not query:
        return jsonify({"error": "missing query parameter q"}), 400

    result = {
        "query": query,
        "google_image": '',
        "bing_image": '',
        "upc": '',
        "upc_image": ''
    }

    if source == "google":
        result["google_image"] = search_google_image(query)
    elif source == "bing":
        result["bing_image"] = search_bing_image(query)
    elif source == "upc":
        result["upc"], result["upc_image"] = search_upc(query)
    else:
        return jsonify({"error": "invalid source parameter, must be one of google, bing, upc"}), 400

    return jsonify(result)

# ----------------- Main -----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)