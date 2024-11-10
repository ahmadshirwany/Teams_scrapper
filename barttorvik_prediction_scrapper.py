import requests
from bs4 import BeautifulSoup
import pandas as pd
from dicord_bot import DiscordWebhook
import traceback
import datetime
import sqlite3


class HTMLTableExtractor:
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
        soup = BeautifulSoup(html_content, 'html.parser')
        datestr = soup.find('h1').text.split(' ')[-1].rstrip().split()[0]
        date_obj = datetime.datetime.strptime(datestr, '%m/%d/%Y')
        table = soup.find('table')  # You can modify this to locate the specific table
        # Extract the headers
        rows_tag = table = soup.find('tbody')
        self.table_data = []
        for row in rows_tag.find_all('tr')[0:]:
            print(row.text)
            row_data = []
            row_data.append(date_obj)
            tags = row.find_all('td')
            row_data.append(tags[0].text)
            team_1 = tags[1].find_all('a')[0].text
            if '(' in team_1:
                team_1 = team_1.split('(')[0].rstrip()
            row_data.append(team_1)
            team_2 = tags[1].find_all('a')[1].text
            if '(' in team_2:
                team_2 = team_2.split('(')[0].rstrip()
            row_data.append(team_2)
            if '-' in tags[2].text:
                row_data.append(tags[2].text.split('-')[0].rstrip())
                if team_1 in tags[2].text.split(',')[0].split('-')[0].rstrip():
                    highest = 1
                else:
                    highest = 2
                score_list = tags[2].text.split(',')[1].rstrip().split(' ')[1].split('-')
                score_list = [int(a) for a in score_list]
                if highest == 1:
                    row_data
                    row_data.append(max(score_list))
                    row_data.append(min(score_list))
                elif highest == 2:
                    row_data.append(min(score_list))
                    row_data.append(max(score_list))
                row_data.append(max(score_list) + min(score_list))
                row_data.append(min(score_list) - max(score_list))
            else:
                row_data.append(tags[2].text.split('(')[0].rstrip())
                row_data.append(None)
                row_data.append(None)
                row_data.append(None)
                row_data.append(None)
            if row_data:
                self.table_data.append(row_data)

        header = ['date', 'Time', 'Team_1', 'Team_2', 'Team1_Score', 'Team_2_Score', ]
        conn = sqlite3.connect('sports_data.db')
        cursor = conn.cursor()

        # SQL command to create the table
        create_table_query = '''
            CREATE TABLE IF NOT EXISTS barttorvik_predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date_ DATETIME,
                time_ TEXT,
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
        INSERT OR IGNORE INTO barttorvik_predictions (date_, time_, team_1, team_2,winning_team, team1_score, team2_score, total_score, score_diffrence)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?,?);
        '''
        cursor.execute('''
                CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_match ON barttorvik_predictions (date_, team_1, team_2);
                ''')
        for record in self.table_data:
            cursor.execute(insert_query, record)

        self.table_data.insert(0, header)
        conn.commit()
        conn.close()
        print('data')

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
    html_extractor = HTMLTableExtractor("https://www.barttorvik.com/schedule.php")
    html_extractor.parse_table()
    DiscordWebhook().send_message(
        'barttorvik_prediction_scrapper_completed ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
except Exception as ex:
    traceback.print_exc()
    print(ex)
    error_message = str(ex).splitlines()[0]  # Gets only the first line of the error message
    print(error_message)
    DiscordWebhook().send_message('barttorvik_prediction_scrapper Failed ' + datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + "\n" + error_message)
