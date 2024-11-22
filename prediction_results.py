import requests
from bs4 import BeautifulSoup
import pandas as pd
from dicord_bot import DiscordWebhook
import traceback
import datetime
import sqlite3
import json

class HTMLTableExtractor:
    def __init__(self, url):
        self.url = url
        self.table_data = None
        self.headers = None

    def fetch_page(self, url):
        # Fake headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.text
        elif response.status_code == 403:
            raise Exception("Access forbidden. The site may be blocking automated requests.")
        else:
            raise Exception(f"Failed to retrieve the page. Status code: {response.status_code}")

    def parse_table(self):
        self.table_data = []
        with open('team_names.json', 'r') as json_file:
            team_names = json.load(json_file)
        team_names_list = [list(d.values()) for d in team_names]
        conn = sqlite3.connect('sports_data.db')
        cursor = conn.cursor()
        find_duplicates_query = '''
            DELETE FROM odd_predictions
            WHERE rowid NOT IN (
                SELECT MIN(rowid)
                FROM odd_predictions
                GROUP BY date_, team_1, team_2
            );
        '''

        cursor.execute(find_duplicates_query)
        conn.commit()
        print(
            "Duplicates removed, keeping only the first occurrence of each unique combination of date_, team_1, and team_2.")


        print("Unique index created on columns date_, team_1, and team_2.")
        cursor.execute('''
                SELECT date_, team_1, team_2, evanmiya_team_1_score, evanmiya_team_2_score, evanmiya_total, evanmiya_odds,
               barttorvik_team_1_score, barttorvik_team_2_score, barttorvik_total, barttorvik_odds,
               haslametrics_team_1_score, haslametrics_team_2_score, haslametrics_total, haslametrics_odds,
               oddshark_team_1_odds, oddshark_team_2_odds, closest_odds,match_result
                FROM odd_predictions2;
            ''')
        all_data = cursor.fetchall()
        all_data = [a for a in all_data if a[-1] == '']
        cursor.execute('''SELECT DISTINCT date_
                          FROM odd_predictions2
                          WHERE match_result = '';''')

        dates = cursor.fetchall()
        for date in dates:
            today =  datetime.datetime.today()
            date_obj = datetime.datetime.strptime(date[0], '%Y-%m-%d %H:%M:%S')
            if date_obj.date() >= today.date():
                continue
            date_str =  date_obj.strftime('%Y%m%d')
            url = f'https://www.barttorvik.com/schedule.php?date={date_str}&conlimit='
            html_content = self.fetch_page(url)
            soup = BeautifulSoup(html_content, 'html.parser')
            table = soup.find('table')  # You can modify this to locate the specific table
            # Extract the headers
            rows_tag = table = soup.find('tbody')
            for row in rows_tag.find_all('tr')[0:-1]:
                # if 'Mississippi' in row.text:
                #     print()
                tags = row.find_all('td')
                team_1 = tags[1].find_all('a')[0].text
                if '(' in team_1:
                    team_1 = team_1.split('(')[0].rstrip()
                team_2 = tags[1].find_all('a')[1].text
                if '(' in team_2:
                    team_2 = team_2.split('(')[0].rstrip()
                team_1_list = [a for a in team_names_list if team_1 in a ]
                if team_1_list:
                    team_1_list = team_1_list[0]
                team_2_list = [a for a in team_names_list if team_2 in a ]
                if team_2_list:
                    team_2_list = team_2_list[0]
                match = [a for a in all_data if a[1] in team_1_list+ team_2_list and a[2] in team_1_list+ team_2_list and date[0] == a[0] ]
                if match:
                    match = list(match[0])
                    match[-1] = tags[-1].text
                    self.table_data.append(match)
                else:
                    print()
        conn = sqlite3.connect('sports_data.db')
        cursor = conn.cursor()
        create_index_query = '''
                CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_match 
                ON odd_predictions2 (date_, team_1, team_2);
            '''
        cursor.execute(create_index_query)
        conn.commit()
        insert_query = '''
                REPLACE INTO odd_predictions2 
                (date_, team_1, team_2, evanmiya_team_1_score, evanmiya_team_2_score, evanmiya_total, evanmiya_odds,
                 barttorvik_team_1_score, barttorvik_team_2_score, barttorvik_total, barttorvik_odds,
                 haslametrics_team_1_score, haslametrics_team_2_score, haslametrics_total, haslametrics_odds,
                 oddshark_team_1_odds, oddshark_team_2_odds, closest_odds, match_result)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?);
            '''
        for record in self.table_data:
            cursor.execute(insert_query, record)

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
        'prediction_results completed ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
except Exception as ex:
    traceback.print_exc()
    print(ex)
    error_message = str(ex).splitlines()[0]  # Gets only the first line of the error message
    print(error_message)
    DiscordWebhook().send_message('prediction_results Failed ' + datetime.datetime.now().strftime(
         "%Y-%m-%d %H:%M:%S") + "\n" + error_message)
