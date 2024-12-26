import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.support.ui import Select
import traceback
from dicord_bot import DiscordWebhook
import datetime
import json

with open('credentials.json', 'r') as file:
    data = json.load(file)

username = data['evanmaya']['name']
password = data['evanmaya']['password']


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
        url = "https://evanmiya.com/?game_predictions"
        driver.get(url)
        time.sleep(10)
        driver.execute_script("document.querySelector('.sweet-overlay').style.display='none';")
        driver.execute_script("document.querySelector('.sweet-alert').style.display='none';")
        driver.find_element(By.XPATH, '//*[@id="login-login_button"]').click()
        time.sleep(2)
        username_key = driver.find_element(By.XPATH, '//*[@id="login-email_login"]')
        password_key = driver.find_element(By.XPATH, '//*[@id="login-password_login"]')
        username_key.send_keys(username)
        password_key.send_keys(password)
        driver.find_element(By.XPATH, '//*[@id="login-login"]').click()
        time.sleep(10)
        self.headers = driver.find_elements(By.CLASS_NAME, 'rt-thead')[-1].text.split('\n')
        dropdown = driver.find_element(By.XPATH,
                                       '//*[@id="game_predictions_page-predict_games"]/div/div[2]/div[1]/div[2]/select')
        select = Select(dropdown)
        options = select.options
        values = [int(option.text) for option in options if option.text.replace('.', '', 1).isdigit()]
        max_value = max(values)
        select.select_by_visible_text(str(max_value))
        time.sleep(3)
        page_source = driver.page_source
        return driver, page_source

    def parse_table(self):
        driver, html_content = self.fetch_page()
        self.table_data = []
        Next = True
        while (Next):
            next_button = driver.find_element(By.XPATH,
                                              '//*[@id="game_predictions_page-predict_games"]/div/div[2]/div[2]/button[6]')
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            driver.execute_script("window.scrollTo(0, 400);")
            table = driver.find_elements(By.CLASS_NAME, 'rt-table')[-1]
            soup = BeautifulSoup(table.get_attribute('outerHTML'), 'html.parser')
            table_rows = soup.find_all('div', class_='rt-tr-group')
            for row in table_rows:
                cells = row.find_all('div', class_='rt-td')
                row_data = [cell.get_text(strip=True) for cell in cells[1:]]
                row_data[13] = datetime.datetime.strptime(row_data[13], "%Y-%m-%d")
                self.table_data.append(row_data)
            if next_button.is_enabled():
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(3)
            else:
                Next = False
        self.headers = [a.text for a in soup.find_all('div', class_='rt-th')[1:] if a.text != '']
        conn = sqlite3.connect('sports_predictions.db')
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS evanmiya_predictions (
            Home TEXT,
            Away TEXT,
            Home_Rank INTEGER,
            Away_Rank INTEGER,
            Home_Score REAL,
            Away_Score REAL,
            Line REAL,
            Vegas_Line REAL,
            OU REAL,
            Vegas_OU REAL,
            Home_Win_Prob TEXT,
            Away_Win_Prob TEXT,
            Venue TEXT,
            Date DATE,
            Time TEXT,
            UNIQUE(Home, Away, Date) -- unique index on Home, Away, and Date
        )
        ''')
        insert_query = '''
        INSERT OR REPLACE INTO evanmiya_predictions (
            Home, Away, Home_Rank, Away_Rank, Home_Score, Away_Score, Line, Vegas_Line, OU, Vegas_OU,
            Home_Win_Prob, Away_Win_Prob, Venue, Date, Time
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        # Execute the insertion with values
        for values in self.table_data:
            cursor.execute(insert_query, values)

        conn.commit()
        conn.close()
        driver.close()

    def to_dataframe(self):
        if self.table_data and self.headers:
            return pd.DataFrame(self.table_data, columns=self.headers)
        else:
            raise Exception("Table data has not been parsed yet. Call `parse_table` first.")

    def save_to_csv(self, file_name):
        df = self.to_dataframe()
        df.to_csv(file_name, index=False)
        print(f"Table saved to {file_name}")


try:
    url = "https://www.evanmiya.com/?team_ratings"
    html_extractor = HTMLTableExtractorSelenium(url)
    html_extractor.parse_table()
    DiscordWebhook().send_message(
        'evanmiya_prediction_scrapper Sucessfull ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
except Exception as ex:
    traceback.print_exc()
    print(ex)
    error_message = str(ex).splitlines()[0]  # Gets only the first line of the error message
    print(error_message)
    DiscordWebhook().send_message('evanmiya_prediction_scrapper Failed ' + datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + "\n" + error_message)
