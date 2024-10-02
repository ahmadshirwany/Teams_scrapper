import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.support.ui import Select

class HTMLTableExtractorSelenium:
    def __init__(self, url):
        self.url = url
        self.table_data = None
        self.headers = None

    def fetch_page(self):
        # Setup Chrome WebDriver using ChromeDriverManager
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")  # Run in headless mode
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-search-engine-choice-screen')
        options.add_argument("--log-level=3")
        options.add_argument("--silent")
        options.add_argument("--disable-gpu")
        options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        # Initialize the WebDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(self.url)
        time.sleep(5)
        dropdown = driver.find_element(By.XPATH,
                                       '//*[@id="team_ratings_page-team_ratings"]/div/div[2]/div[1]/div[2]/select')
        select = Select(dropdown)
        options = select.options
        values = [int(option.text) for option in options if option.text.replace('.', '', 1).isdigit()]
        max_value = max(values)
        select.select_by_visible_text(str(max_value))
        page_source = driver.page_source
        return driver,page_source

    def parse_table(self):
        driver,html_content = self.fetch_page()
        self.headers = driver.find_elements(By.CLASS_NAME,'rt-thead')[-1].text.split('\n')
        # driver.close()
        soup = BeautifulSoup(html_content, 'html.parser')

        row_elements = soup.find_all('div', class_='rt-tr-group')
        self.table_data = []
        if row_elements:
            for row in row_elements:
                columns = row.find_all('div', class_='rt-td-inner')
                column_values = [col.get_text(strip=True) for col in columns]
                self.table_data.append(column_values)
        else:
            print("No elements found")
        self.table_data = self.table_data[100:]




    def to_dataframe(self):
        if self.table_data and self.headers:
            return pd.DataFrame(self.table_data, columns=self.headers)
        else:
            raise Exception("Table data has not been parsed yet. Call `parse_table` first.")

    def save_to_csv(self, file_name):
        df = self.to_dataframe()
        df.to_csv(file_name, index=False)
        print(f"Table saved to {file_name}")

# Usage
url = "https://www.evanmiya.com/?team_ratings"  # Change to the correct URL if needed
html_extractor = HTMLTableExtractorSelenium(url)
html_extractor.parse_table()
df = html_extractor.to_dataframe()
html_extractor.save_to_csv("evanmiya_table.csv")
