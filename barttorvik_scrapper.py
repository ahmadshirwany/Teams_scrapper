import requests
from bs4 import BeautifulSoup
import pandas as pd
from dicord_bot import DiscordWebhook
import traceback
import datetime
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
        table = soup.find('table')  # You can modify this to locate the specific table
        colums_tag =  table = soup.find('thead')
        self.headers = [a.text for a in colums_tag.find_all('tr')[1].find_all('th')[0:]]
        self.table_data = []
        # Extract the headers
        rows_tag = table = soup.find('tbody')
        for row in rows_tag.find_all('tr')[0:]:
            tags = row.find_all('td')
            for tag in tags:
                # Find all <span> elements within the <a> tag
                spans = tag.find_all('span')

                # Decompose each <span> (remove it from the tag)
                for span in spans:
                    span.decompose()
            row_data =  [a.text for a in tags]
            if row_data:
                self.table_data.append(row_data)
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
    html_extractor = HTMLTableExtractor("https://www.barttorvik.com/#")
    html_extractor.parse_table()
    df = html_extractor.to_dataframe()
    html_extractor.save_to_csv("barttorvik_table.csv")
    DiscordWebhook().send_message('barttorvik_scrapper_completed ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
except Exception as ex:
    traceback.print_exc()
    print(ex)
    DiscordWebhook().send_message('barttorvik_scrapper Failed ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
