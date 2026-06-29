from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from bs4 import BeautifulSoup
import pandas as pd
import time

# ----------------------------
# Start Chrome
# ----------------------------
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()

# ----------------------------
# Open Website
# ----------------------------
driver.get("https://www.srilankateaboard.lk/tea-statistics/")
time.sleep(5)

# ----------------------------
# Get All Categories
# ----------------------------
category_dropdown = Select(driver.find_element(By.ID, "teaprice-category"))

categories = []

for option in category_dropdown.options:
    value = option.get_attribute("value")
    text = option.text.strip()

    if value != "":
        categories.append((value, text))

print("Total Categories :", len(categories))

all_data = []

# ----------------------------
# Loop Categories
# ----------------------------
for category_value, category_name in categories:

    print("=" * 60)
    print("Category :", category_name)

    category_dropdown = Select(driver.find_element(By.ID, "teaprice-category"))
    category_dropdown.select_by_value(category_value)

    time.sleep(3)

    # ----------------------------
    # Get Year/Month list
    # ----------------------------
    year_dropdown = Select(driver.find_element(By.ID, "teaprice-year"))

    year_values = []

    for option in year_dropdown.options:
        value = option.get_attribute("value")

        if value != "":
            year_values.append(value)

    print("Months :", len(year_values))

    # ----------------------------
    # Loop Year/Month
    # ----------------------------
    for year_value in year_values:

        print("   Scraping :", year_value)

        year_dropdown = Select(driver.find_element(By.ID, "teaprice-year"))
        year_dropdown.select_by_value(year_value)

        time.sleep(3)

        # ----------------------------
        # Read Table
        # ----------------------------
        table = driver.find_element(By.ID, "rate-table")

        html = table.get_attribute("outerHTML")

        soup = BeautifulSoup(html, "html.parser")

        rows = []

        for tr in soup.find_all("tr"):

            cols = [
                td.get_text(strip=True)
                for td in tr.find_all(["th", "td"])
            ]

            if cols:
                rows.append(cols)

        # Skip empty table
        if len(rows) <= 1:
            continue

        headers = rows[0]

        # ----------------------------
        # Save rows
        # ----------------------------
        for row in rows[1:]:

            data = {
                "Category": category_name,
                "YearMonth": year_value
            }

            for h, v in zip(headers, row):
                data[h] = v

            all_data.append(data)

# ----------------------------
# Save Excel
# ----------------------------
df = pd.DataFrame(all_data)

output_file = "tea_statistics_all.xlsx"

df.to_excel(output_file, index=False)

print("=" * 60)
print("Done")
print("Rows :", len(df))
print("Saved :", output_file)

driver.quit()