from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import pandas as pd

class HTMLTableExtractorSelenium:
    def __init__(self, url):
        self.url = url
        self.table_data = None
        self.headers = None

    def fetch_page(self):
        # Setup Chrome WebDriver using ChromeDriverManager
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run in headless mode
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

        # Wait for the page to load (and potentially JavaScript-rendered content)
        WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.TAG_NAME, 'table'))  # Wait for a table to be present
        )

        # Get the page source after the content has fully loaded
        page_source = driver.page_source

        # Close the browser
        driver.quit()

        return page_source

    def parse_table(self):
        html_content = self.fetch_page()
        soup = BeautifulSoup(html_content, 'html.parser')

        # Find the first table (or modify this if you need to locate a specific table)
        table = soup.find('table')

        if table:
            # Extract the headers
            rows = table.find_all('tr')
            self.headers = [header.text.strip() for header in rows[1].find_all('th')]

            # Extract the table data
            self.table_data = []
            for row in rows[2:]:
                cells = row.find_all('td')
                if cells:
                    cells_index = [cells[0], cells[1], cells[2], cells[3], cells[4], cells[5], cells[7], cells[9],
                                   cells[11], cells[13], cells[15], cells[17], cells[19]]
                    row_data = [cell.text.strip() for cell in cells_index]
                    self.table_data.append(row_data)
        else:
            raise Exception("No table found on the page.")

    def to_dataframe(self):
        if self.table_data and self.headers:
            return pd.DataFrame(self.table_data, columns=self.headers)
        else:
            raise Exception("Table data has not been parsed yet. Call `parse_table` first.")

    def save_to_csv(self, file_name):
        df = self.to_dataframe()
        df['Team'] = df['Team'].str.replace(r'\s\d+$', '', regex=True)
        df.to_csv(file_name, index=False)
        print(f"Table saved to {file_name}")

# Usage
url = "https://kenpom.com"  # Change to the correct URL if needed
html_extractor = HTMLTableExtractorSelenium(url)
html_extractor.parse_table()
df = html_extractor.to_dataframe()
html_extractor.save_to_csv("kenpom_table.csv")
