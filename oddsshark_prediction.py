import requests
from bs4 import BeautifulSoup
import pandas as pd
from dicord_bot import DiscordWebhook
import traceback
import datetime
import sqlite3


class HTMLTableExtractorSelenium:
    def __init__(self, url):
        self.url = url
        self.table_data = None
        self.headers = None

    def fetch_page(self):
        # Fake headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

        response = requests.get(self.url, headers=headers)
        if response.status_code == 200:
            return response.text
        elif response.status_code == 403:
            raise Exception("Access forbidden. The site may be blocking automated requests.")
        else:
            raise Exception(f"Failed to retrieve the page. Status code: {response.status_code}")

    def parse_table(self):
        html_content = self.fetch_page()
        self.table_data = []
        soup = BeautifulSoup(html_content, 'html.parser')
        date_list = soup.find_all('span', class_='long-date')
        events_list = soup.find_all('div', class_='odds--group__events-container')
        for index, date_obj in enumerate(date_list):
            date_str = date_obj.text
            current_year = datetime.datetime.now().year
            date_obj = datetime.datetime.strptime(f"{date_str} {current_year}", "%A, %B %d %Y").date()
            events = events_list[index].find_all('div', class_='odds--group__event-container')

            for event in events:
                row = []
                teams = event.find('div', class_='odds--group__event-participants').text.split('VS /')
                team1 = teams[0].rstrip()
                if 'STTMN' in team1:
                    print()
                print(team1)
                team1 = team1.replace(team1.split(' ')[-1], '', 1).rstrip().lstrip()
                team2 = teams[1].rstrip()
                team2 = team2.replace(team2.split(' ')[-1], '', 1).rstrip().lstrip()
                odds = event.find_all('div', class_='odds-spread')[0:2]
                if odds[0].find('div', attrs={'data-odds-spread': True}) == None:
                    team1_odds = '--'
                    team2_odds = '--'
                else:
                    team1_odds = odds[0].find('div', attrs={'data-odds-spread': True}).text
                    team2_odds = odds[1].find('div', attrs={'data-odds-spread': True}).text
                row.append(date_obj)
                row.append(team1)
                row.append(team2)
                row.append(team1_odds)
                row.append(team2_odds)
                if '' in row:
                    print()
                self.table_data.append(row)
        header = ['date', 'Team_1', 'Team_2', 'Team1_odds', 'Team_2_odds', ]
        conn = sqlite3.connect('sports_data.db')
        cursor = conn.cursor()
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS oddshark_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_ DATETIME,
                team_1 TEXT,
                team_2 TEXT,
                Team1_odds INTEGER,
                Team_2_odds INTEGER
            );
        '''

        cursor.execute(create_table_query)
        cursor.execute(''' CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_match ON oddshark_predictions (date_, team_1, team_2);
                               ''')
        insert_query = '''
            INSERT OR REPLACE INTO oddshark_predictions 
            (date_, team_1, team_2, Team1_odds, Team_2_odds) 
            VALUES (?, ?, ?, ?, ?);
        '''
        for record in self.table_data:
            date_, team_1, team_2, Team1_odds, Team_2_odds = record

            # Check if the record exists
            cursor.execute('''
                SELECT 1 FROM oddshark_predictions 
                WHERE date_ = ? AND team_1 = ? AND team_2 = ?;
            ''', (date_, team_1, team_2))

            if cursor.fetchone() is None:
                # Record does not exist, insert it
                cursor.execute(insert_query, record)
        conn.commit()
        conn.close()


try:
    html_extractor = HTMLTableExtractorSelenium("https://www.oddsshark.com/ncaab/odds")
    html_extractor.parse_table()
    DiscordWebhook().send_message(
        'oddshark_scrapper completed ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
except Exception as ex:
    traceback.print_exc()
    print(ex)
    error_message = str(ex).splitlines()[0]  # Gets only the first line of the error message
    print(error_message)
    DiscordWebhook().send_message(
        'oddshark_scrapper Failed ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n" + error_message)
