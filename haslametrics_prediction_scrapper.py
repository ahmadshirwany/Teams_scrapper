import datetime
import sqlite3
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
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
        date = datetime.datetime.strptime(
            driver.find_element(By.XPATH, '//*[@id="cboUpcomingDates"]').text.split('\n')[0], '%A, %B %d, %Y')
        table = driver.find_element(By.XPATH, '//*[@id="myTable4"]')
        odd_list = table.find_elements(By.CLASS_NAME, 'odd')
        odd_list = [a for a in odd_list if a.text != '' and ':' not in a.text]
        even_list = table.find_elements(By.CLASS_NAME, 'even')
        even_list = [a for a in even_list if a.text != '' and a.text != ' ']
        self.table_data = []
        for a in range(len(odd_list)):
            odd_data = odd_list[a]
            even_data = even_list[a]
            odd_matches = [a.text for a in odd_data.find_elements(By.TAG_NAME, 'td') if a.text != '']
            even_matches = [a.text for a in even_data.find_elements(By.TAG_NAME, 'td') if a.text != '']
            odd_matches = [(odd_matches[i].rsplit(' ', 1)[0], float(odd_matches[i + 1])) for i in
                           range(0, len(odd_matches), 2)]
            even_matches = [(even_matches[i].rsplit(' ', 1)[0], float(even_matches[i + 1])) for i in
                            range(0, len(even_matches), 2)]
            for r in range(len(odd_matches)):
                row = []
                row.append(date)
                row.append(odd_matches[r][0])
                row.append(even_matches[r][0])
                team1_score = float(odd_matches[r][1])
                team2_score = float(even_matches[r][1])
                if team1_score > team2_score:
                    winngteam = 1
                    diffrence = team2_score - team1_score
                else:
                    winngteam = 2
                    diffrence = team1_score - team2_score
                if winngteam == 1:
                    row.append(odd_matches[r][0])
                else:
                    row.append(even_matches[r][0])
                total_score = team1_score + team2_score
                row.append(team1_score)
                row.append(team2_score)
                row.append(total_score)
                row.append(diffrence)
                self.table_data.append(row)

        conn = sqlite3.connect('sports_data.db')
        cursor = conn.cursor()
        create_table_query = '''
                   CREATE TABLE IF NOT EXISTS haslametrics_predictions (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       date_ DATETIME,
                       team_1 TEXT,
                       team_2 TEXT,
                       winning_team TEXT,
                       team1_score INTEGER,
                       team2_score INTEGER,
                       total_score INTEGER,
                       score_diffrence INTEGER
                   );
               '''
        cursor.execute(create_table_query)
        insert_query = '''
               INSERT OR IGNORE INTO haslametrics_predictions (date_, team_1, team_2,winning_team, team1_score, team2_score, total_score, score_diffrence)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?);
               '''
        cursor.execute('''
                       CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_match ON barttorvik_predictions (date_, team_1, team_2);
                       ''')
        for record in self.table_data:
            cursor.execute(insert_query, record)
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
        df['Team'] = df['Team'].str.rstrip()
        df.to_csv(file_name, index=False)
        print(f"Table saved to {file_name}")


try:
    url = "https://www.haslametrics.com/"  # Change to the correct URL if needed
    html_extractor = HTMLTableExtractorSelenium(url)
    html_extractor.parse_table()
    DiscordWebhook().send_message(
        'haslametrics_prediction scrapper Sucessfull ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
except Exception as ex:
    traceback.print_exc()
    print(ex)
    error_message = str(ex).splitlines()[0]  # Gets only the first line of the error message
    print(error_message)
    DiscordWebhook().send_message('haslametrics_prediction scrapper Failed ' + datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + "\n" + error_message)
