import requests
from bs4 import BeautifulSoup
import pandas as pd

class HTMLTableExtractor:
    def __init__(self, url):
        self.url = url
        self.table_data = None
        self.headers = None

    def fetch_page(self):
        # Fake headers to mimic a browser
        # headers = {
        #     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        # }
        from fake_useragent import UserAgent

        ua = UserAgent()

        headers = {
            'User-Agent': ua.random,
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Referer': self.url,
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

        # Extract the headers
        rows = table.find_all('tr')
        self.headers = [header.text.strip() for header in rows[1].find_all('th')]

        # Extract the table data
        self.table_data = []
        for row in rows[2:]:
            cells = row.find_all('td')
            if cells:
                cells_index = [cells[0],cells[1],cells[2],cells[3],cells[4],cells[5],cells[7],cells[9],cells[11],cells[13],cells[15],cells[17],cells[19]]
                row_data = [cell.text.strip() for cell in cells_index]
                self.table_data.append(row_data)

    def to_dataframe(self):
        if self.table_data and self.headers:
            return pd.DataFrame(self.table_data, columns=self.headers)
        else:
            raise Exception("Table data has not been parsed yet. Call `parse_table` first.")

    def save_to_csv(self, file_name):
        df = self.to_dataframe()
        df.to_csv(file_name, index=False)
        print(f"Table saved to {file_name}")

html_extractor = HTMLTableExtractor("https://kenpom.com")
html_extractor.parse_table()
df = html_extractor.to_dataframe()
html_extractor.save_to_csv("kenpom_table.csv")
