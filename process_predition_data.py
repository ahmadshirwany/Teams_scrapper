import sqlite3
import datetime
import json

import traceback
from dicord_bot import DiscordWebhook


def find_closest_key_value(data_dict, target):
    closest_key = None
    closest_value = None
    min_difference = float('inf')

    for key, value in data_dict.items():
        difference = abs(value - target)
        if difference < min_difference:
            min_difference = difference
            closest_key = key
            closest_value = value
    return closest_key, closest_value


def oddshark_data_sort(oddshark_match, team_1, team_2):
    data = []
    if oddshark_match[2] == team_1:
        data.append(oddshark_match[4])
        data.append(oddshark_match[5])
    else:
        data.append(oddshark_match[5])
        data.append(oddshark_match[4])
    return data


def batrovic_data_sort(batrovic_match, team_1, team_2):
    data = []
    winnig_score = max(batrovic_match[6:8])
    losing_score = min(batrovic_match[6:8])
    winning_team = batrovic_match[5]
    if winning_team == team_1:
        data.append(float(winnig_score))
        data.append(float(losing_score))
        odd = float(winnig_score - losing_score)
    else:
        data.append(float(losing_score))
        data.append(float(winnig_score))
        odd = float(losing_score - winnig_score)
    data.append(batrovic_match[8])
    data.append(odd)
    return data


def haslametrics_data_sort(haslametrics_match, team_1, team_2):
    data = []
    winnig_score = max(haslametrics_match[5:7])
    losing_score = min(haslametrics_match[5:7])
    winning_team = haslametrics_match[4]
    if winning_team == team_1:
        data.append(winnig_score)
        data.append(losing_score)
        odd = float(winnig_score - losing_score)
    else:
        data.append(losing_score)
        data.append(winnig_score)
        odd = float(losing_score - winnig_score)
    data.append(haslametrics_match[7])
    data.append(odd)
    return data


def find_matching_dicts(dicts, value):
    for d in dicts:
        if value in d.values():
            return d
    return None


try:
    with open('team_names.json', 'r') as json_file:
        team_names = json.load(json_file)
    team_names_list = [list(d.values()) for d in team_names]
    conn = sqlite3.connect('sports_data.db')
    cursor = conn.cursor()
    latest_date_query = '''
        SELECT MAX(date_) FROM oddshark_predictions;
    '''
    cursor.execute(latest_date_query)
    latest_date = cursor.fetchone()[0]
    latest_date_obj = datetime.datetime.strptime(latest_date, "%Y-%m-%d")

    latest_date_query_oddshark = '''
        SELECT * FROM oddshark_predictions
        WHERE date_ = (SELECT MAX(date_) FROM oddshark_predictions);
    '''
    cursor.execute(latest_date_query_oddshark)
    latest_records_oddshark = cursor.fetchall()

    specific_date_query_evanmiya_predictions = '''
        SELECT * FROM evanmiya_predictions 
        WHERE Date = ?;
    '''
    cursor.execute(specific_date_query_evanmiya_predictions, (latest_date_obj,))
    latest_records_evanmiya = cursor.fetchall()

    specific_date_query_barttorvik_predictions = '''
        SELECT * FROM barttorvik_predictions 
        WHERE date_ = ?;
    '''
    cursor.execute(specific_date_query_barttorvik_predictions, (latest_date_obj,))
    latest_records_barttorvik = cursor.fetchall()

    specific_date_query_haslametrics_predictions = '''
        SELECT * FROM haslametrics_predictions 
        WHERE date_ = ?;
    '''
    cursor.execute(specific_date_query_haslametrics_predictions, (latest_date_obj,))
    latest_records_haslametrics = cursor.fetchall()
    table_data = []
    for match in latest_records_evanmiya:
        team_1 = match[0]
        team_2 = match[1]
        # if team_1 == 'Montana':
        #      print()
        if 'Louisiana-Lafayette' == team_1:
            print()
        team1_matching_dict = find_matching_dicts(team_names, match[0])
        team2_matching_dict = find_matching_dicts(team_names, match[1])
        team1_matching_list = list(team1_matching_dict.values())
        team2_matching_list = list(team2_matching_dict.values())

        batrovic_match = [a for a in latest_records_barttorvik if
                          a[3] in team1_matching_list + team2_matching_list and a[
                              4] in team1_matching_list + team2_matching_list]
        haslametrics_match = [a for a in latest_records_haslametrics if
                              a[2] in team1_matching_list + team2_matching_list and a[
                                  3] in team1_matching_list + team2_matching_list]
        oddshark_match = [a for a in latest_records_oddshark if a[2] in team1_matching_list + team2_matching_list and a[
            3] in team1_matching_list + team2_matching_list]
        row = []
        check_dict = {}
        row.append(latest_date_obj)
        row.append(team_1)
        row.append(team_2)
        row.append(float(match[4]))
        row.append(float(match[5]))
        row.append(float(match[8]))
        row.append(float(match[6]))
        check_dict['evanmiya'] = float(match[6])
        if batrovic_match and None not in batrovic_match[0]:
            batrovic_data = batrovic_data_sort(batrovic_match[0], team_1, team_2)
            check_dict['batrovic'] = batrovic_data[3]
        else:
            batrovic_data = ['', '', '', '']
        row = row + batrovic_data
        if haslametrics_match:
            haslametrics_data = haslametrics_data_sort(haslametrics_match[0], team_1, team_2)
            check_dict['haslametrics'] = haslametrics_data[3]
        else:
            haslametrics_data = ['', '', '', '']
        row = row + haslametrics_data
        if oddshark_match:
            oddshark_data = oddshark_data_sort(oddshark_match[0], team_1, team_2)
            if ' Ev' in oddshark_data:
                oddshark_data = ['', '']
                key = ""
            else:
                key, value = find_closest_key_value(check_dict, oddshark_data[0])
        else:
            oddshark_data = ['', '']
            key = ""
        row = row + oddshark_data

        row.append(key)
        row.append('')

        table_data.append(row)
    header = ['Date', 'Team 1', 'Team 2', 'Evanmiya Team 1 Score', 'Evanmiya Team 2 Score', 'Evanmiya Total',
              'Evanmiya odds'
        , 'barttorvik Team 1 Score', 'barttorvik Team 2 Score', 'barttorvik Total', 'barttorvik odds'
        , 'haslametrics Team 1 Score', 'haslametrics Team 2 Score', 'haslametrics Total', 'haslametrics odds'
        , 'Oddshark Team1 odds', 'Oddshark Team 2 odds', 'closest_odds', 'match_result']

    create_table_query = '''
        CREATE TABLE IF NOT EXISTS odd_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_ DATETIME,
            team_1 TEXT,
            team_2 TEXT,
            evanmiya_team_1_score REAL,
            evanmiya_team_2_score REAL,
            evanmiya_total REAL,
            evanmiya_odds REAL,
            barttorvik_team_1_score REAL,
            barttorvik_team_2_score REAL,
            barttorvik_total REAL,
            barttorvik_odds REAL,
            haslametrics_team_1_score REAL,
            haslametrics_team_2_score REAL,
            haslametrics_total REAL,
            haslametrics_odds REAL,
            oddshark_team_1_odds REAL,
            oddshark_team_2_odds REAL,
            closest_odds TEXT,
            match_result Text
        );
    '''
    cursor.execute(create_table_query)
    create_index_query = '''
        CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_match 
        ON odd_predictions (date_, team_1, team_2);
    '''
    cursor.execute(create_index_query)
    insert_query = '''
        INSERT OR REPLACE INTO odd_predictions 
        (date_, team_1, team_2, evanmiya_team_1_score, evanmiya_team_2_score, evanmiya_total, evanmiya_odds,
         barttorvik_team_1_score, barttorvik_team_2_score, barttorvik_total, barttorvik_odds,
         haslametrics_team_1_score, haslametrics_team_2_score, haslametrics_total, haslametrics_odds,
         oddshark_team_1_odds, oddshark_team_2_odds, closest_odds, match_result)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?);
    '''
    for record in table_data:
        cursor.execute(insert_query, record)
    conn.commit()
    conn.close()
    DiscordWebhook().send_message(
        'prediction_data_processing  completed ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
except Exception as ex:
    traceback.print_exc()
    print(ex)
    DiscordWebhook().send_message(
        'prediction_data_processing Failed ' + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
