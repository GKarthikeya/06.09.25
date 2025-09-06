from flask import Flask, Response, render_template
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import io
import os

app = Flask(__name__)

# 🔐 Credentials from environment variables
IARE_USERNAME = os.getenv("IARE_USERNAME", "your_username")
IARE_PASSWORD = os.getenv("IARE_PASSWORD", "your_password")

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    return webdriver.Chrome(options=options)

def scrape_course_content():
    driver = get_driver()

    # --- 1. Login ---
    driver.get("https://samvidha.iare.ac.in/")
    time.sleep(3)

    driver.find_element(By.ID, "userName").send_keys(IARE_USERNAME)
    driver.find_element(By.ID, "password").send_keys(IARE_PASSWORD, Keys.RETURN)

    time.sleep(5)

    # --- 2. Navigate ---
    driver.get("https://samvidha.iare.ac.in/home?action=course_content")
    time.sleep(5)

    # --- 3. Scrape ---
    all_data = []
    courses = driver.find_elements(By.XPATH, "//table[contains(@class,'table')]")

    for course in courses:
        try:
            course_name = course.find_element(By.XPATH, ".//tr[1]//td[contains(@colspan,'7')]").text.strip()
        except:
            course_name = "Unknown Course"

        rows = course.find_elements(By.XPATH, ".//tr")[1:]
        for row in rows:
            cols = [c.text.strip() for c in row.find_elements(By.TAG_NAME, "td")]
            if cols:
                all_data.append([course_name] + cols)

    driver.quit()

    df = pd.DataFrame(all_data, columns=[
        "Course Name", "S.No", "Date", "Period",
        "Topics Covered", "Status", "Youtube Link", "Powerpoint Lecture"
    ])
    return df


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/scrape")
def scrape():
    df = scrape_course_content()
    output = io.StringIO()
    df.to_csv(output, index=False, encoding="utf-8-sig")
    output.seek(0)
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=course_content.csv"}
    )


@app.route("/show")
def show():
    df = scrape_course_content()
    return df.to_html(classes="table table-striped", index=False)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
