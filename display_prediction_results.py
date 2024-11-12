import sqlite3
import os
import traceback
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

from dicord_bot import DiscordWebhook

try:
    header = ['Date', 'Team 1', 'Team 2', 'Evanmiya Team 1 Score', 'Evanmiya Team 2 Score', 'Evanmiya Total',
              'Evanmiya odds'

        , 'barttorvik Team 1 Score', 'barttorvik Team 2 Score', 'barttorvik Total', 'barttorvik odds'
        , 'haslametrics Team 1 Score', 'haslametrics Team 2 Score', 'haslametrics Total', 'haslametrics odds'
        , 'Oddshark Team1 odds', 'Oddshark Team 2 odds', 'closest_odds', 'match_result']
    conn = sqlite3.connect('sports_data.db')
    cursor = conn.cursor()
    cursor.execute('''
          SELECT date_, team_1, team_2, evanmiya_team_1_score, evanmiya_team_2_score, evanmiya_total, evanmiya_odds,
                 barttorvik_team_1_score, barttorvik_team_2_score, barttorvik_total, barttorvik_odds,
                 haslametrics_team_1_score, haslametrics_team_2_score, haslametrics_total, haslametrics_odds,
                 oddshark_team_1_odds, oddshark_team_2_odds, closest_odds,match_result
          FROM odd_predictions;
      ''')
    rows = cursor.fetchall()
    rows =[a for a in rows if a[-1] != '']
    conn.close()
    print("Database file path:", os.path.abspath('sports_data.db'))
    print("Data inserted successfully.")
    rows.insert(0, header)
    creds = service_account.Credentials.from_service_account_file('keys.json')

    spreadsheet_id = '1n0FAERGuqFIucRnIzleVWcgQXLkkGqi6EZCTAuSDRpY'
    range_name = 'Sheet2!A1'
    service = build('sheets', 'v4', credentials=creds)
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range='Sheet2!A1:S1000000'
    ).execute()
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='RAW',
        body={'values': rows}
    ).execute()
    DiscordWebhook().send_message('display_prediction_data completed ' + datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") )
except Exception as ex:
    traceback.print_exc()
    print(ex)
    error_message = str(ex).splitlines()[0]  # Gets only the first line of the error message
    print(error_message)
    DiscordWebhook().send_message('display_prediction_data Failed ' + datetime.datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S") + "\n" + error_message)
