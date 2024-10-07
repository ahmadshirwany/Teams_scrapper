import pandas as pd
import difflib
import json


def calculate_average(a=None, b=None, c=None, d=None, e=None):
    values = [a, b, c, d, e]
    valid_values = [val for val in values if val is not None and val != '']
    if len(valid_values) == 0:
        return 0
    average = sum(valid_values) / len(valid_values)
    return average


df_barttorvik = pd.read_csv('barttorvik_table.csv')[['Team', 'Barthag', 'Adj T.']]
df_barttorvik['Barthag'] = (df_barttorvik['Barthag'] / df_barttorvik['Barthag'].max()) * 100
df_haslametrics = pd.read_csv('haslametrics_table.csv')[['Team', 'AP%']]
df_haslametrics['AP%'] = df_haslametrics['AP%'] * 100
df_kenpom = pd.read_csv('kenpom_table.csv')[['Team', 'NetRtg', 'AdjT']]
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
header = ['Team', 'evanmiya', 'barttorvik', 'haslametrics', 'kenpom', 'teamrankings', 'Avg', 'KPOM_TEMPO',
          'Barthag_Tempo', 'EvanMiya_True_Tempo']
table_data = []
for team_name_dict in team_names:
    # print(team_name_dict)
    data_point = []
    data_point.append(team_name_dict['evanmiya'])
    evanmiya_b = df_evanmiya[df_evanmiya['Team'] == team_name_dict['evanmiya']].values.tolist()[0][1]
    barttorvik_b = df_barttorvik[df_barttorvik['Team'] == team_name_dict['barttorvik']].values.tolist()[0][1]
    haslametrics_b = df_haslametrics[df_haslametrics['Team'] == team_name_dict['haslametrics']].values.tolist()[0][1]
    kenpom_b = df_kenpom[df_kenpom['Team'] == team_name_dict['kenpom']].values.tolist()[0][1]

    KPOM_TEMPO = df_kenpom[df_kenpom['Team'] == team_name_dict['kenpom']].values.tolist()[0][2]
    Barthag_Tempo = df_barttorvik[df_barttorvik['Team'] == team_name_dict['barttorvik']].values.tolist()[0][2]
    EvanMiya_True_Tempo = df_evanmiya[df_evanmiya['Team'] == team_name_dict['evanmiya']].values.tolist()[0][2]

    if 'teamrankings' in team_name_dict:
        teamrankings_b = df_teamrankings[df_teamrankings['Team'] == team_name_dict['teamrankings']].values.tolist()[0][
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
    table_data.append(data_point)
table_data.insert(0, header)

from google.oauth2 import service_account
from googleapiclient.discovery import build

creds = service_account.Credentials.from_service_account_file('keys.json')
spreadsheet_id = '1n0FAERGuqFIucRnIzleVWcgQXLkkGqi6EZCTAuSDRpY'
range_name = 'Sheet1!A1'
service = build('sheets', 'v4', credentials=creds)
service.spreadsheets().values().update(
    spreadsheetId=spreadsheet_id,
    range=range_name,
    valueInputOption='RAW',
    body={'values': table_data}
).execute()
print('Data Updated on Spreadsheet')

# result = pd.DataFrame(table_data, columns=header)
# result.to_csv('result.csv')

# all_teams_df = pd.DataFrame({
#     'BartTorvik': df_barttorvik['Team'],
#     'Haslametrics': df_haslametrics['Team'],
#     'KenPom': df_kenpom['Team'],
#     'EvanMiya': df_evanmiya['Team'],
#     'TeamRankings': df_teamrankings['Team']
# })
# all_names = []
# for aa in all_teams_df.values.tolist():
#     for a in aa:
#         all_names.append(a)
#
# all_teams_name = df_evanmiya['Team'].values.tolist()
# teams_dict = {}
# for team in all_teams_name:
#     teams_dict[team] = []
#     for name in all_names:
#         matcher = difflib.SequenceMatcher(None, str(team), str(name))
#         similarity_ratio = matcher.ratio()
#         if similarity_ratio > 0.8:
#             teams_dict[team].append(name)
#
# print(all_names)
