import pandas as pd
import difflib
import json
import traceback
from dicord_bot import DiscordWebhook
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build

def calculate_average(a=None, b=None, c=None, d=None, e=None):
    values = [a, b, c, d, e]
    valid_values = [val for val in values if val is not None and val != '']
    if len(valid_values) == 0:
        return 0
    average = sum(valid_values) / len(valid_values)
    return average


try:
    df_barttorvik = pd.read_csv('barttorvik_table.csv')[['Team', 'Barthag', 'Adj T.']]
    df_barttorvik['Barthag'] = (df_barttorvik['Barthag'] / df_barttorvik['Barthag'].max()) * 100
    df_haslametrics = pd.read_csv('haslametrics_table.csv')[['Team', 'AP%']]
    df_haslametrics['AP%'] = df_haslametrics['AP%'] * 100
    df_kenpom = pd.read_csv('kenpom table.csv')[['Team', 'NetRtg', 'AdjT']]
    max_value = df_kenpom['NetRtg'].max()
    df_kenpom['NetRtg'] = 100 - (max_value - df_kenpom['NetRtg'])
    df_evanmiya = pd.read_csv('evanmiya_table.csv')[['Team', 'Relative Rating', 'True Tempo']]
    max_value = df_evanmiya['Relative Rating'].max()
    df_evanmiya['Relative Rating'] = 100 - (max_value - df_evanmiya['Relative Rating'])
    df_teamrankings = pd.read_csv('teamrankings_table.csv')[['Team', 'Rating']]
    max_value = df_teamrankings['Rating'].max()
    df_teamrankings['Rating'] = 100 - (max_value - df_teamrankings['Rating'])

    with open('team_names.json', 'r') as json_file:
        team_names = json.load(json_file)
    # **********For team_names Testing**********88
    # name_lists = []
    # for team_name_dict in team_names:
    #     print(team_name_dict)
    #     name_lists.append(list(team_name_dict.values()))
    # for a in df_evanmiya.values.tolist():
    #     check = False
    #     for aa in name_lists:
    #         if a[0] in aa:
    #             check = True
    #             break
    #     if check == False:
    #         print()
    header = ['Team', 'evanmiya', 'barttorvik', 'haslametrics', 'kenpom', 'teamrankings', 'Avg', 'KPOM_TEMPO',
              'Barthag_Tempo', 'EvanMiya_True_Tempo', 'Avg_TEMPO']
    table_data = []
    for team_name_dict in team_names:
        print(team_name_dict)
        name_list = list(team_name_dict.values())
        data_point = []
        data_point.append(team_name_dict['evanmiya'])
        evanmiya_b_values = df_evanmiya[df_evanmiya['Team'] == team_name_dict['evanmiya']].values
        if evanmiya_b_values.size > 0:
            evanmiya_b = df_evanmiya[df_evanmiya['Team'] == team_name_dict['evanmiya']].values.tolist()[0][1]
        else:
            evanmiya_b_values = df_evanmiya[df_evanmiya['Team'].isin(name_list)].values
            evanmiya_b = evanmiya_b_values.tolist()[0][1]

        barttorvik_b_values = df_barttorvik[df_barttorvik['Team'] == team_name_dict['barttorvik']].values
        if barttorvik_b_values.size > 0:
            barttorvik_b = df_barttorvik[df_barttorvik['Team'] == team_name_dict['barttorvik']].values.tolist()[0][1]
        else:
            barttorvik_b_values = df_barttorvik[df_barttorvik['Team'].isin(name_list)].values
            barttorvik_b = barttorvik_b_values.tolist()[0][1]

        haslametrics_b_values = df_haslametrics[df_haslametrics['Team'] == team_name_dict['haslametrics']].values
        if haslametrics_b_values.size > 0:
            haslametrics_b = \
                df_haslametrics[df_haslametrics['Team'] == team_name_dict['haslametrics']].values.tolist()[0][1]
        else:
            haslametrics_b_values = df_haslametrics[df_haslametrics['Team'].isin(name_list)].values
            haslametrics_b = haslametrics_b_values.tolist()[0][1]

        kenpom_b_values = df_kenpom[df_kenpom['Team'] == team_name_dict['kenpom']].values
        if kenpom_b_values.size > 0:
            kenpom_b = df_kenpom[df_kenpom['Team'] == team_name_dict['kenpom']].values.tolist()[0][1]
        else:
            if team_name_dict['kenpom'] == 'Cal St. Northridge' or team_name_dict['kenpom'] =='Southeast Missouri St.':
                pass
            else:
                kenpom_b_values = df_kenpom[df_kenpom['Team'].isin(name_list)].values
                kenpom_b = kenpom_b_values.tolist()[0][1]
        if team_name_dict['kenpom'] == 'Cal St. Northridge' or team_name_dict['kenpom'] =='Southeast Missouri St.':
            pass
        else:
            KPOM_TEMPO = kenpom_b_values.tolist()[0][2]
        Barthag_Tempo = barttorvik_b_values.tolist()[0][2]
        EvanMiya_True_Tempo = evanmiya_b_values.tolist()[0][2]

        Avg_TEMPO = calculate_average(KPOM_TEMPO, Barthag_Tempo, EvanMiya_True_Tempo)

        if 'teamrankings' in team_name_dict:
            teamrankings_b = \
            df_teamrankings[df_teamrankings['Team'] == team_name_dict['teamrankings']].values.tolist()[0][
                1]
        else:
            teamrankings_b = ''
        avg = calculate_average(evanmiya_b, barttorvik_b, haslametrics_b, kenpom_b, teamrankings_b)
        data_point.append(evanmiya_b)
        data_point.append(barttorvik_b)
        data_point.append(haslametrics_b)
        data_point.append(kenpom_b)
        data_point.append(teamrankings_b)
        data_point.append(avg)
        data_point.append(KPOM_TEMPO)
        data_point.append(Barthag_Tempo)
        data_point.append(EvanMiya_True_Tempo)
        data_point.append(Avg_TEMPO)
        table_data.append(data_point)
    table_data.insert(0, header)
    creds = service_account.Credentials.from_service_account_file('keys.json')
    spreadsheet_id = '1n0FAERGuqFIucRnIzleVWcgQXLkkGqi6EZCTAuSDRpY'
    range_name = 'Sheet1!A1'
    service = build('sheets', 'v4', credentials=creds)
    service.spreadsheets().values().clear(
        spreadsheetId=spreadsheet_id,
        range=range_name
    ).execute()
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=range_name,
        valueInputOption='RAW',
        body={'values': table_data}
    ).execute()
    print('Data Updated on Spreadsheet')
    DiscordWebhook().send_message('data_processing sucessfull ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
except Exception as ex:
    traceback.print_exc()
    print(ex)
    DiscordWebhook().send_message('data_processing Failed ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

