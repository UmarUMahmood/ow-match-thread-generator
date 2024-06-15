import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")


def get_match_id():
    match_url = input("Enter match URL: ")
    return match_url.split("/")[-1]


def fetch_data_from_api(url, headers):
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


def get_match_data(match_id, api_key):
    url = f"https://open.faceit.com/data/v4/matches/{match_id}"
    headers = {"accept": "application/json", "Authorization": f"Bearer {api_key}"}
    return fetch_data_from_api(url, headers)


def get_match_stats(match_id, api_key):
    url = f"https://open.faceit.com/data/v4/matches/{match_id}/stats"
    headers = {"accept": "application/json", "Authorization": f"Bearer {api_key}"}
    return fetch_data_from_api(url, headers)


def get_player_details(player_id, api_key):
    url = f"https://open.faceit.com/data/v4/players/{player_id}"
    headers = {"accept": "application/json", "Authorization": f"Bearer {api_key}"}
    return fetch_data_from_api(url, headers)


def get_team_name(faction_id, match_data):
    for team in match_data["teams"].values():
        if team["faction_id"] == faction_id:
            return team["name"]
    return "Failed to get Team Name"


def get_map_name(map_id, match_data):
    for map_entity in match_data["voting"]["map"]["entities"]:
        if map_entity["game_map_id"] == map_id:
            return map_entity["name"]
    return "Failed to get Map Name"


def get_player_name(player_id, match_data, api_key):
    for team in match_data["teams"].values():
        for player in team["roster"]:
            if player["player_id"] == player_id:
                return player["game_player_name"]
    player_details = get_player_details(player_id, api_key)
    return player_details["games"]["ow2"]["game_player_name"]


def get_team_stats(team_index, map_index, match_stats, match_data, api_key):
    team_stats = []
    for player_data in match_stats["rounds"][map_index]["teams"][team_index]["players"]:
        player_stats = {
            "name": get_player_name(player_data["player_id"], match_data, api_key),
            "player_stats": player_data["player_stats"],
        }
        team_stats.append(player_stats)
    role_order = {"Tank": 0, "Damage": 1, "Support": 2}
    return sorted(
        team_stats, key=lambda x: (role_order[x["player_stats"]["Role"]], x["name"])
    )


def generate_title(match_data):
    team1 = match_data["teams"]["faction1"]["name"]
    team2 = match_data["teams"]["faction2"]["name"]
    competition_name = match_data["competition_name"]
    return f"{team1} vs. {team2} / {competition_name} / Post-Match Discussion"


def generate_header(match_data):
    team1 = match_data["teams"]["faction1"]["name"]
    team2 = match_data["teams"]["faction2"]["name"]
    competition_name = match_data["competition_name"]
    print(f"###{competition_name}")
    print(f"[FACEIT Match Overview]({match_data['faceit_url']})\n")
    print("---")
    print(
        f"###{team1} {match_data['results']['score']['faction1']}-{match_data['results']['score']['faction2']} {team2}"
    )
    print("---")


def generate_map_scores(match_data):
    team1 = match_data["teams"]["faction1"]["name"]
    team2 = match_data["teams"]["faction2"]["name"]
    team1_score = match_data["results"]["score"]["faction1"]
    team2_score = match_data["results"]["score"]["faction2"]
    map_scores_table = (
        f"|{team1}|{team1_score}-{team2_score}|{team2}|\n|--:|:--:|:--|\n"
    )
    maps = match_data["voting"]["map"]["entities"]
    picked_maps_ids = match_data["voting"]["map"]["pick"]
    picked_maps = [m["name"] for m in maps if m["game_map_id"] in picked_maps_ids]
    for i, result in enumerate(match_data["detailed_results"]):
        map_score = f"|{result['factions']['faction1']['score']}|{picked_maps[i]}|{result['factions']['faction2']['score']}|\n"
        map_scores_table += map_score
    return map_scores_table


def generate_map_scoreboards(match_stats, match_data, api_key):
    for i, round_data in enumerate(match_stats["rounds"]):
        map_name = get_map_name(round_data["round_stats"]["Map"], match_data)
        winner_name = get_team_name(round_data["round_stats"]["Winner"], match_data)
        print(f"###MAP {i+1}: {round_data['round_stats']['OW2 Mode']} - {map_name}")
        print(
            f"**Winner: {winner_name}** - {round_data['round_stats']['Score Summary']}\n"
        )
        stats_header = "|E|A|D|K/D|DMG|H|MIT|"
        for team_index in range(2):
            team_name = get_team_name(
                round_data["teams"][team_index]["team_id"], match_data
            )
            print(f"{team_name}{stats_header}")
            print("--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:")
            team_stats = get_team_stats(team_index, i, match_stats, match_data, api_key)
            for player in team_stats:
                stats_row = (
                    f"{player['name']}|{player['player_stats']['Eliminations']}|"
                    f"{player['player_stats']['Assists']}|{player['player_stats']['Deaths']}|"
                    f"{player['player_stats']['K/D Ratio']}|{player['player_stats']['Damage Dealt']}|"
                    f"{player['player_stats']['Healing Done']}|{player['player_stats']['Damage Mitigated']}|"
                )
                print(stats_row)
            print("---")


match_id = get_match_id()
match_data = get_match_data(match_id, API_KEY)
match_stats = get_match_stats(match_id, API_KEY)

print(generate_title(match_data))
generate_header(match_data)
print(generate_map_scores(match_data))
generate_map_scoreboards(match_stats, match_data, API_KEY)
