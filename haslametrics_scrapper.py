import datetime
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
import re
from dicord_bot import DiscordWebhook
import traceback


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
        time.sleep(5)
        page_source = driver.page_source
        return driver, page_source

    def parse_table(self):
        driver, html_content = self.fetch_page()
        self.headers = [a.text for a in driver.find_element(By.XPATH,
                                                            '//*[@id="myTable_wrapper"]/div/div[1]/div/table/thead/tr[3]').find_elements(
            By.TAG_NAME, 'th')]
        rows = driver.find_element(By.XPATH, '//*[@id="myTable"]/tbody')
        html_content = rows.get_attribute('outerHTML')
        soup = BeautifulSoup(html_content, 'html.parser')
        self.table_data = []
        for row in soup.find_all('tr'):
            data = [a.text for a in row.find_all('td')]
            if data[1].count('(') > 1:
                data = [a.text for a in row.find_all('td')]
                result  = re.findall(r'^[^\(]+\([^\)]+\)|\(\d{2}-\d{2}\)', data[1])
                data[1] = result[0]
            else:
                data[1] = data[1].split('(')[0]
            self.table_data.append(data)
        driver.close()

    def to_dataframe(self):
        if self.table_data and self.headers:
            return pd.DataFrame(self.table_data, columns=self.headers)
        else:
            raise Exception("Table data has not been parsed yet. Call `parse_table` first.")

    def save_to_csv(self, file_name):
        df = self.to_dataframe()
        df['Team'] = df['Team'].str.rstrip()
        df.to_csv(file_name, index=False)
        print(f"Table saved to {file_name}")


try:
    url = "https://www.haslametrics.com/"  # Change to the correct URL if needed
    html_extractor = HTMLTableExtractorSelenium(url)
    html_extractor.parse_table()
    df = html_extractor.to_dataframe()
    html_extractor.save_to_csv("haslametrics_table.csv")

    DiscordWebhook().send_message('haslametrics scrapper Sucessfull ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
except Exception as ex:
    traceback.print_exc()
    print(ex)
    DiscordWebhook().send_message('haslametrics scrapper Failed '+ datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
